"""
Gourmet Egypt Scraper
Scrapes product data from https://gourmetegypt.com/
"""

from typing import List, Optional
from decimal import Decimal
import logging
import asyncio
from app.scrapers.base_scraper import BaseScraper, ProductData

logger = logging.getLogger(__name__)

class GourmetScraper(BaseScraper):
    """Scraper for Gourmet Egypt website"""
    
    def __init__(self):
        super().__init__(
            store_name="Gourmet Egypt",
            base_url="https://gourmetegypt.com/"
        )
    
    async def search_product(self, product_name: str) -> List[ProductData]:
        """Search for a specific product on Gourmet Egypt"""
        products = []
        
        try:
            # Use the search functionality
            search_url = f"{self.base_url}search?q={product_name.replace(' ', '+')}"
            await self.page.goto(search_url, wait_until='domcontentloaded')
            await self.wait_for_page_load()
            
            # Wait for products to load
            await self.page.wait_for_selector('.product-item', timeout=10000)
            
            # Get all product cards
            product_elements = await self.page.query_selector_all('.product-item')
            
            for element in product_elements[:10]:  # Limit to first 10 results
                product = await self._extract_product_data(element)
                if product and self.match_product(product.name):
                    products.append(product)
                    
        except Exception as e:
            logger.error(f"Error searching for {product_name} on {self.store_name}: {e}")
        
        return products
    
    async def scrape_all_products(self) -> List[ProductData]:
        """Scrape all tracked products from Gourmet Egypt"""
        all_products = []
        
        try:
            # Handle cookie consent if present
            await self.handle_cookies_popup()
            
            # Navigate to fresh produce category
            categories = [
                '/collections/fresh-vegetables',
                '/collections/fresh-herbs',
                '/collections/organic-produce'
            ]
            
            for category_url in categories:
                try:
                    full_url = self.base_url.rstrip('/') + category_url
                    logger.info(f"Scraping category: {full_url}")
                    
                    await self.page.goto(full_url, wait_until='domcontentloaded')
                    await self.wait_for_page_load()
                    
                    # Scroll to load all products
                    await self.scroll_to_load_more(max_scrolls=3)
                    
                    # Wait for products to load
                    await self.page.wait_for_selector('.product-item, .product-card, [data-product-id]', timeout=10000)
                    
                    # Get all product elements (try multiple selectors)
                    product_selectors = [
                        '.product-item',
                        '.product-card',
                        '[data-product-id]',
                        '.grid-item',
                        '.collection-product'
                    ]
                    
                    product_elements = []
                    for selector in product_selectors:
                        elements = await self.page.query_selector_all(selector)
                        if elements:
                            product_elements = elements
                            logger.info(f"Found {len(elements)} products using selector: {selector}")
                            break
                    
                    # Extract data from each product
                    for element in product_elements:
                        product = await self._extract_product_data(element)
                        if product:
                            # Check if it matches our tracked products
                            matched = self.match_product(product.name)
                            if matched:
                                product.category = f"Category {matched['category']}"
                                all_products.append(product)
                                logger.info(f"Found tracked product: {product.name} - Price: {product.price}")
                    
                except Exception as e:
                    logger.error(f"Error scraping category {category_url}: {e}")
                    continue
            
            # Also search for specific products that might not be in categories
            for product_info in self.products_to_track:
                if not any(p.name == product_info['name'] for p in all_products):
                    logger.info(f"Searching for missing product: {product_info['name']}")
                    search_results = await self.search_product(product_info['name'])
                    all_products.extend(search_results)
                    
        except Exception as e:
            logger.error(f"Error scraping all products from {self.store_name}: {e}")
        
        return all_products
    
    async def _extract_product_data(self, element) -> Optional[ProductData]:
        """Extract product data from a product element"""
        try:
            product = ProductData()
            product.store_name = self.store_name
            
            # Try multiple selectors for product name
            name_selectors = [
                '.product-title',
                '.product-name',
                'h3',
                'h4',
                '.title',
                'a[href*="/products/"]'
            ]
            
            for selector in name_selectors:
                name_element = await element.query_selector(selector)
                if name_element:
                    product.name = await name_element.inner_text()
                    product.name = product.name.strip()
                    break
            
            if not product.name:
                return None
            
            # Extract price
            price_selectors = [
                '.product-price',
                '.price',
                '.money',
                '[class*="price"]',
                'span:has-text("EGP")',
                'span:has-text("LE")'
            ]
            
            for selector in price_selectors:
                price_element = await element.query_selector(selector)
                if price_element:
                    price_text = await price_element.inner_text()
                    product.price = self.clean_price(price_text)
                    if product.price > 0:
                        break
            
            # Check for original price (discounted items)
            original_price_selectors = [
                '.compare-at-price',
                '.was-price',
                's',
                'del',
                '.original-price'
            ]
            
            for selector in original_price_selectors:
                original_price_element = await element.query_selector(selector)
                if original_price_element:
                    original_price_text = await original_price_element.inner_text()
                    product.original_price = self.clean_price(original_price_text)
                    if product.original_price > product.price:
                        product.is_discounted = True
                    break
            
            # Extract pack size and unit
            size_selectors = [
                '.product-weight',
                '.product-size',
                '.weight',
                '.size',
                'small:has-text("kg")',
                'small:has-text("g")',
                'span:has-text("kg")',
                'span:has-text("gram")'
            ]
            
            for selector in size_selectors:
                size_element = await element.query_selector(selector)
                if size_element:
                    size_text = await size_element.inner_text()
                    product.pack_size, product.pack_unit = self._parse_size(size_text)
                    if product.pack_size:
                        break
            
            # If no size found in separate element, try to extract from name
            if not product.pack_size:
                product.pack_size, product.pack_unit = self._parse_size(product.name)
            
            # Calculate price per kg
            if product.pack_size and product.pack_unit:
                product.price_per_kg = self.calculate_price_per_kg(
                    product.price, 
                    product.pack_size, 
                    product.pack_unit
                )
            
            # Check if organic
            full_text = await element.inner_text()
            product.is_organic = self.detect_organic(full_text)
            
            # Check availability
            out_of_stock_selectors = [
                '.out-of-stock',
                '.sold-out',
                'button:has-text("Out of Stock")',
                'button:has-text("Sold Out")',
                '[class*="unavailable"]'
            ]
            
            for selector in out_of_stock_selectors:
                oos_element = await element.query_selector(selector)
                if oos_element:
                    product.is_available = False
                    break
            
            # Get product URL
            link_element = await element.query_selector('a[href*="/products/"]')
            if link_element:
                href = await link_element.get_attribute('href')
                if href:
                    product.product_url = self.base_url.rstrip('/') + href if href.startswith('/') else href
            
            # Get image URL
            img_element = await element.query_selector('img')
            if img_element:
                product.image_url = await img_element.get_attribute('src')
                if product.image_url and product.image_url.startswith('//'):
                    product.image_url = 'https:' + product.image_url
            
            return product
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None
    
    def _parse_size(self, text: str) -> tuple:
        """Parse size and unit from text"""
        import re
        
        # Common patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|كجم|كيلو)',
            r'(\d+(?:\.\d+)?)\s*(g|gm|gram|جم|جرام)',
            r'(\d+(?:\.\d+)?)\s*(lb|pound)',
            r'(\d+)\s*(piece|pcs|قطعة)',
            r'(\d+(?:\.\d+)?)\s*(ml|liter|l)',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                size = match.group(1)
                unit = match.group(2)
                
                # Normalize units
                if unit in ['كجم', 'كيلو']:
                    unit = 'kg'
                elif unit in ['جم', 'جرام', 'gm', 'gram']:
                    unit = 'g'
                elif unit in ['قطعة', 'piece', 'pcs']:
                    unit = 'piece'
                    
                return size, unit
        
        return "", ""