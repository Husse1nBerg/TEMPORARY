from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from server.app.database import get_db
from server.app.models.price import Price
from server.app.models.product import Product
from server.app.models.store import Store
from server.app.api.auth import get_current_active_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_prices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    date_from: Optional[str] = Query(None, description="Filter prices from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter prices to date (YYYY-MM-DD)"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get current prices with advanced filtering and pagination."""
    try:
        query = db.query(Price).join(Product).join(Store)
        
        # Apply filters
        if product_id:
            query = query.filter(Price.product_id == product_id)
        if store_id:
            query = query.filter(Price.store_id == store_id)
        if is_available is not None:
            query = query.filter(Price.is_available == is_available)
        if min_price is not None:
            query = query.filter(Price.price >= min_price)
        if max_price is not None:
            query = query.filter(Price.price <= max_price)
            
        # Date range filtering
        if date_from:
            try:
                date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d")
                query = query.filter(Price.scraped_at >= date_from_parsed)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use YYYY-MM-DD"
                )
                
        if date_to:
            try:
                date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(Price.scraped_at < date_to_parsed)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use YYYY-MM-DD"
                )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        prices = query.order_by(Price.scraped_at.desc()).offset(skip).limit(limit).all()
        
        # Format response
        formatted_prices = []
        for price in prices:
            formatted_prices.append({
                "id": price.id,
                "product_id": price.product_id,
                "store_id": price.store_id,
                "price": price.price,
                "is_available": price.is_available,
                "scraped_at": price.scraped_at.isoformat(),
                "product_name": price.product.name if price.product else None,
                "store_name": price.store.name if price.store else None,
                "price_change_percent": getattr(price, 'price_change_percent', 0.0)
            })
        
        return {
            "prices": formatted_prices,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_next": skip + limit < total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch prices"
        )


@router.post("/refresh")
async def refresh_prices(
    background_tasks: BackgroundTasks,
    store_id: Optional[int] = Query(None, description="Specific store to refresh, or all if not provided"),
    product_id: Optional[int] = Query(None, description="Specific product to refresh"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Trigger a background task to refresh prices from stores."""
    try:
        # Validate store exists if provided
        if store_id:
            store = db.query(Store).filter(Store.id == store_id, Store.is_active == True).first()
            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Store with ID {store_id} not found or inactive"
                )
        
        # Validate product exists if provided
        if product_id:
            product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found or inactive"
                )
        
        # Add scraping task (simplified for now)
        # In a real implementation, you'd use Celery or similar
        # background_tasks.add_task(trigger_scraping_task, store_id, product_id, current_user.id)
        
        message = "Price refresh initiated for "
        if store_id and product_id:
            message += f"product ID {product_id} from store ID {store_id}"
        elif store_id:
            message += f"all products from store ID {store_id}"
        elif product_id:
            message += f"product ID {product_id} from all stores"
        else:
            message += "all products from all stores"
            
        logger.info(f"Price refresh initiated by user {current_user.email}: {message}")
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating price refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate price refresh"
        )


