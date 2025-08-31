# Scripts for Web Search and Content Extraction
# resticted to research papers

import requests
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup
from readability import Document
import pypdf
import io
import time
from config import (
    RESEARCH_DOMAINS, RESEARCH_PATTERNS, REQUEST_TIMEOUT, 
    REQUEST_HEADERS, MAX_URLS_TO_PROCESS, PLACEHOLDER_SEARCH_RESULTS
)

logger = logging.getLogger(__name__)

def search_web(topic: str) -> List[str]:
    """
    Search the web for research papers related to the topic.
    Returns up to 10 candidate URLs from the first results page.
    """
    try:
        # Use a simple search approach - in a real implementation, you'd use
        # a proper search API like SerpAPI, Bing, or Brave Search
        search_query = f"{topic} research paper filetype:pdf OR site:arxiv.org OR site:openreview.net"
        
        # For demonstration, we'll use a simple approach
        # In production, you'd integrate with a real search API
        logger.info(f"🔍 SEARCHING WEB: {search_query}")
        logger.debug(f"Search query constructed: {search_query}")
        
        # Use placeholder results from config
        # In a real implementation, you would:
        # 1. Call a search API (SerpAPI, Bing, Brave, etc.)
        # 2. Parse the results
        # 3. Filter for research paper URLs
        # 4. Return up to 10 candidates
        
        logger.warning("⚠️  Using placeholder search results. Replace with actual search API integration.")
        logger.info(f"📋 Found {len(PLACEHOLDER_SEARCH_RESULTS)} placeholder URLs")
        
        urls = PLACEHOLDER_SEARCH_RESULTS[:MAX_URLS_TO_PROCESS]
        logger.info(f"✅ Returning {len(urls)} URLs for processing")
        
        # Log each URL for debugging
        for i, url in enumerate(urls, 1):
            logger.debug(f"  {i}. {url}")
        
        return urls
        
    except Exception as e:
        logger.error(f"❌ Error in web search: {e}")
        return []

def is_research_paper_url(url: str) -> bool:
    """Check if URL likely points to a research paper."""
    parsed = urlparse(url.lower())
    
    # Check domain
    if any(domain in parsed.netloc for domain in RESEARCH_DOMAINS):
        logger.debug(f"✅ Research domain detected: {parsed.netloc}")
        return True
    
    # Check URL patterns
    for pattern in RESEARCH_PATTERNS:
        if re.search(pattern, url.lower()):
            logger.debug(f"✅ Research pattern matched: {pattern} in {url}")
            return True
    
    logger.debug(f"❌ Not a research paper URL: {url}")
    return False

def fetch_page(url: str) -> Dict[str, Any]:
    """
    Fetch a web page and return its content.
    Returns: {"url": str, "content_type": str, "raw": bytes|str}
    """
    try:
        logger.info(f"🌐 FETCHING PAGE: {url}")
        logger.debug(f"Request headers: {REQUEST_HEADERS}")
        logger.debug(f"Timeout: {REQUEST_TIMEOUT} seconds")
        
        start_time = time.time()
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        fetch_time = time.time() - start_time
        
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        content_length = len(response.content)
        
        logger.info(f"✅ SUCCESSFULLY FETCHED: {url}")
        logger.info(f"   📊 Content-Type: {content_type}")
        logger.info(f"   📏 Content-Length: {content_length:,} bytes")
        logger.info(f"   ⏱️  Fetch Time: {fetch_time:.2f} seconds")
        logger.info(f"   📡 Status Code: {response.status_code}")
        
        # Log response headers for debugging
        logger.debug(f"Response headers: {dict(response.headers)}")
        
        # Handle different content types
        if 'application/pdf' in content_type:
            raw_content = response.content  # Keep as bytes for PDF
            logger.debug(f"📄 PDF content detected, keeping as bytes")
        else:
            raw_content = response.text  # Convert to string for HTML/text
            logger.debug(f"🌐 HTML/Text content detected, converting to string")
        
        result = {
            "url": url,
            "content_type": content_type,
            "raw": raw_content,
            "etag": response.headers.get('etag'),
            "last_modified": response.headers.get('last-modified'),
            "fetch_time": fetch_time,
            "content_length": content_length
        }
        
        logger.info(f"📦 Page data prepared for {url}")
        return result
        
    except requests.exceptions.Timeout:
        logger.error(f"⏰ TIMEOUT FETCHING: {url} (timeout: {REQUEST_TIMEOUT}s)")
        return {"url": url, "content_type": "error", "raw": "timeout"}
    except requests.exceptions.HTTPError as e:
        logger.error(f"🚫 HTTP ERROR FETCHING: {url} - Status: {e.response.status_code}")
        return {"url": url, "content_type": "error", "raw": f"http_error: {e}"}
    except Exception as e:
        logger.error(f"❌ ERROR FETCHING: {url} - {e}")
        return {"url": url, "content_type": "error", "raw": f"error: {e}"}

