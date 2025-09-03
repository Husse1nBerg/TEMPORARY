from typing import List, Optional
import logging
import asyncio
import json
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult

logger = logging.getLogger(__name__)


class RDNAScraper(BaseScraper):
    """Scraper for RDNA (Real DNA) pharmacy and health products."""
    
    def __init__(self):
        super().__init__(
            store_name="RDNA",
            base_url="https://rdna.com.eg/"
        )
        
        # RDNA-specific selectors
        self.product_grid_selector = '.product-item, .product-card, .product-tile'
        self.product_title_selector = '.product-name, .product-title, h3'
        self.product_price_selector = '.price, .current-price, .product-price'
        self.original_price_selector = '.old-price, .was-price, .strike-price'
        self.product_link_selector = 'a'
        self.product_image_selector = 'img'
        self.out_of_stock_selector = '.out-of-stock, .unavailable, .not-available'
        self.sale_badge_selector = '.sale, .discount, .offer, .promo'
        
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        category_urls = [
            '/categories/vitamins-supplements',
            '/categories/baby-care',
            '/categories/personal-care',
            '/categories/skin-care',
            '/categories/hair-care',
            '/categories/oral-care',
            '/categories/medical-devices',
            '/categories/over-the-counter',
            '/categories/health-nutrition',
            '/categories/cosmetics-beauty',
            '/categories/first-aid',
            '/categories/wellness-fitness'
        ]
        
        return [self.make_absolute_url(url) for url in category_urls]
    
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """Scrape products from RDNA."""
        if category_urls is None:
            category_urls = await self.get_category_urls()
        
        all_products = []
        pages_scraped = 0
        
        for category_url in category_urls:
            try:
                logger.info(f"Scraping RDNA category: {category_url}")
                
                if not await self.navigate_to_url(category_url):
                    self.errors.append(f"Failed to navigate to {category_url}")
                    continue
                
                # Wait for products to load
                try:
                    await self.page.wait_for_selector(self.product_grid_selector, timeout=15000)
                except PlaywrightTimeoutError:
                    logger.warning(f"No products found in {category_url}")
                    continue
                
                # Handle pagination
                await self.handle_rdna_pagination()
                
                # Extract products
                products = await self.extract_products_from_page()
                all_products.extend(products)
                pages_scraped += 1
                
                logger.info(f"Found {len(products)} products in {category_url}")
                await self.random_delay()
                
            except Exception as e:
                error_msg = f"Error scraping RDNA category {category_url}: {e}"
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
    
    async def handle_rdna_pagination(self):
        """Handle RDNA pagination system."""
        try:
            page_count = 0
            max_pages = 3
            
            while page_count < max_pages:
                # Scroll to load more products
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                # Look for pagination buttons
                next_btn = await self.page.query_selector('.pagination-next, .next-page, [aria-label="Next"]')
                if next_btn and await next_btn.is_enabled():
                    try:
                        await next_btn.click()
                        await asyncio.sleep(3)
                        page_count += 1
                        continue
                    except:
                        break
                
                # Look for load more button
                load_more = await self.page.query_selector('.load-more, .show-more')
                if load_more:
                    try:
                        await load_more.click()
                        await asyncio.sleep(3)
                        page_count += 1
                        continue
                    except:
                        break
                
                break
                
        except Exception as e:
            logger.warning(f"Error during RDNA pagination: {e}")
    
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
                    logger.warning(f"Error extracting RDNA product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting product elements from RDNA: {e}")
        
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
            
            # Determine category (health/pharmacy products)
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
            logger.warning(f"Error extracting RDNA product from element: {e}")
            return None
    
    def extract_category_from_url(self) -> str:
        """Extract category from current URL."""
        try:
            current_url = self.page.url
            if '/categories/' in current_url:
                category_slug = current_url.split('/categories/')[-1].split('/')[0]
                
                # Map health/pharmacy categories
                category_mapping = {
                    'vitamins-supplements': 'health',
                    'baby-care': 'baby-care',
                    'personal-care': 'personal-care',
                    'skin-care': 'personal-care',
                    'hair-care': 'personal-care',
                    'oral-care': 'personal-care',
                    'medical-devices': 'health',
                    'over-the-counter': 'health',
                    'health-nutrition': 'health',
                    'cosmetics-beauty': 'personal-care',
                    'first-aid': 'health',
                    'wellness-fitness': 'health'
                }
                
                return category_mapping.get(category_slug, 'health')
        except:
            pass
        
        return 'health'
    
    def extract_brand_from_name(self, name: str) -> Optional[str]:
        """Extract brand name from product name."""
        if not name:
            return None
        
        # Common pharmacy/health brands
        known_brands = [
            'Johnson\'s', 'Neutrogena', 'Nivea', 'Garnier', 'L\'Oreal',
            'Olay', 'Dove', 'Vaseline', 'Eucerin', 'Cetaphil',
            'Vichy', 'La Roche-Posay', 'Avene', 'Sebamed', 'Mustela',
            'Bepanthen', 'Bepanthol', 'Pharmaceris', 'SVR', 'RDNA'
        ]
        
        name_upper = name.upper()
        for brand in known_brands:
            if brand.upper() in name_upper:
                return brand
        
        # Try first word as brand
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
        
        stop_words = {'the', 'and', 'or', 'with', 'from', 'for', 'ml', 'mg', 'g'}
        
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
            logger.error(f"Error extracting RDNA product data: {e}")
            return None