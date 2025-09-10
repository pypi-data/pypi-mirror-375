


# Code Quality Intelligence Agent

A comprehensive AI-powered code quality analysis tool that provides intelligent insights into codebases using advanced language models, static analysis techniques, and semantic search capabilities.


## Overview

The Code Quality Intelligence Agent is an enterprise-grade tool that combines traditional static analysis with modern AI capabilities to provide comprehensive code quality assessment. The system integrates multiple analysis engines, semantic search capabilities, and conversational AI to deliver actionable insights for software development teams.

## **Checklist**

- [x] **Core functionality tested and working**  
- [x] **All CLI commands functional (17/17 tests passed)**  
- [x] **Report generation working (JSON, Markdown, Console)**  
- [x] **RAG system implemented and functional**  
- [x] **GitHub and PyPi integration working with cloning**  
- [x] **AI chatbot responding with context**  
- [x] **Error handling graceful and informative**  
- [x] **Documentation updated and complete**  
- [x] **Cross-platform compatibility verified**  
- [x] **Performance acceptable for production**  

### **Future Work**
- [ ] **Cross LLM model inference provider**  
- [ ] **Cross embedding integration**  
- [ ] **Dashboard and visualization**  


## Core Architecture

### Analysis Engine
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, Scala
- **Static Analysis Integration**: Bandit for security, Radon for complexity, Semgrep for patterns
- **AST Parsing**: Deep structural analysis of code syntax and semantics
- **Pattern Recognition**: Security vulnerabilities, performance bottlenecks, maintainability issues

### AI Integration
- **Language Model**: Groq API integration with LangChain framework
- **Model Used**: deepseek-r1-distill-llama-70b for code analysis and conversation
- **Conversation Management**: Context-aware dialogue with memory persistence
- **Fallback System**: Heuristic responses when API unavailable

### RAG System Implementation
- **Vector Database**: FAISS for efficient similarity search
- **Embedding Strategy**: Custom feature extraction optimized for code analysis
- **Feature Dimensions**: 512-dimensional vectors capturing code patterns and semantics
- **Code-Specific Features**:
  - Function and class detection patterns
  - Import statement analysis
  - Security pattern recognition (eval, pickle, SQL injection)
  - Complexity indicators (loops, conditionals, nesting)
  - Vocabulary-based semantic features
- **Text Chunking**: Recursive character splitting optimized for code structure
- **Persistence**: Automatic index saving and loading for performance

### Report Generation
- **Console Output**: Rich formatted terminal reports with color coding and tables
- **JSON Export**: Structured data format for integration with other tools
- **Markdown Export**: Human-readable reports for documentation
- **Interactive Mode**: Real-time Q&A interface with code context

## Installation

### Prerequisites
- Python 3.8 or higher
- Git (for GitHub repository analysis)
- Groq API key (obtain from console.groq.com)

### Core Installation
```bash
# Install core dependencies (recommended)
pip install langchain==0.2.16 langchain-groq==0.1.9 langchain-community==0.2.16 click==8.1.7 rich==13.7.1 gitpython==3.1.43 requests==2.31.0 python-dotenv==1.0.1 bandit==1.7.5 radon==6.0.1 safety==3.2.7 streamlit==1.31.0 pandas==2.2.0 faiss-cpu==1.8.0

# Install from requirements file (may require C++ build tools on Windows)
pip install -r requirements.txt
```

### Package Installation
```bash
# Install as package (after building)
pip install dist/code_quality_intelligence-1.0.0-py3-none-any.whl

# Global commands available after installation
cqi analyze /path/to/code
code-quality analyze /path/to/code --interactive

# Setup web interface for easy access
python setup-web.py
# Then use: python cqi-web.py
```

## Configuration

### API Key Setup
```bash
# Method 1: Environment variable
export GROQ_API_KEY=your_api_key_here

# Method 2: .env file
echo "GROQ_API_KEY=your_api_key_here" > .env

# Method 3: CLI parameter
python cqi.py analyze /path/to/code --groq-key your_api_key_here

# Method 4: Setup wizard
python cqi.py setup
```

### System Validation
```bash
# Validate complete system functionality
python validation.py

# Test RAG system specifically
python -c "from code_quality_agent.rag_system import CodeRAGSystem; rag = CodeRAGSystem(); print('RAG Available:', rag.is_available()); print('System:', rag.get_collection_stats().get('system'))"
```

## Usage

### Basic Analysis Commands

#### Local File Analysis
```bash
# Analyze single file
python cqi.py analyze sample_code/module_a.py --format console

# Analyze directory
python cqi.py analyze sample_code --format console

# Get codebase statistics
python cqi.py info sample_code
```

