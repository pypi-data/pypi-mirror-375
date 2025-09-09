"""Report generation for code quality analysis."""

from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress
from rich.markdown import Markdown


class ReportGenerator:
    """Generate comprehensive code quality reports."""
    
    def __init__(self):
        """Initialize report generator."""
        self.console = Console()
    
    def generate_console_report(self, analysis_results: Dict[str, Any]) -> None:
        """Generate and display a rich console report."""
        self.console.clear()
        
        # Header
        self._print_header(analysis_results)
        
        # Summary
        self._print_summary(analysis_results)
        
        # Issues by severity
        self._print_issues_by_severity(analysis_results.get('issues', []))
        
        # Top issues
        self._print_top_issues(analysis_results.get('issues', []))
        
        # Recommendations
        self._print_recommendations(analysis_results.get('recommendations', []))
        
        # File-level details
        self._print_file_details(analysis_results.get('file_analyses', {}))
    
    def _print_header(self, results: Dict[str, Any]) -> None:
        """Print report header."""
        title = Text("Code Quality Intelligence Report", style="bold blue")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header_panel = Panel(
            f"[bold]Generated on:[/bold] {timestamp}\n"
            f"[bold]Analysis Status:[/bold] {'✅ Complete' if not results.get('error') else '❌ Error'}",
            title=title,
            border_style="blue"
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print analysis summary."""
        summary = results.get('summary', {})
        
        # Create summary table
        summary_table = Table(title="Analysis Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan", width=20)
        summary_table.add_column("Value", style="yellow", width=15)
        summary_table.add_column("Status", style="green", width=15)
        
        # Add rows
        total_files = summary.get('total_files', 0)
        total_issues = summary.get('total_issues', 0)
        
        summary_table.add_row("Files Analyzed", str(total_files), "✅" if total_files > 0 else "⚠️")
        summary_table.add_row("Total Issues", str(total_issues), self._get_issue_status(total_issues))
        
        # Add metrics
        metrics = summary.get('metrics', {})
        for metric, value in metrics.items():
            status = self._get_metric_status(metric, value)
            summary_table.add_row(
                metric.replace('_', ' ').title(),
                f"{value:.1f}",
                status
            )
        
        self.console.print(summary_table)
        self.console.print()
    
    def _print_issues_by_severity(self, issues: List[Dict[str, Any]]) -> None:
        """Print issues grouped by severity."""
        if not issues:
            self.console.print("[green]🎉 No issues found![/green]\n")
            return
        
        # Group by severity
        severity_groups = {}
        for issue in issues:
            severity = issue.get('severity', 'info')
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(issue)
        
        # Create severity table
        severity_table = Table(title="Issues by Severity", show_header=True, header_style="bold red")
        severity_table.add_column("Severity", style="bold", width=12)
        severity_table.add_column("Count", style="yellow", width=8)
        severity_table.add_column("Categories", style="cyan", width=40)
        
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        
        for severity in severity_order:
            if severity in severity_groups:
                count = len(severity_groups[severity])
                categories = set(issue.get('category', 'unknown') for issue in severity_groups[severity])
                
                severity_icon = {
                    'critical': '🚨',
                    'high': '🔴', 
                    'medium': '🟡',
                    'low': '🟢',
                    'info': 'ℹ️'
                }.get(severity, '❓')
                
                severity_table.add_row(
                    f"{severity_icon} {severity.title()}",
                    str(count),
                    ", ".join(categories)
                )
        
        self.console.print(severity_table)
        self.console.print()
    
    def _print_top_issues(self, issues: List[Dict[str, Any]], limit: int = 10) -> None:
        """Print top issues with details."""
        if not issues:
            return
        
        # Sort by severity and take top issues
        top_issues = sorted(issues, 
                           key=lambda x: (
                               {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
                               .get(x.get('severity', 'info'), 0)
                           ), 
                           reverse=True)[:limit]
        
        self.console.print(f"[bold red]Top {len(top_issues)} Issues[/bold red]")
        self.console.print()
        
        for i, issue in enumerate(top_issues, 1):
            self._print_issue_detail(issue, i)
    
    def _print_issue_detail(self, issue: Dict[str, Any], index: int) -> None:
        """Print detailed issue information."""
        severity = issue.get('severity', 'info')
        category = issue.get('category', 'unknown')
        title = issue.get('title', 'Unknown Issue')
        description = issue.get('description', '')
        suggestion = issue.get('suggestion', '')
        file_path = issue.get('file_path', '')
        line_number = issue.get('line_number', 0)
        
        # Severity styling
        severity_styles = {
            'critical': 'bold red',
            'high': 'red',
            'medium': 'yellow', 
            'low': 'green',
            'info': 'blue'
        }
        
        severity_style = severity_styles.get(severity, 'white')
        
        # Create issue panel
        issue_content = []
        
        if description:
            issue_content.append(f"[bold]Description:[/bold] {description}")
        
        if file_path:
            location = f"{file_path}"
            if line_number:
                location += f":{line_number}"
            issue_content.append(f"[bold]Location:[/bold] {location}")
        
        if suggestion:
            issue_content.append(f"[bold]Suggestion:[/bold] {suggestion}")
        
        # Code snippet if available
        code_snippet = issue.get('code_snippet', '')
        if code_snippet:
            issue_content.append(f"[bold]Code:[/bold]\n```\n{code_snippet}\n```")
        
        panel_content = "\n\n".join(issue_content)
        
        issue_panel = Panel(
            panel_content,
            title=f"[{severity_style}]{index}. [{severity.upper()}] {title}[/{severity_style}]",
            subtitle=f"Category: {category}",
            border_style=severity_style
        )
        
        self.console.print(issue_panel)
        self.console.print()
    
    def _print_recommendations(self, recommendations: List[str]) -> None:
        """Print recommendations."""
        if not recommendations:
            return
        
        self.console.print("[bold green]🎯 Recommendations[/bold green]")
        self.console.print()
        
        for i, rec in enumerate(recommendations, 1):
            self.console.print(f"{i}. {rec}")
        
        self.console.print()
    
    def _print_file_details(self, file_analyses: Dict[str, Any]) -> None:
        """Print file-level analysis details."""
        if not file_analyses:
            return
        
        self.console.print("[bold blue]📁 File Analysis Details[/bold blue]")
        self.console.print()
        
        # Create file table
        file_table = Table(show_header=True, header_style="bold blue")
        file_table.add_column("File", style="cyan", width=40)
        file_table.add_column("Issues", style="yellow", width=8)
        file_table.add_column("Complexity", style="magenta", width=12)
        file_table.add_column("Status", style="green", width=10)
        
        for file_path, analysis in file_analyses.items():
            if isinstance(analysis, dict) and not analysis.get('error'):
                issue_count = len(analysis.get('issues', []))
                complexity = analysis.get('metrics', {}).get('complexity_score', 0)
                status = "✅" if issue_count == 0 else f"⚠️ {issue_count}"
                
                file_table.add_row(
                    Path(file_path).name,
                    str(issue_count),
                    f"{complexity:.1f}" if complexity else "N/A",
                    status
                )
        
        self.console.print(file_table)
        self.console.print()
    
    def _get_issue_status(self, count: int) -> str:
        """Get status emoji for issue count."""
        if count == 0:
            return "✅"
        elif count <= 5:
            return "⚠️"
        else:
            return "❌"
    
    def _get_metric_status(self, metric: str, value: float) -> str:
        """Get status emoji for metric value."""
        if metric == 'complexity_score':
            return "✅" if value < 10 else "⚠️" if value < 20 else "❌"
        elif metric == 'maintainability_score':
            return "✅" if value > 70 else "⚠️" if value > 50 else "❌"
        elif metric == 'security_score':
            return "✅" if value > 80 else "⚠️" if value > 60 else "❌"
        elif metric == 'overall_score':
            return "✅" if value > 75 else "⚠️" if value > 50 else "❌"
        else:
            return "ℹ️"
    
    def generate_json_report(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Generate JSON report file."""
        try:
            # Add metadata
            report_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'tool': 'Code Quality Intelligence Agent'
                },
                'analysis': analysis_results
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ JSON report saved to: {output_path}[/green]")
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save JSON report: {e}[/red]")
    
    def generate_markdown_report(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Generate Markdown report file."""
        try:
            summary = analysis_results.get('summary', {})
            issues = analysis_results.get('issues', [])
            recommendations = analysis_results.get('recommendations', [])
            
            # Build markdown content
            md_content = []
            
            # Header
            md_content.append("# Code Quality Intelligence Report")
            md_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            md_content.append("")
            
            # Summary
            md_content.append("## Summary")
            md_content.append(f"- **Files Analyzed**: {summary.get('total_files', 0)}")
            md_content.append(f"- **Total Issues**: {summary.get('total_issues', 0)}")
            md_content.append("")
            
            # Metrics
            metrics = summary.get('metrics', {})
            if metrics:
                md_content.append("### Metrics")
                for metric, value in metrics.items():
                    md_content.append(f"- **{metric.replace('_', ' ').title()}**: {value:.1f}")
                md_content.append("")
            
            # Issues
            if issues:
                md_content.append("## Issues")
                
                # Group by severity
                severity_groups = {}
                for issue in issues:
                    severity = issue.get('severity', 'info')
                    if severity not in severity_groups:
                        severity_groups[severity] = []
                    severity_groups[severity].append(issue)
                
                severity_order = ['critical', 'high', 'medium', 'low', 'info']
                
                for severity in severity_order:
                    if severity in severity_groups:
                        md_content.append(f"### {severity.title()} Issues ({len(severity_groups[severity])})")
                        
                        for issue in severity_groups[severity][:5]:  # Top 5 per severity
                            title = issue.get('title', 'Unknown Issue')
                            description = issue.get('description', '')
                            file_path = issue.get('file_path', '')
                            line_number = issue.get('line_number', 0)
                            
                            md_content.append(f"#### {title}")
                            if description:
                                md_content.append(f"**Description**: {description}")
                            if file_path:
                                location = f"{file_path}"
                                if line_number:
                                    location += f":{line_number}"
                                md_content.append(f"**Location**: `{location}`")
                            
                            suggestion = issue.get('suggestion', '')
                            if suggestion:
                                md_content.append(f"**Suggestion**: {suggestion}")
                            
                            md_content.append("")
            
            # Recommendations
            if recommendations:
                md_content.append("## Recommendations")
                for i, rec in enumerate(recommendations, 1):
                    md_content.append(f"{i}. {rec}")
                md_content.append("")
            
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            
            self.console.print(f"[green]✅ Markdown report saved to: {output_path}[/green]")
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save Markdown report: {e}[/red]")
