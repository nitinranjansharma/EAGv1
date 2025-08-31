# Scripts for Memory Storage

import hashlib
import json
import sqlite3
import time
from typing import Dict, Any, Optional, List
import logging
from config import CACHE_DB_PATH, CACHE_EXPIRY_HOURS

logger = logging.getLogger(__name__)

class MemoryStore:
    """Simple in-memory store with optional SQLite persistence for caching."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or CACHE_DB_PATH
        self.embedding_cache: Dict[str, List[float]] = {}
        self.page_cache: Dict[str, Dict[str, Any]] = {}
        
        if self.db_path:
            self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        url_hash TEXT PRIMARY KEY,
                        embeddings TEXT,
                        timestamp REAL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS pages (
                        url_hash TEXT PRIMARY KEY,
                        url TEXT,
                        content_type TEXT,
                        raw_content TEXT,
                        etag TEXT,
                        last_modified TEXT,
                        timestamp REAL
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to initialize database: {e}")
    
    def _hash_url(self, url: str) -> str:
        """Generate hash for URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired."""
        return time.time() - timestamp > (CACHE_EXPIRY_HOURS * 3600)
    
    def get_embedding(self, url: str) -> Optional[List[float]]:
        """Get cached embedding for URL."""
        url_hash = self._hash_url(url)
        
        # Check memory cache first
        if url_hash in self.embedding_cache:
            return self.embedding_cache[url_hash]
        
        # Check database if available
        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT embeddings, timestamp FROM embeddings WHERE url_hash = ?",
                        (url_hash,)
                    )
                    result = cursor.fetchone()
                    if result and not self._is_expired(result[1]):
                        embeddings = json.loads(result[0])
                        self.embedding_cache[url_hash] = embeddings
                        return embeddings
            except Exception as e:
                logger.warning(f"Failed to retrieve embedding from DB: {e}")
        
        return None
    
    def store_embedding(self, url: str, embeddings: List[float]):
        """Store embedding for URL."""
        url_hash = self._hash_url(url)
        self.embedding_cache[url_hash] = embeddings
        
        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO embeddings (url_hash, embeddings, timestamp) VALUES (?, ?, ?)",
                        (url_hash, json.dumps(embeddings), time.time())
                    )
                    conn.commit()
            except Exception as e:
                logger.warning(f"Failed to store embedding in DB: {e}")
    
    def get_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached page for URL."""
        url_hash = self._hash_url(url)
        
        # Check memory cache first
        if url_hash in self.page_cache:
            return self.page_cache[url_hash]
        
        # Check database if available
        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT url, content_type, raw_content, etag, last_modified, timestamp FROM pages WHERE url_hash = ?",
                        (url_hash,)
                    )
                    result = cursor.fetchone()
                    if result and not self._is_expired(result[5]):
                        page_data = {
                            "url": result[0],
                            "content_type": result[1],
                            "raw": result[2],
                            "etag": result[3],
                            "last_modified": result[4]
                        }
                        self.page_cache[url_hash] = page_data
                        return page_data
            except Exception as e:
                logger.warning(f"Failed to retrieve page from DB: {e}")
        
        return None
    
    def store_page(self, url: str, content_type: str, raw_content: str, 
                   etag: Optional[str] = None, last_modified: Optional[str] = None):
        """Store page for URL."""
        url_hash = self._hash_url(url)
        page_data = {
            "url": url,
            "content_type": content_type,
            "raw": raw_content,
            "etag": etag,
            "last_modified": last_modified
        }
        self.page_cache[url_hash] = page_data
        
        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """INSERT OR REPLACE INTO pages 
                           (url_hash, url, content_type, raw_content, etag, last_modified, timestamp) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (url_hash, url, content_type, raw_content, etag, last_modified, time.time())
                    )
                    conn.commit()
            except Exception as e:
                logger.warning(f"Failed to store page in DB: {e}")
    
    def clear_cache(self):
        """Clear all caches."""
        self.embedding_cache.clear()
        self.page_cache.clear()
        
        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM embeddings")
                    conn.execute("DELETE FROM pages")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Failed to clear database: {e}")
    
    def cleanup_expired(self):
        """Remove expired entries from database."""
        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    current_time = time.time()
                    expiry_time = current_time - (CACHE_EXPIRY_HOURS * 3600)
                    
                    conn.execute("DELETE FROM embeddings WHERE timestamp < ?", (expiry_time,))
                    conn.execute("DELETE FROM pages WHERE timestamp < ?", (expiry_time,))
                    conn.commit()
                    
                    logger.info("Cleaned up expired cache entries")
            except Exception as e:
                logger.warning(f"Failed to cleanup expired entries: {e}")

# Global memory store instance
memory_store = MemoryStore()