#### GitHub Repository Analysis
```bash
# Analyze public repository
python cqi.py analyze https://github.com/pallets/flask --format console

# Analyze specific branch
python cqi.py analyze https://github.com/user/repo --branch develop

# Analyze with interactive chat
python cqi.py analyze https://github.com/user/repo --interactive
```

### Report Generation

#### Export Formats
```bash
# Generate JSON report
python cqi.py analyze sample_code --format json --output analysis_report.json

# Generate Markdown report
python cqi.py analyze sample_code --format markdown --output analysis_report.md

# Console output (default)
python cqi.py analyze sample_code --format console
```

### Interactive Features

#### AI-Powered Chat
```bash
# Interactive analysis with RAG-enhanced responses
python cqi.py analyze sample_code --interactive

# Dedicated chat session
python cqi.py chat

# Chat with GitHub repository context
python cqi.py analyze https://github.com/user/repo --interactive
```

### Advanced Options

#### Customization
```bash
# Override API key
python cqi.py analyze code --groq-key custom_api_key

# Branch-specific analysis
python cqi.py analyze https://github.com/user/repo --branch feature-branch

# Combined options
python cqi.py analyze https://github.com/user/repo --format json --output github_analysis.json --interactive --branch main
```

### Package Execution Methods

#### As Python Module
```bash
# Version information
python -m code_quality_agent --version

# Help documentation
python -m code_quality_agent --help

# Analysis execution
python -m code_quality_agent analyze sample_code --format console

# Interactive mode
python -m code_quality_agent analyze sample_code --interactive
```

#### As Entry Point Script
```bash
# Version information
python cqi.py --version

# Help documentation
python cqi.py --help

# Analysis execution
python cqi.py analyze sample_code --format console

# Interactive mode
python cqi.py analyze sample_code --interactive
```

### Web Interfaces

#### Dashboard Access
```bash
# Simple HTML dashboard (no dependencies)
python simple_dashboard.py
# Access at: http://localhost:8080

# Advanced Streamlit dashboard
streamlit run streamlit_app.py
# Access at: http://localhost:8501

# Launch via CLI
python cqi.py dashboard
```

#### Professional Web Interface
```bash
# Quick launch - single command from anywhere
python cqi-web.py

# Windows batch file
cqi-web.bat

# Direct Streamlit launch
cd Webpage && streamlit run app.py
# Access at: http://localhost:8501
```

**Web Interface Features:**
- Professional UI without emojis for enterprise use
- All CLI functionality accessible through web interface
- Real-time analysis progress and visual reports
- Interactive charts and data visualization
- Multi-page navigation (Home, Setup, Info, Analyze, Chat)
- RAG system statistics and management
- GitHub and local file analysis support

## Technical Implementation

### RAG System Details

The Retrieval-Augmented Generation system implements semantic search capabilities for enhanced code analysis and conversational AI responses.

#### Embedding Implementation
- **Vector Database**: FAISS IndexFlatIP for cosine similarity search
- **Feature Extraction**: Custom 512-dimensional feature vectors
- **Code Patterns**: Function definitions, class structures, import statements
- **Security Patterns**: eval usage, pickle operations, SQL injection indicators
- **Vocabulary Building**: Dynamic term frequency analysis
- **Chunking Strategy**: Recursive character splitting with code-aware separators

#### Fallback Hierarchy
1. **ChromaDB**: Full vector database with sentence transformers (requires C++ build tools)
2. **Simple Embedding RAG**: FAISS-based semantic search with custom features
3. **Simple RAG**: Keyword-based matching and text search
4. **No RAG**: Basic analysis without enhanced context

### Analysis Pipeline

#### File Processing
1. **Input Validation**: Path verification and file type detection
2. **Language Detection**: Automatic programming language identification
3. **Content Extraction**: UTF-8 encoding with error handling
4. **Chunking**: Code-aware text splitting for optimal analysis

#### Quality Assessment
1. **Security Analysis**: Bandit integration for vulnerability detection
2. **Complexity Metrics**: Radon integration for cyclomatic complexity
3. **Pattern Matching**: Semgrep rules for best practice violations
4. **Duplication Detection**: Cross-file similarity analysis

#### AI Enhancement
1. **Context Preparation**: RAG system provides relevant code chunks
2. **LLM Processing**: Groq API analysis with conversation memory
3. **Response Generation**: Contextual insights with actionable recommendations
4. **Follow-up Support**: Conversation continuation with maintained context

## Supported Analysis Categories

### Security Assessment
- SQL injection vulnerabilities
- Cross-site scripting risks
- Unsafe deserialization patterns
- Hardcoded credentials detection
- Command injection vulnerabilities

### Performance Analysis
- Algorithmic complexity assessment
- Memory usage patterns
- Database query optimization
- Loop efficiency analysis
- Resource leak detection

### Code Quality Metrics
- Cyclomatic complexity measurement
- Maintainability index calculation
- Code duplication identification
- Documentation coverage assessment
- Naming convention compliance

