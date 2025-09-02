"""
Price service for managing price data
Path: backend/app/services/price_service.py
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.models.price import Price
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.store import Store

logger = logging.getLogger(__name__)

class PriceService:
    """Service for managing price data and analytics"""
    
    @staticmethod
    def get_current_prices(
        db: Session,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
        category: Optional[str] = None,
        is_available: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """Get current prices with filters"""
        
        # Base query
        query = db.query(Price).join(Product).join(Store)
        
        # Apply filters
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
            func.max(Price.scraped_at).label('max_scraped_at')
        ).group_by(Price.product_id, Price.store_id).subquery()
        
        query = query.join(
            subquery,
            and_(
                Price.product_id == subquery.c.product_id,
                Price.store_id == subquery.c.store_id,
                Price.scraped_at == subquery.c.max_scraped_at
            )
        )
        
        # Execute query
        prices = query.offset(skip).limit(limit).all()
        
        # Format results with price changes
        results = []
        for price in prices:
            price_data = PriceService._format_price_with_change(db, price)
            results.append(price_data)
        
        return results
    
    @staticmethod
    def _format_price_with_change(db: Session, price: Price) -> Dict:
        """Format price with change information"""
        
        # Calculate price change from yesterday
        yesterday = datetime.utcnow() - timedelta(days=1)
        previous_price = db.query(PriceHistory).filter(
            PriceHistory.product_id == price.product_id,
            PriceHistory.store_id == price.store_id,
            PriceHistory.recorded_at < yesterday
        ).order_by(PriceHistory.recorded_at.desc()).first()
        
        price_change = 0
        price_change_percent = 0
        
        if previous_price and previous_price.price > 0:
            price_change = price.price - previous_price.price
            price_change_percent = (price_change / previous_price.price) * 100
        
        return {
            "id": price.id,
            "product_id": price.product_id,
            "product_name": price.product.name,
            "product_category": price.product.category,
            "store_id": price.store_id,
            "store_name": price.store.name,
            "price": price.price,
            "original_price": price.original_price,
            "price_per_kg": price.price_per_kg,
            "pack_size": price.pack_size,
            "pack_unit": price.pack_unit,
            "is_available": price.is_available,
            "is_discounted": price.is_discounted,
            "is_organic": price.product.is_organic,
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_percent, 2),
            "product_url": price.product_url,
            "image_url": price.image_url,
            "scraped_at": price.scraped_at.isoformat() if price.scraped_at else None
        }
    
    @staticmethod
    def save_price(
        db: Session,
        product_id: int,
        store_id: int,
        price: float,
        **kwargs
    ) -> Price:
        """Save a new price entry"""
        
        # Create price entry
        new_price = Price(
            product_id=product_id,
            store_id=store_id,
            price=price,
            **kwargs
        )
        
        db.add(new_price)
        
        # Also add to price history
        history_entry = PriceHistory(
            product_id=product_id,
            store_id=store_id,
            price=price,
            price_per_kg=kwargs.get('price_per_kg'),
            is_available=kwargs.get('is_available', True)
        )
        
        db.add(history_entry)
        db.commit()
        db.refresh(new_price)
        
        return new_price
    
    @staticmethod
    def get_price_trends(
        db: Session,
        product_id: int,
        store_id: Optional[int] = None,
        days: int = 7
    ) -> List[Dict]:
        """Get price trends for a product over time"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= since
        )
        
        if store_id:
            query = query.filter(PriceHistory.store_id == store_id)
        
        history = query.order_by(PriceHistory.recorded_at).all()
        
        # Format trends
        trends = []
        for record in history:
            trends.append({
                "date": record.recorded_at.date().isoformat(),
                "time": record.recorded_at.time().isoformat(),
                "store_id": record.store_id,
                "price": record.price,
                "price_per_kg": record.price_per_kg,
                "is_available": record.is_available
            })
        
        return trends
    
    @staticmethod
    def get_best_prices(
        db: Session,
        product_id: int
    ) -> List[Dict]:
        """Get best prices for a product across all stores"""
        
        # Get current prices for the product from all stores
        prices = db.query(Price).filter(
            Price.product_id == product_id,
            Price.is_available == True
        ).order_by(Price.price).all()
        
        results = []
        for price in prices:
            results.append(PriceService._format_price_with_change(db, price))
        
        return results
    
    @staticmethod
    def get_price_statistics(
        db: Session,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
        days: int = 30
    ) -> Dict:
        """Get price statistics"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PriceHistory).filter(
            PriceHistory.recorded_at >= since
        )
        
        if product_id:
            query = query.filter(PriceHistory.product_id == product_id)
        if store_id:
            query = query.filter(PriceHistory.store_id == store_id)
        
        # Calculate statistics
        avg_price = db.query(func.avg(PriceHistory.price)).filter(
            PriceHistory.recorded_at >= since
        ).scalar() or 0
        
        min_price = db.query(func.min(PriceHistory.price)).filter(
            PriceHistory.recorded_at >= since
        ).scalar() or 0
        
        max_price = db.query(func.max(PriceHistory.price)).filter(
            PriceHistory.recorded_at >= since
        ).scalar() or 0
        
        total_records = query.count()
        
        return {
            "average_price": round(avg_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "total_records": total_records,
            "period_days": days
        }