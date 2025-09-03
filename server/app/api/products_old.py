from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from server.app.database import get_db
from server.app.models.product import Product
from server.app.models.price import Price
from server.app.schemas.product import (
    ProductResponse, ProductListResponse, ProductSearch, ProductStats,
    ProductCreate, ProductUpdate, ProductWithPrices
)
from server.app.api.auth import get_current_active_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=ProductListResponse)
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    store_id: Optional[int] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination."""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    if store_id:
        query = query.filter(Product.store_id == store_id)
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return ProductListResponse(
        products=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )

@router.get("/search", response_model=ProductListResponse)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search products by name and keywords."""
    query = db.query(Product).filter(
        Product.is_active == True,
        Product.name.ilike(f"%{q}%")
    )
    
    if category:
        query = query.filter(Product.category == category)
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return ProductListResponse(
        products=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )

@router.get("/{product_id}", response_model=ProductWithPrices)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product by ID with price information."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Add current prices
    current_prices = db.query(Price).filter(
        Price.product_id == product_id
    ).order_by(Price.scraped_at.desc()).limit(10).all()
    
    return ProductWithPrices(
        **product.__dict__,
        prices=[p.__dict__ for p in current_prices]
    )

@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of available product categories."""
    categories = db.query(Product.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]

@router.get("/{product_id}/stats", response_model=ProductStats)
async def get_product_stats(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product statistics including price trends."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate basic stats from prices
    prices = db.query(Price).filter(Price.product_id == product_id).all()
    
    if not prices:
        return ProductStats(
            id=product.id,
            name=product.name,
            category=product.category
        )
    
    price_values = [p.price for p in prices]
    avg_price = sum(price_values) / len(price_values)
    min_price = min(price_values)
    max_price = max(price_values)
    
    # Calculate availability rate
    available_count = len([p for p in prices if p.is_available])
    availability_rate = (available_count / len(prices)) * 100
    
    # Get unique stores
    store_count = len(set(p.store_id for p in prices))
    
    return ProductStats(
        id=product.id,
        name=product.name,
        category=product.category,
        avg_price=avg_price,
        min_price=min_price,
        max_price=max_price,
        availability_rate=availability_rate,
        store_count=store_count
    )

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_create: ProductCreate,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)."""
    try:
        product = Product(**product_create.dict())
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product created: {product.name} by user {current_user.email}")
        return product
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        for field, value in product_update.dict(exclude_unset=True).items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product updated: {product.name} by user {current_user.email}")
        return product
        
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Soft delete
        product.is_active = False
        db.commit()
        
        logger.info(f"Product deleted: {product.name} by user {current_user.email}")
        return {"message": "Product deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )