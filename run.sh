#!/bin/bash

echo "🚀 Starting APITestGen..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
mkdir -p api-docs logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env file with your configuration before running."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ APITestGen is running!"
    echo ""
    echo "📊 Services:"
    echo "   - Backend API: http://localhost:8000"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Database: localhost:5432"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🛑 To stop services, run: docker-compose down"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi 