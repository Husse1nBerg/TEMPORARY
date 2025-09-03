from typing import List, Optional
import logging
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult

logger = logging.getLogger(__name__)


class RabbitScraper(BaseScraper):
    """Scraper for Rabbit (RabbitMart) delivery service."""
    
    def __init__(self):
        super().__init__(
            store_name="Rabbit",
            base_url="https://rabbit.com.eg/"
        )
        
        # Rabbit-specific selectors
        self.product_grid_selector = '.product-item, .product-card, .item-card'
        self.product_title_selector = '.product-name, .item-name, h3, .product-title'
        self.product_price_selector = '.price, .current-price, .product-price'
        self.original_price_selector = '.old-price, .original-price, .was-price'
        self.product_link_selector = 'a'
        self.product_image_selector = 'img'
        self.out_of_stock_selector = '.out-of-stock, .unavailable, .sold-out'
        self.sale_badge_selector = '.sale, .discount, .offer, .promotion'
        
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        category_urls = [
            '/categories/fresh-vegetables',
            '/categories/fresh-fruits',
            '/categories/dairy-eggs',
            '/categories/meat-poultry',
            '/categories/bakery-bread',
            '/categories/beverages',
            '/categories/pantry-essentials',
            '/categories/frozen-foods',
            '/categories/snacks-sweets',
            '/categories/personal-care',
            '/categories/household-items'
        ]
        
        return [self.make_absolute_url(url) for url in category_urls]
    
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """Scrape products from Rabbit."""
        if category_urls is None:
            category_urls = await self.get_category_urls()
        
        all_products = []
        pages_scraped = 0
        
        for category_url in category_urls:
            try:
                logger.info(f"Scraping Rabbit category: {category_url}")
                
                if not await self.navigate_to_url(category_url):
                    self.errors.append(f"Failed to navigate to {category_url}")
                    continue
                
                # Wait for products to load
                try:
                    await self.page.wait_for_selector(self.product_grid_selector, timeout=15000)
                except PlaywrightTimeoutError:
                    logger.warning(f"No products found in {category_url}")
                    continue
                
                # Handle scrolling and loading
                await self.handle_infinite_scroll()
                
                # Extract products
                products = await self.extract_products_from_page()
                all_products.extend(products)
                pages_scraped += 1
                
                logger.info(f"Found {len(products)} products in {category_url}")
                await self.random_delay()
                
            except Exception as e:
                error_msg = f"Error scraping Rabbit category {category_url}: {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                continue
        
        return ScraperResult(
            success=len(all_products) > 0,
            products=all_products,
            errors=self.errors,
            pages_scraped=pages_scraped,
            duration_seconds=0
        )
    
    async def handle_infinite_scroll(self):
        """Handle infinite scroll for Rabbit."""
        try:
            last_height = await self.page.evaluate("document.body.scrollHeight")
            
            for _ in range(4):  # Max 4 scrolls
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during Rabbit scrolling: {e}")
    
    async def extract_products_from_page(self) -> List[ScrapedProduct]:
        """Extract all products from current page."""
        products = []
        
        try:
            product_elements = await self.page.query_selector_all(self.product_grid_selector)
            logger.info(f"Found {len(product_elements)} product elements")
            
            for element in product_elements:
                try:
                    product = await self.extract_product_from_element(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error extracting Rabbit product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting product elements from Rabbit: {e}")
        
        return products
    
    async def extract_product_from_element(self, element) -> Optional[ScrapedProduct]:
        """Extract product data from a product element."""
        try:
            # Extract name
            name_element = await element.query_selector(self.product_title_selector)
            if not name_element:
                return None
            
            name = await name_element.text_content()
            name = self.clean_text(name)
            
            if not name:
                return None
            
            # Extract price
            price_element = await element.query_selector(self.product_price_selector)
            if not price_element:
                return None
            
            price_text = await price_element.text_content()
            price = self.clean_price(price_text)
            
            if price <= 0:
                return None
            
            # Extract original price
            original_price = None
            original_price_element = await element.query_selector(self.original_price_selector)
            if original_price_element:
                original_price_text = await original_price_element.text_content()
                original_price = self.clean_price(original_price_text)
                if original_price <= price:
                    original_price = None
            
            # Extract product URL
            link_element = await element.query_selector(self.product_link_selector)
            product_url = None
            if link_element:
                href = await link_element.get_attribute('href')
                if href:
                    product_url = self.make_absolute_url(href)
            
            # Extract image URL
            image_element = await element.query_selector(self.product_image_selector)
            image_url = None
            if image_element:
                src = await image_element.get_attribute('src') or await image_element.get_attribute('data-src')
                if src:
                    image_url = self.make_absolute_url(src)
            
            # Check availability
            out_of_stock_element = await element.query_selector(self.out_of_stock_selector)
            is_available = out_of_stock_element is None
            
            # Check if on sale
            sale_element = await element.query_selector(self.sale_badge_selector)
            is_on_sale = sale_element is not None
            is_discounted = original_price is not None
            
            # Extract product ID
            external_id = None
            if product_url:
                external_id = self.extract_product_id(product_url)
            
            # Determine category
            category = self.extract_category_from_url()
            
            # Extract weight/size information
            weight_value, weight_unit = self.extract_weight_info(name)
            
            # Extract brand
            brand = self.extract_brand_from_name(name)
            
            product = ScrapedProduct(
                name=name,
                price=price,
                original_price=original_price,
                category=category,
                brand=brand,
                image_url=image_url,
                product_url=product_url,
                external_id=external_id,
                is_available=is_available,
                is_discounted=is_discounted,
                is_on_sale=is_on_sale,
                weight_value=weight_value,
                weight_unit=weight_unit,
                keywords=self.generate_keywords(name)
            )
            
            return product
            
        except Exception as e:
            logger.warning(f"Error extracting Rabbit product from element: {e}")
            return None
    
    def extract_category_from_url(self) -> str:
        """Extract category from current URL."""
        try:
            current_url = self.page.url
            if '/categories/' in current_url:
                category_slug = current_url.split('/categories/')[-1].split('/')[0]
                
                category_mapping = {
                    'fresh-vegetables': 'vegetables',
                    'fresh-fruits': 'fruits',
                    'dairy-eggs': 'dairy',
                    'meat-poultry': 'meat',
                    'bakery-bread': 'bakery',
                    'beverages': 'beverages',
                    'pantry-essentials': 'pantry',
                    'frozen-foods': 'frozen',
                    'snacks-sweets': 'snacks',
                    'personal-care': 'personal-care',
                    'household-items': 'household'
                }
                
                return category_mapping.get(category_slug, 'pantry')
        except:
            pass
        
        return 'pantry'
    
    def extract_brand_from_name(self, name: str) -> Optional[str]:
        """Extract brand name from product name."""
        if not name:
            return None
        
        known_brands = [
            'Rabbit', 'Almarai', 'Juhayna', 'Domty', 'Beyti', 'Nada',
            'Americana', 'McCain', 'Green Land', 'Panda', 'Molto'
        ]
        
        name_upper = name.upper()
        for brand in known_brands:
            if brand.upper() in name_upper:
                return brand
        
        # Try first word
        words = name.split()
        if len(words) > 1 and len(words[0]) > 2:
            return words[0]
        
        return None
    
    def generate_keywords(self, name: str) -> List[str]:
        """Generate keywords from product name."""
        if not name:
            return []
        
        words = name.lower().replace(',', ' ').replace('-', ' ').split()
        keywords = []
        
        stop_words = {'the', 'and', 'or', 'with', 'from', 'per', 'pack', 'piece'}
        
        for word in words:
            word = word.strip()
            if len(word) > 2 and word not in stop_words and not word.isdigit():
                keywords.append(word)
        
        return keywords[:8]
    
    async def extract_product_data(self) -> Optional[ScrapedProduct]:
        """Extract product data from current page."""
        try:
            return None
        except Exception as e:
            logger.error(f"Error extracting Rabbit product data: {e}")
            return None