"""Core Code Quality Intelligence Agent using LangChain and Groq."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .config import Config
from .analyzers import CodeAnalyzer
from .report_generator import ReportGenerator
from .rag_system import CodeRAGSystem
from .chatbot import CodeQualityChatbot
from .utils.file_handler import FileHandler


class CodeQualityAgent:
    """Main Code Quality Intelligence Agent."""
    
    def __init__(self):
        """Initialize the agent with Groq LLM."""
        Config.validate()
        
        self.llm = None
        if Config.has_groq_api_key():
            self.llm = ChatGroq(
                groq_api_key=Config.get_groq_api_key(),
                model_name=Config.DEFAULT_MODEL,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
        
        self.memory = ConversationBufferMemory(return_messages=True)
        self.analyzer = CodeAnalyzer()
        self.report_generator = ReportGenerator()
        self.file_handler = FileHandler()
        
        # Initialize enhanced features
        self.rag_system = CodeRAGSystem()
        self.chatbot = CodeQualityChatbot(self.rag_system)
        
        # Initialize analysis runnables
        self._setup_analysis_chain()
        self._setup_qa_chain()
    
    def _setup_analysis_chain(self):
        """Setup the code analysis chain."""
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert code quality analyst. Return STRICT JSON only, no prose."),
            ("human",
             "Analyze the following {language} code from file {filename} and identify quality issues.\n\n"
             "Focus on: security, performance, complexity, duplication, testing, documentation, maintainability, best_practices.\n\n"
             "Code to analyze:\n```{language}\n{code}\n```\n\n"
             "Respond with a JSON object with keys: issues (array of objects: category, severity, line_number, title, description, suggestion, code_snippet), metrics (object with complexity_score, maintainability_score, security_score, overall_score), summary (string). Do not include any text outside JSON.")
        ])

        if self.llm:
            self.analysis_runnable = analysis_prompt | self.llm | StrOutputParser()
        else:
            self.analysis_runnable = None
    
    def _setup_qa_chain(self):
        """Setup the interactive Q&A chain."""
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful code quality assistant."),
            ("human", 
             "Analysis Context (JSON):\n{context}\n\n"
             "User Question: {question}\n\n"
             "Provide a concise, actionable answer referencing findings.")
        ])

        if self.llm:
            self.qa_runnable = qa_prompt | self.llm | StrOutputParser()
        else:
            self.qa_runnable = None
    
    async def analyze_codebase(self, path: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a codebase and return comprehensive results."""
        try:
            # Handle file/directory input with optional branch
            files = self.file_handler.get_code_files(path, branch=branch)
            
            if not files:
                return {"error": "No supported code files found"}
            
            all_issues = []
            file_analyses = {}
            duplication_index = {}
            overall_metrics = {
                "complexity_score": 0,
                "maintainability_score": 0, 
                "security_score": 0,
                "overall_score": 0
            }
            
            # Analyze each file
            for file_path in files:
                file_analysis = await self._analyze_file(file_path)
                file_analyses[str(file_path)] = file_analysis
                
                if "issues" in file_analysis:
                    all_issues.extend(file_analysis["issues"])

                # Collect duplication fingerprints
                for fp in (file_analysis.get("duplication_fingerprints") or []):
                    h = fp.get("hash")
                    if not h:
                        continue
                    duplication_index.setdefault(h, []).append({
                        "file_path": str(file_path),
                        "start_line": fp.get("start_line"),
                        "end_line": fp.get("end_line"),
                        "size": fp.get("size", 0)
                    })
                
                # Aggregate metrics
                if "metrics" in file_analysis:
                    for metric, value in file_analysis["metrics"].items():
                        if metric in overall_metrics:
                            overall_metrics[metric] += value
            
            # Calculate average metrics
            num_files = len(files)
            if num_files > 0:
                for metric in overall_metrics:
                    overall_metrics[metric] = round(overall_metrics[metric] / num_files, 2)
            
            # Emit duplication issues for repeated hashes found in multiple files/locations
            for h, occs in duplication_index.items():
                if len(occs) <= 1:
                    continue
                # Group occurrences by file and suppress adjacent windows (sliding dedupe)
                file_to_occs: Dict[str, list] = {}
                for occ in sorted(occs, key=lambda o: (o.get("file_path", ""), o.get("start_line", 0))):
                    file_to_occs.setdefault(occ["file_path"], []).append(occ)

                for file_path, flist in file_to_occs.items():
                    compacted = []
                    prev_end = -1
                    for o in flist:
                        # Skip windows that overlap/are adjacent to previous to avoid flooding
                        if prev_end >= 0 and o.get("start_line", 0) <= prev_end + 1:
                            prev_end = max(prev_end, o.get("end_line", 0))
                            continue
                        compacted.append(o)
                        prev_end = o.get("end_line", 0)

                    # Emit at most one issue per file per duplicate hash
                    if compacted:
                        first = compacted[0]
                        all_issues.append({
                            "category": "code_duplication",
                            "severity": "low",
                            "line_number": first.get("start_line", 0),
                            "title": "Duplicate code block detected",
                            "description": f"This block appears {len(occs)} times across the codebase.",
                            "suggestion": "Extract common logic into a reusable function/module to reduce duplication.",
                            "code_snippet": "",
                            "file_path": file_path
                        })

            # Sort issues by severity
            all_issues.sort(key=lambda x: Config.SEVERITY_LEVELS.get(x.get("severity", "info"), 0), reverse=True)
            
            results = {
                "summary": {
                    "total_files": len(files),
                    "total_issues": len(all_issues),
                    "metrics": overall_metrics
                },
                "issues": all_issues,
                "file_analyses": file_analyses,
                "recommendations": self._generate_recommendations(all_issues)
            }
            
            # Add to RAG system for enhanced Q&A
            if self.rag_system.is_available():
                try:
                    self.rag_system.add_codebase(files, results)
                    self.chatbot.set_analysis_context(results)
                except Exception as e:
                    logging.warning(f"Failed to add to RAG system: {e}")
            
            return results
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Skip if file is too large
            if len(content) > Config.MAX_FILE_SIZE:
                return {"error": "File too large to analyze"}
            
            language = self.file_handler.detect_language(file_path)
            
            # Run static analyzers first
            static_results: Dict[str, Any] = {}
            if language in ["python"]:
                static_results = self.analyzer.analyze_python_file(file_path)
            elif language in ["javascript", "typescript"]:
                static_results = self.analyzer.analyze_javascript_file(file_path)
            elif language == "jupyter":
                static_results = self.analyzer.analyze_jupyter_file(file_path)

            # Run LLM analysis if available
            response = "{}"
            if self.analysis_runnable:
                try:
                    response = await self.analysis_runnable.ainvoke({
                        "code": content,
                        "language": language,
                        "filename": file_path.name
                    })
                except Exception:
                    response = "{}"

            # Parse JSON response (LLM)
            llm_analysis: Dict[str, Any] = {}
            try:
                llm_analysis = json.loads(response)
            except Exception:
                llm_analysis = {"issues": [], "metrics": {}, "summary": ""}

            # Normalize and merge issues
            merged_issues = []
            for issue in llm_analysis.get("issues", []) or []:
                issue["file_path"] = str(file_path)
                merged_issues.append(issue)

            # Map static findings into common issue format
            def add_static(group: str, items: list, category: str, default_severity: str = "medium"):
                for it in items or []:
                    merged_issues.append({
                        "category": category,
                        "severity": it.get("severity", default_severity),
                        "line_number": it.get("line", 0),
                        "title": it.get("type", group),
                        "description": it.get("message", it.get("rule_id", "Static analysis finding")),
                        "suggestion": "",
                        "code_snippet": it.get("code", ""),
                        "file_path": str(file_path)
                    })

            add_static("security_issues", static_results.get("security_issues", []), "security")
            add_static("complexity_issues", static_results.get("complexity_issues", []), "complexity")
            add_static("style_issues", static_results.get("style_issues", []), "maintainability", "low")
            add_static("pattern_issues", static_results.get("pattern_issues", []), "best_practices", "low")

            # Build metrics
            metrics = llm_analysis.get("metrics", {}) or {}
            radon_metrics = static_results.get("metrics", {}) or {}
            if radon_metrics.get("cyclomatic_complexity"):
                avg_complexity = sum(r.get("complexity", 0) for r in radon_metrics["cyclomatic_complexity"]) / max(len(radon_metrics["cyclomatic_complexity"]), 1)
                metrics["complexity_score"] = round(avg_complexity, 2)

            analysis = {
                "issues": merged_issues,
                "metrics": metrics,
                "summary": llm_analysis.get("summary", ""),
                "duplication_fingerprints": static_results.get("duplication", []),
                "debug": {
                    "language": language,
                    "static_counts": {
                        "security": len(static_results.get("security_issues", []) or []),
                        "complexity": len(static_results.get("complexity_issues", []) or []),
                        "style": len(static_results.get("style_issues", []) or []),
                        "patterns": len(static_results.get("pattern_issues", []) or [])
                    },
                    "merged_issue_count": len(merged_issues)
                }
            }

            return analysis
                
        except Exception as e:
            return {"error": f"Failed to analyze {file_path}: {str(e)}"}
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate high-level recommendations based on issues."""
        recommendations = []
        
        # Count issues by category
        category_counts = {}
        severity_counts = {}
        
        for issue in issues:
            category = issue.get("category", "unknown")
            severity = issue.get("severity", "info")
            
            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Generate recommendations based on patterns
        if severity_counts.get("critical", 0) > 0:
            recommendations.append("🚨 Address critical security and performance issues immediately")
        
        if category_counts.get("security", 0) > 3:
            recommendations.append("🔒 Consider implementing a security review process")
        
        if category_counts.get("complexity", 0) > 5:
            recommendations.append("🧩 Refactor complex functions to improve maintainability")
        
        if category_counts.get("testing", 0) > 3:
            recommendations.append("🧪 Increase test coverage for better code reliability")
        
        if category_counts.get("documentation", 0) > 3:
            recommendations.append("📚 Improve code documentation and comments")
        
        return recommendations
    
    async def ask_question(self, question: str, analysis_context: Dict[str, Any]) -> str:
        """Answer questions about the analyzed codebase using enhanced chatbot."""
        try:
            # Use the enhanced chatbot for better conversational experience
            if self.chatbot:
                return self.chatbot.chat(question)
            
            # Fallback to original Q&A system
            if not self.qa_runnable:
                return self._offline_answer(question, analysis_context)
            
            context_str = json.dumps(analysis_context, indent=2)
            response = await self.qa_runnable.ainvoke({
                "question": question,
                "context": context_str
            })
            return response
        except Exception as e:
            return f"Sorry, I couldn't process your question: {str(e)}"

    def _offline_answer(self, question: str, ctx: Dict[str, Any]) -> str:
        """Very lightweight Q&A without LLM: surface top issues relevant to the question."""
        q = question.lower()
        issues = ctx.get("issues", [])
        filtered = []
        buckets = {
            "security": ["security", "xss", "sql", "injection", "secret", "auth", "crypto"],
            "performance": ["performance", "slow", "latency", "memory", "optimize"],
            "complexity": ["complexity", "refactor", "maintainability"],
            "testing": ["test", "coverage"],
            "documentation": ["doc", "comment"],
        }
        target = None
        for cat, kws in buckets.items():
            if any(k in q for k in kws):
                target = cat
                break
        for it in issues:
            if target is None or it.get("category") == target:
                filtered.append(it)
        filtered = sorted(filtered, key=lambda x: Config.SEVERITY_LEVELS.get(x.get("severity", "info"), 0), reverse=True)[:5]
        if not filtered:
            return "No matching issues found. Try asking about security, performance, complexity, testing, or documentation."
        lines = ["Here are relevant issues:"]
        for i, it in enumerate(filtered, 1):
            loc = it.get("file_path", "")
            if it.get("line_number"):
                loc += f":{it.get('line_number')}"
            lines.append(f"{i}. [{it.get('severity','info').upper()}] {it.get('title','Issue')} — {loc}")
            if it.get("suggestion"):
                lines.append(f"   Suggestion: {it.get('suggestion')}")
        return "\n".join(lines)
