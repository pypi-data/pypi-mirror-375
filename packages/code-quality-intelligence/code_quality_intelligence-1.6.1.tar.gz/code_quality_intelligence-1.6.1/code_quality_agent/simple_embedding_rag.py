"""
Simple Embedding-based RAG System for Code Analysis

Uses FAISS with basic text embeddings for semantic code search without complex dependencies.
"""

import os
import json
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from collections import defaultdict
import hashlib

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class SimpleEmbeddingRAG:
    """Simple embedding-based RAG using TF-IDF-like features and FAISS."""
    
    def __init__(self, persist_directory: str = "./simple_embeddings_db"):
        """Initialize the simple embedding RAG system."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Use simple feature extraction instead of complex models
        self.embedding_dimension = 512  # Feature vector size
        
        # Initialize components
        self.index = None
        self.documents = []
        self.metadata = []
        self.vocabulary = {}
        self.text_splitter = None
        
        # File paths
        self.index_path = self.persist_directory / "simple_faiss_index.bin"
        self.docs_path = self.persist_directory / "simple_documents.pkl"
        self.metadata_path = self.persist_directory / "simple_metadata.pkl"
        self.vocab_path = self.persist_directory / "vocabulary.pkl"
        
        self._setup_system()
    
    def _setup_system(self):
        """Set up the simple embedding system."""
        if not FAISS_AVAILABLE or not LANGCHAIN_AVAILABLE:
            logging.warning("FAISS or LangChain not available. Simple Embedding RAG disabled.")
            return
        
        try:
            # Initialize text splitter for code
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=600,
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
            
            # Load or create index
            self._load_or_create_index()
            
            logging.info("Simple Embedding RAG system initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize simple embedding RAG: {e}")
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if (self.index_path.exists() and 
            self.docs_path.exists() and 
            self.metadata_path.exists()):
            try:
                # Load existing components
                self.index = faiss.read_index(str(self.index_path))
                
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                if self.vocab_path.exists():
                    with open(self.vocab_path, 'rb') as f:
                        self.vocabulary = pickle.load(f)
                
                logging.info(f"Loaded simple embedding index with {len(self.documents)} documents")
                
            except Exception as e:
                logging.warning(f"Failed to load index: {e}. Creating new one.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner product for similarity
        self.documents = []
        self.metadata = []
        self.vocabulary = {}
        logging.info("Created new simple embedding index")
    
    def _save_index(self):
        """Save the index and data."""
        try:
            faiss.write_index(self.index, str(self.index_path))
            
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            with open(self.vocab_path, 'wb') as f:
                pickle.dump(self.vocabulary, f)
            
            logging.info("Simple embedding index saved")
            
        except Exception as e:
            logging.error(f"Failed to save index: {e}")
    
    def _extract_code_features(self, text: str) -> np.ndarray:
        """Extract code-specific features for embedding."""
        features = np.zeros(self.embedding_dimension)
        
        # Tokenize and extract features
        words = re.findall(r'\w+', text.lower())
        
        # Code-specific patterns
        patterns = {
            'functions': r'\b(def|function|func|method)\b',
            'classes': r'\b(class|interface|struct)\b',
            'variables': r'\b(var|let|const|=)\b',
            'imports': r'\b(import|from|include|require)\b',
            'loops': r'\b(for|while|foreach)\b',
            'conditionals': r'\b(if|else|elif|switch|case)\b',
            'exceptions': r'\b(try|catch|except|finally|throw|raise)\b',
            'async': r'\b(async|await|promise|future)\b',
            'security': r'\b(eval|exec|pickle|sql|query)\b',
            'complexity': r'\b(nested|deep|complex|recursive)\b',
        }
        
        # Pattern-based features (first 100 dimensions)
        for i, (pattern_name, pattern) in enumerate(patterns.items()):
            if i < 100:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                features[i] = min(matches / 10.0, 1.0)  # Normalize
        
        # Word frequency features (remaining dimensions)
        word_counts = defaultdict(int)
        for word in words:
            if len(word) > 2:  # Skip very short words
                word_counts[word] += 1
                
                # Add to global vocabulary
                if word not in self.vocabulary:
                    self.vocabulary[word] = len(self.vocabulary)
        
        # Use top words for features
        for word, count in word_counts.items():
            if word in self.vocabulary:
                vocab_idx = self.vocabulary[word]
                feature_idx = 100 + (vocab_idx % (self.embedding_dimension - 100))
                features[feature_idx] = min(count / len(words), 1.0)  # Normalized frequency
        
        # Length and structure features
        if len(features) > 10:
            features[-10] = min(len(text) / 1000.0, 1.0)  # Text length
            features[-9] = min(len(words) / 100.0, 1.0)   # Word count
            features[-8] = min(text.count('\n') / 50.0, 1.0)  # Line count
            features[-7] = min(text.count('    ') / 20.0, 1.0)  # Indentation
            features[-6] = min(text.count('{') / 10.0, 1.0)  # Braces
            features[-5] = min(text.count('(') / 20.0, 1.0)  # Parentheses
        
        return features
    
    def is_available(self) -> bool:
        """Check if system is available."""
        return (self.index is not None and 
                FAISS_AVAILABLE and 
                LANGCHAIN_AVAILABLE)
    
    def add_codebase(self, files: List[Path], analysis_results: Dict[str, Any]) -> bool:
        """Add codebase to the embedding system."""
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
                    
                    # Get file analysis
                    file_analysis = analysis_results.get('file_analyses', {}).get(str(file_path), {})
                    
                    # Split into chunks
                    chunks = self.text_splitter.split_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) < 30:  # Skip very small chunks
                            continue
                        
                        # Extract features
                        embedding = self._extract_code_features(chunk)
                        
                        # Create metadata
                        chunk_metadata = {
                            "file_path": str(file_path),
                            "chunk_index": i,
                            "language": file_analysis.get('language', 'unknown'),
                            "issues": file_analysis.get('issues', []),
                            "complexity": file_analysis.get('complexity', {}),
                            "chunk_size": len(chunk),
                            "has_functions": bool(re.search(r'\b(def|function|class)\b', chunk)),
                            "has_imports": bool(re.search(r'\b(import|from|include)\b', chunk)),
                            "has_security": bool(re.search(r'\b(eval|exec|pickle|sql)\b', chunk, re.IGNORECASE)),
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
                
                # Save everything
                self._save_index()
                
                logging.info(f"Added {len(new_documents)} code chunks to simple embedding RAG")
                return True
            
        except Exception as e:
            logging.error(f"Failed to add codebase: {e}")
        
        return False
    
    def get_code_context(self, query: str, analysis_context: Dict[str, Any], top_k: int = 3) -> str:
        """Get relevant code context using embedding similarity."""
        if not self.is_available() or len(self.documents) == 0:
            return "No code context available. Please analyze a codebase first."
        
        try:
            # Extract features from query
            query_embedding = self._extract_code_features(query)
            query_array = np.array([query_embedding]).astype('float32')
            
            # Search FAISS index
            scores, indices = self.index.search(query_array, min(top_k, len(self.documents)))
            
            # Collect relevant chunks
            context_chunks = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents) and score > 0.01:  # Lower similarity threshold
                    chunk = self.documents[idx]
                    metadata = self.metadata[idx]
                    
                    context_chunks.append({
                        "content": chunk,
                        "file": metadata["file_path"],
                        "language": metadata["language"],
                        "issues_count": len(metadata["issues"]),
                        "similarity": float(score),
                        "has_functions": metadata.get("has_functions", False),
                        "has_security": metadata.get("has_security", False),
                    })
            
            # Format context
            if context_chunks:
                context_lines = ["**🔍 Relevant Code Context (Embedding Search):**"]
                
                for i, chunk in enumerate(context_chunks, 1):
                    content = chunk["content"]
                    if len(content) > 400:
                        content = content[:400] + "\n... (truncated)"
                    
                    file_name = Path(chunk["file"]).name
                    context_lines.append(f"\n**{i}. {file_name}** ({chunk['language']}) - Similarity: {chunk['similarity']:.3f}")
                    context_lines.append(f"   • Issues: {chunk['issues_count']} found")
                    context_lines.append(f"   • Functions: {'Yes' if chunk['has_functions'] else 'No'}")
                    context_lines.append(f"   • Security patterns: {'Yes' if chunk['has_security'] else 'No'}")
                    context_lines.append(f"   ```{chunk['language']}")
                    context_lines.append(f"   {content}")
                    context_lines.append("   ```")
                
                return "\n".join(context_lines)
            else:
                return "No semantically similar code found for your query."
            
        except Exception as e:
            logging.error(f"Simple embedding context error: {e}")
            return f"Error retrieving code context: {e}"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding collection."""
        try:
            if not self.is_available():
                return {"error": "Simple Embedding RAG not available"}
            
            stats = {
                "total_chunks": len(self.documents),
                "index_size": self.index.ntotal if self.index else 0,
                "vocabulary_size": len(self.vocabulary),
                "languages": {},
                "files": set(),
                "avg_chunk_size": 0,
                "has_functions": 0,
                "has_security": 0,
                "system": "Simple Embedding RAG (FAISS)"
            }
            
            # Calculate statistics
            total_size = 0
            for metadata in self.metadata:
                # Language distribution
                lang = metadata.get("language", "unknown")
                stats["languages"][lang] = stats["languages"].get(lang, 0) + 1
                
                # File tracking
                stats["files"].add(metadata.get("file_path", ""))
                
                # Feature tracking
                if metadata.get("has_functions", False):
                    stats["has_functions"] += 1
                if metadata.get("has_security", False):
                    stats["has_security"] += 1
                
                # Size tracking
                total_size += metadata.get("chunk_size", 0)
            
            stats["files"] = len(stats["files"])
            stats["avg_chunk_size"] = total_size / len(self.metadata) if self.metadata else 0
            
            return stats
            
        except Exception as e:
            return {"error": f"Simple embedding stats error: {e}"}
    
    def search_similar_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar code using simple embeddings."""
        if not self.is_available() or len(self.documents) == 0:
            return []
        
        try:
            # Extract features from query
            query_embedding = self._extract_code_features(query)
            query_array = np.array([query_embedding]).astype('float32')
            
            # Search FAISS index
            scores, indices = self.index.search(query_array, min(top_k, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents) and score > 0.01:
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "similarity": float(score)
                    })
            
            return results
            
        except Exception as e:
            logging.error(f"Simple embedding search error: {e}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all stored data."""
        try:
            self._create_new_index()
            self._save_index()
            logging.info("Simple embedding collection cleared")
            return True
        except Exception as e:
            logging.error(f"Failed to clear collection: {e}")
            return False
