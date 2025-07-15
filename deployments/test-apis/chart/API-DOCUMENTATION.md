# API Documentation for Test APIs

## 📋 Overview

This document provides comprehensive API documentation for the test APIs with inter-service communication capabilities.

## 🔗 API Endpoints

### 1. User Management API (Port 8001)

**Base URL:** `http://localhost:8001`

#### Authentication Endpoints

##### `POST /auth/register`
Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string", 
  "full_name": "string",
  "password": "string"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-07-13T09:49:13",
  "updated_at": null
}
```

##### `POST /auth/login`
Login user and return access token.

**Query Parameters:**
- `username` (string, required): Username
- `password` (string, required): Password

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### User Management Endpoints

##### `GET /users/me`
Get current user information (requires authentication).

**Headers:**
- `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-07-13T09:49:13",
  "updated_at": null
}
```

##### `GET /users`
Get list of users with optional filtering.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)
- `active_only` (boolean, optional): Filter active users only (default: true)

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": true,
    "created_at": "2025-07-13T09:49:13",
    "updated_at": null
  }
]
```

##### `GET /users/{user_id}`
Get user by ID.

**Path Parameters:**
- `user_id` (integer, required): User ID

**Response (200):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-07-13T09:49:13",
  "updated_at": null
}
```

##### `PUT /users/{user_id}`
Update user information (requires authentication).

**Path Parameters:**
- `user_id` (integer, required): User ID

**Request Body:**
```json
{
  "full_name": "string",
  "email": "string",
  "is_active": boolean
}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "is_active": true,
  "created_at": "2025-07-13T09:49:13",
  "updated_at": "2025-07-13T10:00:00"
}
```

##### `DELETE /users/{user_id}`
Delete user (soft delete, requires authentication).

**Path Parameters:**
- `user_id` (integer, required): User ID

**Response (200):**
```json
{
  "message": "User deleted successfully"
}
```

##### `POST /users/{user_id}/activate`
Activate a user account (requires authentication).

**Path Parameters:**
- `user_id` (integer, required): User ID

**Response (200):**
```json
{
  "message": "User activated successfully"
}
```

### 2. E-commerce API (Port 8002)

**Base URL:** `http://localhost:8002`

#### Category Endpoints

##### `POST /categories`
Create a new product category.

**Request Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic devices and gadgets",
  "created_at": "2025-07-13T09:49:23.995818",
  "updated_at": "2025-07-13T09:49:23.995839"
}
```

##### `GET /categories`
Get list of categories.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and gadgets",
    "created_at": "2025-07-13T09:49:23.995818",
    "updated_at": "2025-07-13T09:49:23.995839"
  }
]
```

##### `GET /categories/{category_id}`
Get category by ID.

**Path Parameters:**
- `category_id` (integer, required): Category ID

**Response (200):**
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic devices and gadgets",
  "created_at": "2025-07-13T09:49:23.995818",
  "updated_at": "2025-07-13T09:49:23.995839"
}
```

##### `PUT /categories/{category_id}`
Update category.

**Path Parameters:**
- `category_id` (integer, required): Category ID

**Request Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated Electronics",
  "description": "Updated description",
  "created_at": "2025-07-13T09:49:23.995818",
  "updated_at": "2025-07-13T10:00:00"
}
```

##### `DELETE /categories/{category_id}`
Delete category.

**Path Parameters:**
- `category_id` (integer, required): Category ID

**Response (200):**
```json
{
  "message": "Category deleted successfully"
}
```

#### Product Endpoints

##### `POST /products`
Create a new product.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "price": 0.0,
  "stock_quantity": 0,
  "category_id": 0,
  "sku": "string"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Smartphone",
  "description": "Latest smartphone model",
  "price": 599.99,
  "stock_quantity": 10,
  "sku": "PHONE001",
  "category_id": 1,
  "created_at": "2025-07-13T09:49:29.209699",
  "updated_at": "2025-07-13T09:49:29.209706"
}
```

##### `GET /products`
Get list of products with optional filtering.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)
- `category_id` (integer, optional): Filter by category ID
- `min_price` (number, optional): Minimum price filter
- `max_price` (number, optional): Maximum price filter
- `in_stock` (boolean, optional): Filter by stock availability

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Smartphone",
    "description": "Latest smartphone model",
    "price": 599.99,
    "stock_quantity": 10,
    "sku": "PHONE001",
    "category_id": 1,
    "created_at": "2025-07-13T09:49:29.209699",
    "updated_at": "2025-07-13T09:49:29.209706"
  }
]
```

##### `GET /products/{product_id}`
Get product by ID.

**Path Parameters:**
- `product_id` (integer, required): Product ID

**Response (200):**
```json
{
  "id": 1,
  "name": "Smartphone",
  "description": "Latest smartphone model",
  "price": 599.99,
  "stock_quantity": 10,
  "sku": "PHONE001",
  "category_id": 1,
  "created_at": "2025-07-13T09:49:29.209699",
  "updated_at": "2025-07-13T09:49:29.209706"
}
```

##### `PUT /products/{product_id}`
Update product.

