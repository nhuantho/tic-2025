#!/bin/bash

echo "🚀 Quick Start for Test APIs with Inter-Service Communication"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi
print_success "Docker is running"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down > /dev/null 2>&1
print_success "Existing containers stopped"

# Start the APIs
print_status "Starting test APIs..."
docker-compose up -d --build

# Wait for APIs to be ready
print_status "Waiting for APIs to be ready..."
sleep 15

# Check if APIs are running
print_status "Checking API status..."

if curl -s http://localhost:8001/health > /dev/null; then
    print_success "User Management API is running at http://localhost:8001"
else
    print_error "User Management API is not responding"
    exit 1
fi

if curl -s http://localhost:8002/health > /dev/null; then
    print_success "E-commerce API is running at http://localhost:8002"
else
    print_error "E-commerce API is not responding"
    exit 1
fi

# Create database tables
print_status "Creating database tables..."
docker exec test-apis-user-api-1 python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)" > /dev/null 2>&1
docker exec test-apis-ecommerce-api-1 python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)" > /dev/null 2>&1
print_success "Database tables created"

echo ""
echo "🎯 Test APIs are ready!"
echo "======================"
echo ""
echo "📋 Available APIs:"
echo "   • User Management API: http://localhost:8001"
echo "   • E-commerce API: http://localhost:8002"
echo ""
echo "📚 API Documentation:"
echo "   • User API Docs: http://localhost:8001/docs"
echo "   • E-commerce API Docs: http://localhost:8002/docs"
echo ""
echo "🧪 Test Inter-Service Communication:"
echo "   • Run: ./test-inter-service.sh"
echo ""
echo "📄 OpenAPI Specifications:"
echo "   • User API: test-apis/user-api-openapi.json"
echo "   • E-commerce API: test-apis/ecommerce-api-openapi.json"
echo ""
echo "🔗 Import these specifications into APITestGen at http://localhost:3000"
echo ""
echo "📝 To stop the APIs:"
echo "   • Run: docker-compose down"
echo ""
echo "🌐 Inter-Service Communication Features:"
echo "   • E-commerce API validates users with User API"
echo "   • E-commerce API retrieves user info from User API"
echo "   • Error handling for network failures"
echo "   • Support for guest orders (no user validation)"
echo ""
print_success "Ready to test! 🚀" 