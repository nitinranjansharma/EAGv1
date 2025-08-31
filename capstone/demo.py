#!/usr/bin/env python3
"""
Demo script for the Research Paper Discovery system.

This script demonstrates the system's capabilities using mock data
to avoid requiring external dependencies like Ollama or web access.
"""

import json
import time
from typing import Dict, Any

def mock_deep_research(topic: str) -> Dict[str, Any]:
    """
    Mock implementation of the deep research pipeline.
    This simulates what the real system would return.
    """
    print(f"🔍 Researching topic: {topic}")
    time.sleep(1)  # Simulate processing time
    
    # Mock research results
    mock_papers = [
        {
            "rank": 1,
            "url": "https://arxiv.org/abs/2023.12345",
            "title": "Graph Neural Networks for Drug Discovery: A Comprehensive Survey",
            "similarity": 0.92,
            "summary_100_words": "This paper presents a comprehensive survey of graph neural networks applied to drug discovery. The authors review recent advances in molecular property prediction, drug-target interaction prediction, and de novo drug design using GNNs. The survey covers various architectures including Graph Convolutional Networks, Graph Attention Networks, and Message Passing Neural Networks. Results show significant improvements over traditional methods in predicting drug properties and interactions."
        },
        {
            "rank": 2,
            "url": "https://openreview.net/forum?id=example2",
            "title": "Molecular Property Prediction with Graph Neural Networks",
            "similarity": 0.87,
            "summary_100_words": "The authors propose a novel graph neural network architecture for molecular property prediction. The model incorporates both molecular structure and chemical features through a hierarchical message passing mechanism. Experimental results on standard benchmarks demonstrate state-of-the-art performance in predicting drug-likeness, toxicity, and binding affinity. The approach shows particular strength in handling complex molecular structures and rare chemical patterns."
        },
        {
            "rank": 3,
            "url": "https://papers.nips.cc/paper/2023/hash/example3",
            "title": "Drug-Target Interaction Prediction Using Attention-Based Graph Neural Networks",
            "similarity": 0.84,
            "summary_100_words": "This work introduces an attention-based graph neural network for predicting drug-target interactions. The model learns representations of both drugs and proteins using graph attention mechanisms, capturing important structural and functional relationships. The approach achieves superior performance on benchmark datasets and provides interpretable attention weights that highlight key molecular interactions. Results suggest the method can accelerate drug discovery by identifying promising drug candidates."
        }
    ]
    
    result = {
        "topic": topic,
        "papers": mock_papers,
        "diagnostics": {
            "candidate_count": 10,
            "discarded": 2,
            "timings_ms": {
                "search_and_collect": 1200.0,
                "fetch_and_extract": 7500.0,
                "rank_by_similarity": 450.0,
                "summarize_top_papers": 12000.0
            },
            "total_time_ms": 21150.0
        }
    }
    
    return result

