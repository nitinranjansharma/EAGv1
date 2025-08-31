"""
Configuration file for Research Paper Discovery System.
Contains all constants, model IDs, and search topics.
"""

# Search Configuration
SEARCH_TOPIC = "Increasing context length for large language models"
OUTPUT_FILE = "output.txt"

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# LLM Provider Configuration
USE_GEMINI = True  # Set to True to use Gemini Flash, False for Ollama
OLLAMA_MODEL = "llama2"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Gemini Flash Configuration
GEMINI_API_KEY = "****"  
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Ollama Configuration
OLLAMA_TEMPERATURE = 0.3
OLLAMA_TOP_P = 0.9
OLLAMA_MAX_TOKENS = 200

# Gemini Configuration
GEMINI_TEMPERATURE = 0.3
GEMINI_MAX_TOKENS = 200
GEMINI_TOP_P = 0.9

# Content Processing Configuration
MAX_CONTENT_LENGTH = 50000
MAX_SUMMARY_LENGTH = 2000
MIN_TEXT_LENGTH = 100
MAX_URLS_TO_PROCESS = 3  # Reduced to ensure exactly 3 URLs
TOP_K_PAPERS = 3
SUMMARY_TARGET_WORDS = 100

# Logging Configuration
LOG_LEVEL = "DEBUG"  # Changed to DEBUG for more verbosity
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Cleanup Configuration
AUTO_CLEANUP_AFTER_OUTPUT = True  # Automatically clear cache after output generation
CLEANUP_VERBOSE = True  # Verbose logging during cleanup

# Research Paper Detection
RESEARCH_DOMAINS = {
    'arxiv.org', 'openreview.net', 'aclweb.org', 'acl-anthology.org',
    'papers.nips.cc', 'proceedings.mlr.press', 'iclr.cc', 'icml.cc',
    'jmlr.org', 'ieee.org', 'acm.org', 'springer.com', 'sciencedirect.com',
    'researchgate.net', 'semanticscholar.org', 'biorxiv.org', 'medrxiv.org'
}

RESEARCH_PATTERNS = [
    r'\.pdf$',
    r'/pdf/',
    r'/paper/',
    r'/papers/',
    r'/article/',
    r'/abstract/',
    r'/abs/',
    r'/pub/',
    r'/publication/',
    r'/research/',
    r'/conference/',
    r'/proceedings/',
    r'/journal/',
    r'/volume/',
    r'/issue/'
]

# Network Configuration
REQUEST_TIMEOUT = 30
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Cache Configuration
CACHE_DB_PATH = "research_cache.db"
CACHE_EXPIRY_HOURS = 24

# MCP Server Configuration
MCP_SERVER_NAME = "research-paper-discovery"

# Search API Configuration (for future integration)
SEARCH_API_CONFIG = {
    "serpapi": {
        "url": "https://serpapi.com/search",
        "engine": "google",
        "api_key": None  # Set your API key here
    },
    "bing": {
        "url": "https://api.bing.microsoft.com/v7.0/search",
        "api_key": None  # Set your API key here
    },
    "brave": {
        "url": "https://api.search.brave.com/res/v1/web/search",
        "api_key": None  # Set your API key here
    }
}

# Placeholder search results (for demo purposes)
PLACEHOLDER_SEARCH_RESULTS = [
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
]

