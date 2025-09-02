#!/usr/bin/env python3
"""
Test script for improved web search functionality
"""

import logging
from perception import search_web, fetch_page, extract_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_search_functionality():
    """Test the improved search functionality."""
    
    print("🧪 TESTING IMPROVED WEB SEARCH FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Web search
    print("\n🔍 TEST 1: Web Search")
    print("-" * 30)
    
    search_topic = "long attention mechanisms in transformers"
    print(f"Searching for: {search_topic}")
    
    try:
        urls = search_web(search_topic)
        print(f"✅ Found {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"   {i}. {url}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return
    
    if not urls:
        print("❌ No URLs found")
        return
    
    # Test 2: Fetch first URL
    print(f"\n🌐 TEST 2: Fetch First URL")
    print("-" * 30)
    
    test_url = urls[0]
    print(f"Fetching: {test_url}")
    
    try:
        page_data = fetch_page(test_url)
        print(f"✅ Fetch successful:")
        print(f"   Content-Type: {page_data.get('content_type', 'Unknown')}")
        print(f"   Content Length: {page_data.get('content_length', 0):,} bytes")
        print(f"   Fetch Time: {page_data.get('fetch_time', 0):.2f}s")
        
        if page_data.get('content_type') == 'error':
            print(f"❌ Fetch error: {page_data.get('raw', 'Unknown error')}")
            return
            
    except Exception as e:
        print(f"❌ Fetch failed: {e}")
        return
    
    # Test 3: Extract text
    print(f"\n📝 TEST 3: Extract Text")
    print("-" * 30)
    
    try:
        doc = extract_text(
            test_url, 
            page_data['raw'], 
            page_data['content_type']
        )
        
        print(f"✅ Text extraction successful:")
        print(f"   Title: {doc.get('title', 'Not found')}")
        print(f"   Text Length: {doc.get('text_length', 0):,} characters")
        print(f"   Extraction Method: {doc.get('extraction_method', 'Unknown')}")
        
        # Show first 200 characters of text
        text_preview = doc.get('text', '')[:200]
        if text_preview:
            print(f"   Text Preview: {text_preview}...")
        else:
            print(f"   Text Preview: No text extracted")
            
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return
    
    print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_search_functionality()
