# DocuMind Enterprise

A production-ready Retrieval-Augmented Generation (RAG) system for enterprise document intelligence with real-time streaming chat capabilities.

## Features

- **Document Processing**: Upload and process PDF documents with intelligent chunking
- **Semantic Search**: Vector-based document retrieval using Pinecone
- **AI Chat Interface**: Real-time streaming responses with Groq LLM integration
- **Enhanced Citations**: Rich metadata with relevance scores and source information
- **Rate Limiting**: Token bucket algorithm for API abuse prevention
- **Production Ready**: Complete Docker containerization with health monitoring

## Architecture

The system consists of two main components:

1. **Backend (Python/FastAPI)**: Document processing, vector storage, and AI chat API
2. **Frontend (React/TypeScript)**: Modern web interface with real-time streaming

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API Keys for:
  - Groq (for AI chat)
  - Pinecone (for vector storage)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd documind-enterprise
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Deploy with Docker:
```bash
chmod +x deploy.sh
./deploy.sh
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

### Development Setup

#### Backend
```bash
cd ai_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn ai_service.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

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

## API Endpoints

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

## Rate Limiting

The system implements sophisticated rate limiting:
- **Chat endpoints**: 30 requests per minute
- **Upload endpoints**: 5 requests per minute
- **General endpoints**: 60 requests per minute

Rate limits use a token bucket algorithm with automatic recovery.

## Project Structure

```
documind-enterprise/
├── ai_service/                 # Backend FastAPI application
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
├── docker-compose.prod.yaml  # Production Docker setup
├── Dockerfile.backend        # Backend Docker image
├── Dockerfile.frontend       # Frontend Docker image
├── deploy.sh                # Deployment script
├── nginx-proxy.conf         # Nginx proxy configuration
└── .env.example            # Environment variables template
```

## Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **Rate Limiting**: Prevents API abuse and ensures fair usage
- **Container Security**: Non-root users and minimal attack surface
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Health Monitoring**: Automated health checks for all services

## Performance

- **Time to First Token (TTFT)**: < 500ms
- **Streaming Speed**: 30-50 tokens per second
- **Concurrent Users**: Supports 50+ simultaneous requests
- **Document Processing**: Handles multiple PDF uploads concurrently

## License

This project is licensed under the MIT License.