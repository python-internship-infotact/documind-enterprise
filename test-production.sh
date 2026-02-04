#!/bin/bash

# DocuMind Enterprise - Production Configuration Test Script
# This script helps test the production build locally before deployment

echo "🚀 DocuMind Enterprise - Production Test"
echo "========================================"

# Check if required files exist
echo "📋 Checking deployment configuration files..."

files=("render.yaml" "vercel.json" "frontend/.env.production" "DEPLOYMENT.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Test backend requirements
echo ""
echo "🐍 Testing backend requirements..."
if [ -f "ai_service/requirements.txt" ]; then
    echo "✅ Backend requirements.txt exists"
    echo "📦 Dependencies:"
    grep -E "^(fastapi|uvicorn|gunicorn|langchain)" ai_service/requirements.txt | head -5
else
    echo "❌ Backend requirements.txt missing"
    exit 1
fi

# Test frontend configuration
echo ""
echo "⚛️  Testing frontend configuration..."
if [ -f "frontend/package.json" ]; then
    echo "✅ Frontend package.json exists"
    cd frontend
    if npm list --depth=0 > /dev/null 2>&1; then
        echo "✅ Frontend dependencies are installed"
    else
        echo "⚠️  Frontend dependencies not installed. Run: cd frontend && npm install"
    fi
    cd ..
else
    echo "❌ Frontend package.json missing"
    exit 1
fi

# Test production build
echo ""
echo "🏗️  Testing production build..."
cd frontend
if npm run build:prod > /dev/null 2>&1; then
    echo "✅ Production build successful"
    if [ -d "dist" ]; then
        echo "✅ Build output directory exists"
        echo "📊 Build size:"
        du -sh dist/
    fi
else
    echo "❌ Production build failed"
    echo "Run 'cd frontend && npm run build:prod' to see detailed errors"
    exit 1
fi
cd ..

echo ""
echo "🎉 All production configuration tests passed!"
echo ""
echo "Next steps:"
echo "1. Deploy backend to Render using render.yaml"
echo "2. Deploy frontend to Vercel using vercel.json"
echo "3. Update API URLs if needed"
echo "4. Test the deployed application"
echo ""
echo "See DEPLOYMENT.md for detailed instructions."