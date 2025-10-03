# 🔬 Deep Research Agent

> **AI-powered research platform that aggregates and analyzes information from social media, web content, and multiple data sources to deliver comprehensive, fact-checked research summaries.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Features

- **Multi-Source Research**: Aggregates data from Reddit, Medium, Google, Wikipedia, news sources, and social media
- **AI-Powered Summarization**: Uses local Mistral-7B model for fact-checked, categorized summaries
- **Real-time Web Scraping**: Dynamic content extraction with intelligent URL generation
- **Social Media Intelligence**: RapidAI integration for Twitter, Instagram, TikTok, and more
- **Categorized Output**: Organizes results by source type (Wikipedia, Reddit, News, etc.)
- **Fact-Checking Prompts**: Prevents hallucination with strict evidence-based summarization
- **Date-Range Filtering**: Historical trend analysis with customizable time periods
- **MCP Protocol Support**: Model Context Protocol for advanced AI agent communication

## 🏗️ System Architecture

![Deep Research Agent Workflow](assets/system-architecture.png)

### AI Agent Ecosystem

The system employs multiple specialized AI agents working in coordination:

1. **🧠 GGUFModel Agent**: Local LLM processing with Mistral-7B
2. **📱 RapidAI Agent**: Social media data aggregation
3. **🔗 URL Generator Agent**: Intelligent search URL creation
4. **🕷️ Web Scrapper Agent**: Content extraction and parsing
5. **📊 Categorization Agent**: Source-based content organization
6. **✅ Fact-Checking Agent**: Evidence-based summarization

### Data Flow Pipeline

```
User Query → API Gateway → Agent Orchestrator → Parallel Processing
    ↓
[RapidAI] + [URL Gen] + [Web Scraper] + [LLM Analysis]
    ↓
Content Categorization → Enhanced Generation → Fact Verification
    ↓
Final Summary → React Frontend
```

## 📁 Project Structure

```
deep-research-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # Command-line interface
│   │   ├── simple_api.py        # Flask API server
│   │   ├── model.py             # GGUF model integration
│   │   ├── scrapper.py          # Web scraping engine
│   │   ├── social_media.py      # RapidAI social media agent
│   │   ├── url_generator.py     # Dynamic URL generation
│   │   └── mcp_client.py        # MCP protocol client
│   ├── backend_api.py           # Legacy API
│   └── mcp_server.py           # MCP protocol server
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── QueryInput.js    # Search interface
│   │   │   └── ResultDisplay.js # Results presentation
│   │   ├── styles/
│   │   └── App.js              # Main React application
│   ├── package.json
│   └── public/
├── models/                     # LLM models (not in repo)
├── docs/
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Git**
- **4GB+ RAM** (for local LLM)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/deep-research-agent.git
cd deep-research-agent
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install flask flask-cors requests beautifulsoup4 python-dotenv
```

#### Download Required Models & Tools

**⚠️ Important**: Due to GitHub file size limits, you must download these separately:

##### A. Download Mistral-7B GGUF Model

```bash
# Create models directory
mkdir -p models

# Download Mistral-7B-Instruct (Q4_K_S variant - ~4.1GB)
cd models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_S.gguf

# Alternative: Use Hugging Face CLI
pip install huggingface_hub
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_S.gguf --local-dir ./
```

##### B. Download & Build llama.cpp

```bash
# Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Windows (with Visual Studio)
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

# macOS/Linux
make -j4
```

#### Update Configuration Paths

Edit the paths in your Python files:

```python
# In model.py, simple_api.py, mcp_server.py, main.py
MODEL_PATH = "path/to/your/mistral-7b-instruct-v0.2.Q4_K_S.gguf"
LLAMA_CLI_BIN = "path/to/your/llama.cpp/build/bin/Release/llama-cli.exe"  # Windows
# LLAMA_CLI_BIN = "path/to/your/llama.cpp/llama-cli"  # macOS/Linux
```

#### Get RapidAI API Key

1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to social media APIs
3. Update `RAPIDAI_API_KEY` in your Python files

### 3. Frontend Setup

```bash
cd ../frontend
npm install

# Add proxy to package.json
# "proxy": "http://localhost:5000"
```

