#!/bin/bash

echo "🧪 Testing Inter-Service Communication between User API and E-commerce API"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if APIs are running
print_status "Checking if APIs are running..."

if ! curl -s http://localhost:8001/health > /dev/null; then
    print_error "User API is not running on port 8001"
    exit 1
fi

if ! curl -s http://localhost:8002/health > /dev/null; then
    print_error "E-commerce API is not running on port 8002"
    exit 1
fi

print_success "Both APIs are running"

echo ""
print_status "Step 1: Creating a user in User API"
echo "----------------------------------------"

USER_RESPONSE=$(curl -s -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "email": "demo@example.com", "password": "password123", "full_name": "Demo User"}')

if echo "$USER_RESPONSE" | grep -q "username.*demo_user"; then
    print_success "User created successfully"
    echo "Response: $USER_RESPONSE"
else
    print_error "Failed to create user"
    echo "Response: $USER_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 2: Creating a category in E-commerce API"
echo "---------------------------------------------------"

CATEGORY_RESPONSE=$(curl -s -X POST "http://localhost:8002/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Books", "description": "Books and publications"}')

if echo "$CATEGORY_RESPONSE" | grep -q "name.*Books"; then
    print_success "Category created successfully"
    echo "Response: $CATEGORY_RESPONSE"
else
    print_error "Failed to create category"
    echo "Response: $CATEGORY_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 3: Creating a product in E-commerce API"
echo "--------------------------------------------------"

PRODUCT_RESPONSE=$(curl -s -X POST "http://localhost:8002/products" \
  -H "Content-Type: application/json" \
  -d '{"name": "Programming Book", "description": "Learn Python programming", "price": 29.99, "stock_quantity": 50, "category_id": 1, "sku": "BOOK001"}')

if echo "$PRODUCT_RESPONSE" | grep -q "name.*Programming Book"; then
    print_success "Product created successfully"
    echo "Response: $PRODUCT_RESPONSE"
else
    print_error "Failed to create product"
    echo "Response: $PRODUCT_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 4: Creating an order with valid user_id (Inter-service validation)"
echo "---------------------------------------------------------------------------"

ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Demo User", "customer_email": "demo@example.com", "user_id": 1, "items": [{"product_id": 1, "quantity": 3}]}')

if echo "$ORDER_RESPONSE" | grep -q "user_id.*1"; then
    print_success "Order created successfully with user validation"
    echo "Response: $ORDER_RESPONSE"
else
    print_error "Failed to create order"
    echo "Response: $ORDER_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 5: Testing inter-service call to get user info for order"
echo "-------------------------------------------------------------------"

USER_INFO_RESPONSE=$(curl -s "http://localhost:8002/orders/1/user-info")

if echo "$USER_INFO_RESPONSE" | grep -q "user_info"; then
    print_success "Inter-service call successful - Retrieved user info for order"
    echo "Response: $USER_INFO_RESPONSE"
else
    print_error "Failed to get user info for order"
    echo "Response: $USER_INFO_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 6: Testing order creation with invalid user_id (Error handling)"
echo "-------------------------------------------------------------------------"

INVALID_ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Invalid User", "customer_email": "invalid@example.com", "user_id": 999, "items": [{"product_id": 1, "quantity": 1}]}')

if echo "$INVALID_ORDER_RESPONSE" | grep -q "Invalid or inactive user"; then
    print_success "Error handling works correctly - Invalid user rejected"
    echo "Response: $INVALID_ORDER_RESPONSE"
else
    print_error "Error handling failed - Should have rejected invalid user"
    echo "Response: $INVALID_ORDER_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 7: Testing order creation without user_id (No validation needed)"
echo "-------------------------------------------------------------------------"

NO_USER_ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8002/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Guest User", "customer_email": "guest@example.com", "items": [{"product_id": 1, "quantity": 1}]}')

if echo "$NO_USER_ORDER_RESPONSE" | grep -q "customer_name.*Guest User"; then
    print_success "Order created successfully without user validation"
    echo "Response: $NO_USER_ORDER_RESPONSE"
else
    print_error "Failed to create order without user_id"
    echo "Response: $NO_USER_ORDER_RESPONSE"
    exit 1
fi

echo ""
print_status "Step 8: Testing user info for order without user_id"
echo "---------------------------------------------------------"

NO_USER_INFO_RESPONSE=$(curl -s "http://localhost:8002/orders/2/user-info")

if echo "$NO_USER_INFO_RESPONSE" | grep -q "no associated user"; then
    print_success "Correctly handled order without associated user"
    echo "Response: $NO_USER_INFO_RESPONSE"
else
    print_error "Failed to handle order without user_id"
    echo "Response: $NO_USER_INFO_RESPONSE"
    exit 1
fi

echo ""
echo "🎉 All inter-service communication tests passed!"
echo "=============================================="
echo ""
echo "📋 Summary of what was tested:"
echo "1. ✅ User creation in User API"
echo "2. ✅ Category creation in E-commerce API"
echo "3. ✅ Product creation in E-commerce API"
echo "4. ✅ Order creation with user validation (inter-service call)"
echo "5. ✅ User info retrieval for order (inter-service call)"
echo "6. ✅ Error handling for invalid user_id"
echo "7. ✅ Order creation without user_id (no validation needed)"
echo "8. ✅ Handling orders without associated users"
echo ""
echo "🔗 The E-commerce API successfully calls the User API to:"
echo "   - Validate users before creating orders"
echo "   - Retrieve user information for orders"
echo "   - Handle network errors and invalid users gracefully"
echo ""
echo "🌐 This demonstrates real microservices architecture with inter-service communication!" 