def extract_text(url: str, raw: Any, content_type: str) -> Dict[str, Any]:
    """
    Extract readable text from raw content.
    Returns: {"url": str, "title": str|None, "text": str}
    """
    try:
        logger.info(f"📝 EXTRACTING TEXT: {url}")
        logger.debug(f"Content-Type: {content_type}")
        logger.debug(f"Raw content type: {type(raw)}")
        
        title = None
        text = ""
        extraction_method = ""
        
        if 'application/pdf' in content_type:
            # Handle PDF content
            extraction_method = "PDF parsing"
            logger.debug(f"📄 Processing as PDF")
            
            if isinstance(raw, bytes):
                try:
                    pdf_file = io.BytesIO(raw)
                    pdf_reader = pypdf.PdfReader(pdf_file)
                    
                    logger.info(f"📄 PDF has {len(pdf_reader.pages)} pages")
                    
                    # Extract title from metadata
                    if pdf_reader.metadata and pdf_reader.metadata.get('/Title'):
                        title = pdf_reader.metadata['/Title']
                        logger.debug(f"📋 PDF Title: {title}")
                    
                    # Extract text from all pages
                    text_parts = []
                    for i, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                            logger.debug(f"📄 Page {i+1}: {len(page_text)} characters")
                        else:
                            logger.debug(f"📄 Page {i+1}: No text extracted")
                    
                    text = "\n".join(text_parts)
                    logger.info(f"📄 PDF text extraction complete: {len(text)} characters")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Error parsing PDF {url}: {e}")
                    text = f"Error parsing PDF: {e}"
            
        elif 'text/html' in content_type:
            # Handle HTML content
            extraction_method = "HTML parsing"
            logger.debug(f"🌐 Processing as HTML")
            
            if isinstance(raw, str):
                try:
                    # Use readability to extract main content
                    doc = Document(raw)
                    title = doc.title()
                    
                    logger.debug(f"📋 HTML Title: {title}")
                    
                    # Parse with BeautifulSoup for better text extraction
                    soup = BeautifulSoup(raw, 'html.parser')
                    
                    # Remove script and style elements
                    scripts_removed = len(soup.find_all(['script', 'style']))
                    for script in soup(["script", "style"]):
                        script.decompose()
                    logger.debug(f"🧹 Removed {scripts_removed} script/style elements")
                    
                    # Get text from readability-processed content
                    readable_content = doc.summary()
                    if readable_content:
                        readable_soup = BeautifulSoup(readable_content, 'html.parser')
                        text = readable_soup.get_text(separator='\n', strip=True)
                        logger.debug(f"📖 Using readability-extracted content")
                    else:
                        # Fallback to main content extraction
                        main_content = soup.find('main') or soup.find('article') or soup.find('body')
                        if main_content:
                            text = main_content.get_text(separator='\n', strip=True)
                            logger.debug(f"📖 Using main content extraction")
                        else:
                            text = soup.get_text(separator='\n', strip=True)
                            logger.debug(f"📖 Using full body extraction")
                    
                    # Clean up text
                    original_length = len(text)
                    text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
                    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                    text = text.strip()
                    cleaned_length = len(text)
                    
                    logger.debug(f"🧹 Text cleaning: {original_length} → {cleaned_length} characters")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Error parsing HTML {url}: {e}")
                    text = f"Error parsing HTML: {e}"
        
        else:
            # Handle plain text
            extraction_method = "Plain text"
            logger.debug(f"📄 Processing as plain text")
            
            if isinstance(raw, str):
                text = raw
            else:
                text = raw.decode('utf-8', errors='ignore')
        
        # Truncate text if too long (keep first 50k characters)
        from config import MAX_CONTENT_LENGTH
        if len(text) > MAX_CONTENT_LENGTH:
            original_length = len(text)
            text = text[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"
            logger.warning(f"⚠️  Content truncated: {original_length:,} → {MAX_CONTENT_LENGTH:,} characters")
        
        result = {
            "url": url,
            "title": title,
            "text": text,
            "extraction_method": extraction_method,
            "text_length": len(text)
        }
        
        logger.info(f"✅ TEXT EXTRACTION COMPLETE: {url}")
        logger.info(f"   📝 Method: {extraction_method}")
        logger.info(f"   📏 Text Length: {len(text):,} characters")
        logger.info(f"   📋 Title: {title or 'Not found'}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ ERROR EXTRACTING TEXT: {url} - {e}")
        return {
            "url": url,
            "title": None,
            "text": f"Error extracting text: {e}",
            "extraction_method": "error",
            "text_length": 0
        }

def filter_research_papers(urls: List[str]) -> List[str]:
    """Filter URLs to keep only those likely to be research papers."""
    logger.info(f"🔍 FILTERING RESEARCH PAPERS: {len(urls)} URLs")
    
    filtered = []
    for i, url in enumerate(urls, 1):
        logger.debug(f"Checking URL {i}/{len(urls)}: {url}")
        
        if is_research_paper_url(url):
            filtered.append(url)
            logger.debug(f"✅ Accepted: {url}")
        else:
            logger.debug(f"❌ Rejected: {url}")
    
    logger.info(f"📊 FILTERING RESULTS: {len(urls)} → {len(filtered)} research papers")
    logger.info(f"   ✅ Accepted: {len(filtered)}")
    logger.info(f"   ❌ Rejected: {len(urls) - len(filtered)}")
    
    return filtered