**Path Parameters:**
- `product_id` (integer, required): Product ID

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "price": 0.0,
  "stock_quantity": 0,
  "category_id": 0
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated Smartphone",
  "description": "Updated description",
  "price": 699.99,
  "stock_quantity": 15,
  "sku": "PHONE001",
  "category_id": 1,
  "created_at": "2025-07-13T09:49:29.209699",
  "updated_at": "2025-07-13T10:00:00"
}
```

##### `DELETE /products/{product_id}`
Delete product.

**Path Parameters:**
- `product_id` (integer, required): Product ID

**Response (200):**
```json
{
  "message": "Product deleted successfully"
}
```

##### `POST /products/{product_id}/stock`
Update product stock quantity.

**Path Parameters:**
- `product_id` (integer, required): Product ID

**Query Parameters:**
- `quantity` (integer, required): New stock quantity

**Response (200):**
```json
{
  "message": "Stock updated to 20"
}
```

#### Order Endpoints

##### `POST /orders`
Create a new order (with optional user validation).

**Request Body:**
```json
{
  "customer_name": "string",
  "customer_email": "string",
  "user_id": 0,
  "items": [
    {
      "product_id": 0,
      "quantity": 0
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "customer_name": "Test User",
  "customer_email": "test@example.com",
  "user_id": 1,
  "total_amount": 1199.98,
  "status": "pending",
  "created_at": "2025-07-13T09:49:34.705869",
  "updated_at": "2025-07-13T09:49:34.705872"
}
```

**Note:** If `user_id` is provided, the API will validate the user with the User API (inter-service call).

##### `GET /orders`
Get list of orders with optional filtering.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)
- `status` (string, optional): Filter by order status
- `user_id` (integer, optional): Filter by user ID

**Response (200):**
```json
[
  {
    "id": 1,
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "user_id": 1,
    "total_amount": 1199.98,
    "status": "pending",
    "created_at": "2025-07-13T09:49:34.705869",
    "updated_at": "2025-07-13T09:49:34.705872"
  }
]
```

##### `GET /orders/{order_id}`
Get order by ID.

**Path Parameters:**
- `order_id` (integer, required): Order ID

**Response (200):**
```json
{
  "id": 1,
  "customer_name": "Test User",
  "customer_email": "test@example.com",
  "user_id": 1,
  "total_amount": 1199.98,
  "status": "pending",
  "created_at": "2025-07-13T09:49:34.705869",
  "updated_at": "2025-07-13T09:49:34.705872"
}
```

##### `PUT /orders/{order_id}/status`
Update order status.

**Path Parameters:**
- `order_id` (integer, required): Order ID

**Query Parameters:**
- `status` (string, required): New order status (pending, confirmed, shipped, delivered, cancelled)

**Response (200):**
```json
{
  "message": "Order status updated to confirmed"
}
```

##### `GET /orders/{order_id}/items`
Get order items.

**Path Parameters:**
- `order_id` (integer, required): Order ID

**Response (200):**
```json
[
  {
    "id": 1,
    "order_id": 1,
    "product_id": 1,
    "quantity": 2,
    "unit_price": 599.99
  }
]
```

##### `GET /orders/{order_id}/user-info`
Get user information for an order (inter-service call).

**Path Parameters:**
- `order_id` (integer, required): Order ID

**Response (200) - Order with user:**
```json
{
  "order_id": 1,
  "user_id": 1,
  "user_info": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": true,
    "created_at": "2025-07-13T09:49:13",
    "updated_at": null
  }
}
```

**Response (200) - Order without user:**
```json
{
  "message": "Order has no associated user",
  "user_info": null
}
```

## 🔗 Inter-Service Communication

### User Validation
When creating an order with `user_id`, the E-commerce API calls the User API to validate the user:

```bash
# This will validate user_id=1 with User API
curl -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "user_id": 1,
    "items": [{"product_id": 1, "quantity": 2}]
  }'
```

### User Information Retrieval
Get user details for an order:

```bash
# This will fetch user info from User API
curl "http://localhost:8002/orders/1/user-info"
```

### Error Handling
If user validation fails:

```json
{
  "detail": "Invalid or inactive user"
}
```

## 📊 Data Models

### User Models
- `UserCreate`: User registration data
- `UserResponse`: User information response
- `UserUpdate`: User update data
- `Token`: Authentication token

### E-commerce Models
- `CategoryCreate`: Category creation data
- `CategoryResponse`: Category information response
- `ProductCreate`: Product creation data
- `ProductResponse`: Product information response
- `ProductUpdate`: Product update data
- `OrderCreate`: Order creation data
- `OrderResponse`: Order information response
- `OrderItemCreate`: Order item creation data
- `OrderItemResponse`: Order item information response
- `OrderStatus`: Order status enum (pending, confirmed, shipped, delivered, cancelled)

## 🚀 Getting Started

### 1. Start the APIs
```bash
cd test-apis
./quick-start.sh
```

### 2. Test Inter-Service Communication
```bash
./test-inter-service.sh
```

### 3. Import to APITestGen
- User API: `test-apis/user-api-openapi.json`
- E-commerce API: `test-apis/ecommerce-api-openapi.json`

## 🔍 Health Checks

### User API Health
```bash
curl http://localhost:8001/health
```

### E-commerce API Health
```bash
curl http://localhost:8002/health
```

## 📚 API Documentation URLs

- User API Docs: http://localhost:8001/docs
- E-commerce API Docs: http://localhost:8002/docs
- User API OpenAPI: http://localhost:8001/openapi.json
- E-commerce API OpenAPI: http://localhost:8002/openapi.json

## 🎯 Testing Scenarios

1. **User Registration and Authentication**
2. **Product and Category Management**
3. **Order Creation with User Validation**
4. **Inter-Service User Information Retrieval**
5. **Error Handling for Invalid Users**
6. **Guest Order Creation (No User Validation)**
7. **Order Status Management**
8. **Stock Management**

This comprehensive API documentation covers all endpoints and demonstrates the inter-service communication capabilities of the test APIs. 