from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from server.app.database import get_db
from server.app.models.product import Product
from server.app.models.price import Price
from server.app.models.store import Store
from server.app.api.auth import get_current_active_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    search: Optional[str] = Query(None, description="Search in product names"),
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination."""
    try:
        query = db.query(Product).filter(Product.is_active == True)
        
        # Apply filters
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))
        if store_id:
            # Filter by products available in specific store
            query = query.join(Price).filter(Price.store_id == store_id)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        # Format response
        formatted_products = []
        for product in products:
            # Get latest price info if needed
            latest_price = None
            if store_id:
                latest_price = db.query(Price).filter(
                    Price.product_id == product.id,
                    Price.store_id == store_id
                ).order_by(Price.scraped_at.desc()).first()
            
            formatted_product = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "brand": getattr(product, 'brand', None),
                "unit": getattr(product, 'unit', None),
                "is_active": product.is_active,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }
            
            if latest_price:
                formatted_product["latest_price"] = {
                    "price": latest_price.price,
                    "is_available": latest_price.is_available,
                    "scraped_at": latest_price.scraped_at.isoformat()
                }
            
            formatted_products.append(formatted_product)
        
        return {
            "products": formatted_products,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_next": skip + limit < total
        }
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search products by name and keywords."""
    try:
        query = db.query(Product).filter(
            Product.is_active == True,
            Product.name.ilike(f"%{q}%")
        )
        
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        # Format products with search relevance
        formatted_products = []
        for product in products:
            # Calculate simple relevance score
            name_lower = product.name.lower()
            query_lower = q.lower()
            relevance = 0
            
            if query_lower in name_lower:
                if name_lower.startswith(query_lower):
                    relevance = 100  # Exact start match
                elif name_lower == query_lower:
                    relevance = 200  # Exact match
                else:
                    relevance = 50  # Contains match
            
            formatted_products.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "brand": getattr(product, 'brand', None),
                "unit": getattr(product, 'unit', None),
                "is_active": product.is_active,
                "relevance": relevance,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            })
        
        # Sort by relevance
        formatted_products.sort(key=lambda x: x['relevance'], reverse=True)
        
        return {
            "products": formatted_products,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_next": skip + limit < total,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search products"
        )


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    include_prices: bool = Query(True, description="Include recent prices"),
    price_limit: int = Query(10, ge=1, le=50, description="Number of recent prices to include"),
    db: Session = Depends(get_db)
):
    """Get product by ID with optional price information."""
    try:
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Format basic product info
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": getattr(product, 'brand', None),
            "unit": getattr(product, 'unit', None),
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        }
        
        if include_prices:
            # Get recent prices
            recent_prices = db.query(Price).filter(
                Price.product_id == product_id
            ).order_by(Price.scraped_at.desc()).limit(price_limit).all()
            
            formatted_prices = []
            for price in recent_prices:
                formatted_prices.append({
                    "id": price.id,
                    "store_id": price.store_id,
                    "price": price.price,
                    "is_available": price.is_available,
                    "scraped_at": price.scraped_at.isoformat(),
                    "store_name": price.store.name if price.store else None
                })
            
            product_data["prices"] = formatted_prices
            
            # Add price statistics
            if recent_prices:
                price_values = [p.price for p in recent_prices]
                available_prices = [p.price for p in recent_prices if p.is_available]
                
                product_data["price_stats"] = {
                    "min_price": min(price_values),
                    "max_price": max(price_values),
                    "avg_price": round(sum(price_values) / len(price_values), 2),
                    "available_stores": len([p for p in recent_prices if p.is_available]),
                    "total_stores": len(set(p.store_id for p in recent_prices))
                }
        
        return product_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product"
        )


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of available product categories."""
    try:
        categories = db.query(Product.category).filter(
            Product.category.isnot(None),
            Product.is_active == True
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        category_list.sort()
        
        return {
            "categories": category_list,
            "total": len(category_list)
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.get("/{product_id}/stats")
async def get_product_stats(
    product_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    db: Session = Depends(get_db)
):
    """Get product statistics including price trends."""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get prices for the specified period
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        prices = db.query(Price).filter(
            Price.product_id == product_id,
            Price.scraped_at >= start_date
        ).all()
        
        if not prices:
            return {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "total_prices": 0,
                "avg_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "availability_rate": 0.0,
                "store_count": 0,
                "date_range_days": days
            }
        
        # Calculate statistics
        price_values = [p.price for p in prices]
        available_count = len([p for p in prices if p.is_available])
        unique_stores = len(set(p.store_id for p in prices))
        
        # Calculate price trend
        sorted_prices = sorted(prices, key=lambda x: x.scraped_at)
        if len(sorted_prices) > 1:
            first_avg = sum(p.price for p in sorted_prices[:len(sorted_prices)//4]) / (len(sorted_prices)//4)
            last_avg = sum(p.price for p in sorted_prices[-len(sorted_prices)//4:]) / (len(sorted_prices)//4)
            price_trend = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
        else:
            price_trend = 0
        
        return {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "total_prices": len(prices),
            "avg_price": round(sum(price_values) / len(price_values), 2),
            "min_price": round(min(price_values), 2),
            "max_price": round(max(price_values), 2),
            "availability_rate": round((available_count / len(prices)) * 100, 2),
            "store_count": unique_stores,
            "price_trend_percent": round(price_trend, 2),
            "date_range_days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product stats for {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product statistics"
        )


# Admin only endpoints
@router.post("/")
async def create_product(
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    unit: Optional[str] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)."""
    try:
        # Check if product already exists
        existing = db.query(Product).filter(Product.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this name already exists"
            )
        
        product_data = {
            "name": name,
            "description": description,
            "category": category,
            "is_active": True
        }
        
        # Add optional fields if they exist in the model
        if hasattr(Product, 'brand'):
            product_data["brand"] = brand
        if hasattr(Product, 'unit'):
            product_data["unit"] = unit
        
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product created: {product.name} by user {current_user.email}")
        
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": getattr(product, 'brand', None),
            "unit": getattr(product, 'unit', None),
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat() if product.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    unit: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update product (admin only)."""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update fields that are provided
        if name is not None:
            # Check if name is already taken by another product
            existing = db.query(Product).filter(
                Product.name == name,
                Product.id != product_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this name already exists"
                )
            product.name = name
        
        if description is not None:
            product.description = description
        if category is not None:
            product.category = category
        if is_active is not None:
            product.is_active = is_active
        
        # Update optional fields if they exist
        if brand is not None and hasattr(product, 'brand'):
            product.brand = brand
        if unit is not None and hasattr(product, 'unit'):
            product.unit = unit
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product updated: {product.name} by user {current_user.email}")
        
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": getattr(product, 'brand', None),
            "unit": getattr(product, 'unit', None),
            "is_active": product.is_active,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        }
        
    except HTTPException:
        raise
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
    hard_delete: bool = Query(False, description="Permanently delete instead of soft delete"),
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete product (admin only)."""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        if hard_delete:
            # Hard delete - remove from database
            db.delete(product)
            message = f"Product permanently deleted: {product.name}"
        else:
            # Soft delete - mark as inactive
            product.is_active = False
            message = f"Product deactivated: {product.name}"
        
        db.commit()
        
        logger.info(f"{message} by user {current_user.email}")
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )