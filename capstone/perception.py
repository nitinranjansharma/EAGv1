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
import random
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
        logger.info(f"🔍 SEARCHING WEB: {topic}")
        
        # Try multiple search strategies
        search_results = []
        
        # Strategy 1: Google Scholar search
        try:
            google_scholar_urls = search_google_scholar(topic)
            search_results.extend(google_scholar_urls)
            logger.info(f"📚 Google Scholar: Found {len(google_scholar_urls)} URLs")
        except Exception as e:
            logger.warning(f"⚠️  Google Scholar search failed: {e}")
        
        # Strategy 2: arXiv direct search
        try:
            arxiv_urls = search_arxiv(topic)
            search_results.extend(arxiv_urls)
            logger.info(f"📄 arXiv: Found {len(arxiv_urls)} URLs")
        except Exception as e:
            logger.warning(f"⚠️  arXiv search failed: {e}")
        
        # Strategy 3: Semantic Scholar search
        try:
            semantic_urls = search_semantic_scholar(topic)
            search_results.extend(semantic_urls)
            logger.info(f"🔬 Semantic Scholar: Found {len(semantic_urls)} URLs")
        except Exception as e:
            logger.warning(f"⚠️  Semantic Scholar search failed: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for url in search_results:
            if url not in seen:
                seen.add(url)
                unique_results.append(url)
        
        # If no real results, fall back to placeholder with warning
        if not unique_results:
            logger.warning("⚠️  No real search results found, using placeholder URLs")
            unique_results = PLACEHOLDER_SEARCH_RESULTS[:MAX_URLS_TO_PROCESS]
        else:
            logger.info(f"✅ Real search completed: Found {len(unique_results)} unique URLs")
        
        # Limit to max URLs
        final_urls = unique_results[:MAX_URLS_TO_PROCESS]
        
        logger.info(f"📋 Final URL collection: {len(final_urls)} URLs")
        for i, url in enumerate(final_urls, 1):
            logger.debug(f"  {i}. {url}")
        
        return final_urls
        
    except Exception as e:
        logger.error(f"❌ Error in web search: {e}")
        logger.warning("⚠️  Falling back to placeholder URLs")
        return PLACEHOLDER_SEARCH_RESULTS[:MAX_URLS_TO_PROCESS]

def search_google_scholar(topic: str) -> List[str]:
    """Search Google Scholar for research papers."""
    try:
        # Create search query
        search_query = f"{topic} research paper filetype:pdf OR site:arxiv.org OR site:openreview.net"
        search_url = f"https://scholar.google.com/scholar?q={requests.utils.quote(search_query)}"
        
        logger.debug(f"🔍 Google Scholar search URL: {search_url}")
        
        # Use a more realistic user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(search_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse HTML for links
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = []
        
        # Look for research paper links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Extract actual URLs from Google Scholar redirects
            if href.startswith('/url?q='):
                actual_url = href.split('/url?q=')[1].split('&')[0]
                if is_research_paper_url(actual_url):
                    urls.append(actual_url)
            elif href.startswith('http') and is_research_paper_url(href):
                urls.append(href)
        
        # Remove duplicates
        unique_urls = list(dict.fromkeys(urls))
        logger.debug(f"🔍 Google Scholar: Found {len(unique_urls)} research URLs")
        
        return unique_urls[:5]  # Limit to top 5
        
    except Exception as e:
        logger.error(f"❌ Google Scholar search error: {e}")
        return []

def search_arxiv(topic: str) -> List[str]:
    """Search arXiv directly for research papers."""
    try:
        # Create arXiv search query
        search_query = topic.replace(' ', '+')
        search_url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=10&sortBy=relevance&sortOrder=descending"
        
        logger.debug(f"🔍 arXiv search URL: {search_url}")
        
        response = requests.get(search_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse XML response
        soup = BeautifulSoup(response.content, 'xml')
        urls = []
        
        # Extract arXiv URLs
        for entry in soup.find_all('entry'):
            id_elem = entry.find('id')
            if id_elem:
                arxiv_id = id_elem.text.strip()
                if arxiv_id.startswith('http://arxiv.org/abs/'):
                    urls.append(arxiv_id)
        
        logger.debug(f"🔍 arXiv: Found {len(urls)} URLs")
        return urls[:5]  # Limit to top 5
        
    except Exception as e:
        logger.error(f"❌ arXiv search error: {e}")
        return []

def search_semantic_scholar(topic: str) -> List[str]:
    """Search Semantic Scholar for research papers."""
    try:
        # Create search query
        search_query = requests.utils.quote(topic)
        search_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={search_query}&limit=10&fields=url,title,abstract"
        
        logger.debug(f"🔍 Semantic Scholar search URL: {search_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        urls = []
        
        # Extract URLs from response
        for paper in data.get('data', []):
            if 'url' in paper and paper['url']:
                url = paper['url']
                if is_research_paper_url(url):
                    urls.append(url)
        
        logger.debug(f"🔍 Semantic Scholar: Found {len(urls)} URLs")
        return urls[:5]  # Limit to top 5
        
    except Exception as e:
        logger.error(f"❌ Semantic Scholar search error: {e}")
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
        
        # Add random delay to be respectful
        time.sleep(random.uniform(1, 3))
        
        # Enhanced headers for better compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Timeout: {REQUEST_TIMEOUT} seconds")
        
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
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
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(raw, 'html.parser')
                    
                    # Special handling for arXiv
                    if 'arxiv.org' in url:
                        title, text = extract_arxiv_content(soup, url)
                        extraction_method = "arXiv-specific extraction"
                    else:
                        # Use readability for general HTML
                        doc = Document(raw)
                        title = doc.title()
                        
                        logger.debug(f"📋 HTML Title: {title}")
                        
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

def extract_arxiv_content(soup: BeautifulSoup, url: str) -> tuple[str, str]:
    """Extract content specifically from arXiv pages."""
    try:
        title = ""
        text = ""
        
        # Extract title
        title_elem = soup.find('h1', class_='title') or soup.find('h1')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Remove "Title:" prefix if present
            if title.startswith('Title:'):
                title = title[6:].strip()
        
        # Extract abstract
        abstract_elem = soup.find('blockquote', class_='abstract') or soup.find('div', class_='abstract')
        if abstract_elem:
            abstract_text = abstract_elem.get_text(strip=True)
            # Remove "Abstract:" prefix if present
            if abstract_text.startswith('Abstract:'):
                abstract_text = abstract_text[9:].strip()
            text += f"Abstract: {abstract_text}\n\n"
        
        # Extract authors
        authors_elem = soup.find('div', class_='authors') or soup.find('div', class_='author')
        if authors_elem:
            authors_text = authors_elem.get_text(strip=True)
            if authors_text.startswith('Authors:'):
                authors_text = authors_text[8:].strip()
            text += f"Authors: {authors_text}\n\n"
        
        # Extract subjects/categories
        subjects_elem = soup.find('div', class_='subjects') or soup.find('div', class_='categories')
        if subjects_elem:
            subjects_text = subjects_elem.get_text(strip=True)
            if subjects_text.startswith('Subjects:'):
                subjects_text = subjects_text[9:].strip()
            text += f"Subjects: {subjects_text}\n\n"
        
        # Extract additional content from main area
        main_content = soup.find('div', class_='leftcolumn') or soup.find('div', id='content')
        if main_content:
            # Get all text content
            content_text = main_content.get_text(separator='\n', strip=True)
            if content_text:
                text += f"Content:\n{content_text}\n"
        
        # If we still don't have much text, try general extraction
        if len(text.strip()) < 100:
            # Fallback to general text extraction
            body_text = soup.find('body')
            if body_text:
                text = body_text.get_text(separator='\n', strip=True)
        
        logger.debug(f"📄 arXiv extraction: Title length={len(title)}, Text length={len(text)}")
        return title, text
        
    except Exception as e:
        logger.warning(f"⚠️  Error in arXiv-specific extraction: {e}")
        # Fallback to general extraction
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ""
        text = soup.get_text(separator='\n', strip=True)
        return title_text, text

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
