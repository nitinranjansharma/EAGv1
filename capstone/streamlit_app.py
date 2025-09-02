#!/usr/bin/env python3
"""
Streamlit UI for Research Paper Discovery System

This provides an interactive web interface for searching and discovering research papers.
"""

import streamlit as st
import json
import time
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add the current directory to Python path to import our modules
sys.path.append(str(Path(__file__).parent))

from agents import research_orchestrator
from config import USE_GEMINI

# Page configuration
st.set_page_config(
    page_title="Research Paper Discovery",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .url-status {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-processed {
        background-color: #d4edda;
        color: #155724;
    }
    .status-discarded {
        background-color: #f8d7da;
        color: #721c24;
    }
    .paper-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .similarity-badge {
        background-color: #007bff;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 Research Paper Discovery</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.info(f"🤖 **LLM Provider**: {'Gemini Flash' if USE_GEMINI else 'Ollama'}")
        
        st.markdown("### 📊 System Status")
        if os.path.exists("research_cache.db"):
            db_size = os.path.getsize("research_cache.db") / 1024  # KB
            st.metric("Cache Size", f"{db_size:.1f} KB")
        else:
            st.metric("Cache Size", "0 KB")
        
        st.markdown("### 🧹 Cache Management")
        if st.button("Clear Cache", type="secondary"):
            try:
                from memory import memory_store
                memory_store.clear_cache()
                st.success("Cache cleared successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing cache: {e}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">🔍 Search Configuration</h2>', unsafe_allow_html=True)
        
        # Search form
        with st.form("search_form"):
            search_topic = st.text_input(
                "Research Topic",
                value="research on long attention",
                placeholder="Enter your research topic here...",
                help="Describe what you want to research (e.g., 'machine learning in healthcare', 'transformer architectures')"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                max_urls = st.number_input(
                    "Max URLs to Process",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="Number of top URLs to process and summarize"
                )
            
            with col2:
                target_words = st.number_input(
                    "Summary Length (words)",
                    min_value=50,
                    max_value=200,
                    value=100,
                    help="Target number of words for each summary"
                )
            
            submitted = st.form_submit_button("🚀 Start Research", type="primary")
    
    with col2:
        st.markdown('<h2 class="sub-header">📋 Quick Stats</h2>', unsafe_allow_html=True)
        
        # Display recent results if available
        if os.path.exists("output.txt"):
            try:
                with open("output.txt", 'r') as f:
                    last_result = json.load(f)
                
                st.metric("Last Topic", last_result.get('topic', 'Unknown')[:30] + "...")
                st.metric("Papers Found", len(last_result.get('papers', [])))
                st.metric("Total URLs", len(last_result.get('searched_urls', [])))
                
                # Show last run time
                if os.path.exists("output.txt"):
                    mod_time = datetime.fromtimestamp(os.path.getmtime("output.txt"))
                    st.metric("Last Run", mod_time.strftime("%H:%M"))
                
            except Exception as e:
                st.error(f"Error reading last results: {e}")
        else:
            st.info("No previous results found. Run your first search!")
    
    # Process search if submitted
    if submitted and search_topic.strip():
        st.markdown("---")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update configuration temporarily
            from config import MAX_URLS_TO_PROCESS, SUMMARY_TARGET_WORDS
            import config
            
            # Store original values
            original_max_urls = config.MAX_URLS_TO_PROCESS
            original_target_words = config.SUMMARY_TARGET_WORDS
            
            # Update temporarily
            config.MAX_URLS_TO_PROCESS = max_urls
            config.SUMMARY_TARGET_WORDS = target_words
            
            # Run research
            status_text.text("🔍 Searching for research papers...")
            progress_bar.progress(25)
            
            status_text.text("🌐 Fetching and extracting content...")
            progress_bar.progress(50)
            
            status_text.text("📊 Ranking by similarity...")
            progress_bar.progress(75)
            
            status_text.text("📝 Generating summaries...")
            progress_bar.progress(90)
            
            result = research_orchestrator.deep_research(search_topic)
            
            # Restore original configuration
            config.MAX_URLS_TO_PROCESS = original_max_urls
            config.SUMMARY_TARGET_WORDS = original_target_words
            
            progress_bar.progress(100)
            status_text.text("✅ Research completed!")
            
            # Save results
            with open("output.txt", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Display results
            display_results(result)
            
        except Exception as e:
            st.error(f"❌ Research failed: {str(e)}")
            st.error(f"Error details: {type(e).__name__}")
            progress_bar.progress(0)
            status_text.text("❌ Research failed")
    
    # Show previous results if available
    elif os.path.exists("output.txt"):
        st.markdown("---")
        st.markdown('<h2 class="sub-header">📚 Previous Results</h2>', unsafe_allow_html=True)
        
        try:
            with open("output.txt", 'r') as f:
                last_result = json.load(f)
            display_results(last_result)
        except Exception as e:
            st.error(f"Error displaying previous results: {e}")

def display_results(result):
    """Display research results in a formatted way."""
    
    # Extract data
    topic = result.get('topic', 'Unknown Topic')
    searched_urls = result.get('searched_urls', [])
    processed_urls = result.get('processed_urls', [])
    papers = result.get('papers', [])
    diagnostics = result.get('diagnostics', {})
    
    # Header
    st.markdown(f'<h2 class="sub-header">📊 Research Results: {topic}</h2>', unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total URLs Found", len(searched_urls))
    
    with col2:
        st.metric("URLs Processed", len(processed_urls))
    
    with col3:
        st.metric("Papers Summarized", len(papers))
    
    with col4:
        success_rate = (len(processed_urls) / max(len(searched_urls), 1)) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # URL Analysis
    st.markdown("### 🔍 URL Analysis")
    
    # Create DataFrame for URLs
    url_data = []
    for url in searched_urls:
        status = "Processed" if url in processed_urls else "Discarded"
        url_data.append({
            "URL": url,
            "Status": status,
            "Domain": url.split('/')[2] if len(url.split('/')) > 2 else "Unknown"
        })
    
    df_urls = pd.DataFrame(url_data)
    
    # Display URL table with status indicators
    for _, row in df_urls.iterrows():
        status_class = "status-processed" if row["Status"] == "Processed" else "status-discarded"
        st.markdown(f"""
        <div class="url-status {status_class}">
            {row["Status"]}
        </div>
        <strong>{row["Domain"]}</strong><br>
        <code>{row["URL"]}</code>
        """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Papers section
    if papers:
        st.markdown("### 📚 Research Papers")
        
        for i, paper in enumerate(papers, 1):
            with st.container():
                st.markdown(f"""
                <div class="paper-card">
                    <h3>#{i} {paper.get('title', 'Unknown Title')}</h3>
                    <p><strong>URL:</strong> <a href="{paper.get('url', '')}" target="_blank">{paper.get('url', '')}</a></p>
                    <p><span class="similarity-badge">Similarity: {paper.get('similarity', 0.0):.3f}</span></p>
                    <p><strong>Summary:</strong></p>
                    <p>{paper.get('summary_100_words', 'No summary available')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Diagnostics
    if diagnostics:
        st.markdown("### 🔧 Performance Diagnostics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Timing Breakdown**")
            timings = diagnostics.get('timings_ms', {})
            for stage, timing in timings.items():
                st.metric(
                    stage.replace('_', ' ').title(),
                    f"{timing:.0f}ms"
                )
        
        with col2:
            st.markdown("**Agent Statistics**")
            agent_stats = diagnostics.get('agent_stats', {})
            
            if 'perception' in agent_stats:
                perception = agent_stats['perception']
                st.metric("URLs Fetched", perception.get('urls_fetched', 0))
                st.metric("URLs Extracted", perception.get('urls_extracted', 0))
                st.metric("Fetch Time", f"{perception.get('total_fetch_time', 0):.2f}s")
            
            if 'decision' in agent_stats:
                decision = agent_stats['decision']
                st.metric("Docs Ranked", decision.get('docs_ranked', 0))
                st.metric("Docs Summarized", decision.get('docs_summarized', 0))
                st.metric("Summarize Time", f"{decision.get('total_summarize_time', 0):.2f}s")
    
    # Download results
    st.markdown("### 💾 Download Results")
    
    # Create JSON string for download
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 Download Results (JSON)",
        data=json_str,
        file_name=f"research_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()
