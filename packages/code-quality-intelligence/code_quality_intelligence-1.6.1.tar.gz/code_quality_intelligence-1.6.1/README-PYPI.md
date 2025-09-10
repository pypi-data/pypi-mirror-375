# Code Quality Intelligence Agent

The Code Quality Intelligence Agent is an enterprise-grade tool that combines traditional static analysis with modern AI capabilities to provide comprehensive code quality assessment. The system integrates multiple analysis engines, semantic search capabilities, and conversational AI to deliver actionable insights for software development teams.


Links:
- PyPI package: [`code-quality-intelligence` 1.6.0](https://pypi.org/project/code-quality-intelligence/1.6.0/)
- Source repository: [Code-Quality-Intelligence-Agent](https://github.com/suvraadeep/Code-Quality-Intelligence-Agent.git)

## 1) Environment and Installation

```bash
# 1. Create and activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

#    macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# 2. Install the package
pip install -U pip
pip install code-quality-intelligence

# Optional: feature extras
pip install "code-quality-intelligence[rag]"    # RAG/semantic search extras
pip install "code-quality-intelligence[full]"   # Web/visualization extras
```

Verify installation and entry points:
```bash
cqi --help | cat
code-quality --help | cat
python -m code_quality_agent --help | cat
```

## 2) Quick Start (CLI)

```bash
# Analyze a local project
cqi analyze . --format console

# JSON report
cqi analyze . --format json --output quality.json

# Markdown report
cqi analyze . --format markdown --output quality.md

# Analyze a GitHub repository
cqi analyze https://github.com/pallets/flask

# Choose a branch
cqi analyze https://github.com/user/repo --branch main

# Interactive Q&A post-analysis
cqi analyze . --interactive
```

The `code-quality` and `code-quality-agent` commands are equivalent entry points.

## 3) Web Interface (Streamlit UI)

The package exposes a full web UI shipped in the repo. To run it from your environment:

```bash
# Install web dependencies
pip install streamlit pandas plotly

# If you cloned the repo, you can run the included web app
cd Webpage
pip install -r requirements.txt
streamlit run app.py
```

Alternatively, create your own minimal Streamlit launcher that calls the CLI under the hood.

Access via http://localhost:8501. Pages: Home, Setup, Info, Analyze, Chat.

## 4) Configuration and API Keys

Basic/static analysis works offline. To enable AI-enhanced and chat/RAG features, configure the Groq API key.

```bash
# A) Environment variable
setx GROQ_API_KEY "your_key_here"           # Windows (restart shell)
export GROQ_API_KEY="your_key_here"        # macOS/Linux

# B) .env file in your project directory
echo GROQ_API_KEY=your_key_here > .env

# C) Setup wizard
cqi setup

# D) Per-command override
cqi analyze . --groq-key your_key_here
```

## 5) What It Does — A→Z Workflow

When you run `cqi analyze`:
1. Input resolution (local path or GitHub URL; optional `--branch`).
2. File discovery and language detection via `FileHandler`.
3. Static analysis: Bandit (security), Radon (complexity), pattern checks.
4. Issue aggregation by severity and category.
5. Optional RAG indexing: embeddings with FAISS/Chroma for semantic Q&A.
6. Report generation: console, JSON, or Markdown.
7. Optional interactive chat: LLM-backed answers grounded in analysis results and RAG retrieval.

Key components (package modules): `code_quality_agent.agent`, `analyzers`, `rag_system` and simple fallback RAG modules, `report_generator`, `cli`.

## 6) CLI Reference

- `cqi analyze PATH [--format console|json|markdown] [--output FILE] [--interactive] [--groq-key KEY] [--branch BRANCH]`
- `cqi info PATH` — quick stats without full analysis
- `cqi setup` — store API key to `.env`, check dependencies
- `cqi chat` — enhanced interactive chat (prompts for a path/URL)
- `cqi dashboard` — launches a demo dashboard

Module mode equivalents:
```bash
python -m code_quality_agent --version
python -m code_quality_agent analyze . --format console
python -m code_quality_agent analyze . --interactive
```

## 7) Features

- Security (Bandit), complexity (Radon), best-practice detection
- GitHub analysis with branch support
- Multi-language coverage (Python, JS/TS, Java, C/C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, Scala)
- RAG-enhanced chat and answers; offline heuristic fallback
- Reports: Console, JSON, Markdown
- Streamlit web UI with charts, tables, and setup checks
- Clear error handling and robust CLI UX

## 8) Troubleshooting

- GROQ_API_KEY not found → `cqi setup` or set env/`.env`.
- No supported files → verify path; run `cqi info <path>`.
- RAG not available → install extras: `pip install "code-quality-intelligence[rag]"`.
- GitHub cloning issues → ensure Git is installed and URL/branch are correct.

## 9) CI/CD Example

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

## 10) License

MIT License. See the source repository for details.

## 11) References

- PyPI: [`code-quality-intelligence` 1.6.0](https://pypi.org/project/code-quality-intelligence/1.6.0/)
- GitHub: [Code-Quality-Intelligence-Agent](https://github.com/suvraadeep/Code-Quality-Intelligence-Agent.git)


