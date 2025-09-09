"""
Conversational Chatbot Interface for Code Quality Intelligence Agent.

This module provides an enhanced conversational interface that supports follow-ups,
context awareness, and natural language interactions about code analysis.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .config import Config


class CodeQualityChatbot:
    """Enhanced conversational chatbot for code quality discussions."""
    
    def __init__(self, rag_system = None):
        """Initialize the chatbot."""
        self.rag_system = rag_system
        self.llm = None
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True
        )
        self.analysis_context = {}
        self.conversation_history = []
        
        # Initialize LLM if API key available
        if Config.has_groq_api_key():
            self.llm = ChatGroq(
                groq_api_key=Config.get_groq_api_key(),
                model_name=Config.DEFAULT_MODEL,
                temperature=0.3,  # Slightly more creative for conversation
                max_tokens=Config.MAX_TOKENS
            )
        
        self._setup_chatbot()
    
    def _setup_chatbot(self):
        """Set up the chatbot with prompts and chains."""
        if not self.llm:
            return
        
        # System prompt for conversational code analysis
        self.system_prompt = """You are an expert code quality assistant with a friendly, conversational personality. 

Your role is to:
1. Help developers understand code quality issues in their codebase
2. Provide practical, actionable advice for improvements  
3. Explain technical concepts in clear, accessible language
4. Support follow-up questions and maintain conversation context
5. Reference specific code examples and analysis results when available

Communication style:
- Be conversational and approachable, not robotic
- Use emojis occasionally to make interactions friendly 😊
- Provide concrete examples and code snippets when helpful
- Ask clarifying questions when the user's intent is unclear
- Acknowledge when you don't know something and suggest alternatives

When discussing code issues:
- Explain WHY something is a problem, not just WHAT the problem is
- Provide step-by-step solutions when possible
- Mention potential risks or benefits of different approaches
- Reference industry best practices and standards

