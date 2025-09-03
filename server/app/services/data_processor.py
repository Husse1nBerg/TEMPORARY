from typing import List, Dict, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging
import re
import statistics
import json
from collections import defaultdict

from server.app.models.product import Product
from server.app.models.price import Price
from server.app.models.price_history import PriceHistory
from server.app.models.store import Store
from server.app.scrapers.base_scraper import ScrapedProduct
from server.app.utils.price_calculator import PriceCalculator

logger = logging.getLogger(__name__)


class DataProcessor:
    """Service for processing and cleaning scraped product data."""
    
    def __init__(self):
        self.similarity_threshold = 0.8
        self.price_change_threshold = 0.05  # 5% change threshold
        
    async def process_scraped_products(
        self,
        db: Session,
        store_id: int,
        scraped_products: List[ScrapedProduct]
    ) -> Dict[str, Any]:
        """
        Process scraped products and update database.
        
        Returns:
            Dict with processing statistics
        """
        stats = {
            'total_scraped': len(scraped_products),
            'products_created': 0,
            'products_updated': 0,
            'prices_added': 0,
            'prices_updated': 0,
            'duplicates_removed': 0,
            'invalid_products': 0,
            'errors': []
        }
        
        try:
            # Remove duplicates from scraped data
            unique_products = self._remove_duplicates(scraped_products)
            stats['duplicates_removed'] = len(scraped_products) - len(unique_products)
            
            # Process each unique product
            for scraped_product in unique_products:
                try:
                    result = await self._process_single_product(db, store_id, scraped_product)
                    
                    if result['action'] == 'created':
                        stats['products_created'] += 1
                        stats['prices_added'] += 1
                    elif result['action'] == 'updated':
                        stats['products_updated'] += 1
                        if result['price_updated']:
                            stats['prices_updated'] += 1
                        else:
                            stats['prices_added'] += 1
                    elif result['action'] == 'invalid':
                        stats['invalid_products'] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing product {scraped_product.name}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['invalid_products'] += 1
            
            # Update store statistics
            await self._update_store_stats(db, store_id, stats)
            
            # Commit all changes
            db.commit()
            
            logger.info(f"Processing completed for store {store_id}: {stats}")
            
        except Exception as e:
            db.rollback()
            error_msg = f"Failed to process scraped products: {e}"
            logger.error(error_msg)
            stats['errors'].append(error_msg)
        
        return stats
    
    def _remove_duplicates(self, products: List[ScrapedProduct]) -> List[ScrapedProduct]:
        """Remove duplicate products based on name and price similarity."""
        unique_products = []
        seen_products = set()
        
        for product in products:
            # Create a normalized identifier
            normalized_name = self._normalize_product_name(product.name)
            price_key = round(product.price, 2)
            
            product_key = f"{normalized_name}_{price_key}"
            
            if product_key not in seen_products:
                seen_products.add(product_key)
                unique_products.append(product)
        
        return unique_products
    
    def _normalize_product_name(self, name: str) -> str:
        """Normalize product name for comparison."""
        if not name:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        normalized = ' '.join(name.lower().strip().split())
        
        # Remove common variations
        normalized = re.sub(r'\b(pack|pcs|pieces|kg|g|ml|l)\b', '', normalized)
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove special characters
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    async def _process_single_product(
        self,
        db: Session,
        store_id: int,
        scraped_product: ScrapedProduct
    ) -> Dict[str, Any]:
        """Process a single scraped product."""
        result = {
            'action': None,
            'product_id': None,
            'price_updated': False
        }
        
        # Validate scraped product
        if not self._validate_scraped_product(scraped_product):
            result['action'] = 'invalid'
            return result
        
        # Find existing product or create new one
        existing_product = await self._find_matching_product(db, store_id, scraped_product)
        
        if existing_product:
            # Update existing product
            updated = await self._update_existing_product(db, existing_product, scraped_product)
            result['action'] = 'updated'
            result['product_id'] = existing_product.id
            result['price_updated'] = updated
        else:
            # Create new product
            new_product = await self._create_new_product(db, store_id, scraped_product)
            result['action'] = 'created'
            result['product_id'] = new_product.id
        
        return result
    
    def _validate_scraped_product(self, product: ScrapedProduct) -> bool:
        """Validate scraped product data."""
        if not product.name or len(product.name.strip()) == 0:
            return False
        
        if product.price <= 0:
            return False
        
        if product.original_price and product.original_price < product.price:
            return False
        
        return True
    
    async def _find_matching_product(
        self,
        db: Session,
        store_id: int,
        scraped_product: ScrapedProduct
    ) -> Optional[Product]:
        """Find existing product that matches scraped product."""
        
        # First, try exact external ID match
        if scraped_product.external_id:
            product = db.query(Product).filter(
                and_(
                    Product.store_id == store_id,
                    Product.external_id == scraped_product.external_id
                )
            ).first()
            if product:
                return product
        
        # Try exact name match
        product = db.query(Product).filter(
            and_(
                Product.store_id == store_id,
                Product.name == scraped_product.name
            )
        ).first()
        if product:
            return product
        
        # Try fuzzy name matching
        normalized_name = self._normalize_product_name(scraped_product.name)
        
        similar_products = db.query(Product).filter(
            Product.store_id == store_id
        ).all()
        
        for product in similar_products:
            if self._calculate_similarity(normalized_name, self._normalize_product_name(product.name)) >= self.similarity_threshold:
                return product
        
        return None
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two product names."""
        if not name1 or not name2:
            return 0.0
        
        # Simple Jaccard similarity based on words
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _create_new_product(
        self,
        db: Session,
        store_id: int,
        scraped_product: ScrapedProduct
    ) -> Product:
        """Create new product from scraped data."""
        
        # Create product
        product = Product(
            name=scraped_product.name,
            category=scraped_product.category or 'pantry',
            subcategory=scraped_product.subcategory,
            description=scraped_product.description,
            image_url=scraped_product.image_url,
            unit=scraped_product.pack_unit,
            weight=scraped_product.weight_value,
            brand=scraped_product.brand,
            is_organic=False,  # Could be determined from name/keywords
            store_id=store_id,
            external_id=scraped_product.external_id,
            keywords=' '.join(scraped_product.keywords) if scraped_product.keywords else None
        )
        
        db.add(product)
        db.flush()  # Get the product ID
        
        # Create initial price
        await self._create_price_entry(db, product.id, store_id, scraped_product)
        
        logger.info(f"Created new product: {product.name} (ID: {product.id})")
        return product
    
    async def _update_existing_product(
        self,
        db: Session,
        product: Product,
        scraped_product: ScrapedProduct
    ) -> bool:
        """Update existing product with new scraped data."""
        price_updated = False
        
        # Update product fields if they have better data
        if scraped_product.description and not product.description:
            product.description = scraped_product.description
        
        if scraped_product.image_url and not product.image_url:
            product.image_url = scraped_product.image_url
        
        if scraped_product.brand and not product.brand:
            product.brand = scraped_product.brand
        
        if scraped_product.weight_value and not product.weight:
            product.weight = scraped_product.weight_value
        
        if scraped_product.pack_unit and not product.unit:
            product.unit = scraped_product.pack_unit
        
        # Update external_id if not set
        if scraped_product.external_id and not product.external_id:
            product.external_id = scraped_product.external_id
        
        # Check if price needs updating
        current_price = db.query(Price).filter(
            and_(
                Price.product_id == product.id,
                Price.store_id == product.store_id
            )
        ).order_by(Price.scraped_at.desc()).first()
        
        if not current_price or self._should_update_price(current_price, scraped_product):
            await self._create_price_entry(db, product.id, product.store_id, scraped_product)
            price_updated = True
            
            # Create price history entry if significant change
            if current_price:
                await self._create_price_history_entry(db, current_price, scraped_product)
        
        product.updated_at = datetime.now()
        
        return price_updated
    
    def _should_update_price(self, current_price: Price, scraped_product: ScrapedProduct) -> bool:
        """Determine if price should be updated."""
        
        # Always update if more than 24 hours old
        if datetime.now() - current_price.scraped_at > timedelta(hours=24):
            return True
        
        # Update if price changed significantly
        price_change = abs(current_price.price - scraped_product.price) / current_price.price
        if price_change >= self.price_change_threshold:
            return True
        
        # Update if availability changed
        if current_price.is_available != scraped_product.is_available:
            return True
        
        # Update if discount status changed
        if current_price.is_discounted != scraped_product.is_discounted:
            return True
        
        return False
    
    async def _create_price_entry(
        self,
        db: Session,
        product_id: int,
        store_id: int,
        scraped_product: ScrapedProduct
    ) -> Price:
        """Create new price entry."""
        
        # Calculate price per kg if possible
        price_per_kg = None
        if scraped_product.weight_value and scraped_product.weight_unit:
            price_per_kg = PriceCalculator.calculate_price_per_unit(
                scraped_product.price,
                scraped_product.weight_value,
                scraped_product.weight_unit
            )
        
        price = Price(
            product_id=product_id,
            store_id=store_id,
            price=scraped_product.price,
            original_price=scraped_product.original_price,
            price_per_kg=price_per_kg,
            discount_percentage=scraped_product.discount_percentage,
            pack_size=scraped_product.pack_size,
            pack_unit=scraped_product.pack_unit,
            weight_value=scraped_product.weight_value,
            weight_unit=scraped_product.weight_unit,
            is_available=scraped_product.is_available,
            is_discounted=scraped_product.is_discounted,
            is_on_sale=scraped_product.is_on_sale,
            product_url=scraped_product.product_url,
            image_url=scraped_product.image_url
        )
        
        db.add(price)
        return price
    
    async def _create_price_history_entry(
        self,
        db: Session,
        old_price: Price,
        scraped_product: ScrapedProduct
    ) -> PriceHistory:
        """Create price history entry."""
        
        # Calculate change
        price_change = scraped_product.price - old_price.price
        change_percentage = (price_change / old_price.price) * 100 if old_price.price > 0 else 0
        
        # Determine change type
        change_type = 'stable'
        if abs(change_percentage) >= 1:  # 1% threshold
            change_type = 'increase' if price_change > 0 else 'decrease'
        
        if not scraped_product.is_available:
            change_type = 'unavailable'
        elif not old_price.is_available and scraped_product.is_available:
            change_type = 'new'
        
        history = PriceHistory(
            product_id=old_price.product_id,
            store_id=old_price.store_id,
            price=old_price.price,
            original_price=old_price.original_price,
            price_per_kg=old_price.price_per_kg,
            discount_percentage=old_price.discount_percentage,
            pack_size=old_price.pack_size,
            pack_unit=old_price.pack_unit,
            is_available=old_price.is_available,
            is_discounted=old_price.is_discounted,
            change_type=change_type,
            change_amount=price_change,
            change_percentage=change_percentage,
            recorded_at=old_price.scraped_at
        )
        
        db.add(history)
        return history
    
    async def _update_store_stats(self, db: Session, store_id: int, stats: Dict[str, Any]):
        """Update store statistics after processing."""
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            return
        
        store.last_scraped = datetime.now()
        store.total_scrapes += 1
        
        if stats['errors']:
            store.failed_scrapes += 1
        
        # Update success rate
        if store.total_scrapes > 0:
            store.success_rate = ((store.total_scrapes - store.failed_scrapes) / store.total_scrapes) * 100
    
    async def clean_old_data(self, db: Session, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean old price history and unused data."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        stats = {
            'price_history_deleted': 0,
            'old_prices_deleted': 0,
            'inactive_products_deleted': 0
        }
        
        try:
            # Delete old price history
            old_history = db.query(PriceHistory).filter(
                PriceHistory.recorded_at < cutoff_date
            )
            stats['price_history_deleted'] = old_history.count()
            old_history.delete()
            
            # Delete old prices (keep only latest for each product-store)
            subquery = db.query(
                Price.product_id,
                Price.store_id,
                func.max(Price.scraped_at).label('max_date')
            ).group_by(Price.product_id, Price.store_id).subquery()
            
            old_prices = db.query(Price).filter(
                ~db.query(subquery).filter(
                    and_(
                        subquery.c.product_id == Price.product_id,
                        subquery.c.store_id == Price.store_id,
                        subquery.c.max_date == Price.scraped_at
                    )
                ).exists(),
                Price.scraped_at < cutoff_date
            )
            
            stats['old_prices_deleted'] = old_prices.count()
            old_prices.delete()
            
            # Mark products as inactive if no recent prices
            inactive_products = db.query(Product).filter(
                ~db.query(Price).filter(
                    and_(
                        Price.product_id == Product.id,
                        Price.scraped_at >= cutoff_date
                    )
                ).exists(),
                Product.is_active == True
            )
            
            for product in inactive_products:
                product.is_active = False
                stats['inactive_products_deleted'] += 1
            
            db.commit()
            logger.info(f"Data cleanup completed: {stats}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during data cleanup: {e}")
        
        return stats
    
    async def generate_product_insights(
        self,
        db: Session,
        product_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate insights for a product."""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get price history
        price_history = db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= start_date
            )
        ).order_by(PriceHistory.recorded_at).all()
        
        if not price_history:
            return {'error': 'No price history available'}
        
        prices = [h.price for h in price_history if h.is_available]
        
        if not prices:
            return {'error': 'No available prices in period'}
        
        insights = {
            'price_stats': {
                'current_price': prices[-1],
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': statistics.mean(prices),
                'median_price': statistics.median(prices),
                'price_volatility': statistics.stdev(prices) if len(prices) > 1 else 0
            },
            'trend_analysis': self._analyze_price_trend(prices),
            'availability_rate': len(prices) / len(price_history) * 100,
            'discount_frequency': len([h for h in price_history if h.is_discounted]) / len(price_history) * 100,
            'significant_changes': len([h for h in price_history if abs(h.change_percentage or 0) >= 10])
        }
        
        return insights
    
    def _analyze_price_trend(self, prices: List[float]) -> str:
        """Analyze price trend from price list."""
        if len(prices) < 3:
            return 'insufficient_data'
        
        # Calculate trend using linear regression slope
        n = len(prices)
        x_values = list(range(n))
        
        sum_x = sum(x_values)
        sum_y = sum(prices)
        sum_xy = sum(x * y for x, y in zip(x_values, prices))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend based on slope
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'