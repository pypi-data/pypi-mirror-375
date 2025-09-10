"""
Embedding-based RAG System for Code Analysis

Uses FAISS vector database with code-specific embeddings for semantic code search.
"""

import os
import json
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
from collections import defaultdict

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    import tiktoken
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class CodeEmbeddingRAG:
    """FAISS-based RAG system with code embeddings for semantic search."""
    
    def __init__(self, persist_directory: str = "./code_embeddings_db"):
        """Initialize the embedding-based RAG system."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Use a code-specific embedding model
        # all-MiniLM-L6-v2 is good for general text, but we'll use it as it's reliable
        # For production, consider: microsoft/codebert-base or microsoft/GraphCodeBERT-base
        self.embedding_model_name = "all-MiniLM-L6-v2"  # Reliable and fast
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        
        # Initialize components
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.metadata = []
        self.text_splitter = None
        
        # File paths for persistence
        self.index_path = self.persist_directory / "faiss_index.bin"
        self.docs_path = self.persist_directory / "documents.pkl"
        self.metadata_path = self.persist_directory / "metadata.pkl"
        
        # Token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except:
            self.tokenizer = None
        
        self._setup_system()
    
    def _setup_system(self):
        """Set up the embedding RAG system."""
        if not EMBEDDING_AVAILABLE or not LANGCHAIN_AVAILABLE:
            logging.warning("FAISS or SentenceTransformers not available. Embedding RAG disabled.")
            return
        
        try:
            # Initialize embedding model
            logging.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Initialize text splitter optimized for code
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,  # Smaller chunks for code
                chunk_overlap=100,
                length_function=len,
                separators=[
                    "\n\nclass ",
                    "\n\ndef ",
                    "\n\nfunction ",
                    "\n\nasync def ",
                    "\n\n",
                    "\n",
                    " ",
                    ""
                ]
            )
            
            # Load or create FAISS index
            self._load_or_create_index()
            
            logging.info("Embedding RAG system initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize embedding RAG: {e}")
            self.embedding_model = None
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if (self.index_path.exists() and 
            self.docs_path.exists() and 
            self.metadata_path.exists()):
            try:
                # Load existing index
                self.index = faiss.read_index(str(self.index_path))
                
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logging.info(f"Loaded existing embedding index with {len(self.documents)} documents")
                
            except Exception as e:
                logging.warning(f"Failed to load existing index: {e}. Creating new one.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner product for cosine similarity
        self.documents = []
        self.metadata = []
        logging.info("Created new FAISS embedding index")
    
    def _save_index(self):
        """Save the FAISS index and associated data."""
        try:
            faiss.write_index(self.index, str(self.index_path))
            
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logging.info("Embedding index saved successfully")
            
        except Exception as e:
            logging.error(f"Failed to save embedding index: {e}")
    
    def is_available(self) -> bool:
        """Check if embedding RAG system is available."""
        return (self.embedding_model is not None and 
                self.index is not None and 
                EMBEDDING_AVAILABLE and 
                LANGCHAIN_AVAILABLE)
    
    def add_codebase(self, files: List[Path], analysis_results: Dict[str, Any]) -> bool:
        """Add codebase to the embedding RAG system."""
        if not self.is_available():
            return False
        
        try:
            new_documents = []
            new_embeddings = []
            new_metadata = []
            
            for file_path in files:
                try:
                    # Convert to Path if string
                    if isinstance(file_path, str):
                        file_path = Path(file_path)
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Get file analysis results
                    file_analysis = analysis_results.get('file_analyses', {}).get(str(file_path), {})
                    
                    # Split into code chunks
                    chunks = self.text_splitter.split_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        # Skip very small chunks
                        if len(chunk.strip()) < 50:
                            continue
                        
                        # Prepare chunk for embedding (add context)
                        chunk_with_context = self._prepare_code_chunk(chunk, file_path, file_analysis)
                        
                        # Generate embedding
                        embedding = self.embedding_model.encode([chunk_with_context])[0]
                        
                        # Normalize for cosine similarity
                        embedding = embedding / np.linalg.norm(embedding)
                        
                        # Create metadata
                        chunk_metadata = {
                            "file_path": str(file_path),
                            "chunk_index": i,
                            "language": file_analysis.get('language', 'unknown'),
                            "issues": file_analysis.get('issues', []),
                            "complexity": file_analysis.get('complexity', {}),
                            "chunk_size": len(chunk),
                            "has_functions": bool(re.search(r'\b(def|function|class)\b', chunk)),
                            "has_imports": bool(re.search(r'\b(import|from|include|require)\b', chunk)),
                            "has_comments": bool(re.search(r'(#|//|/\*|\*)', chunk)),
                        }
                        
                        new_documents.append(chunk)
                        new_embeddings.append(embedding)
                        new_metadata.append(chunk_metadata)
                
                except Exception as e:
                    logging.warning(f"Failed to process file {file_path}: {e}")
                    continue
            
            if new_documents:
                # Add to FAISS index
                embeddings_array = np.array(new_embeddings).astype('float32')
                self.index.add(embeddings_array)
                
                # Add to local storage
                self.documents.extend(new_documents)
                self.metadata.extend(new_metadata)
                
                # Save index
                self._save_index()
                
                logging.info(f"Added {len(new_documents)} code chunks to embedding RAG system")
                return True
            
        except Exception as e:
            logging.error(f"Failed to add codebase to embedding RAG: {e}")
        
        return False
    
    def _prepare_code_chunk(self, chunk: str, file_path: Path, file_analysis: Dict[str, Any]) -> str:
        """Prepare code chunk with context for better embeddings."""
        # Add file context
        language = file_analysis.get('language', 'unknown')
        
        # Create context-rich representation
        context_parts = [
            f"File: {file_path.name}",
            f"Language: {language}",
        ]
        
        # Add issue context if present
        issues = file_analysis.get('issues', [])
        if issues:
            issue_types = set(issue.get('category', 'unknown') for issue in issues)
            context_parts.append(f"Issues: {', '.join(issue_types)}")
        
        # Add function/class context
        if re.search(r'\bclass\s+\w+', chunk):
            context_parts.append("Contains: class definition")
        if re.search(r'\bdef\s+\w+', chunk):
            context_parts.append("Contains: function definition")
        
        # Combine context with code
        context_header = " | ".join(context_parts)
        return f"{context_header}\n\n{chunk}"
    
    def get_code_context(self, query: str, analysis_context: Dict[str, Any], top_k: int = 3) -> str:
        """Get relevant code context for a query using semantic search."""
        if not self.is_available() or len(self.documents) == 0:
            return "No code context available. Please analyze a codebase first."
        
        try:
            # Prepare query for embedding
            query_with_context = f"Code question: {query}"
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query_with_context])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_array = np.array([query_embedding]).astype('float32')
            
            # Search FAISS index
            scores, indices = self.index.search(query_array, min(top_k, len(self.documents)))
            
            # Collect relevant chunks
            context_chunks = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents) and score > 0.3:  # Similarity threshold
                    chunk = self.documents[idx]
                    chunk_metadata = self.metadata[idx]
                    
                    context_chunks.append({
                        "content": chunk,
                        "file": chunk_metadata["file_path"],
                        "language": chunk_metadata["language"],
                        "issues_count": len(chunk_metadata["issues"]),
                        "similarity": float(score),
                        "has_functions": chunk_metadata.get("has_functions", False),
                        "has_imports": chunk_metadata.get("has_imports", False),
                    })
            
            # Format context for AI
            if context_chunks:
                context_lines = ["**📝 Relevant Code Context (Embedding-based):**"]
                
                for i, chunk in enumerate(context_chunks, 1):
                    # Truncate long code for readability
                    content = chunk["content"]
                    if len(content) > 500:
                        content = content[:500] + "\n... (truncated)"
                    
                    context_lines.append(f"\n**{i}. {Path(chunk['file']).name}** ({chunk['language']}) - Similarity: {chunk['similarity']:.2f}")
                    context_lines.append(f"   • Issues found: {chunk['issues_count']}")
                    context_lines.append(f"   • Functions: {'Yes' if chunk['has_functions'] else 'No'}")
                    context_lines.append(f"   • Imports: {'Yes' if chunk['has_imports'] else 'No'}")
                    context_lines.append(f"   ```{chunk['language']}")
                    context_lines.append(f"   {content}")
                    context_lines.append("   ```")
                
                return "\n".join(context_lines)
            else:
                return "No semantically relevant code found for your query."
            
        except Exception as e:
            logging.error(f"Failed to get embedding context: {e}")
            return f"Error retrieving code context: {e}"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding collection."""
        if not self.is_available():
            return {"error": "Embedding RAG system not available"}
        
        try:
            stats = {
                "total_chunks": len(self.documents),
                "index_size": self.index.ntotal if self.index else 0,
                "languages": {},
                "avg_chunk_size": 0,
                "files": set(),
                "has_functions": 0,
                "has_imports": 0,
                "total_issues": 0,
                "system": "Embedding RAG (FAISS)"
            }
            
            # Calculate detailed statistics
            total_size = 0
            for i, metadata in enumerate(self.metadata):
                # Language distribution
                lang = metadata.get("language", "unknown")
                stats["languages"][lang] = stats["languages"].get(lang, 0) + 1
                
                # File tracking
                stats["files"].add(metadata.get("file_path", ""))
                
                # Feature tracking
                if metadata.get("has_functions", False):
                    stats["has_functions"] += 1
                if metadata.get("has_imports", False):
                    stats["has_imports"] += 1
                
                # Issue tracking
                stats["total_issues"] += len(metadata.get("issues", []))
                
                # Size tracking
                total_size += metadata.get("chunk_size", 0)
            
            stats["files"] = len(stats["files"])
            stats["avg_chunk_size"] = total_size / len(self.metadata) if self.metadata else 0
            stats["avg_issues_per_chunk"] = stats["total_issues"] / len(self.metadata) if self.metadata else 0
            
            return stats
            
        except Exception as e:
            return {"error": f"Failed to get embedding stats: {e}"}
    
    def search_similar_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar code chunks using embeddings."""
        if not self.is_available() or len(self.documents) == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_array = np.array([query_embedding]).astype('float32')
            
            # Search
            scores, indices = self.index.search(query_array, min(top_k, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents) and score > 0.2:
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "similarity": float(score)
                    })
            
            return results
            
        except Exception as e:
            logging.error(f"Failed to search similar code: {e}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all stored embeddings and documents."""
        try:
            self._create_new_index()
            self._save_index()
            logging.info("Embedding collection cleared")
            return True
        except Exception as e:
            logging.error(f"Failed to clear embedding collection: {e}")
            return False
    
    def get_code_suggestions(self, query: str, analysis_results: Dict[str, Any]) -> List[str]:
        """Get code-specific suggestions based on query and analysis."""
        suggestions = []
        
        # Search for relevant code
        relevant_chunks = self.search_similar_code(query, top_k=3)
        
        if relevant_chunks:
            for chunk in relevant_chunks:
                metadata = chunk["metadata"]
                issues = metadata.get("issues", [])
                
                if issues:
                    for issue in issues[:2]:  # Limit to top 2 issues per chunk
                        suggestion = f"In {Path(metadata['file_path']).name}: {issue.get('description', 'Issue found')}"
                        suggestions.append(suggestion)
        
        # Add general suggestions based on query keywords
        query_lower = query.lower()
        if "security" in query_lower:
            suggestions.append("Consider using parameterized queries instead of string concatenation")
            suggestions.append("Validate and sanitize all user inputs")
        elif "performance" in query_lower:
            suggestions.append("Profile your code to identify bottlenecks")
            suggestions.append("Consider using more efficient algorithms or data structures")
        elif "complexity" in query_lower:
            suggestions.append("Break down large functions into smaller, focused ones")
            suggestions.append("Use early returns to reduce nesting levels")
        
        return suggestions[:5]  # Return top 5 suggestions
