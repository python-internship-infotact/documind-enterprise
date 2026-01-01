# DocuMind Enterprise Frontend

Modern React frontend for the DocuMind Enterprise RAG system with real-time streaming chat interface.

## Features

- **Real-time Streaming Chat**: Live token-by-token response streaming
- **Document Upload**: Drag-and-drop PDF document upload
- **Safety Indicators**: Visual feedback for query scope and safety
- **Performance Metrics**: Real-time TTFT and response time tracking
- **Modern UI**: Built with React, TypeScript, and Tailwind CSS

## Quick Start

### Prerequisites

- Node.js 18+ 
- DocuMind Enterprise backend running on `http://localhost:8001`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Backend Integration

The frontend connects to the DocuMind Enterprise backend API:

- **Chat Streaming**: `POST /chat/stream` - Real-time chat with SSE
- **Document Upload**: `POST /documents/upload` - PDF document processing
- **Health Check**: `GET /health` - Backend connection status

### Configuration

Update the API base URL in `src/hooks/useConversation.ts`:

```typescript
const API_BASE = 'http://localhost:8001'; // Your backend URL
```

## Architecture

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Radix UI** components
- **Framer Motion** for animations
- **React Query** for API state management

## Components

- `ContextPanel` - Document management and upload
- `QuestionComposer` - Chat input with query quality indicators
- `AIResponse` - Streaming response display with citations
- `MetricsFooter` - Real-time performance metrics

## Development

```bash
npm run dev     # Start development server
npm run build   # Build for production
npm run lint    # Run ESLint
npm run preview # Preview production build
```
