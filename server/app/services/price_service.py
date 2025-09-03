from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
import logging
import statistics
from collections import defaultdict

from server.app.models.product import Product
from server.app.models.price import Price
from server.app.models.price_history import PriceHistory
from server.app.models.store import Store
from server.app.schemas.price import PriceFilter, PriceTrend, PriceComparison
from server.app.utils.price_calculator import PriceCalculator

logger = logging.getLogger(__name__)


class PriceService:
    """Service for price-related operations and analysis."""
    
    @staticmethod
    def get_prices(
        db: Session,
        price_filter: PriceFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Price], int]:
        """Get prices with filtering and pagination."""
        
        query = db.query(Price)
        
        # Apply filters
        if price_filter.product_id:
            query = query.filter(Price.product_id == price_filter.product_id)
        
        if price_filter.store_id:
            query = query.filter(Price.store_id == price_filter.store_id)
        
        if price_filter.category:
            query = query.join(Product).filter(Product.category == price_filter.category)
        
        if price_filter.min_price is not None:
            query = query.filter(Price.price >= price_filter.min_price)
        
        if price_filter.max_price is not None:
            query = query.filter(Price.price <= price_filter.max_price)
        
        if price_filter.is_available is not None:
            query = query.filter(Price.is_available == price_filter.is_available)
        
        if price_filter.is_discounted is not None:
            query = query.filter(Price.is_discounted == price_filter.is_discounted)
        
        if price_filter.date_from:
            query = query.filter(Price.scraped_at >= price_filter.date_from)
        
        if price_filter.date_to:
            query = query.filter(Price.scraped_at <= price_filter.date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        prices = query.order_by(Price.scraped_at.desc()).offset(skip).limit(limit).all()
        
        return prices, total
    
    @staticmethod
    def get_current_prices(db: Session, product_ids: List[int] = None) -> List[Price]:
        """Get current (latest) prices for products."""
        
        # Subquery to get latest price for each product-store combination
        subquery = db.query(
            Price.product_id,
            Price.store_id,
            func.max(Price.scraped_at).label('max_date')
        ).group_by(Price.product_id, Price.store_id).subquery()
        
        query = db.query(Price).join(
            subquery,
            and_(
                Price.product_id == subquery.c.product_id,
                Price.store_id == subquery.c.store_id,
                Price.scraped_at == subquery.c.max_date
            )
        )
        
        if product_ids:
            query = query.filter(Price.product_id.in_(product_ids))
        
        return query.all()
    
    @staticmethod
    def get_price_trends(
        db: Session,
        product_id: int,
        store_id: Optional[int] = None,
        days: int = 30
    ) -> List[PriceTrend]:
        """Get price trends over time."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= start_date
            )
        )
        
        if store_id:
            query = query.filter(PriceHistory.store_id == store_id)
        
        history = query.order_by(PriceHistory.recorded_at).all()
        
        # Group by date and calculate daily averages
        daily_prices = defaultdict(list)
        for entry in history:
            date_key = entry.recorded_at.date()
            if entry.is_available:
                daily_prices[date_key].append(entry.price)
        
        trends = []
        for date_key, prices in sorted(daily_prices.items()):
            avg_price = statistics.mean(prices)
            trends.append(PriceTrend(
                date=date_key,
                price=round(avg_price, 2),
                is_available=True
            ))
        
        return trends
    
    @staticmethod
    def compare_prices(db: Session, product_id: int) -> PriceComparison:
        """Compare prices across different stores for a product."""
        
        # Get current prices for the product
        current_prices = db.query(Price).join(Store).filter(
            and_(
                Price.product_id == product_id,
                Price.is_available == True
            )
        ).order_by(Price.price).all()
        
        if not current_prices:
            return PriceComparison(
                product_id=product_id,
                product_name="Unknown",
                prices=[],
                lowest_price=0,
                highest_price=0,
                avg_price=0
            )
        
        # Get product name
        product = db.query(Product).filter(Product.id == product_id).first()
        product_name = product.name if product else "Unknown"
        
        # Format price data
        price_data = []
        for price in current_prices:
            price_data.append({
                'store_id': price.store_id,
                'store_name': price.store.name,
                'price': price.price,
                'original_price': price.original_price,
                'is_discounted': price.is_discounted,
                'discount_percentage': price.discount_percentage,
                'last_updated': price.scraped_at,
                'is_best_deal': False  # Will be set below
            })
        
        # Mark best deal
        if price_data:
            price_data[0]['is_best_deal'] = True
        
        price_values = [p.price for p in current_prices]
        
        return PriceComparison(
            product_id=product_id,
            product_name=product_name,
            prices=price_data,
            lowest_price=min(price_values),
            highest_price=max(price_values),
            avg_price=round(statistics.mean(price_values), 2),
            best_deal_store=price_data[0]['store_name'] if price_data else None
        )
    
    @staticmethod
    def get_best_deals(
        db: Session,
        category: Optional[str] = None,
        limit: int = 20,
        min_discount: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Get products with the best deals."""
        
        query = db.query(Price).join(Product).filter(
            and_(
                Price.is_available == True,
                Price.is_discounted == True,
                Price.discount_percentage >= min_discount
            )
        )
        
        if category:
            query = query.filter(Product.category == category)
        
        deals = query.order_by(Price.discount_percentage.desc()).limit(limit).all()
        
        result = []
        for deal in deals:
            result.append({
                'product_id': deal.product_id,
                'product_name': deal.product.name,
                'store_id': deal.store_id,
                'store_name': deal.store.name,
                'current_price': deal.price,
                'original_price': deal.original_price,
                'discount_percentage': deal.discount_percentage,
                'savings_amount': round(deal.original_price - deal.price, 2) if deal.original_price else 0,
                'category': deal.product.category,
                'image_url': deal.image_url or deal.product.image_url,
                'last_updated': deal.scraped_at
            })
        
        return result
    
    @staticmethod
    def get_price_alerts(
        db: Session,
        product_id: int,
        target_price: float,
        condition: str = 'below'
    ) -> List[Dict[str, Any]]:
        """Check for price alerts."""
        
        current_prices = PriceService.get_current_prices(db, [product_id])
        alerts = []
        
        for price in current_prices:
            if condition == 'below' and price.price <= target_price:
                alerts.append({
                    'product_id': product_id,
                    'store_id': price.store_id,
                    'store_name': price.store.name,
                    'current_price': price.price,
                    'target_price': target_price,
                    'condition': condition,
                    'triggered_at': datetime.now()
                })
            elif condition == 'above' and price.price >= target_price:
                alerts.append({
                    'product_id': product_id,
                    'store_id': price.store_id,
                    'store_name': price.store.name,
                    'current_price': price.price,
                    'target_price': target_price,
                    'condition': condition,
                    'triggered_at': datetime.now()
                })
        
        return alerts
    
    @staticmethod
    def get_category_price_stats(db: Session, category: str) -> Dict[str, Any]:
        """Get price statistics for a category."""
        
        # Get current prices for category
        current_prices = db.query(Price).join(Product).filter(
            and_(
                Product.category == category,
                Price.is_available == True
            )
        ).all()
        
        if not current_prices:
            return {
                'category': category,
                'total_products': 0,
                'price_stats': None
            }
        
        prices = [p.price for p in current_prices]
        
        return {
            'category': category,
            'total_products': len(current_prices),
            'available_products': len(prices),
            'price_stats': {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': round(statistics.mean(prices), 2),
                'median_price': round(statistics.median(prices), 2),
                'std_deviation': round(statistics.stdev(prices), 2) if len(prices) > 1 else 0
            },
            'discount_stats': {
                'total_discounted': len([p for p in current_prices if p.is_discounted]),
                'avg_discount': round(statistics.mean([
                    p.discount_percentage for p in current_prices 
                    if p.is_discounted and p.discount_percentage
                ]), 2) if any(p.is_discounted for p in current_prices) else 0
            }
        }
    
    @staticmethod
    def get_store_price_performance(db: Session, store_id: int, days: int = 30) -> Dict[str, Any]:
        """Get price performance metrics for a store."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get prices for the period
        prices = db.query(Price).filter(
            and_(
                Price.store_id == store_id,
                Price.scraped_at >= start_date
            )
        ).all()
        
        if not prices:
            return {
                'store_id': store_id,
                'period_days': days,
                'no_data': True
            }
        
        # Calculate metrics
        available_prices = [p for p in prices if p.is_available]
        discounted_prices = [p for p in prices if p.is_discounted]
        
        price_values = [p.price for p in available_prices]
        
        # Get store info
        store = db.query(Store).filter(Store.id == store_id).first()
        
        return {
            'store_id': store_id,
            'store_name': store.name if store else 'Unknown',
            'period_days': days,
            'total_prices': len(prices),
            'available_count': len(available_prices),
            'availability_rate': (len(available_prices) / len(prices)) * 100,
            'discount_rate': (len(discounted_prices) / len(prices)) * 100,
            'price_stats': {
                'min_price': min(price_values) if price_values else 0,
                'max_price': max(price_values) if price_values else 0,
                'avg_price': round(statistics.mean(price_values), 2) if price_values else 0,
                'price_range': max(price_values) - min(price_values) if price_values else 0
            },
            'competitiveness_score': PriceService._calculate_competitiveness_score(db, store_id, available_prices)
        }
    
    @staticmethod
    def _calculate_competitiveness_score(db: Session, store_id: int, store_prices: List[Price]) -> float:
        """Calculate how competitive a store's prices are."""
        
        if not store_prices:
            return 0.0
        
        competitive_count = 0
        total_comparisons = 0
        
        for price in store_prices[:100]:  # Limit for performance
            # Get prices for same product from other stores
            other_prices = db.query(Price).filter(
                and_(
                    Price.product_id == price.product_id,
                    Price.store_id != store_id,
                    Price.is_available == True
                )
            ).all()
            
            if other_prices:
                min_other_price = min(p.price for p in other_prices)
                if price.price <= min_other_price * 1.05:  # Within 5% of best price
                    competitive_count += 1
                total_comparisons += 1
        
        return (competitive_count / total_comparisons) * 100 if total_comparisons > 0 else 0.0
    
    @staticmethod
    def get_price_history_summary(
        db: Session,
        product_id: int,
        store_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get price history summary."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= start_date
            )
        )
        
        if store_id:
            query = query.filter(PriceHistory.store_id == store_id)
        
        history = query.order_by(PriceHistory.recorded_at).all()
        
        if not history:
            return {'error': 'No price history found'}
        
        # Calculate summary statistics
        prices = [h.price for h in history if h.is_available]
        changes = [h for h in history if h.change_type in ['increase', 'decrease']]
        
        return {
            'product_id': product_id,
            'store_id': store_id,
            'period_days': days,
            'total_records': len(history),
            'price_points': len(prices),
            'price_stats': {
                'current_price': prices[-1] if prices else None,
                'min_price': min(prices) if prices else None,
                'max_price': max(prices) if prices else None,
                'avg_price': round(statistics.mean(prices), 2) if prices else None,
                'price_volatility': round(statistics.stdev(prices), 2) if len(prices) > 1 else 0
            },
            'changes': {
                'total_changes': len(changes),
                'increases': len([c for c in changes if c.change_type == 'increase']),
                'decreases': len([c for c in changes if c.change_type == 'decrease']),
                'avg_change_percent': round(statistics.mean([
                    abs(c.change_percentage) for c in changes if c.change_percentage
                ]), 2) if changes else 0
            },
            'availability': {
                'available_count': len([h for h in history if h.is_available]),
                'unavailable_count': len([h for h in history if not h.is_available]),
                'availability_rate': (len([h for h in history if h.is_available]) / len(history)) * 100
            }
        }
    
    @staticmethod
    def calculate_shopping_list_savings(
        db: Session,
        product_ids: List[int]
    ) -> Dict[str, Any]:
        """Calculate potential savings for a shopping list."""
        
        total_best_price = 0.0
        total_avg_price = 0.0
        total_max_price = 0.0
        
        item_details = []
        
        for product_id in product_ids:
            comparison = PriceService.compare_prices(db, product_id)
            
            if comparison.prices:
                best_price = comparison.lowest_price
                avg_price = comparison.avg_price
                max_price = comparison.highest_price
                
                total_best_price += best_price
                total_avg_price += avg_price
                total_max_price += max_price
                
                item_details.append({
                    'product_id': product_id,
                    'product_name': comparison.product_name,
                    'best_price': best_price,
                    'avg_price': avg_price,
                    'max_price': max_price,
                    'best_store': comparison.best_deal_store,
                    'potential_savings': round(max_price - best_price, 2)
                })
        
        total_potential_savings = total_max_price - total_best_price
        avg_potential_savings = total_avg_price - total_best_price
        
        return {
            'total_items': len(product_ids),
            'processed_items': len(item_details),
            'totals': {
                'best_price_total': round(total_best_price, 2),
                'avg_price_total': round(total_avg_price, 2),
                'max_price_total': round(total_max_price, 2)
            },
            'savings': {
                'max_potential_savings': round(total_potential_savings, 2),
                'avg_potential_savings': round(avg_potential_savings, 2),
                'savings_percentage': round((total_potential_savings / total_max_price) * 100, 2) if total_max_price > 0 else 0
            },
            'items': item_details
        }
    
    @staticmethod
    def get_trending_products(
        db: Session,
        category: Optional[str] = None,
        trend_type: str = 'price_drops',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get trending products based on price changes."""
        
        # Get recent price changes
        recent_date = datetime.now() - timedelta(days=7)
        
        query = db.query(PriceHistory).join(Product).filter(
            PriceHistory.recorded_at >= recent_date
        )
        
        if category:
            query = query.filter(Product.category == category)
        
        if trend_type == 'price_drops':
            query = query.filter(
                and_(
                    PriceHistory.change_type == 'decrease',
                    PriceHistory.change_percentage <= -10  # At least 10% drop
                )
            ).order_by(PriceHistory.change_percentage.asc())
        
        elif trend_type == 'new_products':
            query = query.filter(PriceHistory.change_type == 'new')
        
        elif trend_type == 'back_in_stock':
            query = query.filter(
                and_(
                    PriceHistory.change_type == 'new',
                    PriceHistory.is_available == True
                )
            )
        
        changes = query.limit(limit).all()
        
        trending = []
        for change in changes:
            product = change.product
            
            # Get current price
            current_price = db.query(Price).filter(
                and_(
                    Price.product_id == change.product_id,
                    Price.store_id == change.store_id
                )
            ).order_by(Price.scraped_at.desc()).first()
            
            trending.append({
                'product_id': change.product_id,
                'product_name': product.name,
                'category': product.category,
                'store_id': change.store_id,
                'store_name': change.store.name if change.store else 'Unknown',
                'trend_type': trend_type,
                'change_type': change.change_type,
                'old_price': change.price,
                'current_price': current_price.price if current_price else None,
                'change_percentage': change.change_percentage,
                'change_amount': change.change_amount,
                'recorded_at': change.recorded_at,
                'image_url': current_price.image_url if current_price else product.image_url
            })
        
        return trending