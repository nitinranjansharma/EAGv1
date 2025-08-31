# Agents script

import time
import logging
from typing import List, Dict, Any
from perception import search_web, fetch_page, extract_text, filter_research_papers
from decision import cosine_rank, summarize_with_llm
from memory import memory_store
from config import MAX_URLS_TO_PROCESS, TOP_K_PAPERS, MIN_TEXT_LENGTH, AUTO_CLEANUP_AFTER_OUTPUT, CLEANUP_VERBOSE, USE_GEMINI

logger = logging.getLogger(__name__)

class PerceptionAgent:
    """Agent responsible for web search, page fetching, and text extraction."""
    
    def __init__(self):
        self.name = "PerceptionAgent"
        self.stats = {
            "urls_searched": 0,
            "urls_fetched": 0,
            "urls_extracted": 0,
            "urls_failed": 0,
            "total_fetch_time": 0.0,
            "total_extract_time": 0.0
        }
        self.all_searched_urls = []  # Track all URLs that were searched
    
    def search_and_collect(self, topic: str, max_urls: int = None) -> List[str]:
        """Search web and collect candidate URLs."""
        if max_urls is None:
            max_urls = MAX_URLS_TO_PROCESS
            
        logger.info(f"🔍 {self.name}: Starting search for topic: {topic}")
        logger.info(f"📊 {self.name}: Max URLs to process: {max_urls}")
        
        # Search for URLs
        start_time = time.time()
        urls = search_web(topic)
        search_time = time.time() - start_time
        
        logger.info(f"⏱️  {self.name}: Web search completed in {search_time:.2f}s")
        logger.info(f"📋 {self.name}: Found {len(urls)} initial URLs")
        
        # Store all searched URLs for output
        self.all_searched_urls = urls.copy()
        
        # Filter for research papers
        filter_start = time.time()
        research_urls = filter_research_papers(urls)
        filter_time = time.time() - filter_start
        
        logger.info(f"⏱️  {self.name}: URL filtering completed in {filter_time:.2f}s")
        
        # Limit to max_urls (exactly 3)
        if len(research_urls) > max_urls:
            logger.info(f"📊 {self.name}: Limiting from {len(research_urls)} to {max_urls} URLs")
            research_urls = research_urls[:max_urls]
        elif len(research_urls) < max_urls:
            logger.warning(f"⚠️  {self.name}: Only found {len(research_urls)} research URLs, wanted {max_urls}")
        
        self.stats["urls_searched"] = len(research_urls)
        
        logger.info(f"✅ {self.name}: Final URL collection complete")
        logger.info(f"   📊 URLs to process: {len(research_urls)}")
        logger.info(f"   ⏱️  Total collection time: {search_time + filter_time:.2f}s")
        
        # Log the URLs that will be processed
        logger.info(f"🔗 {self.name}: URLs to be processed:")
        for i, url in enumerate(research_urls, 1):
            logger.info(f"   {i}. {url}")
        
        return research_urls
    
    def fetch_and_extract(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch pages and extract text content."""
        logger.info(f"🌐 {self.name}: Starting fetch and extract for {len(urls)} URLs")
        
        extracted_docs = []
        failed_urls = []
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"📄 {self.name}: Processing URL {i}/{len(urls)}: {url}")
                
                # Check cache first
                cached_page = memory_store.get_page(url)
                if cached_page and cached_page.get('content_type') != 'error':
                    # Use cached page
                    page_data = cached_page
                    logger.info(f"💾 {self.name}: Using cached page for {url}")
                else:
                    # Fetch fresh page
                    fetch_start = time.time()
                    page_data = fetch_page(url)
                    fetch_time = time.time() - fetch_start
                    
                    self.stats["total_fetch_time"] += fetch_time
                    self.stats["urls_fetched"] += 1
                    
                    logger.info(f"⏱️  {self.name}: Fetch time for {url}: {fetch_time:.2f}s")
                    
                    # Cache the result if successful
                    if page_data.get('content_type') != 'error':
                        memory_store.store_page(
                            url, 
                            page_data['content_type'], 
                            page_data['raw'],
                            page_data.get('etag'),
                            page_data.get('last_modified')
                        )
                        logger.debug(f"💾 {self.name}: Cached page data for {url}")
                
                # Extract text
                if page_data.get('content_type') != 'error':
                    extract_start = time.time()
                    doc = extract_text(url, page_data['raw'], page_data['content_type'])
                    extract_time = time.time() - extract_start
                    
                    self.stats["total_extract_time"] += extract_time
                    
                    logger.info(f"⏱️  {self.name}: Extract time for {url}: {extract_time:.2f}s")
                    
                    if doc.get('text') and len(doc['text'].strip()) > MIN_TEXT_LENGTH:
                        extracted_docs.append(doc)
                        self.stats["urls_extracted"] += 1
                        logger.info(f"✅ {self.name}: Successfully extracted {url}")
                        logger.debug(f"   📏 Text length: {len(doc['text']):,} characters")
                    else:
                        logger.warning(f"⚠️  {self.name}: Insufficient text from {url}")
                        failed_urls.append(url)
                        self.stats["urls_failed"] += 1
                else:
                    logger.error(f"❌ {self.name}: Failed to fetch {url}: {page_data.get('raw', 'Unknown error')}")
                    failed_urls.append(url)
                    self.stats["urls_failed"] += 1
                
            except Exception as e:
                logger.error(f"❌ {self.name}: Error processing {url}: {e}")
                failed_urls.append(url)
                self.stats["urls_failed"] += 1
                continue
        
        logger.info(f"📊 {self.name}: Fetch and extract summary:")
        logger.info(f"   ✅ Successfully extracted: {len(extracted_docs)}")
        logger.info(f"   ❌ Failed: {len(failed_urls)}")
        logger.info(f"   ⏱️  Total fetch time: {self.stats['total_fetch_time']:.2f}s")
        logger.info(f"   ⏱️  Total extract time: {self.stats['total_extract_time']:.2f}s")
        
        if failed_urls:
            logger.warning(f"⚠️  {self.name}: Failed URLs:")
            for url in failed_urls:
                logger.warning(f"   - {url}")
        
        return extracted_docs

class DecisionAgent:
    """Agent responsible for embedding, ranking, and summarization."""
    
    def __init__(self):
        self.name = "DecisionAgent"
        self.stats = {
            "docs_ranked": 0,
            "docs_summarized": 0,
            "total_rank_time": 0.0,
            "total_summarize_time": 0.0
        }
        
        # Log which LLM provider is being used
        if USE_GEMINI:
            logger.info(f"🤖 {self.name}: Using Gemini Flash for summarization")
        else:
            logger.info(f"📝 {self.name}: Using Ollama for summarization")
    
    def rank_by_similarity(self, topic: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank documents by similarity to topic."""
        logger.info(f"📊 {self.name}: Starting similarity ranking for {len(docs)} documents")
        logger.info(f"🔍 {self.name}: Ranking against topic: {topic}")
        
        if not docs:
            logger.warning(f"⚠️  {self.name}: No documents to rank")
            return []
        
        # Rank documents by cosine similarity
        rank_start = time.time()
        ranked_docs = cosine_rank(topic, docs)
        rank_time = time.time() - rank_start
        
        self.stats["docs_ranked"] = len(ranked_docs)
        self.stats["total_rank_time"] = rank_time
        
        logger.info(f"⏱️  {self.name}: Ranking completed in {rank_time:.2f}s")
        logger.info(f"📊 {self.name}: Ranking results:")
        
        for i, doc in enumerate(ranked_docs[:5], 1):  # Show top 5
            similarity = doc.get('similarity', 0.0)
            title = doc.get('title', 'Unknown Title')
            logger.info(f"   {i}. {title} (similarity: {similarity:.3f})")
        
        if len(ranked_docs) > 5:
            logger.info(f"   ... and {len(ranked_docs) - 5} more documents")
        
        return ranked_docs
    
    def summarize_top_papers(self, docs: List[Dict[str, Any]], top_k: int = None) -> List[Dict[str, Any]]:
        """Summarize the top-k most similar papers."""
        if top_k is None:
            top_k = TOP_K_PAPERS
            
        logger.info(f"📝 {self.name}: Starting summarization of top {top_k} papers")
        
        top_docs = docs[:top_k]
        summarized_docs = []
        
        for i, doc in enumerate(top_docs, 1):
            try:
                url = doc.get('url', 'Unknown URL')
                title = doc.get('title', 'Unknown Title')
                
                logger.info(f"📝 {self.name}: Summarizing paper {i}/{len(top_docs)}: {title}")
                logger.debug(f"   🔗 URL: {url}")
                
                summarize_start = time.time()
                summary = summarize_with_llm(
                    title=title,
                    text=doc.get('text', ''),
                    url=url
                )
                summarize_time = time.time() - summarize_start
                
                self.stats["total_summarize_time"] += summarize_time
                self.stats["docs_summarized"] += 1
                
                logger.info(f"⏱️  {self.name}: Summarization time: {summarize_time:.2f}s")
                logger.info(f"📏 {self.name}: Summary length: {len(summary)} characters")
                
                # Add summary to document
                doc_copy = doc.copy()
                doc_copy['summary_100_words'] = summary
                doc_copy['rank'] = i
                doc_copy['summarize_time'] = summarize_time
                summarized_docs.append(doc_copy)
                
                logger.debug(f"✅ {self.name}: Generated summary for {url}")
                
            except Exception as e:
                logger.error(f"❌ {self.name}: Error summarizing {doc.get('url')}: {e}")
                # Add document with error summary
                doc_copy = doc.copy()
                doc_copy['summary_100_words'] = f"Summary unavailable: {str(e)}"
                doc_copy['rank'] = i
                doc_copy['summarize_time'] = 0.0
                summarized_docs.append(doc_copy)
        
        logger.info(f"📊 {self.name}: Summarization summary:")
        logger.info(f"   ✅ Successfully summarized: {self.stats['docs_summarized']}")
        logger.info(f"   ⏱️  Total summarize time: {self.stats['total_summarize_time']:.2f}s")
        
        return summarized_docs

class ResearchOrchestrator:
    """Main orchestrator that coordinates perception and decision agents."""
    
    def __init__(self):
        self.perception_agent = PerceptionAgent()
        self.decision_agent = DecisionAgent()
        self.timings = {}
        self.stats = {
            "total_urls_processed": 0,
            "total_papers_found": 0,
            "total_processing_time": 0.0
        }
        
        # Log LLM configuration
        logger.info(f"🔧 Research Orchestrator: LLM Provider = {'Gemini Flash' if USE_GEMINI else 'Ollama'}")
    
    def _record_timing(self, stage: str, start_time: float):
        """Record timing for a processing stage."""
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.timings[stage] = duration
        logger.info(f"⏱️  Stage '{stage}' completed in {duration:.2f}ms")
    
    def _cleanup_cache(self):
        """Clean up cache after output generation."""
        if AUTO_CLEANUP_AFTER_OUTPUT:
            logger.info("🧹 AUTO CLEANUP: Starting cache cleanup after output generation")
            
            if CLEANUP_VERBOSE:
                # Get cache stats before cleanup
                stats_before = {
                    "embedding_cache_size": len(memory_store.embedding_cache),
                    "page_cache_size": len(memory_store.page_cache)
                }
                logger.info(f"📊 Cache stats before cleanup: {stats_before}")
            
            # Clear all caches
            memory_store.clear_cache()
            
            if CLEANUP_VERBOSE:
                # Get cache stats after cleanup
                stats_after = {
                    "embedding_cache_size": len(memory_store.embedding_cache),
                    "page_cache_size": len(memory_store.page_cache)
                }
                logger.info(f"📊 Cache stats after cleanup: {stats_after}")
            
            logger.info("✅ AUTO CLEANUP: Cache cleanup completed")
        else:
            logger.info("ℹ️  AUTO CLEANUP: Skipped (disabled in config)")
    
    def deep_research(self, topic: str) -> Dict[str, Any]:
        """Complete research pipeline from topic to summarized papers."""
        logger.info(f"🚀 Starting deep research for topic: {topic}")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Stage 1: Search and collect URLs
        logger.info("📋 STAGE 1: Search and Collect URLs")
        stage_start = time.time()
        urls = self.perception_agent.search_and_collect(topic)
        self._record_timing("search_and_collect", stage_start)
        
        # Stage 2: Fetch and extract content
        logger.info("🌐 STAGE 2: Fetch and Extract Content")
        stage_start = time.time()
        extracted_docs = self.perception_agent.fetch_and_extract(urls)
        self._record_timing("fetch_and_extract", stage_start)
        
        # Stage 3: Rank by similarity
        logger.info("📊 STAGE 3: Rank by Similarity")
        stage_start = time.time()
        ranked_docs = self.decision_agent.rank_by_similarity(topic, extracted_docs)
        self._record_timing("rank_by_similarity", stage_start)
        
        # Stage 4: Summarize top papers
        logger.info("📝 STAGE 4: Summarize Top Papers")
        stage_start = time.time()
        summarized_docs = self.decision_agent.summarize_top_papers(ranked_docs)
        self._record_timing("summarize_top_papers", stage_start)
        
        # Calculate total time
        total_time = (time.time() - start_time) * 1000
        
        # Update stats
        self.stats["total_urls_processed"] = len(urls)
        self.stats["total_papers_found"] = len(summarized_docs)
        self.stats["total_processing_time"] = total_time
        
        # Prepare final result
        result = {
            "topic": topic,
            "searched_urls": self.perception_agent.all_searched_urls,  # Include all searched URLs
            "processed_urls": urls,  # Include the URLs that were actually processed
            "papers": [
                {
                    "rank": doc.get('rank', i + 1),
                    "url": doc.get('url', ''),
                    "title": doc.get('title', 'Unknown Title'),
                    "similarity": doc.get('similarity', 0.0),
                    "summary_100_words": doc.get('summary_100_words', '')
                }
                for i, doc in enumerate(summarized_docs)
            ],
            "diagnostics": {
                "candidate_count": len(urls),
                "discarded": len(urls) - len(extracted_docs),
                "timings_ms": self.timings,
                "total_time_ms": total_time,
                "agent_stats": {
                    "perception": self.perception_agent.stats,
                    "decision": self.decision_agent.stats
                },
                "llm_provider": "Gemini Flash" if USE_GEMINI else "Ollama"
            }
        }
        
        logger.info("=" * 80)
        logger.info(f"🎉 Deep research completed!")
        logger.info(f"📊 Final Results:")
        logger.info(f"   🔍 Topic: {topic}")
        logger.info(f"   📄 Papers found: {len(summarized_docs)}")
        logger.info(f"   ⏱️  Total time: {total_time:.2f}ms")
        logger.info(f"   🌐 URLs processed: {len(urls)}")
        logger.info(f"   📝 Documents extracted: {len(extracted_docs)}")
        logger.info(f"   🤖 LLM Provider: {'Gemini Flash' if USE_GEMINI else 'Ollama'}")
        
        # Cleanup cache after output generation
        self._cleanup_cache()
        
        return result

# Global orchestrator instance
research_orchestrator = ResearchOrchestrator()
