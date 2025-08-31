#!/usr/bin/env python3
"""
Test script for the Research Paper Discovery system.

This script tests the individual components without requiring the MCP server
to be running, making it useful for development and debugging.
"""

import sys
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported correctly."""
    logger.info("Testing imports...")
    
    try:
        import memory
        logger.info("✓ memory module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import memory: {e}")
        return False
    
    try:
        import perception
        logger.info("✓ perception module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import perception: {e}")
        return False
    
    try:
        import decision
        logger.info("✓ decision module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import decision: {e}")
        return False
    
    try:
        import agents
        logger.info("✓ agents module imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import agents: {e}")
        return False
    
    return True

def test_memory_store():
    """Test the memory store functionality."""
    logger.info("Testing memory store...")
    
    try:
        from memory import memory_store
        
        # Test storing and retrieving embeddings
        test_url = "https://example.com/test"
        test_embeddings = [0.1, 0.2, 0.3, 0.4]
        
        memory_store.store_embedding(test_url, test_embeddings)
        retrieved = memory_store.get_embedding(test_url)
        
        if retrieved == test_embeddings:
            logger.info("✓ Memory store embedding test passed")
        else:
            logger.error("✗ Memory store embedding test failed")
            return False
        
        # Test storing and retrieving pages
        test_page_data = {
            "url": test_url,
            "content_type": "text/html",
            "raw": "<html><body>Test content</body></html>",
            "etag": "test-etag",
            "last_modified": "2023-01-01"
        }
        
        memory_store.store_page(
            test_url,
            test_page_data["content_type"],
            test_page_data["raw"],
            test_page_data["etag"],
            test_page_data["last_modified"]
        )
        
        retrieved_page = memory_store.get_page(test_url)
        if retrieved_page and retrieved_page["raw"] == test_page_data["raw"]:
            logger.info("✓ Memory store page test passed")
        else:
            logger.error("✗ Memory store page test failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Memory store test failed: {e}")
        return False

def test_perception():
    """Test perception module functions."""
    logger.info("Testing perception module...")
    
    try:
        from perception import search_web, is_research_paper_url, filter_research_papers
        
        # Test research paper URL detection
        test_urls = [
            "https://arxiv.org/abs/2023.12345",
            "https://openreview.net/forum?id=example",
            "https://papers.nips.cc/paper/2023/hash/example",
            "https://example.com/not-a-paper",
            "https://example.com/paper.pdf"
        ]
        
        expected_results = [True, True, True, False, True]
        actual_results = [is_research_paper_url(url) for url in test_urls]
        
        if actual_results == expected_results:
            logger.info("✓ Research paper URL detection test passed")
        else:
            logger.error(f"✗ Research paper URL detection test failed")
            logger.error(f"Expected: {expected_results}")
            logger.error(f"Actual: {actual_results}")
            return False
        
        # Test filtering
        filtered = filter_research_papers(test_urls)
        expected_filtered = [url for url, expected in zip(test_urls, expected_results) if expected]
        
        if filtered == expected_filtered:
            logger.info("✓ URL filtering test passed")
        else:
            logger.error("✗ URL filtering test failed")
            return False
        
        # Test search (should return placeholder results)
        search_results = search_web("test topic")
        if isinstance(search_results, list):
            logger.info("✓ Search web test passed (placeholder results)")
        else:
            logger.error("✗ Search web test failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Perception test failed: {e}")
        return False

def test_decision():
    """Test decision module functions."""
    logger.info("Testing decision module...")
    
    try:
        from decision import embed_texts, cosine_rank, count_words
        
        # Test embedding generation
        test_texts = ["This is a test document.", "Another test document."]
        embeddings = embed_texts(test_texts)
        
        if len(embeddings) == 2 and embeddings.shape[1] == 384:  # all-MiniLM-L6-v2 has 384 dimensions
            logger.info("✓ Embedding generation test passed")
        else:
            logger.error("✗ Embedding generation test failed")
            return False
        
        # Test cosine ranking
        test_docs = [
            {"url": "https://example1.com", "title": "Test 1", "text": "This is about machine learning."},
            {"url": "https://example2.com", "title": "Test 2", "text": "This is about cooking."},
            {"url": "https://example3.com", "title": "Test 3", "text": "This is about AI and neural networks."}
        ]
        
        query = "machine learning and artificial intelligence"
        ranked_docs = cosine_rank(query, test_docs)
        
        if len(ranked_docs) == 3 and all('similarity' in doc for doc in ranked_docs):
            logger.info("✓ Cosine ranking test passed")
        else:
            logger.error("✗ Cosine ranking test failed")
            return False
        
        # Test word counting
        test_text = "This is a test sentence with seven words."
        word_count = count_words(test_text)
        
        if word_count == 7:
            logger.info("✓ Word counting test passed")
        else:
            logger.error(f"✗ Word counting test failed: expected 7, got {word_count}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Decision test failed: {e}")
        return False

def test_agents():
    """Test agents module."""
    logger.info("Testing agents module...")
    
    try:
        from agents import research_orchestrator
        
        # Test that the orchestrator can be created
        if research_orchestrator is not None:
            logger.info("✓ Research orchestrator creation test passed")
        else:
            logger.error("✗ Research orchestrator creation test failed")
            return False
        
        # Test that agents exist
        if hasattr(research_orchestrator, 'perception_agent'):
            logger.info("✓ Perception agent exists")
        else:
            logger.error("✗ Perception agent missing")
            return False
        
        if hasattr(research_orchestrator, 'decision_agent'):
            logger.info("✓ Decision agent exists")
        else:
            logger.error("✗ Decision agent missing")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Agents test failed: {e}")
        return False

def test_end_to_end():
    """Test a simplified end-to-end flow."""
    logger.info("Testing end-to-end flow...")
    
    try:
        from agents import research_orchestrator
        
        # Test with a simple topic
        topic = "test topic"
        result = research_orchestrator.deep_research(topic)
        
        # Check result structure
        required_keys = ["topic", "papers", "diagnostics"]
        if all(key in result for key in required_keys):
            logger.info("✓ End-to-end test passed (structure correct)")
        else:
            logger.error("✗ End-to-end test failed (missing keys)")
            return False
        
        # Check that topic is preserved
        if result["topic"] == topic:
            logger.info("✓ Topic preservation test passed")
        else:
            logger.error("✗ Topic preservation test failed")
            return False
        
        # Check diagnostics structure
        diagnostics = result["diagnostics"]
        if "candidate_count" in diagnostics and "total_time_ms" in diagnostics:
            logger.info("✓ Diagnostics structure test passed")
        else:
            logger.error("✗ Diagnostics structure test failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ End-to-end test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting Research Paper Discovery System Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Memory Store Test", test_memory_store),
        ("Perception Test", test_perception),
        ("Decision Test", test_decision),
        ("Agents Test", test_agents),
        ("End-to-End Test", test_end_to_end)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name}...")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The system is ready to use.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
