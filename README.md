# DocuMind Enterprise

A production-ready Retrieval-Augmented Generation (RAG) system for enterprise document intelligence with real-time streaming chat capabilities.

## 🚀 Features

- **📄 Document Processing**: Upload and process PDF documents with intelligent chunking
- **🔍 Semantic Search**: Vector-based document retrieval using Pinecone
- **💬 AI Chat Interface**: Real-time streaming responses with Groq LLM integration
- **📚 Enhanced Citations**: Rich metadata with relevance scores and source information
- **🛡️ Rate Limiting**: Token bucket algorithm for API abuse prevention
- **🐳 Production Ready**: Complete Docker containerization with health monitoring
- **🔒 Safety Features**: Hallucination prevention and query scope validation
- **⚡ High Performance**: Sub-500ms response times with 30-50 tokens/second streaming

## 🏗️ Architecture

The system consists of two main components:

1. **Backend (Python/FastAPI)**: Document processing, vector storage, and AI chat API
2. **Frontend (React/TypeScript)**: Modern web interface with real-time streaming

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- API Keys for:
  - [Groq](https://console.groq.com/) (for AI chat)
  - [Pinecone](https://www.pinecone.io/) (for vector storage)

### Local Development

1. **Clone the repository:**

```bash
git clone <repository-url>
cd documind-enterprise
```

2. **Set up environment variables:**

```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Backend Setup:**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r ai_service/requirements.txt

# Start backend server
python -m uvicorn ai_service.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Frontend Setup (in a new terminal):**

```bash
cd frontend
npm install
npm run dev
```

The application will be available at:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 🌐 Production Deployment

For production deployment to Render (backend) and Vercel (frontend):

1. **Test production configuration:**
   ```bash
   # On Windows:
   test-production.bat
   
   # On macOS/Linux:
   ./test-production.sh
   ```

2. **Follow the deployment guide:**
   See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:
   - **Backend**: Render (with `render.yaml`)
   - **Frontend**: Vercel (with `vercel.json`)

### 🐳 Docker Deployment (Local Production)

For local production testing with Docker:

```bash
chmod +x deploy.sh
./deploy.sh
```

This will start all services with:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Groq Configuration (for AI chat)
GROQ_API_KEY=your_groq_api_key_here

# Pinecone Configuration (for vector storage)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=documind-hf

# Embedding Configuration
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50
```

## 📡 API Endpoints

### Document Management

- `POST /documents/upload` - Upload and process PDF documents
- `DELETE /documents/{filename}` - Delete specific documents
- `GET /documents/search` - Search documents using semantic similarity

### Chat Interface

- `POST /chat/stream` - Real-time streaming chat with enhanced citations
- `POST /chat` - Traditional chat responses
- `GET /chat/history` - Retrieve conversation history
- `DELETE /chat/history/{session_id}` - Clear conversation history

### System Management

- `GET /health` - System health check
- `GET /stats` - System statistics
- `GET /rate-limit-status` - Current rate limit status
- `POST /api/clear-memory` - Clear all conversation memory
- `POST /api/clear-rate-limits` - Reset rate limiter state

## 🛡️ Rate Limiting

The system implements sophisticated rate limiting:

- **Chat endpoints**: 30 requests per minute
- **Upload endpoints**: 5 requests per minute
- **General endpoints**: 60 requests per minute

Rate limits use a token bucket algorithm with automatic recovery.

## 🗂️ Project Structure

```
documind-enterprise/
├── ai_service/                 # Main FastAPI application
│   ├── app/
│   │   ├── config.py          # Configuration settings
│   │   ├── models.py          # Pydantic models
│   │   ├── database/          # Vector database integration
│   │   ├── ingestion/         # Document processing pipeline
│   │   ├── rag/              # RAG engine and prompts
│   │   └── middleware/        # Rate limiting middleware
│   ├── main.py               # FastAPI application entry point
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/           # Custom React hooks
│   │   └── lib/             # Utility functions
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
├── backend/                  # Alternative backend implementation
├── docker-compose.prod.yaml  # Production Docker setup
├── Dockerfile.backend        # Backend Docker image
├── Dockerfile.frontend       # Frontend Docker image
├── deploy.sh                # Deployment script
├── clear_documents.py       # System reset utility
└── .env.example            # Environment variables template
```

## 🔒 Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **Rate Limiting**: Prevents API abuse and ensures fair usage
- **Hallucination Prevention**: AI safety guards prevent false information
- **Query Scope Validation**: Ensures responses stay within document boundaries
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Container Security**: Non-root users and minimal attack surface

## ⚡ Performance

- **Time to First Token (TTFT)**: < 500ms
- **Streaming Speed**: 30-50 tokens per second
- **Concurrent Users**: Supports 50+ simultaneous requests
- **Document Processing**: Handles multiple PDF uploads concurrently

## 🧹 System Maintenance

### Clear All Data

To completely reset the system (clear all documents and conversation history):

```bash
python clear_documents.py
```

This will:
- Clear all documents from Pinecone vector database
- Clear conversation memory and session history
- Reset rate limiter state
- Provide detailed progress reporting

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd ai_service
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd ai_service
flake8 app/

# Frontend linting
cd frontend
npm run lint
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the [API documentation](http://localhost:8000/docs) when running locally
- Review the comprehensive system documentation in `DEVELOPMENT.md`
