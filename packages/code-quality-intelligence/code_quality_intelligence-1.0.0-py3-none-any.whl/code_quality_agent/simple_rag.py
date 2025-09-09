"""
Simple RAG System without external vector databases.
This provides basic RAG functionality using simple text matching and keyword search.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from collections import defaultdict


class SimpleRAGSystem:
    """Simple RAG system using keyword matching and text search."""
    
    def __init__(self):
        """Initialize the simple RAG system."""
        self.documents = []
        self.file_index = defaultdict(list)
        self.keyword_index = defaultdict(list)
        self.available = True
        
    def is_available(self) -> bool:
        """Check if RAG system is available."""
        return self.available
    
    def add_codebase(self, files: List[Path], analysis_results: Dict[str, Any]) -> bool:
        """Add codebase to the simple RAG system."""
        try:
            for file_path in files:
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Split into chunks (simple line-based splitting)
                    lines = content.split('\n')
                    chunks = []
                    
                    current_chunk = []
                    for line in lines:
                        current_chunk.append(line)
                        if len(current_chunk) >= 20 or (line.strip() and line.strip().startswith(('def ', 'class ', 'function ', 'var ', 'const '))):
                            if current_chunk:
                                chunks.append('\n'.join(current_chunk))
                                current_chunk = []
                    
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    
                    # Get file analysis
                    file_analysis = analysis_results.get('files', {}).get(str(file_path), {})
                    
                    # Add chunks to system
                    for i, chunk in enumerate(chunks):
                        doc_id = f"{file_path}_{i}"
                        
                        doc = {
                            "id": doc_id,
                            "content": chunk,
                            "file_path": str(file_path),
                            "chunk_index": i,
                            "language": file_analysis.get('language', 'unknown'),
                            "issues": file_analysis.get('issues', []),
                            "complexity": file_analysis.get('complexity', {}),
                        }
                        
                        self.documents.append(doc)
                        self.file_index[str(file_path)].append(len(self.documents) - 1)
                        
                        # Index keywords
                        self._index_keywords(chunk, len(self.documents) - 1)
                
                except Exception as e:
                    logging.warning(f"Failed to process file {file_path}: {e}")
                    continue
            
            logging.info(f"Added {len(files)} files to Simple RAG system ({len(self.documents)} chunks)")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add codebase to Simple RAG: {e}")
            return False
    
    def _index_keywords(self, content: str, doc_index: int):
        """Index keywords from content."""
        # Extract keywords (functions, classes, variables)
        keywords = set()
        
        # Function definitions
        func_matches = re.findall(r'def\s+(\w+)', content)
        keywords.update(func_matches)
        
        # Class definitions
        class_matches = re.findall(r'class\s+(\w+)', content)
        keywords.update(class_matches)
        
        # Variable assignments
        var_matches = re.findall(r'(\w+)\s*=', content)
        keywords.update(var_matches)
        
        # Import statements
        import_matches = re.findall(r'import\s+(\w+)', content)
        keywords.update(import_matches)
        
        # Add to keyword index
        for keyword in keywords:
            if len(keyword) > 2:  # Skip very short keywords
                self.keyword_index[keyword.lower()].append(doc_index)
    
    def get_code_context(self, question: str, analysis_context: Dict[str, Any], top_k: int = 3) -> str:
        """Get relevant code context for a question."""
        if not self.documents:
            return "No code context available. Please analyze a codebase first."
        
        try:
            # Extract keywords from question
            question_words = re.findall(r'\w+', question.lower())
            question_keywords = [word for word in question_words if len(word) > 2]
            
            # Score documents based on keyword matches
            doc_scores = defaultdict(int)
            
            for keyword in question_keywords:
                if keyword in self.keyword_index:
                    for doc_idx in self.keyword_index[keyword]:
                        doc_scores[doc_idx] += 1
                
                # Also check content directly
                for i, doc in enumerate(self.documents):
                    if keyword in doc["content"].lower():
                        doc_scores[i] += 1
            
            # Get top scoring documents
            if doc_scores:
                sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
                top_docs = sorted_docs[:top_k]
                
                context_parts = ["**Relevant Code Context:**"]
                
                for i, (doc_idx, score) in enumerate(top_docs, 1):
                    doc = self.documents[doc_idx]
                    content_preview = doc["content"][:400] + "..." if len(doc["content"]) > 400 else doc["content"]
                    
                    context_parts.append(f"\n{i}. File: {doc['file_path']} ({doc['language']})")
                    context_parts.append(f"   Issues: {len(doc['issues'])} found")
                    context_parts.append(f"   Relevance Score: {score}")
                    context_parts.append(f"   Code:\n   ```\n   {content_preview}\n   ```")
                
                return "\n".join(context_parts)
            
            # Fallback: return first few documents
            context_parts = ["**General Code Context:**"]
            for i, doc in enumerate(self.documents[:2], 1):
                content_preview = doc["content"][:300] + "..." if len(doc["content"]) > 300 else doc["content"]
                context_parts.append(f"\n{i}. File: {doc['file_path']} ({doc['language']})")
                context_parts.append(f"   Code: {content_preview}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Simple RAG context error: {e}")
            return "Error retrieving code context."
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the stored documents."""
        try:
            if not self.documents:
                return {"total_chunks": 0, "system": "Simple RAG"}
            
            # Calculate statistics
            languages = defaultdict(int)
            files = set()
            total_issues = 0
            
            for doc in self.documents:
                languages[doc["language"]] += 1
                files.add(doc["file_path"])
                total_issues += len(doc["issues"])
            
            return {
                "total_chunks": len(self.documents),
                "languages": dict(languages),
                "files": len(files),
                "avg_issues_per_chunk": total_issues / len(self.documents) if self.documents else 0,
                "system": "Simple RAG",
                "keywords_indexed": len(self.keyword_index)
            }
            
        except Exception as e:
            return {"error": f"Simple RAG stats error: {e}"}
    
    def clear_collection(self) -> bool:
        """Clear all stored data."""
        try:
            self.documents = []
            self.file_index = defaultdict(list)
            self.keyword_index = defaultdict(list)
            logging.info("Simple RAG collection cleared")
            return True
        except Exception as e:
            logging.error(f"Failed to clear Simple RAG: {e}")
            return False
