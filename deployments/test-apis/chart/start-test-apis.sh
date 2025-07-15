#!/bin/bash

echo "🚀 Starting Test APIs for APITestGen..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start the test APIs
echo "📦 Building and starting User Management API..."
cd user-api
docker build -t user-api .
cd ..

echo "📦 Building and starting E-commerce API..."
cd ecommerce-api
docker build -t ecommerce-api .
cd ..

# Start both APIs using Docker Compose
echo "🔧 Starting both APIs with Docker Compose..."
docker-compose up -d

# Wait for APIs to be ready
echo "⏳ Waiting for APIs to be ready..."
sleep 10

# Check if APIs are running
echo "🔍 Checking API status..."

# Check User API
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ User Management API is running at http://localhost:8001"
    echo "   📚 API Docs: http://localhost:8001/docs"
    echo "   📄 OpenAPI Spec: http://localhost:8001/openapi.json"
else
    echo "❌ User Management API is not responding"
fi

# Check E-commerce API
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ E-commerce API is running at http://localhost:8002"
    echo "   📚 API Docs: http://localhost:8002/docs"
    echo "   📄 OpenAPI Spec: http://localhost:8002/openapi.json"
else
    echo "❌ E-commerce API is not responding"
fi

echo ""
echo "🎯 Test APIs are ready for APITestGen!"
echo ""
echo "📋 Available OpenAPI specifications:"
echo "   • User Management API: test-apis/user-api-openapi.json"
echo "   • E-commerce API: test-apis/ecommerce-api-openapi.json"
echo ""
echo "🔗 You can now import these specifications into APITestGen at http://localhost:3000"
echo ""
echo "📝 To stop the APIs, run: docker-compose down" 