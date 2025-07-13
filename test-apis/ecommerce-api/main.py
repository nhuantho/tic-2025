from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid
import httpx

from models import (
    Product, ProductCreate, ProductUpdate, ProductResponse,
    Category, CategoryCreate, CategoryResponse,
    Order, OrderCreate, OrderResponse, OrderStatus,
    OrderItem, OrderItemCreate, OrderItemResponse
)
from database import get_db, engine, Base
from config import settings

app = FastAPI(
    title="E-commerce API",
    description="A simple e-commerce system for testing APITestGen",
    version="1.0.0",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    print(f"🔗 User API URL: {settings.USER_API_URL}")

# User API Service
class UserAPIService:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user information from User API"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Error calling User API: {e}")
            return None
    
    async def validate_user(self, user_id: int) -> bool:
        """Validate if user exists and is active"""
        user = await self.get_user(user_id)
        return user is not None and user.get("is_active", False)

user_service = UserAPIService(settings.USER_API_URL)

@app.get("/")
async def root():
    return {"message": "E-commerce API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Category endpoints
@app.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new product category"""
    db_category = Category(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of categories"""
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int, 
    category_update: CategoryCreate, 
    db: Session = Depends(get_db)
):
    """Update category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_category.name = category_update.name
    db_category.description = category_update.description
    
    db.commit()
    db.refresh(db_category)
    return db_category

@app.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Product endpoints
@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Verify category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        sku=product.sku or str(uuid.uuid4())
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    db: Session = Depends(get_db)
):
    """Get list of products with optional filtering"""
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        else:
            query = query.filter(Product.stock_quantity == 0)
    
    products = query.offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """Update product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_update.name is not None:
        db_product.name = product_update.name
    if product_update.description is not None:
        db_product.description = product_update.description
    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.stock_quantity is not None:
        db_product.stock_quantity = product_update.stock_quantity
    if product_update.category_id is not None:
        # Verify category exists
        category = db.query(Category).filter(Category.id == product_update.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        db_product.category_id = product_update.category_id
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

@app.post("/products/{product_id}/stock")
async def update_stock(
    product_id: int, 
    quantity: int,
    db: Session = Depends(get_db)
):
    """Update product stock quantity"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.stock_quantity = quantity
    db.commit()
    return {"message": f"Stock updated to {quantity}"}

# Order endpoints
@app.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Validate user if user_id is provided
    if order.user_id:
        user_valid = await user_service.validate_user(order.user_id)
        if not user_valid:
            raise HTTPException(status_code=400, detail="Invalid or inactive user")
    
    # Calculate total and validate products
    total_amount = 0
    order_items = []
    
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        total_amount += product.price * item.quantity
        order_items.append((product, item.quantity))
    
    # Create order
    db_order = Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        user_id=order.user_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items and update stock
    for product, quantity in order_items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price
        )
        db.add(order_item)
        
        # Update stock
        product.stock_quantity -= quantity
    
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get list of orders with optional filtering"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int, 
    status: OrderStatus,
    db: Session = Depends(get_db)
):
    """Update order status"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = status
    db.commit()
    return {"message": f"Order status updated to {status}"}

@app.get("/orders/{order_id}/items", response_model=List[OrderItemResponse])
async def get_order_items(order_id: int, db: Session = Depends(get_db)):
    """Get order items"""
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    if not order_items:
        raise HTTPException(status_code=404, detail="Order not found or has no items")
    return order_items

# New endpoint to test inter-service communication
@app.get("/orders/{order_id}/user-info")
async def get_order_user_info(order_id: int, db: Session = Depends(get_db)):
    """Get user information for an order (demonstrates inter-service call)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not order.user_id:
        return {"message": "Order has no associated user", "user_info": None}
    
    # Call User API to get user information
    user_info = await user_service.get_user(order.user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found in User API")
    
    return {
        "order_id": order_id,
        "user_id": order.user_id,
        "user_info": user_info
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True) 