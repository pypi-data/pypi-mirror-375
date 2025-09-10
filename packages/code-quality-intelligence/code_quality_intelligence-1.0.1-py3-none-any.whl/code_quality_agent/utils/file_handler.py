"""File handling utilities for the Code Quality Agent."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import subprocess

import git
from git import Repo

from ..config import Config


class FileHandler:
    """Handle file operations and repository cloning."""
    
    def __init__(self):
        """Initialize file handler."""
        self.temp_dirs = []
    
    def get_code_files(self, path: str, branch: Optional[str] = None) -> List[Path]:
        """Get all supported code files from path or GitHub URL."""
        if self._is_github_url(path):
            return self._get_files_from_github(path, branch=branch)
        else:
            return self._get_files_from_local(path)
    
    def _is_github_url(self, path: str) -> bool:
        """Check if path is a GitHub URL."""
        try:
            parsed = urlparse(path)
            return parsed.netloc.lower() in ['github.com', 'www.github.com']
        except:
            return False
    
    def _parse_github_url(self, github_url: str) -> dict:
        """Parse GitHub URL to extract owner, repo, and branch info."""
        try:
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub URL format")
            
            owner = path_parts[0]
            repo = path_parts[1]
            
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            
            # Extract branch from URL if present (e.g., /tree/branch-name)
            branch = None
            if len(path_parts) >= 4 and path_parts[2] == 'tree':
                branch = path_parts[3]
            
            return {
                'owner': owner,
                'repo': repo,
                'branch': branch,
                'full_name': f"{owner}/{repo}"
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse GitHub URL: {e}")
    
    def _get_files_from_github(self, github_url: str, branch: Optional[str] = None) -> List[Path]:
        """Clone GitHub repo and get code files."""
        try:
            # Parse URL to extract repo info
            repo_info = self._parse_github_url(github_url)
            
            # Override branch from URL with CLI parameter if provided
            target_branch = branch or repo_info['branch']
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            self.temp_dirs.append(temp_dir)
            
            # Clone repository
            print(f"🐙 Cloning GitHub repository: {repo_info['owner']}/{repo_info['repo']}")
            if target_branch:
                print(f"📋 Branch: {target_branch}")
            
            try:
                # Clone with specific branch if provided
                if target_branch:
                    repo = Repo.clone_from(github_url.split('/tree/')[0], temp_dir, branch=target_branch)
                else:
                    repo = Repo.clone_from(github_url.split('/tree/')[0], temp_dir)
                
                print(f"✅ Successfully cloned to temporary directory")
                
                # Get repository statistics
                commit_count = len(list(repo.iter_commits('HEAD', max_count=100)))
                print(f"📊 Repository info: {commit_count}+ commits")
                
            except Exception as clone_error:
                print(f"❌ Clone failed: {clone_error}")
                return []
            
            # Get code files from cloned repo
            files = self._get_files_from_local(temp_dir)
            print(f"📁 Found {len(files)} code files to analyze")
            
            return files
            
        except Exception as e:
            print(f"❌ Error processing GitHub repository: {e}")
            return []
    
    def _get_files_from_local(self, path: str) -> List[Path]:
        """Get code files from local path."""
        path_obj = Path(path)
        
        if not path_obj.exists():
            return []
        
        code_files = []
        
        if path_obj.is_file():
            # Single file
            if self._is_supported_file(path_obj):
                code_files.append(path_obj)
        else:
            # Directory - walk through files
            for file_path in path_obj.rglob('*'):
                if (file_path.is_file() and 
                    self._is_supported_file(file_path) and
                    not self._should_ignore_file(file_path)):
                    code_files.append(file_path)
        
        # Sort by size (smaller files first for faster analysis)
        code_files.sort(key=lambda f: f.stat().st_size)
        
        # Limit number of files to prevent overwhelming analysis
        return code_files[:100]  # Analyze max 100 files
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file extension is supported."""
        return file_path.suffix.lower() in Config.SUPPORTED_EXTENSIONS
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = [
            '.git', '__pycache__', 'node_modules', '.pytest_cache',
            'venv', 'env', '.env', 'dist', 'build', '.next',
            'coverage', '.coverage', '.nyc_output', 'target',
            'bin', 'obj', '.vs', '.vscode'
        ]
        
        # Check if any parent directory matches ignore patterns
        for parent in file_path.parents:
            if parent.name in ignore_patterns:
                return True
        
        # Check file size
        try:
            if file_path.stat().st_size > Config.MAX_FILE_SIZE:
                return True
        except:
            return True
        
        # Check specific file patterns
        if file_path.name.startswith('.') and file_path.suffix not in ['.py', '.js', '.ts']:
            return True
        
        return False
    
    def detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript', 
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.ipynb': 'jupyter'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    def get_file_content(self, file_path: Path) -> Optional[str]:
        """Get file content safely."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
    
    def get_file_stats(self, file_path: Path) -> dict:
        """Get file statistics."""
        try:
            stat = file_path.stat()
            content = self.get_file_content(file_path)
            
            stats = {
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'language': self.detect_language(file_path)
            }
            
            if content:
                lines = content.split('\n')
                stats.update({
                    'total_lines': len(lines),
                    'non_empty_lines': len([line for line in lines if line.strip()]),
                    'comment_lines': self._count_comment_lines(content, stats['language'])
                })
            
            return stats
        except Exception:
            return {}
    
    def _count_comment_lines(self, content: str, language: str) -> int:
        """Count comment lines based on language."""
        lines = content.split('\n')
        comment_count = 0
        
        if language in ['python']:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    comment_count += 1
        
        elif language in ['javascript', 'typescript', 'java', 'cpp', 'c', 'csharp', 'go', 'rust', 'swift', 'kotlin', 'scala']:
            in_block_comment = False
            for line in lines:
                stripped = line.strip()
                
                # Check for block comments
                if '/*' in stripped:
                    in_block_comment = True
                if '*/' in stripped:
                    in_block_comment = False
                    if stripped.startswith('*/') or stripped == '*/':
                        comment_count += 1
                    continue
                
                # Count block comment lines
                if in_block_comment:
                    comment_count += 1
                # Count single line comments
                elif stripped.startswith('//'):
                    comment_count += 1
        
        elif language in ['php']:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//'):
                    comment_count += 1
        
        elif language in ['ruby']:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    comment_count += 1
        
        return comment_count
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
        self.temp_dirs.clear()
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()
