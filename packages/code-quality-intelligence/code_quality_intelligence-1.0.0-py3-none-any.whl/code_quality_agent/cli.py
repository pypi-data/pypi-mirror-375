"""Command Line Interface for Code Quality Intelligence Agent."""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from .config import Config
from .agent import CodeQualityAgent
from .report_generator import ReportGenerator


# Force UTF-8 stdout/stderr on Windows to avoid Unicode errors
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

console = Console(emoji=False)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Code Quality Intelligence Agent - Analyze code repositories with AI-powered insights."""
    pass


@cli.command()
@click.argument('path', type=str)
@click.option('--output', '-o', type=str, help='Output file for report (JSON or Markdown)')
@click.option('--format', '-f', type=click.Choice(['console', 'json', 'markdown']), 
              default='console', help='Output format')
@click.option('--interactive', '-i', is_flag=True, help='Enable interactive Q&A mode after analysis')
@click.option('--groq-key', type=str, help='Groq API key (overrides environment variable)')
@click.option('--branch', '-b', type=str, help='Specific branch to analyze (GitHub repos only)')
def analyze(path: str, output: Optional[str], format: str, interactive: bool, groq_key: Optional[str], branch: Optional[str]):
    """Analyze code repository for quality issues.
    
    PATH can be:
    - Local file path
    - Local directory path  
    - GitHub repository URL (https://github.com/user/repo)
    - GitHub repository with branch (https://github.com/user/repo/tree/branch-name)
    
    Examples:
    python cli.py analyze /path/to/code
    python cli.py analyze https://github.com/pallets/flask
    python cli.py analyze https://github.com/user/repo --branch develop
    python cli.py analyze https://github.com/user/repo --interactive --format json --output report.json
    """
    # Set API key if provided
    if groq_key:
        import os
        os.environ['GROQ_API_KEY'] = groq_key
    
    # Validate configuration (offline allowed)
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[red]❌ Configuration Error: {e}[/red]")
        sys.exit(1)
    
    # Handle branch parameter for GitHub URLs
    if branch and not path.startswith('http'):
        console.print(f"[yellow]⚠️ Branch parameter ignored for local paths[/yellow]")
        branch = None
    
    # Run analysis
    asyncio.run(_run_analysis(path, output, format, interactive, branch))


async def _run_analysis(path: str, output: Optional[str], format: str, interactive: bool, branch: Optional[str] = None):
    """Run the analysis workflow."""
    try:
        # Initialize agent
        console.print("[blue]🚀 Initializing Code Quality Intelligence Agent...[/blue]")
        agent = CodeQualityAgent()
        
        # Show analysis start
        _show_analysis_start(path)
        
        # Run analysis
        with console.status("[bold blue]Analyzing codebase...") as status:
            results = await agent.analyze_codebase(path, branch=branch)
        
        # Check for errors
        if 'error' in results:
            console.print(f"[red]❌ Analysis failed: {results['error']}[/red]")
            return
        
        # Generate report
        report_generator = ReportGenerator()
        
        if format == 'console':
            report_generator.generate_console_report(results)
        elif format == 'json' and output:
            report_generator.generate_json_report(results, output)
        elif format == 'markdown' and output:
            report_generator.generate_markdown_report(results, output)
        
        # Interactive Q&A mode
        if interactive:
            if not Config.has_groq_api_key():
                console.print("[yellow]ℹ️ Running in offline mode: answers will be heuristic-based.[/yellow]")
            await _interactive_mode(agent, results)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Analysis interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        if '--debug' in sys.argv:
            import traceback
            console.print(traceback.format_exc())


def _show_analysis_start(path: str):
    """Show analysis start information."""
    # Determine path type
    if path.startswith('http'):
        path_type = "GitHub Repository"
        icon = "🐙"
    elif Path(path).is_file():
        path_type = "File"
        icon = "📄"
    elif Path(path).is_dir():
        path_type = "Directory"
        icon = "📁"
    else:
        path_type = "Path"
        icon = "❓"
    
    start_panel = Panel(
        f"[bold]Target:[/bold] {path}\n"
        f"[bold]Type:[/bold] {path_type}",
        title=f"{icon} Starting Analysis",
        border_style="blue"
    )
    
    console.print(start_panel)
    console.print()


async def _interactive_mode(agent: CodeQualityAgent, analysis_results: dict):
    """Run interactive Q&A mode."""
    console.print("\n[bold green]🤖 Interactive Q&A Mode[/bold green]")
    console.print("[dim]Ask questions about your codebase. Type 'exit' to quit.[/dim]\n")
    
    while True:
        try:
            # Get user question
            question = Prompt.ask("[bold blue]Your question")
            
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            if not question.strip():
                continue
            
            # Get answer from agent
            with console.status("[bold blue]Thinking..."):
                answer = await agent.ask_question(question, analysis_results)
            
            # Display answer
            answer_panel = Panel(
                answer,
                title="🤖 AI Assistant",
                border_style="green"
            )
            console.print(answer_panel)
            console.print()
        
        except KeyboardInterrupt:
            break
    
    console.print("[green]👋 Thanks for using Code Quality Intelligence Agent![/green]")


@cli.command()
def setup():
    """Setup the Code Quality Intelligence Agent."""
    console.print("[bold blue]🔧 Code Quality Intelligence Agent Setup[/bold blue]\n")
    
    # Check API key
    if not Config.GROQ_API_KEY:
        console.print("[yellow]⚠️ GROQ_API_KEY not found in environment[/yellow]")
        
        if Confirm.ask("Would you like to set up your Groq API key now?"):
            api_key = Prompt.ask("Enter your Groq API key", password=True)
            
            # Create .env file
            env_content = f"GROQ_API_KEY={api_key}\n"
            
            try:
                with open('.env', 'w') as f:
                    f.write(env_content)
                console.print("[green]✅ API key saved to .env file[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to save API key: {e}[/red]")
                console.print(f"[yellow]💡 Please set GROQ_API_KEY={api_key} in your environment[/yellow]")
    else:
        console.print("[green]✅ Groq API key found[/green]")
    
    # Check dependencies
    console.print("\n[blue]Checking dependencies...[/blue]")
    
    missing_deps = []
    
    try:
        import langchain
        console.print("✅ LangChain")
    except ImportError:
        missing_deps.append("langchain")
        console.print("❌ LangChain")
    
    try:
        import langchain_groq
        console.print("✅ LangChain-Groq")
    except ImportError:
        missing_deps.append("langchain-groq")
        console.print("❌ LangChain-Groq")
    
    try:
        import git
        console.print("✅ GitPython")
    except ImportError:
        missing_deps.append("gitpython")
        console.print("❌ GitPython")
    
    if missing_deps:
        console.print(f"\n[yellow]⚠️ Missing dependencies: {', '.join(missing_deps)}[/yellow]")
        console.print("[blue]💡 Run: pip install -r requirements.txt[/blue]")
    else:
        console.print("\n[green]🎉 All dependencies installed![/green]")
    
    console.print("\n[bold green]✨ Setup complete! You can now use 'python cli.py analyze <path>'[/bold green]")


@cli.command()
@click.argument('path', type=str)
def info(path: str):
    """Get information about a codebase without full analysis."""
    try:
        from .utils.file_handler import FileHandler
        
        console.print(f"[blue]📊 Analyzing codebase structure: {path}[/blue]\n")
        
        file_handler = FileHandler()
        files = file_handler.get_code_files(path)
        
        if not files:
            console.print("[red]❌ No supported code files found[/red]")
            return
        
        # Language distribution
        language_counts = {}
        total_size = 0
        total_lines = 0
        
        for file_path in files:
            language = file_handler.detect_language(file_path)
            language_counts[language] = language_counts.get(language, 0) + 1
            
            stats = file_handler.get_file_stats(file_path)
            total_size += stats.get('size_bytes', 0)
            total_lines += stats.get('total_lines', 0)
        
        # Display info
        info_text = []
        info_text.append(f"[bold]Total Files:[/bold] {len(files)}")
        info_text.append(f"[bold]Total Size:[/bold] {total_size / 1024:.1f} KB")
        info_text.append(f"[bold]Total Lines:[/bold] {total_lines:,}")
        info_text.append("")
        info_text.append("[bold]Languages:[/bold]")
        
        for language, count in sorted(language_counts.items()):
            percentage = (count / len(files)) * 100
            info_text.append(f"  • {language}: {count} files ({percentage:.1f}%)")
        
        info_panel = Panel(
            "\n".join(info_text),
            title="📊 Codebase Information",
            border_style="blue"
        )
        
        console.print(info_panel)
        
        # Cleanup
        file_handler.cleanup()
    
    except Exception as e:
        console.print(f"[red]❌ Error getting codebase info: {e}[/red]")


@cli.command()
def dashboard():
    """Launch the Streamlit dashboard for interactive analysis."""
    try:
        import subprocess
        import sys
        
        console.print("[blue]🚀 Launching Code Quality Intelligence Dashboard...[/blue]")
        console.print("[dim]This will open in your web browser at http://localhost:8501[/dim]\n")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Failed to launch dashboard: {e}[/red]")
        console.print("[blue]💡 Try running: streamlit run streamlit_app.py[/blue]")


@cli.command()
def chat():
    """Start an enhanced interactive chat session with your codebase."""
    console.print("[bold green]🤖 Enhanced Code Quality Chat[/bold green]")
    console.print("[dim]This version includes RAG and conversational features![/dim]\n")
    
    # Get path
    path = Prompt.ask("[bold blue]Enter path or GitHub URL to analyze")
    
    if not path:
        console.print("[red]No path provided[/red]")
        return
    
    try:
        # Run analysis
        console.print("[blue]🔍 Analyzing codebase...[/blue]")
        asyncio.run(_enhanced_chat_session(path))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat session ended by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Chat session error: {e}[/red]")


async def _enhanced_chat_session(path: str):
    """Run enhanced chat session with RAG and conversational features."""
    from .agent import CodeQualityAgent
    
    # Initialize agent
    agent = CodeQualityAgent()
    
    # Run analysis
    with console.status("[bold blue]Analyzing codebase..."):
        results = await agent.analyze_codebase(path)
    
    if 'error' in results:
        console.print(f"[red]❌ Analysis failed: {results['error']}[/red]")
        return
    
    # Show quick summary
    summary = results.get('summary', {})
    console.print(Panel(
        f"[bold]Analysis Complete![/bold]\n"
        f"Files: {summary.get('total_files', 0)} | "
        f"Issues: {summary.get('total_issues', 0)} | "
        f"RAG: {'✅' if agent.rag_system.is_available() else '❌'}",
        title="📊 Quick Summary",
        border_style="green"
    ))
    
    # Start enhanced chat
    console.print("\n[bold green]💬 Enhanced Chat Mode[/bold green]")
    console.print("[dim]Features: Conversational AI, RAG search, follow-ups, context awareness[/dim]")
    console.print("[dim]Type 'exit' to quit, 'help' for commands[/dim]\n")
    
    while True:
        try:
            question = Prompt.ask("[bold blue]You")
            
            if question.lower() in ['exit', 'quit', 'q']:
                break
            elif question.lower() == 'help':
                _show_chat_help()
                continue
            elif question.lower() == 'stats':
                _show_rag_stats(agent.rag_system)
                continue
            elif not question.strip():
                continue
            
            # Get enhanced response
            with console.status("[bold blue]Thinking..."):
                response = await agent.ask_question(question, results)
            
            # Display response with better formatting
            console.print(Panel(
                response,
                title="🤖 AI Assistant",
                border_style="magenta",
                padding=(1, 2)
            ))
            console.print()
            
        except KeyboardInterrupt:
            break
    
    console.print("[green]👋 Thanks for using Enhanced Code Quality Chat![/green]")


def _show_chat_help():
    """Show chat help commands."""
    help_text = """
[bold]Available Commands:[/bold]
• [cyan]help[/cyan] - Show this help message
• [cyan]stats[/cyan] - Show RAG system statistics  
• [cyan]exit[/cyan] - Exit chat session

[bold]Example Questions:[/bold]
• "What security issues did you find?"
• "How can I reduce code complexity?"
• "Show me the most critical problems"
• "What files have the most issues?"
• "Explain this error in detail"
"""
    console.print(Panel(help_text, title="💡 Chat Help", border_style="blue"))


def _show_rag_stats(rag_system):
    """Show RAG system statistics."""
    if rag_system and rag_system.is_available():
        stats = rag_system.get_collection_stats()
        
        if 'error' not in stats:
            stats_text = f"""
[bold]RAG System Status:[/bold] ✅ Active

[bold]Statistics:[/bold]
• Code chunks stored: {stats.get('total_chunks', 0)}
• Average issues per chunk: {stats.get('avg_issues_per_chunk', 0):.1f}

[bold]Languages:[/bold]
"""
            for lang, count in stats.get('languages', {}).items():
                stats_text += f"• {lang}: {count} chunks\n"
            
            console.print(Panel(stats_text, title="🧠 RAG Statistics", border_style="cyan"))
        else:
            console.print(Panel(f"❌ {stats['error']}", title="RAG Error", border_style="red"))
    else:
        console.print(Panel("❌ RAG system not available", title="RAG Status", border_style="red"))


if __name__ == '__main__':
    cli()
