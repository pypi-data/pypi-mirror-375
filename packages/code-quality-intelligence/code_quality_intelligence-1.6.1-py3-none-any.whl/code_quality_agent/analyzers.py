"""Code analyzers for different quality aspects."""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import hashlib

try:
    import bandit
    from bandit.core import config as bandit_config
    from bandit.core import manager as bandit_manager
except ImportError:
    bandit = None

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit, h_visit
except ImportError:
    cc_visit = mi_visit = h_visit = None


class CodeAnalyzer:
    """Comprehensive code analyzer for multiple languages."""
    
    def __init__(self):
        """Initialize analyzer with available tools."""
        self.available_tools = self._check_available_tools()
    
    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which analysis tools are available."""
        tools = {
            'bandit': bandit is not None,
            'radon': cc_visit is not None,
            'semgrep': self._check_semgrep(),
            'ast': True  # Built-in
        }
        return tools
    
    def _check_semgrep(self) -> bool:
        """Check if semgrep is available."""
        try:
            subprocess.run(['semgrep', '--version'], 
                          capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file for quality issues."""
        results = {
            'security_issues': [],
            'complexity_issues': [],
            'style_issues': [],
            'metrics': {},
            'duplication': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # AST-based analysis
            try:
                tree = ast.parse(content)
                results.update(self._analyze_python_ast(tree, content))
            except SyntaxError as e:
                results['syntax_errors'] = [str(e)]
            
            # Security analysis with Bandit
            if self.available_tools['bandit']:
                results['security_issues'].extend(
                    self._run_bandit_analysis(file_path)
                )
            
            # Complexity analysis with Radon
            if self.available_tools['radon']:
                results['metrics'].update(
                    self._run_radon_analysis(content)
                )
            
            # Semgrep analysis
            if self.available_tools['semgrep']:
                results['pattern_issues'] = self._run_semgrep_analysis(file_path)

            # Lightweight regex-based checks to ensure core findings
            results = self._augment_python_with_patterns(content, results)

            # Duplication fingerprints per function for cross-file aggregation
            results['duplication'].extend(self._fingerprint_code_blocks(content, language='python'))
            
        except Exception as e:
            results['analysis_error'] = str(e)
        
        return results
    
    def analyze_javascript_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file."""
        results = {
            'security_issues': [],
            'complexity_issues': [],
            'style_issues': [],
            'metrics': {},
            'duplication': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Basic pattern-based analysis
            results.update(self._analyze_js_patterns(content))
            
            # Semgrep analysis for JS/TS
            if self.available_tools['semgrep']:
                results['pattern_issues'] = self._run_semgrep_analysis(file_path)

            # Duplication fingerprints for functions/blocks
            results['duplication'].extend(self._fingerprint_code_blocks(content, language='javascript'))
            
        except Exception as e:
            results['analysis_error'] = str(e)
        
        return results
    
    def analyze_jupyter_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Jupyter notebook file for quality issues."""
        results = {
            'security_issues': [],
            'complexity_issues': [],
            'style_issues': [],
            'metrics': {},
            'duplication': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse JSON content of notebook
            try:
                import json
                notebook_data = json.loads(content)
                
                # Extract code cells and analyze them
                code_cells = []
                for cell in notebook_data.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        cell_source = ''.join(cell.get('source', []))
                        if cell_source.strip():
                            code_cells.append(cell_source)
                
                # Combine all code cells for analysis
                if code_cells:
                    combined_code = '\n\n'.join(code_cells)
                    
                    # Analyze as Python code (most notebooks are Python)
                    try:
                        tree = ast.parse(combined_code)
                        results.update(self._analyze_python_ast(tree, combined_code))
                    except SyntaxError as e:
                        results['syntax_errors'] = [f"Syntax error in notebook: {str(e)}"]
                    
                    # Security analysis with Bandit if available
                    if self.available_tools['bandit']:
                        # Create temporary file for Bandit analysis
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                            temp_file.write(combined_code)
                            temp_file.flush()
                            temp_path = Path(temp_file.name)
                            try:
                                results['security_issues'].extend(
                                    self._run_bandit_analysis(temp_path)
                                )
                            finally:
                                temp_path.unlink(missing_ok=True)
                    
                    # Complexity analysis with Radon
                    if self.available_tools['radon']:
                        results['metrics'].update(
                            self._run_radon_analysis(combined_code)
                        )
                    
                    # Pattern-based analysis
                    results = self._augment_python_with_patterns(combined_code, results)
                    
                    # Duplication fingerprints
                    results['duplication'].extend(self._fingerprint_code_blocks(combined_code, language='python'))
                    
                    # Add notebook-specific metrics
                    results['metrics']['notebook_stats'] = {
                        'total_cells': len(notebook_data.get('cells', [])),
                        'code_cells': len(code_cells),
                        'empty_cells': len([cell for cell in notebook_data.get('cells', []) if not ''.join(cell.get('source', [])).strip()])
                    }
                else:
                    results['style_issues'].append({
                        'line': 1,
                        'type': 'empty_notebook',
                        'message': 'Notebook contains no code cells',
                        'severity': 'low'
                    })
                    
            except json.JSONDecodeError as e:
                results['analysis_error'] = f"Invalid notebook format: {str(e)}"
            
        except Exception as e:
            results['analysis_error'] = str(e)
        
        return results
    
    def _analyze_python_ast(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Analyze Python AST for various issues."""
        issues = {
            'complexity_issues': [],
            'style_issues': [],
            'best_practice_issues': []
        }
        
        class QualityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.function_complexity = {}
                self.class_complexity = {}
                self.imports = []
                self.todos = []
                
            def visit_FunctionDef(self, node):
                # Check function complexity
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    issues['complexity_issues'].append({
                        'line': node.lineno,
                        'type': 'high_complexity',
                        'message': f'Function "{node.name}" has high complexity ({complexity})',
                        'severity': 'medium' if complexity < 15 else 'high'
                    })
                
                # Check function length
                if hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        issues['style_issues'].append({
                            'line': node.lineno,
                            'type': 'long_function',
                            'message': f'Function "{node.name}" is too long ({length} lines)',
                            'severity': 'low'
                        })
                
                # Check for missing docstring
                if not ast.get_docstring(node):
                    issues['style_issues'].append({
                        'line': node.lineno,
                        'type': 'missing_docstring',
                        'message': f'Function "{node.name}" missing docstring',
                        'severity': 'low'
                    })
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check for missing docstring
                if not ast.get_docstring(node):
                    issues['style_issues'].append({
                        'line': node.lineno,
                        'type': 'missing_docstring',
                        'message': f'Class "{node.name}" missing docstring',
                        'severity': 'low'
                    })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append(alias.name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    self.imports.append(node.module)
                self.generic_visit(node)
            
            def _calculate_cyclomatic_complexity(self, node):
                """Calculate cyclomatic complexity of a function."""
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                        complexity += 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                    elif isinstance(child, (ast.With, ast.AsyncWith)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                
                return complexity
        
        visitor = QualityVisitor()
        visitor.visit(tree)
        
        return issues

    def _augment_python_with_patterns(self, content: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Add regex-based findings for Python to catch common issues reliably."""
        lines = content.split('\n')

        patterns = [
            # Security
            (r"pickle\.(loads|load)\(", 'Unsafe deserialization (pickle)', 'high', 'security_issues'),
            (r"eval\s*\(", 'Use of eval() is dangerous', 'high', 'security_issues'),
            (r"exec\s*\(", 'Use of exec() is dangerous', 'high', 'security_issues'),
            (r"SELECT\s+.*\{.*\}", 'Possible SQL string formatting in query (f-string)', 'high', 'security_issues'),
            (r"SELECT.+\+.+", 'Possible SQL concatenation; use parameters', 'high', 'security_issues'),
            (r"(sk|gsk)[_-][A-Za-z0-9]{16,}", 'Possible hardcoded secret or API key', 'medium', 'security_issues'),
            # Style / Best practices
            (r"except:\s*$", 'Bare except detected; catch specific exceptions', 'low', 'style_issues'),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message, severity, bucket in patterns:
                if re.search(pattern, line):
                    results[bucket].append({
                        'line': i,
                        'type': 'pattern',
                        'message': message,
                        'severity': severity,
                        'code': line.strip()
                    })

        return results
    
    def _analyze_js_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript content using regex patterns."""
        issues = {
            'security_issues': [],
            'style_issues': [],
            'best_practice_issues': []
        }
        
        lines = content.split('\n')
        
        # Security patterns
        security_patterns = [
            (r'eval\s*\(', 'Use of eval() is dangerous', 'high'),
            (r'innerHTML\s*=', 'Direct innerHTML assignment can lead to XSS', 'medium'),
            (r'document\.write\s*\(', 'document.write can be dangerous', 'medium'),
            (r'setTimeout\s*\(\s*["\']', 'String-based setTimeout is dangerous', 'medium'),
        ]
        
        # Style patterns  
        style_patterns = [
            (r'var\s+\w+', 'Use let/const instead of var', 'low'),
            (r'==\s*(?!null)', 'Use === instead of ==', 'low'),
            (r'function\s+\w+\s*\([^)]*\)\s*{[^}]{200,}', 'Function is too long', 'medium'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Check security patterns
            for pattern, message, severity in security_patterns:
                if re.search(pattern, line):
                    issues['security_issues'].append({
                        'line': i,
                        'type': 'security_pattern',
                        'message': message,
                        'severity': severity,
                        'code': line.strip()
                    })
            
            # Check style patterns
            for pattern, message, severity in style_patterns:
                if re.search(pattern, line):
                    issues['style_issues'].append({
                        'line': i,
                        'type': 'style_pattern', 
                        'message': message,
                        'severity': severity,
                        'code': line.strip()
                    })
        
        return issues
    
    def _run_bandit_analysis(self, file_path: Path) -> List[Dict[str, Any]]:
        """Run Bandit security analysis on Python file."""
        try:
            # Create temporary config
            conf = bandit_config.BanditConfig()
            
            # Create manager and run analysis
            b_mgr = bandit_manager.BanditManager(conf, 'file')
            b_mgr.discover_files([str(file_path)])
            b_mgr.run_tests()
            
            issues = []
            for result in b_mgr.get_issue_list():
                issues.append({
                    'line': result.lineno,
                    'type': 'security',
                    'test_id': result.test_id,
                    'message': result.text,
                    'severity': result.severity.lower(),
                    'confidence': result.confidence.lower(),
                    'code': result.get_code(max_lines=1)
                })
            
            return issues
        except Exception:
            return []
    
    def _run_radon_analysis(self, content: str) -> Dict[str, Any]:
        """Run Radon complexity analysis."""
        try:
            metrics = {}
            
            # Cyclomatic complexity
            if cc_visit:
                cc_results = cc_visit(content)
                metrics['cyclomatic_complexity'] = [
                    {
                        'name': result.name,
                        'complexity': result.complexity,
                        'lineno': result.lineno
                    }
                    for result in cc_results
                ]
            
            # Maintainability index
            if mi_visit:
                mi_results = mi_visit(content, multi=True)
                metrics['maintainability_index'] = mi_results
            
            # Halstead metrics
            if h_visit:
                h_results = h_visit(content)
                metrics['halstead'] = h_results._asdict() if h_results else {}
            
            return metrics
        except Exception:
            return {}
    
    def _run_semgrep_analysis(self, file_path: Path) -> List[Dict[str, Any]]:
        """Run Semgrep pattern analysis."""
        try:
            # Run semgrep with auto rules
            result = subprocess.run([
                'semgrep', '--config=auto', '--json', str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                issues = []
                
                for finding in data.get('results', []):
                    issues.append({
                        'line': finding.get('start', {}).get('line', 0),
                        'type': 'pattern',
                        'rule_id': finding.get('check_id', ''),
                        'message': finding.get('message', ''),
                        'severity': finding.get('extra', {}).get('severity', 'info'),
                        'code': finding.get('extra', {}).get('lines', '')
                    })
                
                return issues
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        
        return []

    def _fingerprint_code_blocks(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Create content fingerprints to detect near-duplicate code across files.
        Returns a list of {hash, start_line, end_line, size} entries.
        """
        lines = content.split('\n')
        window = 10  # sliding window size
        fingerprints: List[Dict[str, Any]] = []

        def normalize(snippet: str) -> str:
            # Remove whitespace and comments crudely for robustness
            cleaned = '\n'.join(l.strip() for l in snippet.split('\n') if l.strip())
            return cleaned

        for i in range(0, max(0, len(lines) - window + 1)):
            block = '\n'.join(lines[i:i + window])
            norm = normalize(block)
            if len(norm) < 40:
                continue
            digest = hashlib.sha1(norm.encode('utf-8')).hexdigest()
            fingerprints.append({
                'hash': digest,
                'start_line': i + 1,
                'end_line': i + window,
                'size': len(norm)
            })
        return fingerprints
