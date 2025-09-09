"""
Streamlit Dashboard for Code Quality Intelligence Agent.
This module provides a web-based dashboard with visualizations, charts,
and interactive features for code quality analysis.
"""

import streamlit as st
import pandas as pdg 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import asyncio
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent))

from code_quality_agent.agent import CodeQualityAgent
from code_quality_agent.chatbot import CodeQualityChatbot
from code_quality_agent.rag_system import CodeRAGSystem
from code_quality_agent.config import Config

st.set_page_config(
    page_title="Code Quality Intelligence Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

def setup_rag_and_chatbot():
    if st.session_state.rag_system is None:
        st.session_state.rag_system = CodeRAGSystem()
    
    if st.session_state.chatbot is None:
        st.session_state.chatbot = CodeQualityChatbot(st.session_state.rag_system)

@st.cache_data
def run_analysis(path: str, branch: str = None):
    try:
        agent = CodeQualityAgent()
        # Since we can't use asyncio.run in Streamlit easily, we'll use a workaround
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(agent.analyze_codebase(path, branch=branch))
        loop.close()
        return results
    except Exception as e:
        return {"error": str(e)}

def create_overview_metrics(results):
    if not results or 'error' in results:
        st.error("No analysis results available")
        return
    
    summary = results.get('summary', {})
    issues = results.get('issues', [])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📁 Files Analyzed",
            value=summary.get('total_files', 0)
        )
    
    with col2:
        st.metric(
            label="🐛 Total Issues",
            value=summary.get('total_issues', 0),
            delta=f"{len([i for i in issues if i.get('severity') in ['high', 'critical']])} critical/high"
        )
    
    with col3:
        complexity_score = summary.get('metrics', {}).get('complexity_score', 0)
        st.metric(
            label="🧩 Complexity Score",
            value=f"{complexity_score:.1f}",
            delta="Lower is better"
        )
    
    with col4:
        security_issues = len([i for i in issues if i.get('category') == 'security'])
        st.metric(
            label="🔒 Security Issues",
            value=security_issues,
            delta="Critical priority" if security_issues > 0 else "All clear"
        )

