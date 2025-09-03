from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import statistics
import logging
import re

from server.app.models.price import Price
from server.app.models.price_history import PriceHistory
from server.app.models.product import Product

logger = logging.getLogger(__name__)


class PriceCalculator:
    """Utility class for price calculations and analysis."""
    
    UNIT_CONVERSIONS_TO_KG = {
        'g': 0.001,
        'gram': 0.001,
        'grams': 0.001,
        'kg': 1.0,
        'kilogram': 1.0,
        'kilograms': 1.0,
        'lb': 0.453592,
        'pound': 0.453592,
        'pounds': 0.453592,
        'oz': 0.0283495,
        'ounce': 0.0283495,
        'ounces': 0.0283495
    }
    
    UNIT_CONVERSIONS_TO_L = {
        'ml': 0.001,
        'milliliter': 0.001,
        'milliliters': 0.001,
        'l': 1.0,
        'liter': 1.0,
        'liters': 1.0,
        'fl oz': 0.0295735,
        'fluid ounce': 0.0295735
    }
    
    @staticmethod
    def calculate_price_per_kg(price: float, size: str, unit: str) -> Optional[float]:
        """Calculate price per kilogram."""
        try:
            size_value = float(re.sub(r'[^\d.]', '', str(size)))
            conversion_factor = PriceCalculator.UNIT_CONVERSIONS_TO_KG.get(unit.lower())
            
            if not conversion_factor or size_value <= 0:
                return None
            
            weight_in_kg = size_value * conversion_factor
            price_per_kg = price / weight_in_kg
            return round(price_per_kg, 2)
            
        except Exception:
            return None
    
    @staticmethod
    def calculate_price_per_unit(price: float, weight: float, unit: str) -> Optional[float]:
        """Calculate price per standard unit."""
        if not weight or weight <= 0:
            return None
        
        standard_weight = PriceCalculator.convert_to_standard_unit(weight, unit)
        if not standard_weight:
            return None
        
        return round(price / standard_weight, 2)
    
    @staticmethod
    def convert_to_standard_unit(value: float, unit: str) -> Optional[float]:
        """Convert weight/volume to standard units."""
        if not unit:
            return None
        
        unit = unit.lower().strip()
        
        if unit in PriceCalculator.UNIT_CONVERSIONS_TO_KG:
            return value * PriceCalculator.UNIT_CONVERSIONS_TO_KG[unit]
        elif unit in PriceCalculator.UNIT_CONVERSIONS_TO_L:
            return value * PriceCalculator.UNIT_CONVERSIONS_TO_L[unit]
        
        return None
    
    @staticmethod
    def calculate_discount_percentage(original_price: float, current_price: float) -> float:
        """Calculate discount percentage."""
        if original_price <= 0 or current_price >= original_price:
            return 0.0
        
        return round(((original_price - current_price) / original_price) * 100, 2)
    
    @staticmethod
    def get_price_trend(db: Session, product_id: int, days: int = 30) -> Dict:
        """Get price trend analysis for a product."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        prices = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= start_date,
            PriceHistory.is_available == True
        ).order_by(PriceHistory.recorded_at).all()
        
        if len(prices) < 2:
            return {
                'trend': 'stable',
                'change_percentage': 0.0,
                'change_amount': 0.0,
                'data_points': len(prices)
            }
        
        price_values = [p.price for p in prices]
        first_price = price_values[0]
        last_price = price_values[-1]
        
        change_amount = last_price - first_price
        change_percentage = (change_amount / first_price) * 100 if first_price > 0 else 0
        
        if abs(change_percentage) < 5:
            trend = 'stable'
        elif change_percentage > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'change_percentage': round(change_percentage, 2),
            'change_amount': round(change_amount, 2),
            'data_points': len(prices),
            'avg_price': round(statistics.mean(price_values), 2),
            'min_price': min(price_values),
            'max_price': max(price_values)
        }
    
    @staticmethod
    def compare_prices(db: Session, product_id: int) -> Dict:
        """Compare prices across different stores for a product."""
        prices = db.query(Price).filter(
            Price.product_id == product_id,
            Price.is_available == True
        ).order_by(Price.price).all()
        
        if not prices:
            return {
                'product_id': product_id,
                'stores': [],
                'lowest_price': None,
                'highest_price': None,
                'price_difference': None
            }
        
        store_prices = []
        for price in prices:
            store_prices.append({
                'store_id': price.store_id,
                'store_name': price.store.name if price.store else 'Unknown',
                'price': price.price,
                'original_price': price.original_price,
                'is_discounted': price.is_discounted,
                'discount_percentage': price.discount_percentage,
                'last_updated': price.scraped_at
            })
        
        price_values = [p.price for p in prices]
        lowest = min(price_values)
        highest = max(price_values)
        
        return {
            'product_id': product_id,
            'stores': store_prices,
            'lowest_price': lowest,
            'highest_price': highest,
            'price_difference': round(highest - lowest, 2),
            'average_price': round(statistics.mean(price_values), 2)
        }