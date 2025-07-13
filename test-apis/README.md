# Test APIs for APITestGen

This directory contains two test backend applications designed to be used with APITestGen for testing and demonstration purposes. The APIs demonstrate **inter-service communication** to simulate real-world microservices architecture.

## 🚀 Quick Start

1. **Start the test APIs:**
   ```bash
   ./start-test-apis.sh
   ```

2. **Access APITestGen:**
   - Open http://localhost:3000 in your browser
   - Import the OpenAPI specifications from the files below

3. **Stop the APIs:**
   ```bash
   docker-compose down
   ```

## 📋 Available Test APIs

### 1. User Management API
- **Port:** 8001
- **URL:** http://localhost:8001
- **Documentation:** http://localhost:8001/docs
- **OpenAPI Spec:** http://localhost:8001/openapi.json
- **Local Spec File:** `user-api-openapi.json`

**Features:**
- User registration and authentication
- JWT-based authentication
- User CRUD operations
- User activation/deactivation
- Role-based access control

**Endpoints:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /users/me` - Get current user (authenticated)
- `GET /users` - List users with filtering
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user (authenticated)
- `DELETE /users/{id}` - Delete user (authenticated)
- `POST /users/{id}/activate` - Activate user (authenticated)

### 2. E-commerce API
- **Port:** 8002
- **URL:** http://localhost:8002
- **Documentation:** http://localhost:8002/docs
- **OpenAPI Spec:** http://localhost:8002/openapi.json
- **Local Spec File:** `ecommerce-api-openapi.json`

**Features:**
- Product catalog management
- Category management
- Order processing with user validation
- Stock management
- Order status tracking
- **Inter-service communication** with User API

**Endpoints:**
- `GET /categories` - List categories
- `POST /categories` - Create category
- `GET /categories/{id}` - Get category by ID
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category
- `GET /products` - List products with filtering
- `POST /products` - Create product
- `GET /products/{id}` - Get product by ID
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product
- `POST /products/{id}/stock` - Update stock
- `GET /orders` - List orders with filtering
- `POST /orders` - Create order (validates user with User API)
- `GET /orders/{id}` - Get order by ID
- `PUT /orders/{id}/status` - Update order status
- `GET /orders/{id}/items` - Get order items
- `GET /orders/{id}/user-info` - Get user info for order (inter-service call)

## 🔗 Inter-Service Communication

The E-commerce API demonstrates **real inter-service communication** by calling the User API:

### How it works:
1. **User Validation:** When creating an order with `user_id`, E-commerce API calls User API to validate the user
2. **User Info Retrieval:** The `/orders/{id}/user-info` endpoint fetches user details from User API
3. **Error Handling:** Proper error handling for network failures and invalid users

### Example Flow:
```bash
# 1. Create a user in User API
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# 2. Create an order with user_id in E-commerce API
curl -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test User", "customer_email": "test@example.com", "user_id": 1, "items": [{"product_id": 1, "quantity": 2}]}'

# 3. Get user info for the order (inter-service call)
curl "http://localhost:8002/orders/1/user-info"
```

## 🧪 Testing Scenarios

### User Management API Test Cases

**Authentication Tests:**
- Register new user with valid data
- Register user with duplicate email/username
- Login with valid credentials
- Login with invalid credentials
- Access protected endpoints without token
- Access protected endpoints with invalid token

**User Management Tests:**
- Get user list with pagination
- Get user by valid ID
- Get user by invalid ID
- Update user with valid data
- Update user with invalid data
- Delete user (soft delete)
- Activate deactivated user

### E-commerce API Test Cases

**Category Tests:**
- Create category with valid data
- Create category with duplicate name
- Get category list with pagination
- Get category by valid ID
- Get category by invalid ID
- Update category
- Delete category

**Product Tests:**
- Create product with valid data
- Create product with invalid category
- Get product list with various filters
- Get product by valid ID
- Get product by invalid ID
- Update product
- Delete product
- Update stock quantity

**Order Tests:**
- Create order with valid items
- Create order with insufficient stock
- Create order with invalid product
- Create order with valid user_id (inter-service validation)
- Create order with invalid user_id (inter-service validation)
- Create order with inactive user (inter-service validation)
- Get order list with status filtering
- Get order by valid ID
- Get order by invalid ID
- Update order status
- Get order items
- Get order user info (inter-service call)

**Inter-Service Communication Tests:**
- Test order creation with valid user
- Test order creation with invalid user
- Test order creation with inactive user
- Test user info retrieval for order
- Test network failure scenarios
- Test timeout scenarios

## 📁 File Structure

```
test-apis/
├── user-api/                    # User Management API
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models & Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── config.py               # Settings configuration
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Docker configuration
├── ecommerce-api/              # E-commerce API
│   ├── main.py                 # FastAPI application with inter-service calls
│   ├── models.py               # SQLAlchemy models & Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── config.py               # Settings configuration
│   ├── requirements.txt        # Python dependencies (includes httpx)
│   └── Dockerfile              # Docker configuration
├── user-api-openapi.json       # OpenAPI specification for User API
├── ecommerce-api-openapi.json  # OpenAPI specification for E-commerce API
├── docker-compose.yml          # Docker Compose configuration with networking
├── start-test-apis.sh          # Startup script
└── README.md                   # This file
```

## 🔧 Manual Setup (Alternative)

If you prefer to run the APIs manually without Docker:

### User Management API
```bash
cd user-api
pip install -r requirements.txt
python main.py
```

### E-commerce API
```bash
cd ecommerce-api
pip install -r requirements.txt
# Set environment variable for User API URL
export USER_API_URL=http://localhost:8001
python main.py
```

## 🎯 Integration with APITestGen

1. **Start APITestGen:**
   ```bash
   ./run.sh
   ```

2. **Import API Specifications:**
   - Go to http://localhost:3000
   - Navigate to "API Specifications"
   - Import the OpenAPI JSON files:
     - `test-apis/user-api-openapi.json`
     - `test-apis/ecommerce-api-openapi.json`

3. **Generate Test Cases:**
   - Select an imported API specification
   - Click "Generate Test Cases"
   - Choose test types (normal, edge, missing fields)

4. **Execute Tests:**
   - Select test cases to run
   - Set base URL (e.g., http://localhost:8001 for User API, http://localhost:8002 for E-commerce API)
   - Execute tests and view results

5. **Test Inter-Service Communication:**
   - Import both API specifications
   - Create test cases for order creation with user validation
   - Test the `/orders/{id}/user-info` endpoint
   - Verify inter-service communication works correctly

## 🐛 Troubleshooting

**APIs not starting:**
- Check if Docker is running
- Ensure ports 8001 and 8002 are available
- Check Docker logs: `docker-compose logs`

**Inter-service communication failing:**
- Ensure both APIs are running
- Check network connectivity between containers
- Verify USER_API_URL environment variable
- Check User API health: `curl http://localhost:8001/health`

**Database issues:**
- Remove existing database files and restart
- Check database permissions
- Verify DATABASE_URL environment variable

## 🌟 Key Features for Testing

1. **Real Microservices Architecture:** Two independent services with their own databases
2. **Inter-Service Communication:** E-commerce API calls User API for validation
3. **Error Handling:** Proper handling of network failures and invalid data
4. **Authentication:** JWT-based authentication in User API
5. **Data Validation:** Cross-service data validation
6. **Network Resilience:** Timeout and connection error handling

This setup provides a realistic environment for testing API testing tools like APITestGen with actual inter-service communication scenarios. 