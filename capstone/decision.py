# Scripts for Decision Making, embedding and summarization

import numpy as np
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
import re
import time
from config import (
    EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, 
    USE_GEMINI, OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TOP_P, OLLAMA_MAX_TOKENS,
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_URL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS, GEMINI_TOP_P,
    SUMMARY_TARGET_WORDS, MAX_SUMMARY_LENGTH
)

logger = logging.getLogger(__name__)

# Global model instance
_embedding_model = None

def get_embedding_model():
    """Get or create the sentence transformer model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"🧠 Loading sentence transformer model: {EMBEDDING_MODEL}")
        logger.debug(f"📊 Expected dimensions: {EMBEDDING_DIMENSIONS}")
        
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        logger.info(f"✅ Model loaded successfully")
        logger.debug(f"📊 Model device: {_embedding_model.device}")
        logger.debug(f"📊 Model max sequence length: {_embedding_model.max_seq_length}")
    return _embedding_model

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed a list of texts using sentence-transformers.
    Returns numpy array of embeddings.
    """
    try:
        logger.info(f"🧠 Starting embedding generation for {len(texts)} texts")
        
        model = get_embedding_model()
        
        # Clean and prepare texts
        cleaned_texts = []
        original_lengths = []
        
        for i, text in enumerate(texts):
            if isinstance(text, str) and text.strip():
                # Truncate to reasonable length for embedding
                original_length = len(text)
                cleaned_text = text[:1000]  # Limit to first 1000 chars for embedding
                cleaned_texts.append(cleaned_text)
                original_lengths.append(original_length)
                
                logger.debug(f"📝 Text {i+1}: {original_length} → {len(cleaned_text)} characters")
            else:
                cleaned_texts.append("")
                original_lengths.append(0)
                logger.debug(f"📝 Text {i+1}: Empty or invalid text")
        
        logger.info(f"🧹 Text preprocessing complete")
        logger.debug(f"📊 Average text length: {sum(original_lengths) / len(original_lengths):.1f} characters")
        
        # Generate embeddings
        logger.info(f"🧠 Generating embeddings...")
        embed_start = time.time()
        embeddings = model.encode(cleaned_texts, convert_to_numpy=True)
        embed_time = time.time() - embed_start
        
        logger.info(f"✅ Embedding generation completed in {embed_time:.2f}s")
        logger.info(f"📊 Generated {len(embeddings)} embeddings")
        logger.info(f"📊 Embedding shape: {embeddings.shape}")
        logger.info(f"📊 Embedding dimensions: {embeddings.shape[1]}")
        
        # Log embedding statistics
        if len(embeddings) > 0:
            mean_norm = np.mean(np.linalg.norm(embeddings, axis=1))
            std_norm = np.std(np.linalg.norm(embeddings, axis=1))
            logger.debug(f"📊 Embedding statistics - Mean norm: {mean_norm:.4f}, Std norm: {std_norm:.4f}")
        
        return embeddings
        
    except Exception as e:
        logger.error(f"❌ Error generating embeddings: {e}")
        # Return zero embeddings as fallback
        fallback_embeddings = np.zeros((len(texts), EMBEDDING_DIMENSIONS))
        logger.warning(f"⚠️  Using fallback zero embeddings: {fallback_embeddings.shape}")
        return fallback_embeddings

