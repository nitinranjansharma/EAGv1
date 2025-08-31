# mcp server --

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from agents import research_orchestrator
from perception import search_web, fetch_page, extract_text
from decision import embed_texts, cosine_rank, summarize_with_llm
from memory import memory_store
from config import (
    LOG_LEVEL, LOG_FORMAT, MCP_SERVER_NAME, SEARCH_TOPIC, OUTPUT_FILE,
    AUTO_CLEANUP_AFTER_OUTPUT, CLEANUP_VERBOSE, USE_GEMINI
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool()
def search_web_tool(topic: str) -> List[str]:
    """
    Search the web for research papers related to the topic.
    Returns up to 10 candidate URLs from the first search results page.
    """
    try:
        logger.info(f"🔍 MCP: search_web called with topic: {topic}")
        urls = search_web(topic)
        logger.info(f"✅ MCP: search_web returned {len(urls)} URLs")
        return urls
    except Exception as e:
        logger.error(f"❌ MCP: search_web error: {e}")
        return []

@mcp.tool()
def fetch_page_tool(url: str) -> Dict[str, Any]:
    """
    Fetch a web page and return its content.
    Returns: {"url": str, "content_type": str, "raw": str|bytes}
    """
    try:
        logger.info(f"🌐 MCP: fetch_page called with URL: {url}")
        
        # Check cache first
        cached_page = memory_store.get_page(url)
        if cached_page and cached_page.get('content_type') != 'error':
            logger.info(f"💾 MCP: fetch_page using cached result for {url}")
            return {
                "url": url,
                "content_type": cached_page['content_type'],
                "raw": cached_page['raw']
            }
        
        # Fetch fresh page
        page_data = fetch_page(url)
        
        # Cache the result if successful
        if page_data.get('content_type') != 'error':
            memory_store.store_page(
                url,
                page_data['content_type'],
                page_data['raw'],
                page_data.get('etag'),
                page_data.get('last_modified')
            )
        
        logger.info(f"✅ MCP: fetch_page completed for {url}")
        return {
            "url": url,
            "content_type": page_data['content_type'],
            "raw": page_data['raw']
        }
    except Exception as e:
        logger.error(f"❌ MCP: fetch_page error for {url}: {e}")
        return {
            "url": url,
            "content_type": "error",
            "raw": f"Error: {str(e)}"
        }

@mcp.tool()
def extract_text_tool(url: str, raw: Any, content_type: str) -> Dict[str, Any]:
    """
    Extract readable text from raw content.
    Returns: {"url": str, "title": str|None, "text": str}
    """
    try:
        logger.info(f"📝 MCP: extract_text called for {url}")
        result = extract_text(url, raw, content_type)
        logger.info(f"✅ MCP: extract_text completed for {url}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP: extract_text error for {url}: {e}")
        return {
            "url": url,
            "title": None,
            "text": f"Error extracting text: {str(e)}"
        }

@mcp.tool()
def embed_tool(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using sentence-transformers.
    Returns: List of embedding vectors
    """
    try:
        logger.info(f"🧠 MCP: embed called with {len(texts)} texts")
        embeddings = embed_texts(texts)
        # Convert numpy array to list of lists for JSON serialization
        embeddings_list = embeddings.tolist()
        logger.info(f"✅ MCP: embed completed, generated {len(embeddings_list)} embeddings")
        return embeddings_list
    except Exception as e:
        logger.error(f"❌ MCP: embed error: {e}")
        return []

@mcp.tool()
def rank_tool(topic: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank documents by cosine similarity to topic.
    Returns: List of docs with similarity scores, sorted descending
    """
    try:
        logger.info(f"📊 MCP: rank called with topic: {topic}, {len(candidates)} candidates")
        ranked_docs = cosine_rank(topic, candidates)
        logger.info(f"✅ MCP: rank completed, ranked {len(ranked_docs)} documents")
        return ranked_docs
    except Exception as e:
        logger.error(f"❌ MCP: rank error: {e}")
        # Return original candidates with zero similarity scores
        for doc in candidates:
            doc['similarity'] = 0.0
        return candidates

@mcp.tool()
def summarize_tool(title: str, text: str, url: str) -> str:
    """
    Generate a summary using the configured LLM provider (Gemini or Ollama).
    Returns: ~100-word summary
    """
    try:
        logger.info(f"📝 MCP: summarize called for {url}")
        summary = summarize_with_llm(title, text, url)
        logger.info(f"✅ MCP: summarize completed for {url}")
        return summary
    except Exception as e:
        logger.error(f"❌ MCP: summarize error for {url}: {e}")
        return f"Summary unavailable: {str(e)}"

@mcp.tool()
def deep_research_tool(topic: str = None) -> Dict[str, Any]:
    """
    Complete end-to-end research pipeline.
    Returns: Structured JSON with top 3 papers, summaries, and diagnostics
    """
    try:
        if topic is None:
            topic = SEARCH_TOPIC
            
        logger.info(f"🚀 MCP: deep_research called with topic: {topic}")
        result = research_orchestrator.deep_research(topic)
        
        # Save result to output file
        try:
            logger.info(f"💾 MCP: Saving result to {OUTPUT_FILE}")
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ MCP: Result saved to {OUTPUT_FILE}")
        except Exception as e:
            logger.warning(f"⚠️ MCP: Failed to save result to file: {e}")
        
        # Note: Cache cleanup is already handled by the orchestrator
        logger.info(f"✅ MCP: deep_research completed for topic: {topic}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP: deep_research error: {e}")
        return {
            "topic": topic or SEARCH_TOPIC,
            "papers": [],
            "diagnostics": {
                "candidate_count": 0,
                "discarded": 0,
                "timings_ms": {},
                "total_time_ms": 0,
                "error": str(e)
            }
        }

@mcp.tool()
def clear_cache_tool() -> str:
    """
    Clear all cached embeddings and pages.
    Returns: Success message
    """
    try:
        logger.info("🧹 MCP: clear_cache called")
        
        if CLEANUP_VERBOSE:
            # Get cache stats before cleanup
            stats_before = {
                "embedding_cache_size": len(memory_store.embedding_cache),
                "page_cache_size": len(memory_store.page_cache)
            }
            logger.info(f"📊 MCP: Cache stats before cleanup: {stats_before}")
        
        memory_store.clear_cache()
        
        if CLEANUP_VERBOSE:
            # Get cache stats after cleanup
            stats_after = {
                "embedding_cache_size": len(memory_store.embedding_cache),
                "page_cache_size": len(memory_store.page_cache)
            }
            logger.info(f"📊 MCP: Cache stats after cleanup: {stats_after}")
        
        logger.info("✅ MCP: clear_cache completed")
        return "Cache cleared successfully"
    except Exception as e:
        logger.error(f"❌ MCP: clear_cache error: {e}")
        return f"Error clearing cache: {str(e)}"

@mcp.tool()
def get_cache_stats_tool() -> Dict[str, Any]:
    """
    Get statistics about the cache.
    Returns: Cache statistics
    """
    try:
        logger.info("📊 MCP: get_cache_stats called")
        stats = {
            "embedding_cache_size": len(memory_store.embedding_cache),
            "page_cache_size": len(memory_store.page_cache),
            "has_persistence": memory_store.db_path is not None,
            "auto_cleanup_enabled": AUTO_CLEANUP_AFTER_OUTPUT
        }
        logger.info("✅ MCP: get_cache_stats completed")
        return stats
    except Exception as e:
        logger.error(f"❌ MCP: get_cache_stats error: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_llm_config_tool() -> Dict[str, Any]:
    """
    Get current LLM configuration.
    Returns: LLM configuration details
    """
    try:
        logger.info("🔧 MCP: get_llm_config called")
        config = {
            "use_gemini": USE_GEMINI,
            "llm_provider": "Gemini Flash" if USE_GEMINI else "Ollama",
            "gemini_model": "gemini-1.5-flash" if USE_GEMINI else None,
            "ollama_model": "llama2" if not USE_GEMINI else None,
            "temperature": 0.3,
            "max_tokens": 200,
            "summary_target_words": 100
        }
        logger.info("✅ MCP: get_llm_config completed")
        return config
    except Exception as e:
        logger.error(f"❌ MCP: get_llm_config error: {e}")
        return {"error": str(e)}

def main():
    """Start the MCP server."""
    logger.info("🚀 Starting Research Paper Discovery MCP Server...")
    
    # Log available tools
    tools = [
        "search_web_tool",
        "fetch_page_tool", 
        "extract_text_tool",
        "embed_tool",
        "rank_tool",
        "summarize_tool",
        "deep_research_tool",
        "clear_cache_tool",
        "get_cache_stats_tool",
        "get_llm_config_tool"
    ]
    
    logger.info(f"📋 Registered {len(tools)} MCP tools:")
    for tool in tools:
        logger.info(f"   • {tool}")
    
    logger.info(f"🔧 Configuration:")
    logger.info(f"   • LLM Provider: {'Gemini Flash' if USE_GEMINI else 'Ollama'}")
    logger.info(f"   • Auto Cleanup: {'Enabled' if AUTO_CLEANUP_AFTER_OUTPUT else 'Disabled'}")
    logger.info(f"   • Cleanup Verbose: {'Enabled' if CLEANUP_VERBOSE else 'Disabled'}")
    logger.info(f"   • Output File: {OUTPUT_FILE}")
    
    # Start the server
    logger.info("🌐 Starting MCP server...")
    mcp.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("⏹️ Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