Remember: You're here to help developers improve their code quality through friendly, expert guidance."""

        # Create the conversational chain
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Analysis Context:\n{analysis_context}\n\nRAG Context:\n{rag_context}\n\nConversation History:\n{conversation_history}\n\nUser Question: {question}")
        ])
        
        self.chat_chain = self.chat_prompt | self.llm | StrOutputParser()
    
    def set_analysis_context(self, analysis_results: Dict[str, Any]):
        """Set the current analysis context for the conversation."""
        self.analysis_context = analysis_results
        
        # Add to RAG system if available
        if self.rag_system and self.rag_system.is_available():
            try:
                # Extract file paths from analysis results
                from pathlib import Path
                file_analyses = analysis_results.get('file_analyses', {})
                files = [Path(fp) for fp in file_analyses.keys()]
                
                if files:
                    self.rag_system.add_codebase(files, analysis_results)
            except Exception as e:
                logging.warning(f"Failed to add analysis to RAG: {e}")
    
    def chat(self, message: str) -> str:
        """Have a conversation about the code analysis."""
        try:
            # Get RAG context if available
            rag_context = ""
            if self.rag_system and self.rag_system.is_available():
                rag_context = self.rag_system.get_code_context(message, self.analysis_context)
            
            # Prepare conversation history
            history_text = self._format_conversation_history()
            
            # Prepare analysis context
            analysis_summary = self._summarize_analysis_context()
            
            if self.llm:
                # Use LLM for intelligent response
                response = self.chat_chain.invoke({
                    "analysis_context": analysis_summary,
                    "rag_context": rag_context,
                    "conversation_history": history_text,
                    "question": message
                })
            else:
                # Fallback to rule-based responses
                response = self._fallback_response(message)
            
            # Update conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": message,
                "assistant": response,
                "context_used": bool(rag_context)
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-15:]
            
            return response
            
        except Exception as e:
            logging.error(f"Chat error: {e}")
            return f"I apologize, but I encountered an error while processing your question. Could you please try rephrasing it? 🤔\n\nError details: {str(e)}"
    
    def _summarize_analysis_context(self) -> str:
        """Create a summary of the current analysis context."""
        if not self.analysis_context:
            return "No analysis context available."
        
        summary = self.analysis_context.get('summary', {})
        issues = self.analysis_context.get('issues', [])
        
        # Count issues by severity and category
        severity_counts = {}
        category_counts = {}
        
        for issue in issues:
            severity = issue.get('severity', 'info')
            category = issue.get('category', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Build summary
        parts = [
            f"Files analyzed: {summary.get('total_files', 0)}",
            f"Total issues: {summary.get('total_issues', 0)}",
            f"Complexity score: {summary.get('metrics', {}).get('complexity_score', 0)}"
        ]
        
        if severity_counts:
            severity_text = ", ".join([f"{k}: {v}" for k, v in severity_counts.items()])
            parts.append(f"Issues by severity: {severity_text}")
        
        if category_counts:
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            category_text = ", ".join([f"{k}: {v}" for k, v in top_categories])
            parts.append(f"Top issue categories: {category_text}")
        
        return " | ".join(parts)
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for context."""
        if not self.conversation_history:
            return "No previous conversation."
        
        # Get last 5 exchanges
        recent_history = self.conversation_history[-5:]
        
        formatted = []
        for exchange in recent_history:
            formatted.append(f"User: {exchange['user']}")
            formatted.append(f"Assistant: {exchange['assistant'][:200]}{'...' if len(exchange['assistant']) > 200 else ''}")
            formatted.append("---")
        
        return "\n".join(formatted)
    
    def _fallback_response(self, message: str) -> str:
        """Provide fallback responses when LLM is not available."""
        message_lower = message.lower()
        
        # Pattern-based responses
        if any(word in message_lower for word in ['security', 'vulnerable', 'exploit']):
            return self._get_security_response()
        elif any(word in message_lower for word in ['complexity', 'complex', 'refactor']):
            return self._get_complexity_response()
        elif any(word in message_lower for word in ['test', 'testing', 'coverage']):
            return self._get_testing_response()
        elif any(word in message_lower for word in ['performance', 'slow', 'optimize']):
            return self._get_performance_response()
        elif any(word in message_lower for word in ['documentation', 'docs', 'comment']):
            return self._get_documentation_response()
        elif any(word in message_lower for word in ['hello', 'hi', 'help']):
            return self._get_greeting_response()
        else:
            return self._get_generic_response()
    
    def _get_security_response(self) -> str:
        """Get response about security issues."""
        security_issues = [
            issue for issue in self.analysis_context.get('issues', [])
            if issue.get('category') == 'security'
        ]
        
        if security_issues:
            response = f"I found {len(security_issues)} security issues in your codebase! 🔒\n\n"
            for i, issue in enumerate(security_issues[:3], 1):
                response += f"{i}. {issue.get('title', 'Security Issue')} (Line {issue.get('line_number', 'N/A')})\n"
                response += f"   {issue.get('description', 'No description available')}\n\n"
            
            response += "Would you like me to explain any of these security issues in detail?"
        else:
            response = "Great news! I didn't find any major security issues in your codebase. 🛡️\n\n"
            response += "However, it's always good to follow security best practices like:\n"
            response += "• Avoiding eval() and exec() functions\n"
            response += "• Using parameterized queries for databases\n"
            response += "• Validating user input\n"
            response += "• Keeping dependencies updated"
        
        return response
    
    def _get_complexity_response(self) -> str:
        """Get response about complexity issues."""
        complexity_issues = [
            issue for issue in self.analysis_context.get('issues', [])
            if issue.get('category') in ['complexity', 'maintainability']
        ]
        
        if complexity_issues:
            response = f"I found {len(complexity_issues)} complexity-related issues. 🧩\n\n"
            response += "Complex code can be harder to maintain and debug. Consider:\n"
            response += "• Breaking large functions into smaller ones\n"
            response += "• Reducing nested loops and conditions\n"
            response += "• Using descriptive variable names\n"
            response += "• Adding comments for complex logic"
        else:
            response = "Your code complexity looks good! ✅\n\n"
            response += "Keep following good practices like keeping functions focused and using clear naming."
        
        return response
    
    def _get_testing_response(self) -> str:
        """Get response about testing."""
        return "Testing is crucial for code quality! 🧪\n\n" + \
               "Based on your codebase, I recommend:\n" + \
               "• Writing unit tests for critical functions\n" + \
               "• Adding integration tests for workflows\n" + \
               "• Using test coverage tools\n" + \
               "• Following the AAA pattern (Arrange, Act, Assert)"
    
    def _get_performance_response(self) -> str:
        """Get response about performance."""
        return "Performance optimization is important! ⚡\n\n" + \
               "Some general tips:\n" + \
               "• Profile your code to find bottlenecks\n" + \
               "• Optimize database queries\n" + \
               "• Use appropriate data structures\n" + \
               "• Consider caching for expensive operations"
    
    def _get_documentation_response(self) -> str:
        """Get response about documentation."""
        doc_issues = [
            issue for issue in self.analysis_context.get('issues', [])
            if 'docstring' in issue.get('title', '').lower() or issue.get('category') == 'documentation'
        ]
        
        if doc_issues:
            response = f"I found {len(doc_issues)} documentation issues. 📚\n\n"
            response += "Good documentation helps other developers (and future you!) understand the code.\n"
            response += "Consider adding:\n"
            response += "• Function docstrings explaining parameters and return values\n"
            response += "• Class docstrings describing purpose and usage\n"
            response += "• Inline comments for complex logic"
        else:
            response = "Your documentation looks good! 📝\n\n"
            response += "Keep maintaining clear docstrings and comments as your code evolves."
        
        return response
    
    def _get_greeting_response(self) -> str:
        """Get greeting response."""
        return "Hello! 👋 I'm here to help you understand and improve your code quality.\n\n" + \
               "I can help you with:\n" + \
               "• Understanding security issues and how to fix them\n" + \
               "• Reducing code complexity and improving maintainability\n" + \
               "• Improving test coverage and documentation\n" + \
               "• Performance optimization suggestions\n\n" + \
               "What would you like to know about your codebase?"
    
    def _get_generic_response(self) -> str:
        """Get generic response."""
        return "I'd be happy to help you with your code quality questions! 😊\n\n" + \
               "You can ask me about:\n" + \
               "• Specific issues found in your code\n" + \
               "• Best practices for improvement\n" + \
               "• Explanations of code quality concepts\n" + \
               "• How to implement suggested fixes\n\n" + \
               "What specific aspect of your codebase would you like to discuss?"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation."""
        return {
            "total_exchanges": len(self.conversation_history),
            "rag_enabled": self.rag_system is not None and self.rag_system.is_available(),
            "llm_available": self.llm is not None,
            "analysis_context_set": bool(self.analysis_context),
            "recent_topics": self._extract_recent_topics()
        }
    
    def _extract_recent_topics(self) -> List[str]:
        """Extract topics from recent conversation."""
        if not self.conversation_history:
            return []
        
        topics = []
        keywords = {
            'security': ['security', 'vulnerable', 'exploit', 'auth'],
            'performance': ['performance', 'slow', 'optimize', 'speed'],
            'complexity': ['complexity', 'complex', 'refactor', 'maintainability'],
            'testing': ['test', 'testing', 'coverage', 'unit'],
            'documentation': ['documentation', 'docs', 'comment', 'docstring']
        }
        
        recent_messages = [ex['user'].lower() for ex in self.conversation_history[-5:]]
        
        for topic, words in keywords.items():
            if any(word in message for message in recent_messages for word in words):
                topics.append(topic)
        
        return list(set(topics))
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.memory.clear()
