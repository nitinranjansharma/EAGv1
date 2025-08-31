#!/usr/bin/env python3
"""
Standalone Research Paper Discovery Script

This script runs the complete research pipeline and saves results to output.txt.
It can be run independently without the MCP server.
"""

import json
import logging
import sys
import time
from agents import research_orchestrator
from config import SEARCH_TOPIC, OUTPUT_FILE, LOG_LEVEL, LOG_FORMAT, AUTO_CLEANUP_AFTER_OUTPUT, USE_GEMINI

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

def main():
    """Run the research pipeline and save results."""
    try:
        logger.info("🚀 RESEARCH PAPER DISCOVERY PIPELINE")
        logger.info("=" * 80)
        logger.info(f"🔍 Search Topic: {SEARCH_TOPIC}")
        logger.info(f"📄 Output File: {OUTPUT_FILE}")
        logger.info(f"🤖 LLM Provider: {'Gemini Flash' if USE_GEMINI else 'Ollama'}")
        logger.info(f"🧹 Auto Cleanup: {'Enabled' if AUTO_CLEANUP_AFTER_OUTPUT else 'Disabled'}")
        logger.info("=" * 80)
        
        # Run the research pipeline
        logger.info("🔄 Starting research pipeline...")
        pipeline_start = time.time()
        
        result = research_orchestrator.deep_research(SEARCH_TOPIC)
        
        pipeline_time = time.time() - pipeline_start
        
        # Save results to file
        logger.info(f"💾 Saving results to {OUTPUT_FILE}...")
        save_start = time.time()
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        save_time = time.time() - save_start
        
        logger.info(f"✅ Results saved successfully in {save_time:.2f}s")
        
        # Print summary
        logger.info("=" * 80)
        logger.info("🎉 RESEARCH COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        
        # Extract statistics
        papers = result.get('papers', [])
        searched_urls = result.get('searched_urls', [])
        processed_urls = result.get('processed_urls', [])
        diagnostics = result.get('diagnostics', {})
        timings = diagnostics.get('timings_ms', {})
        agent_stats = diagnostics.get('agent_stats', {})
        llm_provider = diagnostics.get('llm_provider', 'Unknown')
        
        # Print overall results
        logger.info(f"📊 OVERALL RESULTS:")
        logger.info(f"   🔍 Topic: {result.get('topic', 'Unknown')}")
        logger.info(f"   📄 Papers found: {len(papers)}")
        logger.info(f"   ⏱️  Total Pipeline Time: {pipeline_time:.2f}s")
        logger.info(f"   💾 Save Time: {save_time:.2f}s")
        logger.info(f"   📄 Output File: {OUTPUT_FILE}")
        logger.info(f"   🤖 LLM Provider: {llm_provider}")
        
        # Print URL information
        logger.info(f"🔗 URL INFORMATION:")
        logger.info(f"   📋 Total URLs searched: {len(searched_urls)}")
        logger.info(f"   ✅ URLs processed: {len(processed_urls)}")
        logger.info(f"   📊 Success rate: {(len(processed_urls) / max(len(searched_urls), 1) * 100):.1f}%")
        
        # Print searched URLs
        logger.info(f"🔍 SEARCHED URLS:")
        for i, url in enumerate(searched_urls, 1):
            status = "✅ Processed" if url in processed_urls else "❌ Filtered out"
            logger.info(f"   {i}. {url} ({status})")
        
        # Print processed URLs
        logger.info(f"✅ PROCESSED URLS:")
        for i, url in enumerate(processed_urls, 1):
            logger.info(f"   {i}. {url}")
        
        # Print timing breakdown
        logger.info(f"⏱️  TIMING BREAKDOWN:")
        for stage, timing in timings.items():
            logger.info(f"   • {stage.replace('_', ' ').title()}: {timing:.2f}ms")
        
        # Print agent statistics
        if agent_stats:
            perception_stats = agent_stats.get('perception', {})
            decision_stats = agent_stats.get('decision', {})
            
            logger.info(f"🤖 AGENT STATISTICS:")
            logger.info(f"   📋 Perception Agent:")
            logger.info(f"      • URLs Searched: {perception_stats.get('urls_searched', 0)}")
            logger.info(f"      • URLs Fetched: {perception_stats.get('urls_fetched', 0)}")
            logger.info(f"      • URLs Extracted: {perception_stats.get('urls_extracted', 0)}")
            logger.info(f"      • URLs Failed: {perception_stats.get('urls_failed', 0)}")
            logger.info(f"      • Total Fetch Time: {perception_stats.get('total_fetch_time', 0):.2f}s")
            logger.info(f"      • Total Extract Time: {perception_stats.get('total_extract_time', 0):.2f}s")
            
            logger.info(f"   🧠 Decision Agent:")
            logger.info(f"      • Documents Ranked: {decision_stats.get('docs_ranked', 0)}")
            logger.info(f"      • Documents Summarized: {decision_stats.get('docs_summarized', 0)}")
            logger.info(f"      • Total Rank Time: {decision_stats.get('total_rank_time', 0):.2f}s")
            logger.info(f"      • Total Summarize Time: {decision_stats.get('total_summarize_time', 0):.2f}s")
        
        # Print paper details
        logger.info(f"📚 PAPER DETAILS:")
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown Title')
            url = paper.get('url', 'Unknown URL')
            similarity = paper.get('similarity', 0.0)
            summary = paper.get('summary_100_words', 'No summary')
            
            logger.info(f"   {i}. {title}")
            logger.info(f"      🔗 URL: {url}")
            logger.info(f"      📊 Similarity: {similarity:.4f}")
            logger.info(f"      📝 Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
            logger.info("")
        
        # Print diagnostics
        logger.info(f"🔍 DIAGNOSTICS:")
        logger.info(f"   📊 Candidate URLs: {diagnostics.get('candidate_count', 0)}")
        logger.info(f"   ❌ Discarded URLs: {diagnostics.get('discarded', 0)}")
        logger.info(f"   📈 Success Rate: {((diagnostics.get('candidate_count', 0) - diagnostics.get('discarded', 0)) / max(diagnostics.get('candidate_count', 1), 1) * 100):.1f}%")
        logger.info(f"   🤖 LLM Provider Used: {llm_provider}")
        
        # Print file information
        logger.info(f"📄 FILE INFORMATION:")
        logger.info(f"   📁 Output File: {OUTPUT_FILE}")
        logger.info(f"   📏 File Size: {len(json.dumps(result, indent=2)):,} characters")
        logger.info(f"   📊 JSON Structure: {len(result)} top-level keys")
        
        logger.info("=" * 80)
        logger.info("✨ Research pipeline completed successfully!")
        logger.info(f"📄 Results saved to: {OUTPUT_FILE}")
        logger.info("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        logger.error("❌ Research interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Research failed: {e}")
        logger.error(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