def cosine_rank(query: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank documents by cosine similarity to query.
    Returns list of docs with similarity scores, sorted descending.
    """
    try:
        logger.info(f"📊 Starting cosine similarity ranking")
        logger.info(f"🔍 Query: {query}")
        logger.info(f"📄 Documents to rank: {len(docs)}")
        
        if not docs:
            logger.warning(f"⚠️  No documents to rank")
            return []
        
        # Prepare texts for embedding
        texts = [doc.get('text', '') for doc in docs]
        texts.insert(0, query)  # Add query as first text
        
        logger.info(f"📝 Preparing {len(texts)} texts for embedding (1 query + {len(docs)} documents)")
        
        # Generate embeddings
        embeddings = embed_texts(texts)
        
        if len(embeddings) == 0:
            logger.error(f"❌ No embeddings generated")
            return docs
        
        # Calculate cosine similarities
        logger.info(f"📊 Calculating cosine similarities...")
        
        query_embedding = embeddings[0:1]  # Query embedding
        doc_embeddings = embeddings[1:]    # Document embeddings
        
        logger.debug(f"📊 Query embedding shape: {query_embedding.shape}")
        logger.debug(f"📊 Document embeddings shape: {doc_embeddings.shape}")
        
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        logger.info(f"✅ Similarity calculation complete")
        logger.debug(f"📊 Similarity scores: {similarities}")
        
        # Add similarity scores to documents
        ranked_docs = []
        for i, doc in enumerate(docs):
            doc_copy = doc.copy()
            doc_copy['similarity'] = float(similarities[i])
            ranked_docs.append(doc_copy)
            
            logger.debug(f"📄 Document {i+1}: {doc.get('title', 'Unknown')} - Similarity: {similarities[i]:.4f}")
        
        # Sort by similarity (descending)
        ranked_docs.sort(key=lambda x: x['similarity'], reverse=True)
        
        logger.info(f"📊 Ranking complete - Top 3 similarities:")
        for i, doc in enumerate(ranked_docs[:3]):
            title = doc.get('title', 'Unknown Title')
            similarity = doc.get('similarity', 0.0)
            logger.info(f"   {i+1}. {title} (similarity: {similarity:.4f})")
        
        return ranked_docs
        
    except Exception as e:
        logger.error(f"❌ Error in cosine ranking: {e}")
        # Return original docs with zero similarity scores
        for doc in docs:
            doc['similarity'] = 0.0
        return docs

def summarize_with_gemini(title: str, text: str, url: str, target_words: int = None) -> str:
    """
    Generate a summary using Google Gemini Flash API.
    Uses low temperature for consistent, concise summaries.
    """
    try:
        if target_words is None:
            target_words = SUMMARY_TARGET_WORDS
            
        logger.info(f"🤖 Starting Gemini Flash summarization")
        logger.info(f"📋 Title: {title or 'Unknown'}")
        logger.info(f"🔗 URL: {url}")
        logger.info(f"📏 Target words: {target_words}")
        
        # Prepare the text for summarization
        if not text or len(text.strip()) < 50:
            logger.warning(f"⚠️  Insufficient text content for summarization")
            return "Insufficient text content for summarization."
        
        logger.info(f"📏 Original text length: {len(text):,} characters")
        
        # Truncate text if too long (keep first 2000 chars for summarization)
        truncated_text = text[:MAX_SUMMARY_LENGTH]
        if len(text) > MAX_SUMMARY_LENGTH:
            truncated_text += "\n\n[Content truncated for summarization]"
            logger.warning(f"⚠️  Text truncated: {len(text):,} → {MAX_SUMMARY_LENGTH:,} characters")
        
        logger.info(f"📏 Truncated text length: {len(truncated_text):,} characters")
        
        # Create prompt for summarization
        prompt = f"""Please provide a concise summary of the following research paper in approximately {target_words} words.

Title: {title or 'Unknown'}
URL: {url}

Content:
{truncated_text}

Summary (approximately {target_words} words):"""

        logger.debug(f"📝 Generated prompt length: {len(prompt):,} characters")
        
        # Call Gemini API
        logger.info(f"🤖 Calling Gemini Flash API...")
        logger.debug(f"🔗 Gemini URL: {GEMINI_URL}")
        logger.debug(f"🤖 Model: {GEMINI_MODEL}")
        logger.debug(f"🌡️  Temperature: {GEMINI_TEMPERATURE}")
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": GEMINI_TEMPERATURE,
                "topP": GEMINI_TOP_P,
                "maxOutputTokens": GEMINI_MAX_TOKENS,
                "stopSequences": []
            }
        }
        
        # Add API key to URL
        api_url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
        
        request_start = time.time()
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        request_time = time.time() - request_start
        
        response.raise_for_status()
        
        logger.info(f"✅ Gemini API response received in {request_time:.2f}s")
        logger.debug(f"📡 Response status: {response.status_code}")
        
        result = response.json()
        
        # Extract text from Gemini response
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    summary = parts[0]['text'].strip()
                else:
                    raise ValueError("No text found in Gemini response parts")
            else:
                raise ValueError("Invalid response structure from Gemini API")
        else:
            raise ValueError("No candidates found in Gemini response")
        
        logger.info(f"📏 Raw summary length: {len(summary):,} characters")
        
        # Clean up the summary
        original_summary = summary
        summary = re.sub(r'\n+', ' ', summary)  # Remove excessive newlines
        summary = re.sub(r'\s+', ' ', summary)  # Normalize whitespace
        summary = summary.strip()
        
        logger.debug(f"🧹 Summary cleaning: {len(original_summary)} → {len(summary)} characters")
        
        # Ensure summary is not too long
        words = summary.split()
        if len(words) > target_words * 1.5:  # Allow 50% overflow
            original_words = len(words)
            summary = ' '.join(words[:int(target_words * 1.5)]) + "..."
            logger.warning(f"⚠️  Summary truncated: {original_words} → {len(summary.split())} words")
        
        word_count = len(summary.split())
        logger.info(f"✅ Gemini summary generation complete")
        logger.info(f"📏 Final summary: {word_count} words, {len(summary)} characters")
        logger.info(f"📊 Summary quality: {'Good' if word_count >= target_words * 0.8 else 'Short'}")
        
        return summary
        
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Gemini API connection error")
        return f"Summary unavailable: Gemini API connection failed"
    except requests.exceptions.Timeout:
        logger.error(f"⏰ Timeout calling Gemini API")
        return "Summary unavailable: Timeout while generating summary."
    except Exception as e:
        logger.error(f"❌ Error generating Gemini summary: {e}")
        return f"Summary unavailable: {str(e)}"

def summarize_with_ollama(title: str, text: str, url: str, target_words: int = None) -> str:
    """
    Generate a summary using local Ollama LLM.
    Uses low temperature for consistent, concise summaries.
    """
    try:
        if target_words is None:
            target_words = SUMMARY_TARGET_WORDS
            
        logger.info(f"📝 Starting Ollama summarization")
        logger.info(f"📋 Title: {title or 'Unknown'}")
        logger.info(f"🔗 URL: {url}")
        logger.info(f"📏 Target words: {target_words}")
        
        # Prepare the text for summarization
        if not text or len(text.strip()) < 50:
            logger.warning(f"⚠️  Insufficient text content for summarization")
            return "Insufficient text content for summarization."
        
        logger.info(f"📏 Original text length: {len(text):,} characters")
        
        # Truncate text if too long (keep first 2000 chars for summarization)
        truncated_text = text[:MAX_SUMMARY_LENGTH]
        if len(text) > MAX_SUMMARY_LENGTH:
            truncated_text += "\n\n[Content truncated for summarization]"
            logger.warning(f"⚠️  Text truncated: {len(text):,} → {MAX_SUMMARY_LENGTH:,} characters")
        
        logger.info(f"📏 Truncated text length: {len(truncated_text):,} characters")
        
        # Create prompt for summarization
        prompt = f"""Please provide a concise summary of the following research paper in approximately {target_words} words.

Title: {title or 'Unknown'}
URL: {url}

Content:
{truncated_text}

Summary (approximately {target_words} words):"""

        logger.debug(f"📝 Generated prompt length: {len(prompt):,} characters")
        
        # Call Ollama API
        logger.info(f"🤖 Calling Ollama API...")
        logger.debug(f"🔗 Ollama URL: {OLLAMA_URL}")
        logger.debug(f"🤖 Model: {OLLAMA_MODEL}")
        logger.debug(f"🌡️  Temperature: {OLLAMA_TEMPERATURE}")
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": OLLAMA_TEMPERATURE,
                "top_p": OLLAMA_TOP_P,
                "max_tokens": OLLAMA_MAX_TOKENS
            }
        }
        
        request_start = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        request_time = time.time() - request_start
        
        response.raise_for_status()
        
        logger.info(f"✅ Ollama API response received in {request_time:.2f}s")
        logger.debug(f"📡 Response status: {response.status_code}")
        
        result = response.json()
        summary = result.get('response', '').strip()
        
        logger.info(f"📏 Raw summary length: {len(summary):,} characters")
        
        # Clean up the summary
        original_summary = summary
        summary = re.sub(r'\n+', ' ', summary)  # Remove excessive newlines
        summary = re.sub(r'\s+', ' ', summary)  # Normalize whitespace
        summary = summary.strip()
        
        logger.debug(f"🧹 Summary cleaning: {len(original_summary)} → {len(summary)} characters")
        
        # Ensure summary is not too long
        words = summary.split()
        if len(words) > target_words * 1.5:  # Allow 50% overflow
            original_words = len(words)
            summary = ' '.join(words[:int(target_words * 1.5)]) + "..."
            logger.warning(f"⚠️  Summary truncated: {original_words} → {len(summary.split())} words")
        
        word_count = len(summary.split())
        logger.info(f"✅ Ollama summary generation complete")
        logger.info(f"📏 Final summary: {word_count} words, {len(summary)} characters")
        logger.info(f"📊 Summary quality: {'Good' if word_count >= target_words * 0.8 else 'Short'}")
        
        return summary
        
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Ollama server not running or not accessible")
        return f"Summary unavailable: Ollama server not running. Please start Ollama with: ollama serve"
    except requests.exceptions.Timeout:
        logger.error(f"⏰ Timeout calling Ollama API")
        return "Summary unavailable: Timeout while generating summary."
    except Exception as e:
        logger.error(f"❌ Error generating Ollama summary: {e}")
        return f"Summary unavailable: {str(e)}"

def summarize_with_llm(title: str, text: str, url: str, target_words: int = None) -> str:
    """
    Generate a summary using the configured LLM provider (Gemini or Ollama).
    """
    if USE_GEMINI:
        logger.info(f"🤖 Using Gemini Flash for summarization")
        return summarize_with_gemini(title, text, url, target_words)
    else:
        logger.info(f"📝 Using Ollama for summarization")
        return summarize_with_ollama(title, text, url, target_words)

def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())

def validate_summary_quality(summary: str, target_words: int = None) -> bool:
    """Validate that summary meets quality criteria."""
    if target_words is None:
        target_words = SUMMARY_TARGET_WORDS
        
    if not summary or summary.startswith("Summary unavailable"):
        logger.debug(f"❌ Summary validation failed: Empty or error summary")
        return False
    
    word_count = count_words(summary)
    
    # Check if summary is within reasonable bounds
    if word_count < 20 or word_count > target_words * 2:
        logger.debug(f"❌ Summary validation failed: Word count {word_count} outside bounds [20, {target_words * 2}]")
        return False
    
    # Check if summary seems meaningful (not just error messages)
    if len(summary) < 50:
        logger.debug(f"❌ Summary validation failed: Too short ({len(summary)} characters)")
        return False
    
    logger.debug(f"✅ Summary validation passed: {word_count} words, {len(summary)} characters")
    return True