## 🚀 Running the Application

### Method 1: Flask API (Recommended)

```bash
# Terminal 1: Backend API
cd backend/app
python simple_api.py

# Terminal 2: Frontend
cd frontend
npm start
```

Access the application at `http://localhost:3000`

### Method 2: MCP Protocol

```bash
# Terminal 1: MCP Server
cd backend
python mcp_server.py

# Terminal 2: Flask API with MCP
python backend_api.py

# Terminal 3: Frontend
cd frontend
npm start
```

### Method 3: Command Line

```bash
cd backend/app
python main.py
```

## 📖 API Documentation

### Research Endpoint

**POST** `/api/research`

```json
{
  "query": "trending AI topics",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "max_sources": 5
}
```

**Response:**
```json
{
  "success": true,
  "final_summary": "### Wikipedia Summary\n...\n### Reddit Summary\n...",
  "query": "trending AI topics",
  "sources_processed": 4,
  "urls_scraped": 5
}
```

### Health Check

**GET** `/api/health`

```json
{
  "status": "healthy",
  "message": "Deep Research Agent API is running",
  "version": "1.0.0"
}
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in the backend directory:

```env
MODEL_PATH=/path/to/mistral-7b-instruct-v0.2.Q4_K_S.gguf
LLAMA_CLI_PATH=/path/to/llama.cpp/llama-cli
RAPIDAI_API_KEY=your_rapidai_key_here
FLASK_ENV=development
FLASK_PORT=5000
```

### Model Configuration

Adjust model parameters in `model.py`:

```python
model = GGUFModel(
    model_path=MODEL_PATH,
    llama_cli_path=LLAMA_CLI_BIN,
    threads=6,           # CPU threads
    max_tokens=256,      # Max tokens per chunk
    temperature=0.7,     # Creativity level
    timeout=600,         # Generation timeout
)
```

## 🧪 Testing

```bash
# Test API endpoint
curl -X POST http://localhost:5000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query":"AI trends 2024","max_sources":3}'

# Test health endpoint
curl http://localhost:5000/api/health
```

## 🎯 Usage Examples

### Basic Research Query

```python
# Command line
python main.py
# Enter: "machine learning trends 2024"

# API call
import requests
response = requests.post('http://localhost:5000/api/research', 
    json={"query": "machine learning trends 2024"})
```

### Historical Analysis

```python
# With date range
payload = {
    "query": "cryptocurrency market",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "max_sources": 10
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Add unit tests for new features
- Update documentation for API changes

## 🐛 Troubleshooting

### Common Issues

**1. Model Loading Errors**
```bash
# Check model path and file existence
ls -la path/to/model.gguf
# Ensure sufficient RAM (4GB+ required)
```

**2. llama.cpp Build Issues**
```bash
# Install build tools
# Windows: Visual Studio Build Tools
# macOS: Xcode Command Line Tools
# Linux: build-essential cmake
```

**3. API Connection Errors**
```bash
# Check if ports are available
netstat -an | grep 5000
netstat -an | grep 3000
```

**4. Frontend 404 Errors**
```json
// Ensure package.json has proxy
"proxy": "http://localhost:5000"
```

## 📊 Performance Notes

- **Model**: Mistral-7B requires ~4GB RAM
- **Concurrent Users**: Single instance supports 1-5 users
- **Response Time**: 10-30 seconds per query
- **Scaling**: Use multiple model instances for production

## 🔐 Security Considerations

- Store API keys in environment variables
- Use HTTPS in production
- Implement rate limiting
- Sanitize user inputs
- Regular dependency updates

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mistral AI** - For the Mistral-7B model
- **llama.cpp** - For GGUF model inference
- **RapidAPI** - For social media data access
- **React Community** - For the frontend framework
- **Flask** - For the web framework

## 🏗️ System Architecture

![Deep-Research-AI](assets/sysetm desigm for deep research.png)


## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/deep-research-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/deep-research-agent/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/deep-research-agent/wiki)

---

**⭐ Star this repository if you find it helpful!**

Built with ❤️ by [Your Name](https://github.com/yourusername)
