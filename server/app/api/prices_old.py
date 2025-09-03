from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from server.app.database import get_db
from server.app.models.price import Price
from server.app.models.product import Product
from server.app.models.store import Store
from server.app.schemas.price import PriceResponse, PriceTrend, PriceStats, PriceListResponse
from server.app.api.auth import get_current_active_user, get_admin_user
from server.app.tasks.scraping_tasks import trigger_scraping_task

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=PriceListResponse)
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
        
        return PriceListResponse(
            prices=[PriceResponse.from_orm(price) for price in prices],
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            has_next=skip + limit < total
        )
        
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
        
        # Add scraping task
        task_data = {
            "store_id": store_id,
            "product_id": product_id,
            "user_id": current_user.id
        }
        background_tasks.add_task(trigger_scraping_task, **task_data)
        
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

@router.get("/trends/{product_id}", response_model=List[PriceTrend])
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
                    
                    trends.append(PriceTrend(
                        date=current_group.isoformat() if hasattr(current_group, 'isoformat') else str(current_group),
                        avg_price=round(avg_price, 2),
                        min_price=round(min_price, 2),
                        max_price=round(max_price, 2),
                        availability_rate=round(availability_rate, 2),
                        data_points=len(group_prices)
                    ))
                
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
            
            trends.append(PriceTrend(
                date=current_group.isoformat() if hasattr(current_group, 'isoformat') else str(current_group),
                avg_price=round(avg_price, 2),
                min_price=round(min_price, 2),
                max_price=round(max_price, 2),
                availability_rate=round(availability_rate, 2),
                data_points=len(group_prices)
            ))
        
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price trends for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch price trends"
        )