### Best Practice Validation
- Error handling patterns
- Design pattern implementation
- Testing coverage gaps
- API design principles
- Security best practices

## Integration Examples

### CI/CD Pipeline Integration
```yaml
name: Code Quality Assessment
on: [push, pull_request]

jobs:
  quality_check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Code Quality Agent
        run: pip install code-quality-intelligence
      - name: Run Analysis
        run: cqi analyze . --format json --output quality_report.json
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: quality-report
          path: quality_report.json
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
python cqi.py analyze $(git diff --cached --name-only --diff-filter=ACM)
```

## Performance Characteristics

### Execution Metrics
- **Local Analysis**: Instant results for codebases under 100 files
- **GitHub Analysis**: 2-3 minutes for repositories with 100+ files
- **RAG Indexing**: 0.5-2 seconds per code chunk
- **Embedding Generation**: 50-100ms per code chunk
- **AI Response Time**: 2-5 seconds (depending on API latency)

### Scalability
- **File Limit**: Automatically handles up to 100 files per analysis
- **Size Limit**: Files larger than 1MB are skipped for performance
- **Memory Usage**: Optimized for systems with 4GB+ RAM
- **Concurrent Processing**: Parallel analysis of multiple files

## Error Handling

### Graceful Degradation
- **API Unavailable**: Falls back to heuristic responses
- **RAG Disabled**: Continues with basic analysis
- **Network Issues**: Local analysis remains functional
- **Invalid Paths**: Clear error messages with suggestions

### Troubleshooting

#### Common Issues
**"GROQ_API_KEY not found"**
- Solution: Set environment variable or use --groq-key parameter
- Command: `python cqi.py setup`

**"No supported files found"**
- Solution: Verify file extensions and path correctness
- Command: `python cqi.py info /path/to/code`

**"RAG system not available"**
- Solution: Install optional dependencies or use without RAG
- Command: `pip install faiss-cpu sentence-transformers`

**"GitHub cloning failed"**
- Solution: Verify Git installation and repository access
- Command: Ensure Git is in system PATH

## Development and Customization

### Extending Analysis Rules
The system supports custom analysis rules through the LangChain integration:

```python
# Custom analyzer implementation
from code_quality_agent.analyzers import CodeAnalyzer

class CustomAnalyzer(CodeAnalyzer):
    def analyze_custom_patterns(self, content: str) -> List[Dict]:
        # Implement custom analysis logic
        pass
```

### Adding Language Support
```python
# Language-specific analyzer
def analyze_rust_file(self, file_path: Path) -> Dict[str, Any]:
    # Implement Rust-specific analysis
    return {
        'language': 'rust',
        'issues': [],
        'complexity': {}
    }
```

## API Reference

### Core Classes
- `CodeQualityAgent`: Main analysis orchestrator
- `CodeAnalyzer`: Multi-language static analysis engine
- `CodeRAGSystem`: Semantic search and context retrieval
- `CodeQualityChatbot`: Conversational AI interface
- `ReportGenerator`: Multi-format report generation

### Configuration
- `Config.DEFAULT_MODEL`: LLM model selection
- `Config.MAX_FILE_SIZE`: File size limit (1MB default)
- `Config.SUPPORTED_EXTENSIONS`: Supported file types
- `Config.QUALITY_CATEGORIES`: Analysis categories

## Testing and Validation

### Comprehensive Test Suite
```bash
# Complete system validation
python ship_validation.py

# Feature-specific testing
python test_all_features.py

# Package functionality testing
python -m code_quality_agent analyze sample_code
python cqi.py analyze sample_code --interactive
```

### Expected Results
- **Local Analysis**: 11 issues detected in sample code (3 high-severity security issues)
- **GitHub Analysis**: 136+ issues detected in test repositories
- **RAG System**: 200+ code chunks indexed with semantic search
- **Performance**: Complete validation in under 3 minutes

## License and Attribution

### License
MIT License - see LICENSE file for details

### Dependencies
- **LangChain**: Agent framework and LLM integration
- **Groq**: High-performance LLM inference
- **FAISS**: Efficient similarity search and clustering
- **Rich**: Terminal formatting and user interface
- **Click**: Command-line interface framework
- **GitPython**: Git repository operations
- **Bandit**: Python security analysis
- **Radon**: Code complexity metrics


## Support and Contributing

### Bug Reports
Report issues through the GitHub issue tracker with detailed reproduction steps and environment information.

### Feature Requests
Submit enhancement proposals with clear use cases and implementation suggestions.

### Contributing Guidelines
1. Fork the repository
2. Create feature branch with descriptive name
3. Implement changes with appropriate test coverage
4. Submit pull request with detailed description
5. Ensure all validation tests pass