def create_severity_chart(issues):
    if not issues:
        st.info("No issues to display")
        return
    
    severity_counts = {}
    for issue in issues:
        severity = issue.get('severity', 'info').title()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    fig = px.pie(
        values=list(severity_counts.values()),
        names=list(severity_counts.keys()),
        title="Issues by Severity",
        color_discrete_map={
            'Critical': '#ff4444',
            'High': '#ff8800',
            'Medium': '#ffbb33',
            'Low': '#00C851',
            'Info': '#33b5e5'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def create_category_chart(issues):
    if not issues:
        return
    
    category_counts = {}
    for issue in issues:
        category = issue.get('category', 'unknown').replace('_', ' ').title()
        category_counts[category] = category_counts.get(category, 0) + 1
    
    fig = px.bar(
        x=list(category_counts.values()),
        y=list(category_counts.keys()),
        orientation='h',
        title="Issues by Category",
        color=list(category_counts.values()),
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

def create_file_analysis_table(results):
    file_analyses = results.get('file_analyses', {})
    if not file_analyses:
        st.info("No file analysis data available")
        return
    
    table_data = []
    for file_path, analysis in file_analyses.items():
        issues = analysis.get('issues', [])
        metrics = analysis.get('metrics', {})
        
        severity_counts = {}
        for issue in issues:
            severity = issue.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        table_data.append({
            'File': Path(file_path).name,
            'Full Path': file_path,
            'Issues': len(issues),
            'Critical': severity_counts.get('critical', 0),
            'High': severity_counts.get('high', 0),
            'Medium': severity_counts.get('medium', 0),
            'Low': severity_counts.get('low', 0),
            'Complexity': metrics.get('complexity_score', 0),
            'Language': analysis.get('debug', {}).get('language', 'unknown')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        def highlight_issues(val):
            if val > 5:
                return 'background-color: #ffcccc'
            elif val > 2:
                return 'background-color: #fff2cc'
            return ''
        
        styled_df = df.style.applymap(highlight_issues, subset=['Issues', 'Critical', 'High'])
        st.dataframe(styled_df, use_container_width=True)

def create_timeline_chart(analysis_history):
    if not analysis_history:
        st.info("No analysis history available")
        return
    
    df = pd.DataFrame(analysis_history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = px.line(
        df, 
        x='timestamp', 
        y='total_issues',
        title='Code Quality Over Time',
        markers=True
    )
    
    fig.update_layout(xaxis_title="Analysis Date", yaxis_title="Total Issues")
    st.plotly_chart(fig, use_container_width=True)

def create_recommendations_section(results):
    recommendations = results.get('recommendations', [])
    if not recommendations:
        st.info("No specific recommendations available")
        return
    
    st.subheader("🎯 Recommendations")
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

def create_chatbot_interface():
    st.subheader("💬 Chat with Your Codebase")
    
    setup_rag_and_chatbot()
    
    if st.session_state.analysis_results and st.session_state.chatbot:
        st.session_state.chatbot.set_analysis_context(st.session_state.analysis_results)
    
    if st.session_state.chatbot:
        for message in st.session_state.chat_history:
            with st.container():
                st.markdown(
                    f'<div class="chat-message user-message"><strong>You:</strong> {message["user"]}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["assistant"]}</div>',
                    unsafe_allow_html=True
                )
        
        user_input = st.text_input("Ask about your code:", placeholder="e.g., What security issues did you find?")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send", type="primary"):
                if user_input:
                    with st.spinner("Thinking..."):
                        response = st.session_state.chatbot.chat(user_input)
                    
                    st.session_state.chat_history.append({
                        "user": user_input,
                        "assistant": response
                    })
                    st.rerun()
        
        with col2:
            if st.button("Clear Chat"):
                st.session_state.chat_history = []
                if st.session_state.chatbot:
                    st.session_state.chatbot.clear_conversation()
                st.rerun()
    else:
        st.warning("Chatbot not available. Please check your API key configuration.")

def create_rag_stats():
    if st.session_state.rag_system and st.session_state.rag_system.is_available():
        stats = st.session_state.rag_system.get_collection_stats()
        
        if 'error' not in stats:
            st.subheader("🧠 RAG System Status")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Code Chunks Stored", stats.get('total_chunks', 0))
            with col2:
                st.metric("Avg Issues per Chunk", f"{stats.get('avg_issues_per_chunk', 0):.1f}")
            
            if 'languages' in stats:
                lang_df = pd.DataFrame(
                    list(stats['languages'].items()),
                    columns=['Language', 'Chunks']
                )
                fig = px.bar(lang_df, x='Language', y='Chunks', title='Code Chunks by Language')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("RAG system not available or not initialized")

def main():
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">🤖 Code Quality Intelligence Dashboard</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Analysis Settings")
        
        groq_key = st.text_input("Groq API Key", type="password", value=Config.get_groq_api_key())
        if groq_key:
            os.environ['GROQ_API_KEY'] = groq_key
        
        st.subheader("📂 Code Analysis")
        analysis_type = st.radio("Analysis Type", ["Local Path", "GitHub Repository"])
        
        if analysis_type == "Local Path":
            path_input = st.text_input("Local Path", placeholder="./my-project")
            branch_input = None
        else:
            path_input = st.text_input("GitHub URL", placeholder="https://github.com/user/repo")
            branch_input = st.text_input("Branch (optional)", placeholder="main")
        
        if st.button("🔍 Analyze Code", type="primary"):
            if path_input:
                with st.spinner("Analyzing code... This may take a few minutes."):
                    results = run_analysis(path_input, branch_input)
                    st.session_state.analysis_results = results
                    
                    if 'error' not in results:
                        st.session_state.analysis_history.append({
                            'timestamp': datetime.now(),
                            'path': path_input,
                            'total_issues': results.get('summary', {}).get('total_issues', 0),
                            'total_files': results.get('summary', {}).get('total_files', 0)
                        })
                
                st.rerun()
            else:
                st.error("Please enter a path or GitHub URL")
        
        if st.button("🗑️ Clear Results"):
            st.session_state.analysis_results = None
            st.session_state.chat_history = []
            st.rerun()
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        if 'error' in results:
            st.error(f"Analysis failed: {results['error']}")
        else:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Charts", "📋 Details", "💬 Chat", "🧠 RAG"])
            
            with tab1:
                st.header("Analysis Overview")
                create_overview_metrics(results)
                
                st.header("Recommendations")
                create_recommendations_section(results)
                
                if st.session_state.analysis_history:
                    st.header("Quality Trends")
                    create_timeline_chart(st.session_state.analysis_history)
            
            with tab2:
                st.header("Issue Distribution")
                
                col1, col2 = st.columns(2)
                with col1:
                    create_severity_chart(results.get('issues', []))
                with col2:
                    create_category_chart(results.get('issues', []))
            
            with tab3:
                st.header("Detailed Analysis")
                
                st.subheader("📁 File Analysis")
                create_file_analysis_table(results)
                
                st.subheader("🔥 Top Issues")
                issues = results.get('issues', [])
                if issues:
                    for i, issue in enumerate(issues[:10], 1):
                        severity_color = {
                            'critical': '🚨', 'high': '🔴', 'medium': '🟡', 'low': '🟢', 'info': 'ℹ️'
                        }.get(issue.get('severity', 'info'), '❓')
                        
                        with st.expander(f"{severity_color} {issue.get('title', 'Issue')} - {Path(issue.get('file_path', '')).name}:{issue.get('line_number', 'N/A')}"):
                            st.write(f"**Category:** {issue.get('category', 'unknown').title()}")
                            st.write(f"**Severity:** {issue.get('severity', 'info').title()}")
                            st.write(f"**Description:** {issue.get('description', 'No description available')}")
                            if issue.get('suggestion'):
                                st.write(f"**Suggestion:** {issue.get('suggestion')}")
                            if issue.get('code_snippet'):
                                st.code(issue.get('code_snippet'), language=issue.get('language', 'text'))
                else:
                    st.info("No issues found! 🎉")
            
            with tab4:
                create_chatbot_interface()
            
            with tab5:
                create_rag_stats()
    
    else:
        st.markdown("""
        ## Welcome to Code Quality Intelligence Dashboard! 🚀
        
        This dashboard helps you analyze and improve your code quality using AI-powered insights.
        
        ### Features:
        - **Comprehensive Analysis**: Security, performance, complexity, and style issues
        - **GitHub Integration**: Analyze repositories directly from GitHub
        - **Conversational AI**: Chat about your code and get explanations
        - **RAG System**: Semantic search through large codebases
        - **Visual Reports**: Charts and graphs for easy understanding
        
        ### Getting Started:
        1. Enter your Groq API key in the sidebar (optional for basic analysis)
        2. Choose to analyze a local path or GitHub repository
        3. Click "Analyze Code" and wait for results
        4. Explore the different tabs for insights and chat with your codebase!
        
        ### Supported Languages:
        Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, Scala
        """)

if __name__ == "__main__":
    main()
