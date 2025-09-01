"""
Prices API endpoints
Path: backend/app/api/prices.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.store import Store
from app.schemas.price import PriceResponse, PriceCreate, PriceTrend
from app.api.auth import get_current_user
from app.tasks.scraping_tasks import trigger_scraping

router = APIRouter()

@router.get("/", response_model=List[PriceResponse])
def get_prices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    category: Optional[str] = None,
    is_available: Optional[bool] = None
):
    """Get current prices with filters"""
    query = db.query(Price).join(Product).join(Store)
    
    if product_id:
        query = query.filter(Price.product_id == product_id)
    if store_id:
        query = query.filter(Price.store_id == store_id)
    if category:
        query = query.filter(Product.category == category)
    if is_available is not None:
        query = query.filter(Price.is_available == is_available)
    
    # Get latest prices only (most recent for each product-store combination)
    subquery = db.query(
        Price.product_id,
        Price.store_id,
        db.func.max(Price.scraped_at).label('max_scraped_at')
    ).group_by(Price.product_id, Price.store_id).subquery()
    
    query = query.join(
        subquery,
        db.and_(
            Price.product_id == subquery.c.product_id,
            Price.store_id == subquery.c.store_id,
            Price.scraped_at == subquery.c.max_scraped_at
        )
    )
    
    prices = query.offset(skip).limit(limit).all()
    
    # Format response
    results = []
    for price in prices:
        # Calculate price change
        yesterday = datetime.utcnow() - timedelta(days=1)
        previous_price = db.query(PriceHistory).filter(
            PriceHistory.product_id == price.product_id,
            PriceHistory.store_id == price.store_id,
            PriceHistory.recorded_at < yesterday
        ).order_by(PriceHistory.recorded_at.desc()).first()
        
        price_change = 0
        price_change_percent = 0
        if previous_price:
            price_change = price.price - previous_price.price
            if previous_price.price > 0:
                price_change_percent = (price_change / previous_price.price) * 100
        
        results.append({
            "id": price.id,
            "product_id": price.product_id,
            "product_name": price.product.name,
            "store_id": price.store_id,
            "store_name": price.store.name,
            "price": price.price,
            "original_price": price.original_price,
            "price_per_kg": price.price_per_kg,
            "pack_size": price.pack_size,
            "pack_unit": price.pack_unit,
            "is_available": price.is_available,
            "is_discounted": price.is_discounted,
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "product_url": price.product_url,
            "image_url": price.image_url,
            "scraped_at": price.scraped_at
        })
    
    return results

@router.post("/refresh")
async def refresh_prices(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Trigger price refresh (scraping)"""
    # Add scraping task to background
    background_tasks.add_task(trigger_scraping, db)
    
    # Update store statuses
    stores = db.query(Store).filter(Store.is_active == True).all()
    for store in stores:
        store.status = "scraping"
    db.commit()
    
    return {"message": "Price refresh initiated", "stores_count": len(stores)}

@router.get("/trends", response_model=List[PriceTrend])
def get_price_trends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    product_id: int = Query(...),
    store_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=30)
):
    """Get price trends for a product"""
    since = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.recorded_at >= since
    )
    
    if store_id:
        query = query.filter(PriceHistory.store_id == store_id)
    
    history = query.order_by(PriceHistory.recorded_at).all()
    
    # Group by date and store
    trends = {}
    for record in history:
        date_key = record.recorded_at.date().isoformat()
        store_key = record.store_id
        
        if date_key not in trends:
            trends[date_key] = {}
        
        trends[date_key][store_key] = {
            "price": record.price,
            "price_per_kg": record.price_per_kg,
            "is_available": record.is_available
        }
    
    return trends

@router.get("/{price_id}", response_model=PriceResponse)
def get_price(
    price_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific price by ID"""
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    return price