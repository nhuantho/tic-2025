# Changelog - Test APIs with Inter-Service Communication

## [2.0.0] - 2025-07-13

### 🎉 Major Features Added

#### Inter-Service Communication
- **User Validation**: E-commerce API now validates users with User API when creating orders
- **User Information Retrieval**: New endpoint `/orders/{id}/user-info` to fetch user details from User API
- **Error Handling**: Robust error handling for network failures and invalid users
- **Flexible Order Creation**: Support for both authenticated and guest orders

#### New Endpoints
- `GET /orders/{order_id}/user-info` - Get user information for an order (inter-service call)

#### Enhanced Order Model
- Added `user_id` field to Order model for linking with User API
- Updated OrderCreate schema to support optional user validation
- Added user_id filtering to order listing endpoint

### 🔧 Technical Improvements

#### Dependencies
- Added `httpx==0.25.2` to E-commerce API for HTTP client functionality

#### Configuration
- Added `USER_API_URL` environment variable for User API endpoint
- Updated Docker Compose with networking and service dependencies
- Added support for both localhost and Docker service discovery

#### Database
- Updated Order table schema to include user_id field
- Added startup events to ensure database tables are created properly

### 📚 Documentation

#### New Files Created
- `INTER-SERVICE-COMMUNICATION.md` - Detailed guide on inter-service communication
- `API-DOCUMENTATION.md` - Comprehensive API documentation
- `test-inter-service.sh` - Automated test script for inter-service communication
- `quick-start.sh` - Quick start script for the entire setup
- `CHANGELOG.md` - This changelog file

#### Updated Files
- `README.md` - Updated with inter-service communication information
- `docker-compose.yml` - Added networking and environment variables
- `ecommerce-api-openapi.json` - Regenerated with new endpoints
- `user-api-openapi.json` - Regenerated with latest schema

### 🧪 Testing

#### New Test Scenarios
1. **User Validation Tests**
   - Valid user order creation
   - Invalid user order creation
   - Inactive user order creation

2. **Inter-Service Communication Tests**
   - User info retrieval for orders
   - Network failure handling
   - Timeout scenarios

3. **Guest Order Tests**
   - Order creation without user validation
   - Handling orders without associated users

#### Automated Testing
- Created comprehensive test script (`test-inter-service.sh`)
- Added health checks and validation
- Color-coded test output for better readability

### 🚀 Deployment

#### Docker Improvements
- Added Docker networking for service communication
- Configured service dependencies
- Added health checks
- Improved container startup process

#### Quick Start
- One-command setup with `./quick-start.sh`
- Automatic database table creation
- Health check validation
- Clear status reporting

### 🔗 Architecture

#### Before (v1.0.0)
```
┌─────────────────┐    ┌─────────────────┐
│   User API      │    │  E-commerce API │
│   (Port 8001)   │    │   (Port 8002)   │
└─────────────────┘    └─────────────────┘
        │                       │
   SQLite DB              SQLite DB
   (users)                (products, orders)
```

#### After (v2.0.0)
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

### 🎯 Benefits for APITestGen

1. **Realistic Testing Environment**: Actual inter-service communication
2. **Complex Test Scenarios**: Network failures, timeouts, invalid data
3. **Microservices Patterns**: Service discovery, error handling, validation
4. **Production-Like Setup**: Docker networking, health checks, logging

### 📋 Migration Guide

#### From v1.0.0 to v2.0.0

1. **Stop existing containers**:
   ```bash
   docker-compose down
   ```

2. **Update to new version**:
   ```bash
   git pull origin main
   ```

3. **Start with new features**:
   ```bash
   ./quick-start.sh
   ```

4. **Test inter-service communication**:
   ```bash
   ./test-inter-service.sh
   ```

#### Breaking Changes
- Order model now includes `user_id` field
- New validation logic for orders with user_id
- Updated OpenAPI specifications

### 🔍 Monitoring

#### Health Checks
- User API: `http://localhost:8001/health`
- E-commerce API: `http://localhost:8002/health`

#### Logs
- User API: `docker-compose logs user-api`
- E-commerce API: `docker-compose logs ecommerce-api`

#### Network Connectivity
- Inter-service test: `docker exec test-apis-ecommerce-api-1 curl http://user-api:8001/health`

### 🎉 What's New for Users

1. **Import Updated Specifications**: Use the new OpenAPI JSON files
2. **Test Inter-Service Scenarios**: Create test cases for user validation
3. **Validate Error Handling**: Test network failures and invalid users
4. **Explore New Endpoints**: Test the `/orders/{id}/user-info` endpoint

### 🚀 Future Enhancements

- [ ] Add more inter-service communication patterns
- [ ] Implement service mesh for advanced routing
- [ ] Add metrics and monitoring
- [ ] Support for multiple user services
- [ ] Add message queue integration

---

**Version 2.0.0** represents a significant upgrade that transforms the test APIs from simple standalone services into a realistic microservices environment with actual inter-service communication capabilities. 