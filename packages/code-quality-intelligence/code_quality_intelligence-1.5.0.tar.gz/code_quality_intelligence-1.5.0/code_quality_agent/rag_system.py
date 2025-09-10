"""
RAG (Retrieval-Augmented Generation) System for Code Quality Intelligence Agent.

This module implements a vector database system for storing and retrieving code chunks,
enabling efficient analysis of large codebases through semantic search.
"""

import os
import hashlib
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import logging

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    import tiktoken
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Import RAG alternatives
try:
    from .simple_rag import SimpleRAGSystem
    SIMPLE_RAG_AVAILABLE = True
except ImportError:
    SIMPLE_RAG_AVAILABLE = False

try:
    from .simple_embedding_rag import SimpleEmbeddingRAG
    EMBEDDING_RAG_AVAILABLE = True
except ImportError:
    EMBEDDING_RAG_AVAILABLE = False


class CodeRAGSystem:
    """RAG system for code analysis with vector storage and retrieval."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the RAG system with fallback to FAISS."""
        self.persist_directory = persist_directory
        self.collection_name = "code_analysis"
        self.embedding_model_name = "all-MiniLM-L6-v2"
        
        # Initialize components
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.text_splitter = None
        
        # RAG alternatives
        self.simple_rag = None
        self.embedding_rag = None
        
        # Token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except:
            self.tokenizer = None
        
        self._setup_rag_system()
    
    def _setup_rag_system(self):
        """Set up the RAG system components with FAISS fallback."""
        # Try ChromaDB first
        if CHROMADB_AVAILABLE and LANGCHAIN_AVAILABLE:
            try:
                self._setup_chromadb()
                return
            except Exception as e:
                logging.warning(f"ChromaDB setup failed: {e}. Trying FAISS fallback.")
        
        # Try Embedding RAG first
        if EMBEDDING_RAG_AVAILABLE:
            try:
                self.embedding_rag = SimpleEmbeddingRAG()
                if self.embedding_rag.is_available():
                    logging.info("Using Simple Embedding RAG system")
                    return
            except Exception as e:
                logging.warning(f"Embedding RAG setup failed: {e}")
        
        # Fallback to Simple RAG
        if SIMPLE_RAG_AVAILABLE:
            try:
                self.simple_rag = SimpleRAGSystem()
                if self.simple_rag.is_available():
                    logging.info("Using Simple RAG system as fallback")
                    return
            except Exception as e:
                logging.warning(f"Simple RAG setup failed: {e}")
        
        logging.warning("No RAG system available. Enhanced features disabled.")
    
    def _setup_chromadb(self):
        """Set up ChromaDB components."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Code analysis chunks with metadata"}
                )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Initialize text splitter for code
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=[
                    "\n\nclass ",
                    "\n\ndef ",
                    "\n\nasync def ",
                    "\n\n",
                    "\n",
                    " ",
                    ""
                ]
            )
            
            logging.info("RAG system initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize RAG system: {e}")
            self.client = None
    
    def _setup_faiss(self):
        """Set up FAISS-based RAG system as fallback."""
        try:
            # Simple FAISS implementation
            self.faiss_rag = {
                "embedding_model": SentenceTransformer(self.embedding_model_name),
                "text_splitter": RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len,
                    separators=["\n\nclass ", "\n\ndef ", "\n\nasync def ", "\n\n", "\n", " ", ""]
                ),
                "documents": [],
                "available": True
            }
            logging.info("FAISS RAG system initialized")
        except Exception as e:
            logging.error(f"FAISS setup failed: {e}")
            self.faiss_rag = None
    
    def is_available(self) -> bool:
        """Check if RAG system is available."""
        return ((self.client is not None and self.collection is not None) or
                (self.embedding_rag is not None and self.embedding_rag.is_available()) or
                (self.simple_rag is not None and self.simple_rag.is_available()))
    
    def add_codebase(self, files: List[Path], analysis_results: Dict[str, Any]) -> bool:
        """Add codebase to the vector database (ChromaDB or FAISS)."""
        if not self.is_available():
            return False
        
        # Use Embedding RAG if available
        if self.embedding_rag and self.embedding_rag.is_available():
            return self.embedding_rag.add_codebase(files, analysis_results)
        
        # Use Simple RAG if ChromaDB not available
        if self.simple_rag and self.simple_rag.is_available():
            return self._add_to_simple_rag(files, analysis_results)
        
        try:
            documents = []
            metadatas = []
            ids = []
            
            # Process each file
            for file_path in files:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if not content.strip():
                        continue
                    
                    # Create chunks from the file
                    chunks = self.text_splitter.split_text(content)
                    
                    # Get file analysis if available
                    file_analysis = analysis_results.get('file_analyses', {}).get(str(file_path), {})
                    issues = file_analysis.get('issues', [])
                    metrics = file_analysis.get('metrics', {})
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) < 50:  # Skip very small chunks
                            continue
                        
                        # Create unique ID
                        chunk_id = hashlib.md5(f"{file_path}_{i}_{chunk[:100]}".encode()).hexdigest()
                        
                        # Create metadata
                        metadata = {
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "language": self._detect_language(file_path),
                            "chunk_index": i,
                            "chunk_size": len(chunk),
                            "token_count": self._count_tokens(chunk),
                            "has_issues": len(issues) > 0,
                            "issue_count": len(issues),
                            "complexity_score": metrics.get('complexity_score', 0),
                            "content_type": self._classify_content(chunk)
                        }
                        
                        documents.append(chunk)
                        metadatas.append(metadata)
                        ids.append(chunk_id)
                
                except Exception as e:
                    logging.warning(f"Failed to process file {file_path}: {e}")
                    continue
            
            if documents:
                # Add to collection in batches
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i + batch_size]
                    batch_metas = metadatas[i:i + batch_size]
                    batch_ids = ids[i:i + batch_size]
                    
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
                
                logging.info(f"Added {len(documents)} code chunks to vector database")
                return True
            
        except Exception as e:
            logging.error(f"Failed to add codebase to RAG: {e}")
        
        return False
    
    def search_similar_code(self, query: str, n_results: int = 5, 
                          filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar code chunks based on semantic similarity."""
        if not self.is_available():
            return []
        
        try:
            # Build where clause for filtering
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if key in ["language", "file_name", "content_type"]:
                        where_clause[key] = value
                    elif key == "has_issues" and isinstance(value, bool):
                        where_clause[key] = value
                    elif key == "min_complexity" and isinstance(value, (int, float)):
                        where_clause["complexity_score"] = {"$gte": value}
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else None
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Failed to search similar code: {e}")
            return []
    
    def get_code_context(self, question: str, analysis_results: Dict[str, Any]) -> str:
        """Get relevant code context for answering questions."""
        if not self.is_available():
            return "RAG system not available. Using basic analysis context."
        
        # Use Embedding RAG if available
        if self.embedding_rag and self.embedding_rag.is_available():
            return self.embedding_rag.get_code_context(question, analysis_results)
        
        # Use Simple RAG if available
        if self.simple_rag and self.simple_rag.is_available():
            return self.simple_rag.get_code_context(question, analysis_results)
        
        try:
            # Search for relevant code chunks
            relevant_chunks = self.search_similar_code(question, n_results=3)
            
            if not relevant_chunks:
                return "No relevant code context found."
            
            # Build context string
            context_parts = []
            for chunk in relevant_chunks:
                metadata = chunk['metadata']
                content = chunk['content']
                
                context_part = f"""
File: {metadata['file_name']} ({metadata['language']})
Issues: {metadata['issue_count']} | Complexity: {metadata.get('complexity_score', 0)}
Content Type: {metadata.get('content_type', 'unknown')}

Code:
```{metadata['language']}
{content[:500]}{'...' if len(content) > 500 else ''}
```
"""
                context_parts.append(context_part)
            
            return "\n---\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Failed to get code context: {e}")
            return "Error retrieving code context."
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except:
                pass
        return len(text.split())  # Fallback to word count
    
    def _classify_content(self, content: str) -> str:
        """Classify the type of code content."""
        content_lower = content.lower()
        
        if 'class ' in content_lower and 'def ' in content_lower:
            return 'class_definition'
        elif 'def ' in content_lower or 'function ' in content_lower:
            return 'function_definition'
        elif 'import ' in content_lower or 'from ' in content_lower:
            return 'imports'
        elif 'test' in content_lower and ('def test' in content_lower or 'class test' in content_lower):
            return 'test_code'
        elif any(keyword in content_lower for keyword in ['config', 'setting', 'constant']):
            return 'configuration'
        elif content_lower.strip().startswith('#') or content_lower.strip().startswith('"""'):
            return 'documentation'
        else:
            return 'general_code'
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection."""
        if not self.is_available():
            return {"error": "RAG system not available"}
        
        # Use Embedding RAG if available
        if self.embedding_rag and self.embedding_rag.is_available():
            return self.embedding_rag.get_collection_stats()
        
        # Use Simple RAG if available
        if self.simple_rag and self.simple_rag.is_available():
            return self.simple_rag.get_collection_stats()
        
        try:
            count = self.collection.count()
            
            # Get sample of metadata for analysis
            if count > 0:
                sample = self.collection.get(limit=min(100, count))
                
                # Analyze metadata
                languages = {}
                content_types = {}
                total_issues = 0
                
                for metadata in sample['metadatas']:
                    lang = metadata.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    content_type = metadata.get('content_type', 'unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                    
                    total_issues += metadata.get('issue_count', 0)
                
                return {
                    "total_chunks": count,
                    "languages": languages,
                    "content_types": content_types,
                    "avg_issues_per_chunk": total_issues / len(sample['metadatas']) if sample['metadatas'] else 0
                }
            else:
                return {"total_chunks": 0}
                
        except Exception as e:
            return {"error": f"Failed to get collection stats: {e}"}
    
    def clear_collection(self) -> bool:
        """Clear the vector database collection."""
        if not self.is_available():
            return False
        
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Code analysis chunks with metadata"}
            )
            logging.info("Cleared vector database collection")
            return True
        except Exception as e:
            logging.error(f"Failed to clear collection: {e}")
            return False
    
    def _add_to_faiss(self, files: List[Path], analysis_results: Dict[str, Any]) -> bool:
        """Add codebase to FAISS system."""
        try:
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                chunks = self.faiss_rag["text_splitter"].split_text(content)
                for chunk in chunks:
                    self.faiss_rag["documents"].append({
                        "content": chunk,
                        "file_path": str(file_path),
                        "language": analysis_results.get('files', {}).get(str(file_path), {}).get('language', 'unknown')
                    })
            
            logging.info(f"Added {len(files)} files to FAISS RAG")
            return True
        except Exception as e:
            logging.error(f"FAISS add failed: {e}")
            return False
    
    def _add_to_simple_rag(self, files, analysis_results):
        """Add files to Simple RAG system."""
        try:
            # Import Path here to avoid issues
            from pathlib import Path as PathLib
            
            for file_path in files:
                if isinstance(file_path, str):
                    file_path = PathLib(file_path)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                chunks = self.simple_rag.text_splitter.split_text(content) if hasattr(self.simple_rag, 'text_splitter') else [content]
                for chunk in chunks:
                    self.simple_rag.documents.append({
                        "content": chunk,
                        "file_path": str(file_path),
                        "language": analysis_results.get('files', {}).get(str(file_path), {}).get('language', 'unknown')
                    })
            
            logging.info(f"Added {len(files)} files to Simple RAG")
            return True
        except Exception as e:
            logging.error(f"Simple RAG add failed: {e}")
            return False
    
    def _get_faiss_context(self, question: str, analysis_results: Dict[str, Any]) -> str:
        """Get context from FAISS system."""
        try:
            if not self.faiss_rag or not self.faiss_rag["documents"]:
                return "No code context available."
            
            # Simple keyword matching for now
            question_lower = question.lower()
            relevant_chunks = []
            
            for doc in self.faiss_rag["documents"][:5]:  # Limit to first 5 for demo
                if any(word in doc["content"].lower() for word in question_lower.split()):
                    relevant_chunks.append(doc)
            
            if relevant_chunks:
                context_lines = ["**Relevant Code Context:**"]
                for i, chunk in enumerate(relevant_chunks[:3], 1):
                    content_preview = chunk["content"][:300] + "..." if len(chunk["content"]) > 300 else chunk["content"]
                    context_lines.append(f"\n{i}. File: {chunk['file_path']} ({chunk['language']})")
                    context_lines.append(f"   Code: {content_preview}")
                
                return "\n".join(context_lines)
            
            return "No relevant code context found."
            
        except Exception as e:
            logging.error(f"FAISS context error: {e}")
            return "Error retrieving code context."
    
    def _get_faiss_stats(self) -> Dict[str, Any]:
        """Get FAISS system statistics."""
        try:
            if not self.faiss_rag:
                return {"error": "FAISS system not available"}
            
            docs = self.faiss_rag["documents"]
            languages = {}
            
            for doc in docs:
                lang = doc.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
            
            return {
                "total_chunks": len(docs),
                "languages": languages,
                "avg_issues_per_chunk": 0,  # Simplified for demo
                "system": "FAISS"
            }
            
        except Exception as e:
            return {"error": f"FAISS stats error: {e}"}
