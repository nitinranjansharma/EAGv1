# Research Paper Discovery System

A Python application that automatically discovers, analyzes, and summarizes research papers related to a given topic using web scraping, semantic embeddings, and local/cloud LLM summarization.

## Features

- 🔍 **Web Search**: Automatically searches for research papers related to a topic
- 📄 **Content Extraction**: Extracts text from HTML and PDF documents
- 🧠 **Semantic Ranking**: Uses sentence transformers to rank papers by relevance
- 🤖 **LLM Summarization**: Generates ~100-word summaries using either:
  - **Ollama** (local LLM) - Default
  - **Gemini Flash** (Google's cloud LLM)
- 📊 **Structured Output**: Returns JSON with titles, URLs, similarity scores, and summaries
- 🧹 **Automatic Cleanup**: Clears cache after output generation
- 📝 **Verbose Logging**: Detailed progress tracking and statistics
- 🔧 **MCP Server**: Exposes tools via Model Context Protocol

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd capstone_offline

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure LLM Provider

The system supports two LLM providers for summarization:

#### Option A: Ollama (Local - Default)
```bash
# Start Ollama server
ollama serve

# Pull the model
ollama pull llama2
```

#### Option B: Gemini Flash (Cloud)
```bash
# Switch to Gemini Flash
python switch_llm.py gemini

# Edit config.py and add your API key
# GEMINI_API_KEY = "your_actual_api_key_here"
```

### 3. Run Research

#### Standalone Mode (Recommended)
```bash
python run_research.py
```

#### MCP Server Mode
```bash
python server.py
```

## Configuration

### LLM Provider Switching

Use the utility script to easily switch between LLM providers:

```bash
# Show current configuration
python switch_llm.py show

# Switch to Ollama
python switch_llm.py ollama

# Switch to Gemini Flash
python switch_llm.py gemini
```

### Configuration File (`config.py`)

Key settings you can customize:

```python
# Search Configuration
SEARCH_TOPIC = "graph neural networks for drug discovery"
OUTPUT_FILE = "output.txt"

# LLM Provider Configuration
USE_GEMINI = False  # Set to True for Gemini Flash, False for Ollama

# Gemini Flash Configuration
GEMINI_API_KEY = "your_gemini_api_key_here"
GEMINI_MODEL = "gemini-1.5-flash"

# Ollama Configuration
OLLAMA_MODEL = "llama2"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Processing Configuration
MAX_URLS_TO_PROCESS = 10
TOP_K_PAPERS = 3
SUMMARY_TARGET_WORDS = 100

# Logging Configuration
LOG_LEVEL = "DEBUG"  
AUTO_CLEANUP_AFTER_OUTPUT = True
CLEANUP_VERBOSE = True
```

## File Structure

```
capstone_offline/
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── run_research.py       # Standalone research script
├── server.py             # MCP server
├── switch_llm.py         # LLM provider switcher
├── agents.py             # Agent orchestration
├── perception.py         # Web search and content extraction
├── decision.py           # Embedding, ranking, and summarization
├── memory.py             # Caching and persistence
├── output.txt            # Generated results
├── research_cache.db     # SQLite cache database
└── README.md            # This file
```

## Usage Examples

### Basic Research Pipeline

```python
from agents import research_orchestrator

# Run complete research pipeline
result = research_orchestrator.deep_research("machine learning in healthcare")

# Access results
for paper in result['papers']:
    print(f"Title: {paper['title']}")
    print(f"URL: {paper['url']}")
    print(f"Similarity: {paper['similarity']:.3f}")
    print(f"Summary: {paper['summary_100_words']}")
    print()
```

### Individual Components

```python
from perception import search_web, fetch_page, extract_text
from decision import embed_texts, cosine_rank, summarize_with_llm

# Search for papers
urls = search_web("deep learning")

# Fetch and extract content
page_data = fetch_page(urls[0])
doc = extract_text(urls[0], page_data['raw'], page_data['content_type'])

# Generate embeddings
embeddings = embed_texts([doc['text']])

# Rank by similarity
ranked_docs = cosine_rank("deep learning", [doc])

# Generate summary
summary = summarize_with_llm(doc['title'], doc['text'], doc['url'])
```

## MCP Tools

The system exposes the following MCP tools:

- `search_web_tool(topic: str)` → List[str]
- `fetch_page_tool(url: str)` → Dict
- `extract_text_tool(url: str, raw: Any, content_type: str)` → Dict
- `embed_tool(texts: List[str])` → List[List[float]]
- `rank_tool(topic: str, candidates: List[Dict])` → List[Dict]
- `summarize_tool(title: str, text: str, url: str)` → str
- `deep_research_tool(topic: str)` → Dict
- `clear_cache_tool()` → str
- `get_cache_stats_tool()` → Dict
- `get_llm_config_tool()` → Dict

## Output Format

The system generates structured JSON output:

```json
{
  "topic": "graph neural networks for drug discovery",
  "papers": [
    {
      "rank": 1,
      "url": "https://arxiv.org/abs/example",
      "title": "Example Research Paper",
      "similarity": 0.85,
      "summary_100_words": "This paper presents..."
    }
  ],
  "diagnostics": {
    "candidate_count": 10,
    "discarded": 2,
    "timings_ms": {
      "search_and_collect": 1500,
      "fetch_and_extract": 8000,
      "rank_by_similarity": 500,
      "summarize_top_papers": 12000
    },
    "total_time_ms": 22000,
    "agent_stats": {
      "perception": {...},
      "decision": {...}
    },
    "llm_provider": "Ollama"
  }
}
```

## Logging and Monitoring

The system provides comprehensive logging:

- 🔍 **Search Progress**: URLs found, filtering results
- 🌐 **Website Visits**: Fetch times, content types, sizes
- 📝 **Processing Stats**: Text extraction, embedding generation
- 🤖 **LLM Operations**: Summarization times, quality metrics
- 🧹 **Cache Management**: Cleanup operations, memory usage

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   ```bash
   # Make sure Ollama is running
   ollama serve
   ```

2. **Gemini API Error**
   ```bash
   # Check your API key in config.py
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

3. **Cache Issues**
   ```bash
   # Clear cache manually
   python -c "from memory import memory_store; memory_store.clear_cache()"
   ```

### Performance Tips

- Use `LOG_LEVEL = "INFO"` for production to reduce log verbosity
- Set `AUTO_CLEANUP_AFTER_OUTPUT = False` to preserve cache between runs
- Adjust `MAX_URLS_TO_PROCESS` based on your needs
- Use Gemini Flash for faster summarization (requires API key)

## Dependencies

- `mcp` - Model Context Protocol
- `sentence-transformers` - Semantic embeddings
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `readability-lxml` - Content extraction
- `pypdf` - PDF parsing
- `scikit-learn` - Cosine similarity
- `sqlite3` - Cache persistence

## License

This project is licensed under the MIT License.
