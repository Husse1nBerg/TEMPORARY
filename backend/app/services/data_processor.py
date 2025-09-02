"""
Data Processor Service
Path: backend/app/services/data_processor.py
"""

from typing import List, Dict
from decimal import Decimal
import re
from app.scrapers.base_scraper import ProductData

class DataProcessor:
    """
    Processes raw scraped data before saving to the database.
    - Cleans data (removes extra whitespace, etc.)
    - Normalizes data (e.g., calculates price per kg)
    - Enriches data (e.g., classifies products)
    """

    def __init__(self, raw_data: List[ProductData]):
        self.raw_data = raw_data
        self.processed_data: List[ProductData] = []

    def process(self) -> List[ProductData]:
        """
        Main processing method.
        """
        for item in self.raw_data:
            processed_item = self._process_item(item)
            if processed_item:
                self.processed_data.append(processed_item)
        
        return self.processed_data

    def _process_item(self, item: ProductData) -> ProductData | None:
        """
        Process a single product data item.
        """
        # Clean name
        item.name = self._clean_text(item.name)
        
        # Validate price
        if not isinstance(item.price, Decimal) or item.price <= 0:
            return None # Skip items with invalid prices

        # Normalize pack size and unit
        item.pack_size, item.pack_unit = self._normalize_pack_size(item.name, item.pack_size, item.pack_unit)

        # Recalculate price per kg if needed
        if item.price_per_kg is None and item.pack_size and item.pack_unit:
            item.price_per_kg = self._calculate_price_per_kg(
                item.price, item.pack_size, item.pack_unit
            )
            
        return item

    def _clean_text(self, text: str) -> str:
        """
        Remove extra whitespace and special characters from text.
        """
        return re.sub(r'\s+', ' ', text).strip()

    def _normalize_pack_size(self, name: str, pack_size: str, pack_unit: str) -> tuple[str, str]:
        """
        Standardize pack size and unit.
        """
        # Attempt to extract from name if not present
        if not pack_size:
            match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|gm|kilo|gram)', name, re.IGNORECASE)
            if match:
                pack_size = match.group(1)
                pack_unit = match.group(2)

        # Normalize units
        if pack_unit:
            unit_lower = pack_unit.lower()
            if unit_lower in ['g', 'gm', 'gram']:
                pack_unit = 'g'
            elif unit_lower in ['kg', 'kilo']:
                pack_unit = 'kg'

        return pack_size, pack_unit

    def _calculate_price_per_kg(self, price: Decimal, size: str, unit: str) -> Decimal | None:
        """
        Calculate price per kilogram.
        """
        try:
            size_val = Decimal(size)
            if unit == 'g':
                return (price / size_val) * 1000
            elif unit == 'kg':
                return price / size_val
        except:
            return None

        return None