def print_results(result: Dict[str, Any]):
    """Pretty print the research results."""
    print("\n" + "="*80)
    print(f"📊 RESEARCH RESULTS FOR: {result['topic'].upper()}")
    print("="*80)
    
    print(f"\n🔍 Found {len(result['papers'])} relevant papers")
    print(f"⏱️  Total processing time: {result['diagnostics']['total_time_ms']:.2f}ms")
    
    print(f"\n📈 Performance Metrics:")
    print(f"   • Candidate URLs found: {result['diagnostics']['candidate_count']}")
    print(f"   • URLs discarded: {result['diagnostics']['discarded']}")
    print(f"   • Success rate: {((result['diagnostics']['candidate_count'] - result['diagnostics']['discarded']) / result['diagnostics']['candidate_count'] * 100):.1f}%")
    
    print(f"\n⏱️  Stage Timings:")
    for stage, timing in result['diagnostics']['timings_ms'].items():
        print(f"   • {stage.replace('_', ' ').title()}: {timing:.2f}ms")
    
    print(f"\n📚 TOP PAPERS:")
    for i, paper in enumerate(result['papers'], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   🔗 URL: {paper['url']}")
        print(f"   📊 Similarity Score: {paper['similarity']:.3f}")
        print(f"   📝 Summary: {paper['summary_100_words']}")

def demo_individual_tools():
    """Demonstrate individual tool usage."""
    print("\n" + "="*80)
    print("🔧 INDIVIDUAL TOOL DEMONSTRATION")
    print("="*80)
    
    print("\n1. 🔍 Web Search Tool")
    print("   Input: 'graph neural networks for drug discovery'")
    print("   Output: List of research paper URLs")
    print("   Example URLs:")
    print("   • https://arxiv.org/abs/2023.12345")
    print("   • https://openreview.net/forum?id=example")
    print("   • https://papers.nips.cc/paper/2023/hash/example")
    
    print("\n2. 📄 Page Fetch Tool")
    print("   Input: URL")
    print("   Output: {url, content_type, raw_content}")
    print("   Handles: HTML, PDF, and other content types")
    
    print("\n3. 📝 Text Extraction Tool")
    print("   Input: {url, raw_content, content_type}")
    print("   Output: {url, title, text}")
    print("   Features: PDF parsing, HTML readability, content cleaning")
    
    print("\n4. 🧠 Embedding Tool")
    print("   Input: List of texts")
    print("   Output: List of embedding vectors (384 dimensions)")
    print("   Model: all-MiniLM-L6-v2")
    
    print("\n5. 📊 Ranking Tool")
    print("   Input: topic + list of documents")
    print("   Output: Documents ranked by cosine similarity")
    print("   Algorithm: Cosine similarity with sentence transformers")
    
    print("\n6. 📋 Summarization Tool")
    print("   Input: {title, text, url}")
    print("   Output: ~100-word summary")
    print("   LLM: Local Ollama (llama2 model)")

def demo_mcp_integration():
    """Demonstrate MCP integration."""
    print("\n" + "="*80)
    print("🔌 MCP SERVER INTEGRATION")
    print("="*80)
    
    print("\n📋 Available MCP Tools:")
    tools = [
        ("search_web_tool", "Search for research papers by topic"),
        ("fetch_page_tool", "Fetch web page content"),
        ("extract_text_tool", "Extract readable text from content"),
        ("embed_tool", "Generate text embeddings"),
        ("rank_tool", "Rank documents by similarity"),
        ("summarize_tool", "Generate summaries using Ollama"),
        ("deep_research_tool", "Complete end-to-end research pipeline"),
        ("clear_cache_tool", "Clear all caches"),
        ("get_cache_stats_tool", "Get cache statistics")
    ]
    
    for i, (tool_name, description) in enumerate(tools, 1):
        print(f"   {i}. {tool_name}: {description}")
    
    print("\n💻 Example MCP Client Usage:")
    print("""
import asyncio
from mcptools import Client

async def main():
    client = Client("research-paper-discovery")
    
    # Complete pipeline
    result = await client.deep_research_tool("graph neural networks")
    
    # Individual tools
    urls = await client.search_web_tool("transformer models")
    page_data = await client.fetch_page_tool(urls[0])
    text_data = await client.extract_text_tool(
        urls[0], page_data['raw'], page_data['content_type']
    )
    
    print(json.dumps(result, indent=2))

asyncio.run(main())
    """)

def demo_architecture():
    """Demonstrate the system architecture."""
    print("\n" + "="*80)
    print("🏗️  SYSTEM ARCHITECTURE")
    print("="*80)
    
    print("\n📁 File Structure:")
    files = [
        ("server.py", "MCP server with tool definitions"),
        ("agents.py", "Agent orchestrator (Perception + Decision)"),
        ("perception.py", "Web search and content extraction"),
        ("decision.py", "Embedding, ranking, and summarization"),
        ("memory.py", "Caching system (in-memory + SQLite)"),
        ("client_example.py", "Example client usage"),
        ("test_system.py", "System testing and validation"),
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Documentation")
    ]
    
    for filename, description in files:
        print(f"   • {filename}: {description}")
    
    print("\n🤖 Agent Architecture:")
    print("   • Perception Agent: search_web, fetch_page, extract_text")
    print("   • Decision Agent: embed_texts, cosine_rank, summarize_with_ollama")
    print("   • Research Orchestrator: Coordinates both agents")
    
    print("\n💾 Caching System:")
    print("   • In-memory cache: Fast access to embeddings and pages")
    print("   • SQLite persistence: Long-term storage")
    print("   • ETag support: HTTP caching headers")
    print("   • Automatic cleanup: Configurable expiration")

def main():
    """Main demo function."""
    print("🚀 RESEARCH PAPER DISCOVERY SYSTEM DEMO")
    print("="*80)
    
    # Demo the complete pipeline
    topic = "graph neural networks for drug discovery"
    result = mock_deep_research(topic)
    print_results(result)
    
    # Demo individual tools
    demo_individual_tools()
    
    # Demo MCP integration
    demo_mcp_integration()
    
    # Demo architecture
    demo_architecture()
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS")
    print("="*80)
    
    print("\n1. 📦 Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2. 🐙 Install and start Ollama:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print("   ollama serve")
    print("   ollama pull llama2")
    
    print("\n3. 🚀 Start the MCP server:")
    print("   python server.py")
    
    print("\n4. 🔧 Integrate with real search API:")
    print("   • Replace placeholder search in perception.py")
    print("   • Add API keys for SerpAPI, Bing, or Brave Search")
    
    print("\n5. 🧪 Run tests:")
    print("   python test_system.py")
    
    print("\n6. 📖 Read documentation:")
    print("   See README.md for detailed usage instructions")
    
    print("\n" + "="*80)
    print("✨ Demo completed! The system is ready for real-world use.")
    print("="*80)

if __name__ == "__main__":
    main()
