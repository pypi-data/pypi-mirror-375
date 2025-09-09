"""Setup script for Code Quality Intelligence Agent package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "AI-powered code quality analysis tool"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "langchain==0.2.16",
        "langchain-groq==0.1.9",
        "langchain-community==0.2.16",
        "click==8.1.7",
        "rich==13.7.1",
        "gitpython==3.1.43",
        "requests==2.31.0",
        "python-dotenv==1.0.1",
        "bandit==1.7.5",
        "radon==6.0.1",
        "safety==3.2.7",
    ]

setup(
    name="code-quality-intelligence",
    version="1.0.0",
    description="AI-powered code quality analysis tool with GitHub integration and interactive chatbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Suvraadeep Das",
    author_email="suvraadeep.das@gmail.com",
    url="https://github.com/suvraadeep/Code-Quality-Intelligence-Agent",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "langchain==0.2.16",
        "langchain-groq==0.1.9", 
        "langchain-community==0.2.16",
        "click==8.1.7",
        "rich==13.7.1",
        "gitpython==3.1.43",
        "requests==2.31.0",
        "python-dotenv==1.0.1",
        "bandit==1.7.5",
        "radon==6.0.1",
        "safety==3.2.7",
        "pygments==2.17.2",
        "pathspec==0.12.1",
        "tqdm==4.66.2",
    ],
    extras_require={
        "full": [
            "streamlit==1.31.0",
            "pandas==2.2.0", 
            "matplotlib==3.8.4",
            "plotly==5.19.0",
            "seaborn==0.13.2",
            "altair==5.2.0",
        ],
        "rag": [
            "chromadb==0.4.22",
            "sentence-transformers==2.2.2",
            "tiktoken==0.5.2",
            "faiss-cpu==1.8.0",
        ],
        "dev": [
            "pytest",
            "black", 
            "flake8",
            "mypy",
        ]
    },
    entry_points={
        "console_scripts": [
            "cqi=code_quality_agent.cli:cli",
            "code-quality=code_quality_agent.cli:cli",
            "code-quality-agent=code_quality_agent.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="code quality, static analysis, AI, LLM, security, complexity, GitHub, chatbot",
    project_urls={
        "Bug Reports": "https://github.com/suvraadeep/Code-Quality-Intelligence-Agent/issues",
        "Source": "https://github.com/suvraadeep/Code-Quality-Intelligence-Agent",
        "Documentation": "https://github.com/suvraadeep/Code-Quality-Intelligence-Agent#readme",
    },
)