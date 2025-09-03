# In husse1nberg/temporary/TEMPORARY-1d5658443074cfe4adffd6ffbe88de9df95c4942/backend/app/scrapers/rabbit_scraper.py
"""
Rabbit Mart Scraper
Scrapes product data from https://www.rabbitmart.com/
Path: backend/app/scrapers/rabbit_scraper.py
"""

from typing import List, Optional
from decimal import Decimal
import logging
import asyncio
from app.scrapers.base_scraper import BaseScraper, ProductData

logger = logging.getLogger(__name__)

class RabbitScraper(BaseScraper):
    """Scraper for Rabbit Mart website"""

    def __init__(self):
        super().__init__(
            store_name="Rabbit",
            base_url="https://www.rabbitmart.com/eg/"
        )

    async def search_product(self, product_name: str) -> List[ProductData]:
        """Search for a specific product on Rabbit Mart"""
        products = []
        try:
            search_url = f"{self.base_url}search?q={product_name.replace(' ', '+')}"
            await self.page.goto(search_url, wait_until='domcontentloaded')
            await self.wait_for_page_load()

            await self.page.wait_for_selector('.product-grid .product-item', timeout=10000)
            product_elements = await self.page.query_selector_all('.product-grid .product-item')

            for element in product_elements[:10]:
                product = await self._extract_product_data(element)
                if product and self.match_product(product.name):
                    products.append(product)
        except Exception as e:
            logger.error(f"Error searching Rabbit Mart: {e}")
        return products

    async def scrape_all_products(self) -> List[ProductData]:
        """Scrape all tracked products from Rabbit Mart"""
        all_products = []
        categories = [
            'fruits-vegetables',
            'organic-food'
        ]
        try:
            for category_url in categories:
                full_url = self.base_url + category_url
                await self.page.goto(full_url, wait_until='domcontentloaded')
                await self.wait_for_page_load()
                await self.scroll_to_load_more(max_scrolls=5)

                product_elements = await self.page.query_selector_all('.product-grid .product-item')
                for element in product_elements:
                    product = await self._extract_product_data(element)
                    if product and self.match_product(product.name):
                        all_products.append(product)
        except Exception as e:
            logger.error(f"Error scraping Rabbit Mart: {e}")

        return all_products

    async def _extract_product_data(self, element) -> Optional[ProductData]:
        """Extract product data from element"""
        try:
            product = ProductData()
            product.store_name = self.store_name

            name_element = await element.query_selector('.product-name')
            if name_element:
                product.name = (await name_element.inner_text()).strip()

            if not product.name:
                return None

            price_element = await element.query_selector('.price-after-discount')
            if not price_element:
                price_element = await element.query_selector('.product-price')

            if price_element:
                price_text = await price_element.inner_text()
                product.price = self.clean_price(price_text)

            size_element = await element.query_selector('.product-weight')
            if size_element:
                size_text = await size_element.inner_text()
                product.pack_size, product.pack_unit = self._parse_size(size_text)

            if product.pack_size and product.pack_unit:
                product.price_per_kg = self.calculate_price_per_kg(
                    product.price, product.pack_size, product.pack_unit
                )

            out_of_stock_element = await element.query_selector('.out-of-stock-label')
            product.is_available = out_of_stock_element is None
            
            return product
        except Exception as e:
            logger.error(f"Error extracting Rabbit Mart product data: {e}")
            return None

    def _parse_size(self, text: str) -> tuple:
        """Parse size and unit from text"""
        import re
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|g|gm|kilo|gram)',
            r'(\d+)\s*(piece|pcs)',
        ]
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1), match.group(2)
        return "", ""