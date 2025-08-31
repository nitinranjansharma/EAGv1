#!/usr/bin/env python3
"""
Example client for the Research Paper Discovery MCP Server.

This demonstrates how to use the MCP tools to perform research paper discovery
and summarization.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from config import SEARCH_TOPIC, OUTPUT_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_individual_tools():
    """Example using individual MCP tools."""
    logger.info("=== Example: Using Individual Tools ===")
    
    # This would be replaced with actual MCP client calls
    # For demonstration, we'll show the expected flow
    
    topic = "graph neural networks for drug discovery"
    
    print(f"1. Searching for: {topic}")
    # urls = await client.search_web_tool(topic)
    print("   Expected: List of research paper URLs")
    
    print("\n2. Fetching pages...")
    # for url in urls[:3]:  # Process first 3 URLs
    #     page_data = await client.fetch_page_tool(url)
    #     if page_data['content_type'] != 'error':
    #         text_data = await client.extract_text_tool(url, page_data['raw'], page_data['content_type'])
    print("   Expected: Extracted text from research papers")
    
    print("\n3. Ranking by similarity...")
    # ranked_docs = await client.rank_tool(topic, extracted_docs)
    print("   Expected: Documents ranked by similarity to topic")
    
    print("\n4. Summarizing top papers...")
    # for doc in ranked_docs[:3]:
    #     summary = await client.summarize_tool(doc['title'], doc['text'], doc['url'])
    print("   Expected: 100-word summaries of top 3 papers")

async def example_end_to_end():
    """Example using the end-to-end deep_research tool."""
    logger.info("=== Example: End-to-End Research ===")
    
    topic = "transformer models for computer vision"
    
    print(f"Running complete research pipeline for: {topic}")
    
    # This would be the actual MCP client call:
    # result = await client.deep_research_tool(topic)
    
    # Example expected result structure:
    result = {
        "topic": topic,
        "papers": [
            {
                "rank": 1,
                "url": "https://arxiv.org/abs/2023.12345",
                "title": "Vision Transformer: An Image is Worth 16x16 Words",
                "similarity": 0.89,
                "summary_100_words": "This paper introduces Vision Transformer (ViT), which applies the Transformer architecture to image classification tasks. The authors demonstrate that pure transformers can perform well on image recognition when trained on sufficient data. The model divides images into patches, processes them as sequences, and achieves state-of-the-art results on ImageNet."
            },
            {
                "rank": 2,
                "url": "https://openreview.net/forum?id=example2",
                "title": "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows",
                "similarity": 0.76,
                "summary_100_words": "The Swin Transformer introduces a hierarchical vision transformer that uses shifted windows for efficient computation. This approach reduces computational complexity while maintaining high performance on vision tasks. The model achieves excellent results on object detection and semantic segmentation benchmarks."
            },
            {
                "rank": 3,
                "url": "https://papers.nips.cc/paper/2023/hash/example3",
                "title": "DeiT: Training data-efficient image transformers",
                "similarity": 0.72,
                "summary_100_words": "DeiT presents a data-efficient approach to training vision transformers using knowledge distillation from a CNN teacher. The method achieves competitive results with much less training data and computational resources, making transformers more accessible for practical applications."
            }
        ],
        "diagnostics": {
            "candidate_count": 10,
            "discarded": 2,
            "timings_ms": {
                "search_and_collect": 1500.0,
                "fetch_and_extract": 8000.0,
                "rank_by_similarity": 500.0,
                "summarize_top_papers": 15000.0
            },
            "total_time_ms": 25000.0
        }
    }
    
    print(f"\nResearch Results for: {result['topic']}")
    print(f"Found {len(result['papers'])} papers")
    print(f"Total processing time: {result['diagnostics']['total_time_ms']:.2f}ms")
    
    print("\nTop Papers:")
    for paper in result['papers']:
        print(f"\n{paper['rank']}. {paper['title']}")
        print(f"   URL: {paper['url']}")
        print(f"   Similarity: {paper['similarity']:.3f}")
        print(f"   Summary: {paper['summary_100_words']}")
    
    print(f"\nDiagnostics:")
    print(f"  - Candidate URLs found: {result['diagnostics']['candidate_count']}")
    print(f"  - URLs discarded: {result['diagnostics']['discarded']}")
    print(f"  - Stage timings:")
    for stage, timing in result['diagnostics']['timings_ms'].items():
        print(f"    * {stage}: {timing:.2f}ms")

async def example_cache_management():
    """Example of cache management tools."""
    logger.info("=== Example: Cache Management ===")
    
    print("1. Getting cache statistics...")
    # stats = await client.get_cache_stats_tool()
    # print(f"   Embedding cache size: {stats['embedding_cache_size']}")
    # print(f"   Page cache size: {stats['page_cache_size']}")
    # print(f"   Has persistence: {stats['has_persistence']}")
    print("   Expected: Current cache statistics")
    
    print("\n2. Clearing cache...")
    # result = await client.clear_cache_tool()
    # print(f"   Result: {result}")
    print("   Expected: Cache cleared successfully")

def print_usage_instructions():
    """Print usage instructions for the MCP server."""
    print("\n" + "="*60)
    print("RESEARCH PAPER DISCOVERY MCP SERVER")
    print("="*60)
    
    print("\nTo use this system:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start Ollama server: ollama serve")
    print("3. Run the MCP server: python server.py")
    print("4. Connect with an MCP client to use the tools")
    print("5. Or run standalone: python run_research.py")
    
    print("\nAvailable MCP Tools:")
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
    
    for tool_name, description in tools:
        print(f"  - {tool_name}: {description}")
    
    print("\nExample Usage:")
    print("  # Complete research pipeline")
    print("  result = await client.deep_research_tool('graph neural networks')")
    print("  print(json.dumps(result, indent=2))")
    
    print("\nConfiguration:")
    print(f"  - Search topic: {SEARCH_TOPIC}")
    print(f"  - Output file: {OUTPUT_FILE}")
    
    print("\nNote: The search_web function currently uses placeholder results.")
    print("In production, integrate with a real search API (SerpAPI, Bing, etc.).")
    print("="*60)

async def main():
    """Main example function."""
    print("Research Paper Discovery MCP Server - Client Examples")
    print("="*60)
    
    # Run examples
    await example_individual_tools()
    print("\n" + "-"*40 + "\n")
    
    await example_end_to_end()
    print("\n" + "-"*40 + "\n")
    
    await example_cache_management()
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    asyncio.run(main())
