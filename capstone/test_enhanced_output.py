#!/usr/bin/env python3
"""
Test script to demonstrate enhanced output format with URL tracking.
"""

import json
from config import SEARCH_TOPIC, USE_GEMINI

def create_sample_output():
    """Create a sample output to demonstrate the enhanced format."""
    
    sample_result = {
        "topic": SEARCH_TOPIC,
        "searched_urls": [
            "https://arxiv.org/abs/2308.03296",  # RoPE: Rotary Position Embedding
            "https://arxiv.org/abs/2306.15595",  # LongNet: Scaling Transformers to 1M Tokens
            "https://arxiv.org/abs/2305.19370",  # FlashAttention-2: Faster Attention with Better Parallelism
            "https://arxiv.org/abs/2304.11062",  # Scaling Laws for Neural Language Models
            "https://arxiv.org/abs/2303.08774",  # Extending Context Window of Large Language Models
            "https://arxiv.org/abs/2302.05442",  # Efficiently Scaling Transformer Inference
            "https://arxiv.org/abs/2301.03236",  # Long Range Arena: A Benchmark for Efficient Transformers
            "https://arxiv.org/abs/2212.10554",  # FlashAttention: Fast and Memory-Efficient Exact Attention
            "https://arxiv.org/abs/2210.11416",  # Efficiently Modeling Long Sequences with Structured State Spaces
            "https://arxiv.org/abs/2203.15556"   # PaLM: Scaling Language Modeling with Pathways
        ],
        "processed_urls": [
            "https://arxiv.org/abs/2308.03296",  # RoPE: Rotary Position Embedding
            "https://arxiv.org/abs/2306.15595",  # LongNet: Scaling Transformers to 1M Tokens
            "https://arxiv.org/abs/2305.19370"   # FlashAttention-2: Faster Attention with Better Parallelism
        ],
        "papers": [
            {
                "rank": 1,
                "url": "https://arxiv.org/abs/2308.03296",
                "title": "RoPE: Rotary Position Embedding for Scaling Transformers",
                "similarity": 0.92,
                "summary_100_words": "This paper introduces Rotary Position Embedding (RoPE), a novel method for encoding positional information in transformer models. RoPE applies rotation matrices to embed absolute positions, enabling the model to generalize to longer sequences than those seen during training. The method is efficient, requiring no additional parameters, and has been shown to significantly improve performance on long-context tasks."
            },
            {
                "rank": 2,
                "url": "https://arxiv.org/abs/2306.15595",
                "title": "LongNet: Scaling Transformers to 1M Tokens and Beyond",
                "similarity": 0.89,
                "summary_100_words": "LongNet presents a novel approach to scaling transformer models to handle sequences of up to 1 million tokens. The method uses dilated attention mechanisms and hierarchical processing to maintain computational efficiency while dramatically increasing context length. Experimental results show significant improvements in long-range dependency modeling and language understanding tasks."
            },
            {
                "rank": 3,
                "url": "https://arxiv.org/abs/2305.19370",
                "title": "FlashAttention-2: Faster Attention with Better Parallelism",
                "similarity": 0.85,
                "summary_100_words": "FlashAttention-2 improves upon the original FlashAttention algorithm with better parallelism and reduced memory usage. The enhanced version achieves up to 2x speedup over the original while maintaining numerical accuracy. This advancement enables training and inference of larger models with longer context windows, making it crucial for scaling language models."
            }
        ],
        "diagnostics": {
            "candidate_count": 3,
            "discarded": 0,
            "timings_ms": {
                "search_and_collect": 1500,
                "fetch_and_extract": 8000,
                "rank_by_similarity": 500,
                "summarize_top_papers": 12000
            },
            "total_time_ms": 22000,
            "agent_stats": {
                "perception": {
                    "urls_searched": 3,
                    "urls_fetched": 3,
                    "urls_extracted": 3,
                    "urls_failed": 0,
                    "total_fetch_time": 8.0,
                    "total_extract_time": 2.5
                },
                "decision": {
                    "docs_ranked": 3,
                    "docs_summarized": 3,
                    "total_rank_time": 0.5,
                    "total_summarize_time": 12.0
                }
            },
            "llm_provider": "Gemini Flash" if USE_GEMINI else "Ollama"
        }
    }
    
    return sample_result

def main():
    """Demonstrate the enhanced output format."""
    print("🔍 ENHANCED OUTPUT FORMAT DEMONSTRATION")
    print("=" * 80)
    
    # Create sample output
    result = create_sample_output()
    
    # Display the structure
    print(f"📋 OUTPUT STRUCTURE:")
    print(f"   • topic: {result['topic']}")
    print(f"   • searched_urls: {len(result['searched_urls'])} URLs (all found)")
    print(f"   • processed_urls: {len(result['processed_urls'])} URLs (top 3 selected)")
    print(f"   • papers: {len(result['papers'])} summarized papers")
    print(f"   • diagnostics: Performance metrics and timing")
    
    print(f"\n🔍 SEARCHED URLS ({len(result['searched_urls'])} total):")
    for i, url in enumerate(result['searched_urls'], 1):
        status = "✅ Processed" if url in result['processed_urls'] else "❌ Filtered out"
        print(f"   {i:2d}. {url} ({status})")
    
    print(f"\n✅ PROCESSED URLS ({len(result['processed_urls'])} selected):")
    for i, url in enumerate(result['processed_urls'], 1):
        print(f"   {i}. {url}")
    
    print(f"\n📚 SUMMARIZED PAPERS:")
    for i, paper in enumerate(result['papers'], 1):
        print(f"   {i}. {paper['title']}")
        print(f"      🔗 URL: {paper['url']}")
        print(f"      📊 Similarity: {paper['similarity']:.3f}")
        print(f"      📝 Summary: {paper['summary_100_words']}")
        print()
    
    print(f"📊 DIAGNOSTICS:")
    diagnostics = result['diagnostics']
    print(f"   • LLM Provider: {diagnostics['llm_provider']}")
    print(f"   • Total Time: {diagnostics['total_time_ms']:.0f}ms")
    print(f"   • Success Rate: {((diagnostics['candidate_count'] - diagnostics['discarded']) / max(diagnostics['candidate_count'], 1) * 100):.1f}%")
    
    # Save to file
    with open('output.txt', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sample output saved to: output.txt")
    print("=" * 80)

if __name__ == "__main__":
    main()
