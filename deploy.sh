#!/bin/bash

# DocuMind Enterprise Production Deployment Script
#
# This script automates the deployment of DocuMind Enterprise using Docker Compose.
# It handles environment validation, Docker image building, and service orchestration
# for a complete production-ready deployment.
#
# Features:
# - Environment file validation
# - Docker and Docker Compose availability checks
# - Automated image building and deployment
# - Health check monitoring
# - Service status reporting
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Requirements:
# - Docker and Docker Compose installed
# - .env file with required API keys
# - Sufficient system resources for all services

set -e  # Exit on any error

echo "DocuMind Enterprise - Production Deployment"
echo "=============================================="

# Check if Docker is installed and available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed and available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists, create from template if not
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys before continuing."
    echo "   Required: GROQ_API_KEY, PINECONE_API_KEY"
    read -p "Press Enter after updating .env file..."
fi

# Validate required environment variables
source .env
if [ -z "$GROQ_API_KEY" ] || [ -z "$PINECONE_API_KEY" ]; then
    echo "Error: Missing required API keys in .env file"
    echo "   Please set GROQ_API_KEY and PINECONE_API_KEY"
    exit 1
fi

echo "Environment variables validated"

# Create necessary directories for logs and SSL certificates
mkdir -p logs ssl

# Build Docker images for all services
echo "Building Docker images..."
docker-compose -f docker-compose.prod.yaml build

# Start all services in detached mode
echo "Starting services..."
docker-compose -f docker-compose.prod.yaml up -d

# Wait for services to initialize and become healthy
echo "Waiting for services to be ready..."
sleep 30

# Perform health checks on all services
echo "Checking service health..."

# Check backend service health endpoint
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend service is healthy"
else
    echo "Error: Backend service is not responding"
    docker-compose -f docker-compose.prod.yaml logs backend
    exit 1
fi

# Check frontend service availability
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "Frontend service is healthy"
else
    echo "Error: Frontend service is not responding"
    docker-compose -f docker-compose.prod.yaml logs frontend
    exit 1
fi

# Display deployment success information
echo ""
echo "Deployment successful!"
echo "=============================================="
echo "Frontend: http://localhost:8080"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Management Commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yaml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yaml down"
echo "  Restart: docker-compose -f docker-compose.prod.yaml restart"
echo ""
echo "The system is now ready for use!"