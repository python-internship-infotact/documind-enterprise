#!/bin/bash

# DocuMind Enterprise Production Deployment Script

set -e

echo "🚀 DocuMind Enterprise - Production Deployment"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before continuing."
    echo "   Required: GROQ_API_KEY, PINECONE_API_KEY"
    read -p "Press Enter after updating .env file..."
fi

# Validate required environment variables
source .env
if [ -z "$GROQ_API_KEY" ] || [ -z "$PINECONE_API_KEY" ]; then
    echo "❌ Missing required API keys in .env file"
    echo "   Please set GROQ_API_KEY and PINECONE_API_KEY"
    exit 1
fi

echo "✅ Environment variables validated"

# Create necessary directories
mkdir -p logs ssl

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yaml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yaml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service is not responding"
    docker-compose -f docker-compose.prod.yaml logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
    docker-compose -f docker-compose.prod.yaml logs frontend
    exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo "=============================================="
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Management Commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yaml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yaml down"
echo "  Restart: docker-compose -f docker-compose.prod.yaml restart"
echo ""
echo "🔧 To run tests:"
echo "  python tests/end_to_end_test.py"
echo "  python tests/stress_test.py"