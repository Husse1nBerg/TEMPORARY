from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from server.app.database import get_db
from server.app.models.store import Store
from server.app.models.product import Product
from server.app.models.price import Price
from server.app.api.auth import get_current_active_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_stores(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search store names"),
    include_stats: bool = Query(False, description="Include store statistics"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all stores with filtering and pagination."""
    try:
        query = db.query(Store)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Store.is_active == is_active)
        if search:
            query = query.filter(Store.name.ilike(f"%{search}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        stores = query.offset(skip).limit(limit).all()
        
        # Format response
        formatted_stores = []
        for store in stores:
            store_data = {
                "id": store.id,
                "name": store.name,
                "description": getattr(store, 'description', None),
                "website_url": getattr(store, 'website_url', None),
                "logo_url": getattr(store, 'logo_url', None),
                "is_active": store.is_active,
                "scraper_enabled": getattr(store, 'scraper_enabled', True),
                "created_at": store.created_at.isoformat() if store.created_at else None,
                "updated_at": store.updated_at.isoformat() if store.updated_at else None
            }
            
            if include_stats:
                # Get basic statistics for this store
                total_products = db.query(Price.product_id).filter(
                    Price.store_id == store.id
                ).distinct().count()
                
                latest_scrape = db.query(Price.scraped_at).filter(
                    Price.store_id == store.id
                ).order_by(Price.scraped_at.desc()).first()
                
                available_products = db.query(Price).filter(
                    Price.store_id == store.id,
                    Price.is_available == True
                ).count() if total_products > 0 else 0
                
                store_data["stats"] = {
                    "total_products": total_products,
                    "available_products": available_products,
                    "availability_rate": round((available_products / total_products) * 100, 2) if total_products > 0 else 0,
                    "last_scraped": latest_scrape[0].isoformat() if latest_scrape else None
                }
            
            formatted_stores.append(store_data)
        
        return {
            "stores": formatted_stores,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_next": skip + limit < total
        }
        
    except Exception as e:
        logger.error(f"Error fetching stores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stores"
        )


@router.get("/{store_id}")
async def get_store(
    store_id: int,
    include_recent_prices: bool = Query(False, description="Include recent price updates"),
    price_limit: int = Query(20, ge=1, le=100, description="Number of recent prices to include"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get store by ID with optional recent prices."""
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        # Basic store information
        store_data = {
            "id": store.id,
            "name": store.name,
            "description": getattr(store, 'description', None),
            "website_url": getattr(store, 'website_url', None),
            "logo_url": getattr(store, 'logo_url', None),
            "is_active": store.is_active,
            "scraper_enabled": getattr(store, 'scraper_enabled', True),
            "created_at": store.created_at.isoformat() if store.created_at else None,
            "updated_at": store.updated_at.isoformat() if store.updated_at else None
        }
        
        # Add statistics
        total_products = db.query(Price.product_id).filter(
            Price.store_id == store_id
        ).distinct().count()
        
        available_products = db.query(Price).filter(
            Price.store_id == store_id,
            Price.is_available == True
        ).count()
        
        latest_scrape = db.query(Price.scraped_at).filter(
            Price.store_id == store_id
        ).order_by(Price.scraped_at.desc()).first()
        
        store_data["stats"] = {
            "total_products": total_products,
            "available_products": available_products,
            "availability_rate": round((available_products / total_products) * 100, 2) if total_products > 0 else 0,
            "last_scraped": latest_scrape[0].isoformat() if latest_scrape else None
        }
        
        if include_recent_prices:
            # Get recent price updates
            recent_prices = db.query(Price).filter(
                Price.store_id == store_id
            ).order_by(Price.scraped_at.desc()).limit(price_limit).all()
            
            formatted_prices = []
            for price in recent_prices:
                formatted_prices.append({
                    "id": price.id,
                    "product_id": price.product_id,
                    "product_name": price.product.name if price.product else None,
                    "price": price.price,
                    "is_available": price.is_available,
                    "scraped_at": price.scraped_at.isoformat()
                })
            
            store_data["recent_prices"] = formatted_prices
        
        return store_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching store {store_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch store"
        )


@router.get("/{store_id}/products")
async def get_store_products(
    store_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by product category"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get products available in a specific store with their latest prices."""
    try:
        # Verify store exists
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        # Build query for products with prices in this store
        query = db.query(Price).filter(Price.store_id == store_id).join(Product)
        
        # Apply filters
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if is_available is not None:
            query = query.filter(Price.is_available == is_available)
        if min_price is not None:
            query = query.filter(Price.price >= min_price)
        if max_price is not None:
            query = query.filter(Price.price <= max_price)
        
        # Get latest price for each product
        from sqlalchemy import func
        latest_prices_subquery = db.query(
            Price.product_id,
            func.max(Price.scraped_at).label('latest_scraped_at')
        ).filter(Price.store_id == store_id).group_by(Price.product_id).subquery()
        
        # Join with the subquery to get only latest prices
        query = query.join(
            latest_prices_subquery,
            (Price.product_id == latest_prices_subquery.c.product_id) &
            (Price.scraped_at == latest_prices_subquery.c.latest_scraped_at)
        )
        
        # Get total count and apply pagination
        total = query.count()
        prices = query.order_by(Product.name.asc()).offset(skip).limit(limit).all()
        
        # Format response
        products = []
        for price in prices:
            products.append({
                "product_id": price.product_id,
                "product_name": price.product.name if price.product else "Unknown Product",
                "product_category": price.product.category if price.product else None,
                "price": price.price,
                "is_available": price.is_available,
                "last_updated": price.scraped_at.isoformat()
            })
        
        return {
            "store_id": store_id,
            "store_name": store.name,
            "products": products,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_next": skip + limit < total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching products for store {store_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch store products"
        )


@router.get("/{store_id}/stats")
async def get_store_stats(
    store_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get detailed statistics for a store."""
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        # Date range for statistics
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get prices within date range
        prices = db.query(Price).filter(
            Price.store_id == store_id,
            Price.scraped_at >= start_date
        ).all()
        
        if not prices:
            return {
                "store_id": store_id,
                "store_name": store.name,
                "date_range_days": days,
                "total_price_points": 0,
                "unique_products": 0,
                "avg_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "availability_rate": 0.0,
                "price_updates_per_day": 0.0
            }
        
        # Calculate statistics
        price_values = [p.price for p in prices]
        available_count = len([p for p in prices if p.is_available])
        unique_products = len(set(p.product_id for p in prices))
        
        # Calculate categories breakdown
        category_counts = {}
        for price in prices:
            if price.product and price.product.category:
                cat = price.product.category
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "store_id": store_id,
            "store_name": store.name,
            "date_range_days": days,
            "total_price_points": len(prices),
            "unique_products": unique_products,
            "avg_price": round(sum(price_values) / len(price_values), 2),
            "min_price": round(min(price_values), 2),
            "max_price": round(max(price_values), 2),
            "availability_rate": round((available_count / len(prices)) * 100, 2),
            "price_updates_per_day": round(len(prices) / days, 2),
            "category_breakdown": category_counts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching store stats for {store_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch store statistics"
        )


# Admin only endpoints
@router.post("/")
async def create_store(
    name: str,
    description: Optional[str] = None,
    website_url: Optional[str] = None,
    logo_url: Optional[str] = None,
    scraper_enabled: bool = True,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new store (admin only)."""
    try:
        # Check if store already exists
        existing = db.query(Store).filter(Store.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store with this name already exists"
            )
        
        store_data = {
            "name": name,
            "is_active": True
        }
        
        # Add optional fields if they exist in the model
        if hasattr(Store, 'description'):
            store_data["description"] = description
        if hasattr(Store, 'website_url'):
            store_data["website_url"] = website_url
        if hasattr(Store, 'logo_url'):
            store_data["logo_url"] = logo_url
        if hasattr(Store, 'scraper_enabled'):
            store_data["scraper_enabled"] = scraper_enabled
        
        store = Store(**store_data)
        db.add(store)
        db.commit()
        db.refresh(store)
        
        logger.info(f"Store created: {store.name} by user {current_user.email}")
        
        return {
            "id": store.id,
            "name": store.name,
            "description": getattr(store, 'description', None),
            "website_url": getattr(store, 'website_url', None),
            "logo_url": getattr(store, 'logo_url', None),
            "is_active": store.is_active,
            "scraper_enabled": getattr(store, 'scraper_enabled', True),
            "created_at": store.created_at.isoformat() if store.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating store: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create store"
        )


@router.put("/{store_id}")
async def update_store(
    store_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    website_url: Optional[str] = None,
    logo_url: Optional[str] = None,
    is_active: Optional[bool] = None,
    scraper_enabled: Optional[bool] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update store (admin only)."""
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        # Update fields that are provided
        if name is not None:
            # Check if name is already taken by another store
            existing = db.query(Store).filter(
                Store.name == name,
                Store.id != store_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Store with this name already exists"
                )
            store.name = name
        
        if is_active is not None:
            store.is_active = is_active
        
        # Update optional fields if they exist
        if description is not None and hasattr(store, 'description'):
            store.description = description
        if website_url is not None and hasattr(store, 'website_url'):
            store.website_url = website_url
        if logo_url is not None and hasattr(store, 'logo_url'):
            store.logo_url = logo_url
        if scraper_enabled is not None and hasattr(store, 'scraper_enabled'):
            store.scraper_enabled = scraper_enabled
        
        db.commit()
        db.refresh(store)
        
        logger.info(f"Store updated: {store.name} by user {current_user.email}")
        
        return {
            "id": store.id,
            "name": store.name,
            "description": getattr(store, 'description', None),
            "website_url": getattr(store, 'website_url', None),
            "logo_url": getattr(store, 'logo_url', None),
            "is_active": store.is_active,
            "scraper_enabled": getattr(store, 'scraper_enabled', True),
            "updated_at": store.updated_at.isoformat() if store.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating store: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update store"
        )


@router.delete("/{store_id}")
async def delete_store(
    store_id: int,
    hard_delete: bool = Query(False, description="Permanently delete instead of soft delete"),
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete store (admin only)."""
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        if hard_delete:
            # Check if store has associated prices
            price_count = db.query(Price).filter(Price.store_id == store_id).count()
            if price_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete store with {price_count} associated prices. Use soft delete instead."
                )
            
            # Hard delete - remove from database
            db.delete(store)
            message = f"Store permanently deleted: {store.name}"
        else:
            # Soft delete - mark as inactive
            store.is_active = False
            message = f"Store deactivated: {store.name}"
        
        db.commit()
        
        logger.info(f"{message} by user {current_user.email}")
        return {"message": "Store deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting store: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete store"
        )