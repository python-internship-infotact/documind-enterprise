# DocuMind Enterprise

Enterprise Document Intelligence and RAG (Retrieval-Augmented Generation) System

## Overview

DocuMind Enterprise is a comprehensive document processing and intelligent retrieval system designed for enterprise environments. It provides advanced PDF processing, intelligent chunking, vector storage, and semantic search capabilities.

## Features

- **Advanced PDF Processing**: Extract text with accurate page metadata and structure preservation
- **Intelligent Chunking**: Context-aware document chunking with parent-child relationships
- **Vector Storage**: Pinecone integration for scalable semantic search
- **Enterprise API**: FastAPI-based REST API with comprehensive endpoints
- **Metadata Preservation**: Complete audit trail with source citations

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Pinecone Account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/python-internship-infotact/documind-enterprise.git
cd documind-enterprise
```

2. Install dependencies:
```bash
cd ai_service
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp ../.env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /documents/upload` - Upload and process PDF
- `GET /search` - Search documents
- `DELETE /documents/{filename}` - Delete document
- `GET /stats` - Pipeline statistics

## Architecture

```
ai_service/
├── app/
│   ├── config.py          # Configuration management
│   ├── models.py          # Pydantic models
│   ├── ingestion/         # Document processing
│   │   ├── pdf_processor.py
│   │   ├── chunking.py
│   │   └── pipeline.py
│   └── database/          # Vector DB operations
│       └── pinecone_client.py
├── main.py               # FastAPI application
└── requirements.txt      # Dependencies
```

## Week 1 Implementation Status

✅ **Day 1**: Environment setup and dependencies  
✅ **Day 2**: PDF processing with metadata extraction  
✅ **Day 3**: Intelligent chunking strategy  
✅ **Day 4**: Pinecone integration and embeddings  
✅ **Day 5**: Pipeline integration and API endpoints  

## Testing

Run tests with:
```bash
pytest test_main.py -v
```

## Next Steps

- Week 2: RAG retrieval engine with hallucination guardrails
- Week 3: Streaming responses and production features
- Week 4: Optimization and deployment

## License

MIT License