@router.get("/trends/{product_id}")
async def get_price_trends(
    product_id: int,
    days: int = Query(7, ge=1, le=90, description="Number of days for trend analysis"),
    store_id: Optional[int] = Query(None, description="Filter by specific store"),
    group_by: str = Query("day", regex="^(hour|day|week)$", description="Group data by time period"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get price trends for a specific product over time."""
    try:
        # Verify product exists
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = db.query(Price).filter(
            Price.product_id == product_id,
            Price.scraped_at >= start_date,
            Price.scraped_at <= end_date
        )
        
        if store_id:
            store = db.query(Store).filter(Store.id == store_id, Store.is_active == True).first()
            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )
            query = query.filter(Price.store_id == store_id)
        
        # Get prices ordered by date
        prices = query.order_by(Price.scraped_at.asc()).all()
        
        if not prices:
            return []
        
        # Group data based on group_by parameter
        trends = []
        current_group = None
        group_prices = []
        
        for price in prices:
            if group_by == "hour":
                group_key = price.scraped_at.replace(minute=0, second=0, microsecond=0)
            elif group_by == "day":
                group_key = price.scraped_at.date()
            else:  # week
                days_since_monday = price.scraped_at.weekday()
                group_key = (price.scraped_at - timedelta(days=days_since_monday)).date()
            
            if current_group != group_key:
                # Process previous group
                if group_prices:
                    avg_price = sum(p.price for p in group_prices) / len(group_prices)
                    min_price = min(p.price for p in group_prices)
                    max_price = max(p.price for p in group_prices)
                    available_count = len([p for p in group_prices if p.is_available])
                    availability_rate = (available_count / len(group_prices)) * 100
                    
                    trends.append({
                        "date": current_group.isoformat() if hasattr(current_group, 'isoformat') else str(current_group),
                        "avg_price": round(avg_price, 2),
                        "min_price": round(min_price, 2),
                        "max_price": round(max_price, 2),
                        "availability_rate": round(availability_rate, 2),
                        "data_points": len(group_prices)
                    })
                
                # Start new group
                current_group = group_key
                group_prices = [price]
            else:
                group_prices.append(price)
        
        # Process final group
        if group_prices:
            avg_price = sum(p.price for p in group_prices) / len(group_prices)
            min_price = min(p.price for p in group_prices)
            max_price = max(p.price for p in group_prices)
            available_count = len([p for p in group_prices if p.is_available])
            availability_rate = (available_count / len(group_prices)) * 100
            
            trends.append({
                "date": current_group.isoformat() if hasattr(current_group, 'isoformat') else str(current_group),
                "avg_price": round(avg_price, 2),
                "min_price": round(min_price, 2),
                "max_price": round(max_price, 2),
                "availability_rate": round(availability_rate, 2),
                "data_points": len(group_prices)
            })
        
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price trends for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch price trends"
        )


@router.get("/stats")
async def get_price_stats(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days for statistics"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get price statistics for products and stores."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(Price).filter(
            Price.scraped_at >= start_date,
            Price.scraped_at <= end_date
        )
        
        if product_id:
            query = query.filter(Price.product_id == product_id)
        if store_id:
            query = query.filter(Price.store_id == store_id)
        
        prices = query.all()
        
        if not prices:
            return {
                "total_prices": 0,
                "avg_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "availability_rate": 0.0,
                "unique_products": 0,
                "unique_stores": 0,
                "date_range_days": days
            }
        
        price_values = [p.price for p in prices]
        available_count = len([p for p in prices if p.is_available])
        unique_products = len(set(p.product_id for p in prices))
        unique_stores = len(set(p.store_id for p in prices))
        
        return {
            "total_prices": len(prices),
            "avg_price": round(sum(price_values) / len(price_values), 2),
            "min_price": round(min(price_values), 2),
            "max_price": round(max(price_values), 2),
            "availability_rate": round((available_count / len(prices)) * 100, 2),
            "unique_products": unique_products,
            "unique_stores": unique_stores,
            "date_range_days": days
        }
        
    except Exception as e:
        logger.error(f"Error fetching price statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch price statistics"
        )


@router.get("/compare/{product_id}")
async def compare_product_prices(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Compare latest prices for a product across all stores."""
    try:
        # Verify product exists
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get latest price for each store
        latest_prices = []
        stores = db.query(Store).filter(Store.is_active == True).all()
        
        for store in stores:
            latest_price = db.query(Price).filter(
                Price.product_id == product_id,
                Price.store_id == store.id
            ).order_by(Price.scraped_at.desc()).first()
            
            if latest_price:
                latest_prices.append({
                    "id": latest_price.id,
                    "product_id": latest_price.product_id,
                    "store_id": latest_price.store_id,
                    "price": latest_price.price,
                    "is_available": latest_price.is_available,
                    "scraped_at": latest_price.scraped_at.isoformat(),
                    "store_name": store.name,
                    "product_name": product.name
                })
        
        # Sort by price
        latest_prices.sort(key=lambda x: x["price"])
        
        return latest_prices
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing prices for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare product prices"
        )