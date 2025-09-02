"""
Metro Market Scraper
Scrapes product data from https://www.metro-markets.com/
Path: backend/app/scrapers/metro_scraper.py
"""

from typing import List, Optional
from decimal import Decimal
import logging
import asyncio
from app.scrapers.base_scraper import BaseScraper, ProductData

logger = logging.getLogger(__name__)

class MetroScraper(BaseScraper):
    """Scraper for Metro Market website"""
    
    def __init__(self):
        super().__init__(
            store_name="Metro",
            base_url="https://www.metro-markets.com/"
        )
    
    async def search_product(self, product_name: str) -> List[ProductData]:
        """Search for a specific product on Metro"""
        products = []
        
        try:
            # Navigate to search or category
            search_url = f"{self.base_url}search?q={product_name.replace(' ', '+')}"
            await self.page.goto(search_url, wait_until='domcontentloaded')
            await self.wait_for_page_load()
            
            # Wait for products
            await self.page.wait_for_selector('.product-item, .product-card', timeout=10000)
            
            # Get product elements
            product_elements = await self.page.query_selector_all('.product-item, .product-card')
            
            for element in product_elements[:10]:
                product = await self._extract_product_data(element)
                if product and self.match_product(product.name):
                    products.append(product)
                    
        except Exception as e:
            logger.error(f"Error searching for {product_name} on {self.store_name}: {e}")
        
        return products
    
    async def scrape_all_products(self) -> List[ProductData]:
        """Scrape all tracked products from Metro"""
        all_products = []
        
        try:
            await self.handle_cookies_popup()
            
            # Navigate to fresh produce sections
            categories = [
                '/fresh-vegetables',
                '/fresh-fruits',
                '/organic'
            ]
            
            for category_url in categories:
                try:
                    full_url = self.base_url.rstrip('/') + category_url
                    logger.info(f"Scraping Metro category: {full_url}")
                    
                    await self.page.goto(full_url, wait_until='domcontentloaded')
                    await self.wait_for_page_load()
                    await self.scroll_to_load_more(max_scrolls=3)
                    
                    # Get product elements
                    product_elements = await self.page.query_selector_all(
                        '.product-item, .product-card, [data-product]'
                    )
                    
                    for element in product_elements:
                        product = await self._extract_product_data(element)
                        if product:
                            matched = self.match_product(product.name)
                            if matched:
                                product.category = f"Category {matched['category']}"
                                all_products.append(product)
                                logger.info(f"Found: {product.name} - {product.price} EGP")
                    
                except Exception as e:
                    logger.error(f"Error scraping Metro category {category_url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping Metro: {e}")
        
        return all_products
    
    async def _extract_product_data(self, element) -> Optional[ProductData]:
        """Extract product data from element"""
        try:
            product = ProductData()
            product.store_name = self.store_name
            
            # Extract name
            name_element = await element.query_selector(
                '.product-name, .product-title, h3, h4, [class*="title"]'
            )
            if name_element:
                product.name = (await name_element.inner_text()).strip()
            
            if not product.name:
                return None
            
            # Extract price
            price_element = await element.query_selector(
                '.price, .product-price, [class*="price"]:not([class*="old"])'
            )
            if price_element:
                price_text = await price_element.inner_text()
                product.price = self.clean_price(price_text)
            
            # Check for discount
            old_price_element = await element.query_selector(
                '.old-price, .original-price, s, del'
            )
            if old_price_element:
                old_price_text = await old_price_element.inner_text()
                product.original_price = self.clean_price(old_price_text)
                product.is_discounted = True
            
            # Extract size
            size_element = await element.query_selector(
                '.weight, .size, .pack-size, [class*="weight"]'
            )
            if size_element:
                size_text = await size_element.inner_text()
                product.pack_size, product.pack_unit = self._parse_size(size_text)
            
            # Calculate price per kg
            if product.pack_size and product.pack_unit:
                product.price_per_kg = self.calculate_price_per_kg(
                    product.price, product.pack_size, product.pack_unit
                )
            
            # Check organic
            full_text = await element.inner_text()
            product.is_organic = self.detect_organic(full_text)
            
            # Check availability
            out_of_stock = await element.query_selector(
                '.out-of-stock, .unavailable, [class*="out-of-stock"]'
            )
            product.is_available = out_of_stock is None
            
            # Get URL
            link = await element.query_selector('a[href*="/product"]')
            if link:
                href = await link.get_attribute('href')
                product.product_url = self.base_url + href if href.startswith('/') else href
            
            # Get image
            img = await element.query_selector('img')
            if img:
                product.image_url = await img.get_attribute('src')
            
            return product
            
        except Exception as e:
            logger.error(f"Error extracting Metro product data: {e}")
            return None
    
    def _parse_size(self, text: str) -> tuple:
        """Parse size and unit from text"""
        import re
        
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|كجم)',
            r'(\d+(?:\.\d+)?)\s*(g|جم|gram)',
            r'(\d+)\s*(piece|pcs|قطعة)',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1), match.group(2)
        
        return "", ""