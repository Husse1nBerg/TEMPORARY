"""
Price calculation utilities
Path: backend/app/utils/price_calculator.py
"""

from decimal import Decimal
from typing import Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class PriceCalculator:
    """Utility class for price calculations and conversions"""
    
    # Conversion factors to kilograms
    UNIT_CONVERSIONS = {
        'kg': 1.0,
        'كجم': 1.0,
        'كيلو': 1.0,
        'kilogram': 1.0,
        'g': 0.001,
        'جم': 0.001,
        'جرام': 0.001,
        'gram': 0.001,
        'gm': 0.001,
        'mg': 0.000001,
        'lb': 0.453592,
        'pound': 0.453592,
        'oz': 0.0283495,
        'ounce': 0.0283495,
        'l': 1.0,  # Assuming 1L = 1kg for liquids
        'liter': 1.0,
        'ml': 0.001,
        'milliliter': 0.001,
    }
    
    @staticmethod
    def calculate_price_per_kg(
        price: float,
        size: str,
        unit: str
    ) -> Optional[float]:
        """
        Calculate price per kilogram
        
        Args:
            price: Product price
            size: Size value (e.g., "500", "1.5")
            unit: Unit of measurement (e.g., "g", "kg", "lb")
        
        Returns:
            Price per kilogram or None if cannot calculate
        """
        try:
            # Clean and convert size to float
            size_value = float(re.sub(r'[^\d.]', '', str(size)))
            
            # Get conversion factor
            unit_lower = unit.lower().strip()
            conversion_factor = PriceCalculator.UNIT_CONVERSIONS.get(unit_lower)
            
            if not conversion_factor:
                logger.warning(f"Unknown unit: {unit}")
                return None
            
            # Calculate weight in kg
            weight_in_kg = size_value * conversion_factor
            
            if weight_in_kg <= 0:
                return None
            
            # Calculate price per kg
            price_per_kg = price / weight_in_kg
            
            return round(price_per_kg, 2)
            
        except Exception as e:
            logger.error(f"Error calculating price per kg: {e}")
            return None
    
    @staticmethod
    def parse_size_from_text(text: str) -> Tuple[str, str]:
        """
        Extract size and unit from product text
        
        Args:
            text: Product text containing size information
        
        Returns:
            Tuple of (size, unit) or ("", "") if not found
        """
        # Common patterns for size extraction
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|كجم|كيلو)',
            r'(\d+(?:\.\d+)?)\s*(g|gm|gram|جم|جرام)',
            r'(\d+(?:\.\d+)?)\s*(lb|pound)',
            r'(\d+(?:\.\d+)?)\s*(l|liter|لتر)',
            r'(\d+(?:\.\d+)?)\s*(ml|milliliter|مل)',
            r'(\d+)\s*(piece|pcs|قطعة)',
            r'(\d+)\s*(pack|bundle)',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                size = match.group(1)
                unit = match.group(2)
                
                # Normalize units
                unit_mappings = {
                    'كجم': 'kg',
                    'كيلو': 'kg',
                    'جم': 'g',
                    'جرام': 'g',
                    'gm': 'g',
                    'gram': 'g',
                    'لتر': 'l',
                    'مل': 'ml',
                    'قطعة': 'piece',
                    'pcs': 'piece',
                }
                
                unit = unit_mappings.get(unit, unit)
                return size, unit
        
        return "", ""
    
    @staticmethod
    def calculate_discount_percentage(
        original_price: float,
        discounted_price: float
    ) -> float:
        """
        Calculate discount percentage
        
        Args:
            original_price: Original price before discount
            discounted_price: Price after discount
        
        Returns:
            Discount percentage
        """
        if original_price <= 0:
            return 0.0
        
        discount = original_price - discounted_price
        percentage = (discount / original_price) * 100
        
        return round(percentage, 2)
    
    @staticmethod
    def clean_price_text(price_text: str) -> float:
        """
        Clean and extract numeric price from text
        
        Args:
            price_text: Price text with currency symbols and text
        
        Returns:
            Numeric price value
        """
        try:
            # Remove common currency symbols and text
            price_text = re.sub(r'[^\d.,]', '', price_text)
            
            # Handle different decimal separators
            # Replace comma with dot for decimal
            price_text = price_text.replace(',', '.')
            
            # Remove multiple dots except the last one
            parts = price_text.split('.')
            if len(parts) > 2:
                price_text = ''.join(parts[:-1]) + '.' + parts[-1]
            
            return float(price_text)
            
        except Exception as e:
            logger.error(f"Error cleaning price '{price_text}': {e}")
            return 0.0