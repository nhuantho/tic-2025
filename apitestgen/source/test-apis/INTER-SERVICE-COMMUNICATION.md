# Inter-Service Communication in Test APIs

## 🎯 Overview

The test APIs now demonstrate **real inter-service communication** between the User Management API and E-commerce API, simulating a realistic microservices architecture.

## 🔗 Architecture

```
┌─────────────────┐    HTTP Calls    ┌─────────────────┐
│   User API      │◄────────────────►│  E-commerce API │
│   (Port 8001)   │                  │   (Port 8002)   │
└─────────────────┘                  └─────────────────┘
        │                                     │
        │                                     │
   SQLite DB                              SQLite DB
   (users)                                (products, orders)
```

## 🚀 How It Works

### 1. User Validation
When creating an order with a `user_id`, the E-commerce API calls the User API to validate the user:

```python
# In E-commerce API
if order.user_id:
    user_valid = await user_service.validate_user(order.user_id)
    if not user_valid:
        raise HTTPException(status_code=400, detail="Invalid or inactive user")
```

### 2. User Information Retrieval
The E-commerce API can fetch user details from the User API:

```python
# GET /orders/{order_id}/user-info
user_info = await user_service.get_user(order.user_id)
```

### 3. Error Handling
Proper error handling for network failures and invalid users:

```python
try:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{self.base_url}/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        return None
except Exception as e:
    print(f"Error calling User API: {e}")
    return None
```

## 📋 API Endpoints

### User API (Port 8001)
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /users/{id}` - Get user by ID
- `GET /users` - List users
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### E-commerce API (Port 8002)
- `POST /categories` - Create category
- `GET /categories` - List categories
- `POST /products` - Create product
- `GET /products` - List products
- `POST /orders` - Create order (with user validation)
- `GET /orders` - List orders
- `GET /orders/{id}/user-info` - Get user info for order (inter-service call)

## 🧪 Testing Scenarios

### 1. Valid User Order Creation
```bash
# Create user
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Create order with user_id
curl -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test User", "customer_email": "test@example.com", "user_id": 1, "items": [{"product_id": 1, "quantity": 2}]}'
```

### 2. Invalid User Order Creation
```bash
# This should fail
curl -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Invalid User", "customer_email": "invalid@example.com", "user_id": 999, "items": [{"product_id": 1, "quantity": 1}]}'
# Response: {"detail": "Invalid or inactive user"}
```

### 3. Inter-Service User Info Retrieval
```bash
# Get user info for an order
curl "http://localhost:8002/orders/1/user-info"
# Response: {"order_id": 1, "user_id": 1, "user_info": {...}}
```

### 4. Order Without User (Guest Order)
```bash
# Create order without user_id (no validation needed)
curl -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Guest User", "customer_email": "guest@example.com", "items": [{"product_id": 1, "quantity": 1}]}'
```

## 🔧 Configuration

### Docker Environment
```yaml
# docker-compose.yml
services:
  user-api:
    ports:
      - "8001:8001"
    networks:
      - test-network

  ecommerce-api:
    environment:
      - USER_API_URL=http://user-api:8001  # Docker service name
    depends_on:
      - user-api
    networks:
      - test-network
```

### Local Environment
```bash
# Set environment variable for User API URL
export USER_API_URL=http://localhost:8001
```

## 🌟 Key Features

### 1. Real Microservices Architecture
- Two independent services with separate databases
- Network communication between services
- Service discovery using Docker networking

### 2. Robust Error Handling
- Network timeout handling (5 seconds)
- Invalid user rejection
- Graceful degradation when User API is unavailable

### 3. Flexible User Management
- Orders can be created with or without user validation
- Guest orders supported
- User information retrieval on demand

### 4. Production-Ready Patterns
- Async HTTP client with timeout
- Proper error logging
- Service health checks
- Docker networking

## 🚀 Running the Tests

### Quick Test
```bash
cd test-apis
./test-inter-service.sh
```

### Manual Testing
```bash
# Start the APIs
docker-compose up -d

# Create database tables
docker exec test-apis-user-api-1 python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
docker exec test-apis-ecommerce-api-1 python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Run the test script
./test-inter-service.sh
```

## 📊 Test Results

The test script validates:
- ✅ User creation in User API
- ✅ Category creation in E-commerce API
- ✅ Product creation in E-commerce API
- ✅ Order creation with user validation (inter-service call)
- ✅ User info retrieval for order (inter-service call)
- ✅ Error handling for invalid user_id
- ✅ Order creation without user_id (no validation needed)
- ✅ Handling orders without associated users

## 🎯 Benefits for APITestGen

This setup provides:

1. **Realistic Testing Environment**: Actual inter-service communication
2. **Complex Test Scenarios**: Network failures, timeouts, invalid data
3. **Microservices Patterns**: Service discovery, error handling, validation
4. **Production-Like Setup**: Docker networking, health checks, logging

## 🔍 Monitoring

### Health Checks
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Logs
```bash
docker-compose logs user-api
docker-compose logs ecommerce-api
```

### Network Connectivity
```bash
# Test inter-service communication
docker exec test-apis-ecommerce-api-1 curl http://user-api:8001/health
```

This inter-service communication setup provides a comprehensive testing environment for APITestGen to validate real-world microservices scenarios. 