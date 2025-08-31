# Deep Research Multi-Agent System with Ollama Integration

A sophisticated multi-agent research system built using MCP (Model Context Protocol) tools and Ollama for local LLM processing. The system provides comprehensive research capabilities including technical paper analysis, research paper search with ranking, citation extraction, and interactive research sessions.

## 🚀 Key Features

### 🔬 Technical Paper Analysis
- **Upload and analyze technical papers/books**
- **Multiple analysis types**: Summary, methodology critique, results interpretation, question answering
- **Citation extraction and management**
- **Structured analysis reports**

### 📚 Research Paper Search
- **Search academic papers** across multiple databases (arXiv, Google Scholar)
- **Rank papers by relevance and recency**
- **Extract bite-sized insights** from papers
- **Citation analysis and management**

### 🤖 Local LLM Integration
- **Ollama integration** for local generative models
- **No cloud dependencies** - runs entirely locally
- **Customizable models** (llama2, codellama, etc.)
- **Advanced prompt engineering** for research tasks

### 🔄 Interactive Research Sessions
- **Interactive command-line interface**
- **Real-time research workflows**
- **Session management and history**
- **Iterative refinement capabilities**

## 🏗️ System Architecture

The system consists of 8 core modules:

1. **`memory.py`** - Persistent Knowledge Base
2. **`perception.py`** - Context Agent & Intent Interpretation
3. **`decision.py`** - Task Routing Engine
4. **`agents.py`** - Functional Agents (Document, Web, Summary, Analysis, Technical Analysis)
5. **`action.py`** - Action Layer & Response Assembly
6. **`ollama_integration.py`** - Ollama Local LLM Integration
7. **`web_research.py`** - Enhanced Web Research & Paper Search
8. **`server.py`** - MCP Server & Interactive Interface

## 📋 Installation

### Prerequisites
1. **Python 3.8+**
2. **Ollama** installed and running locally
3. **Git**

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd capstone
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and start Ollama**:
   ```bash
   # Install Ollama (macOS/Linux)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   
   # Pull a model (in another terminal)
   ollama pull llama2
   ```

4. **Run the system**:
   ```bash
   python server.py
   ```

## 🧪 Usage

### Interactive Research Session

When you run `python server.py`, you'll be presented with an interactive menu:

```
🎯 Choose mode:
1. Interactive Research Session
2. MCP Server Mode (for external clients)
```

Select option 1 for the interactive session, which provides:

#### 1. Technical Paper Analysis
- Upload technical papers or books
- Choose analysis type:
  - Summary
  - Methodology Critique
  - Results Interpretation
  - Question Answering
  - Citation Extraction
  - Structured Analysis

#### 2. Research Paper Search
- Search for papers on any topic
- Get ranked results by relevance/recency
- Extract insights and citations
- Generate research summaries

#### 3. General Research Query
- Ask research questions
- Get multi-source analysis
- Receive suggestions for further research

#### 4. Document Upload and Analysis
- Upload custom text content
- Get comprehensive analysis
- Extract key insights and citations

### Example Usage

```python
# Technical Paper Analysis
"Analyze this technical paper with methodology critique"

# Research Paper Search
"Search for papers on machine learning optimization"

# General Research
"What are the latest developments in transformer models?"

# Document Analysis
"Upload and analyze this research document"
```

## 🔧 Configuration

### Ollama Configuration

The system can be configured through the config dictionary:

```python
config = {
    "storage_path": "./data/knowledge_base",  # Knowledge base storage
    "data_path": "./data/documents",          # Local documents path
    "ollama_model": "llama2",                 # Ollama model to use
    "ollama_temperature": 0.7,                # Generation temperature
}
```

### Available Ollama Models

The system works with any Ollama model. Recommended models:

- **llama2** - General purpose research
- **codellama** - Technical/code analysis
- **mistral** - Fast and efficient
- **llama2:13b** - Higher quality (requires more RAM)

## 📁 Project Structure

```
capstone/
├── memory.py              # Knowledge base and data storage
├── perception.py          # Context agent and intent interpretation
├── decision.py            # Task routing and workflow orchestration
├── agents.py              # Functional agents (document, web, summary, analysis, technical)
├── action.py              # Action layer and response compilation
├── ollama_integration.py  # Ollama local LLM integration
├── web_research.py        # Enhanced web research and paper search
├── server.py              # MCP server and interactive interface
├── test_system.py         # Comprehensive test suite
├── requirements.txt       # Dependencies
├── README.md              # This file
└── data/                  # Data storage (created automatically)
    ├── knowledge_base/    # Knowledge base files
    └── documents/         # Local documents for analysis
```

## 🔬 Research Capabilities

### Technical Paper Analysis

The system can analyze technical papers and books with:

- **Comprehensive summaries** with key findings
- **Methodology critique** with strengths/weaknesses
- **Results interpretation** with statistical analysis
- **Question answering** based on paper content
- **Citation extraction** and management
- **Structured analysis** reports

### Research Paper Search

Search capabilities include:

- **Multi-database search** (arXiv, Google Scholar)
- **Relevance ranking** based on query and content
- **Recency scoring** for up-to-date research
- **Insight extraction** from abstracts and titles
- **Citation analysis** and reference management
- **Research synthesis** across multiple papers

### Local LLM Processing

Ollama integration provides:

- **No cloud dependencies** - complete privacy
- **Customizable prompts** for different research tasks
- **High-quality analysis** using local models
- **Fast processing** without API rate limits
- **Offline capability** for research work

## 🎯 Use Cases

### Academic Research
- Literature review automation
- Paper analysis and critique
- Citation management
- Research synthesis

### Technical Documentation
- Technical paper analysis
- Methodology review
- Results interpretation
- Question answering

### Research Discovery
- Finding relevant papers
- Ranking by importance
- Extracting key insights
- Identifying research gaps

### Content Analysis
- Document summarization
- Key insight extraction
- Citation analysis
- Structured reporting

## 🚧 Development Roadmap

### ✅ Completed Features
- [x] Core multi-agent architecture
- [x] Ollama integration for local LLM
- [x] Technical paper analysis
- [x] Research paper search
- [x] Citation extraction
- [x] Interactive research sessions
- [x] MCP server interface

### 🔄 Future Enhancements
- [ ] PDF document processing
- [ ] Enhanced citation parsing
- [ ] Research trend analysis
- [ ] Collaborative research sessions
- [ ] Advanced NLP capabilities
- [ ] Research visualization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Troubleshooting

**Ollama Connection Issues**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

**Model Download Issues**:
```bash
# Pull a specific model
ollama pull llama2

# List available models
ollama list
```

**Dependency Issues**:
```bash
# Update pip
pip install --upgrade pip

# Install dependencies with specific versions
pip install -r requirements.txt --force-reinstall
```

### Getting Help

For questions, issues, or contributions:
1. Check the troubleshooting section above
2. Review the system logs for error messages
3. Open an issue on the repository
4. Check the Ollama documentation for model-specific issues

## 🔮 Future Enhancements

- **Multi-modal Support**: Handle images, audio, and video
- **Advanced NLP**: Named entity recognition, sentiment analysis
- **Research Visualization**: Charts, graphs, and visual summaries
- **Collaborative Features**: Multi-user research sessions
- **API Integration**: Connect to external research databases
- **Real-time Updates**: Live research monitoring and alerts
