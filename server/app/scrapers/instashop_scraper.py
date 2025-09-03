from typing import List, Optional
import logging
import asyncio
import json
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult

logger = logging.getLogger(__name__)


class InstashopScraper(BaseScraper):
    """Scraper for Instashop delivery service."""
    
    def __init__(self):
        super().__init__(
            store_name="Instashop",
            base_url="https://instashop.com.eg/"
        )
        
        # Instashop-specific selectors
        self.product_grid_selector = '.product-item, .product-card, [data-cy="product-item"]'
        self.product_title_selector = '.product-name, .product-title, [data-cy="product-name"]'
        self.product_price_selector = '.product-price, .price-current, [data-cy="product-price"]'
        self.original_price_selector = '.price-original, .price-before, .old-price'
        self.product_link_selector = 'a'
        self.product_image_selector = 'img'
        self.out_of_stock_selector = '.out-of-stock, .unavailable, [data-cy="out-of-stock"]'
        self.sale_badge_selector = '.sale-badge, .discount, .offer'
        self.store_selector = '.store-name, [data-cy="store-name"]'
        
        # Instashop aggregates multiple stores
        self.target_stores = [
            'Carrefour', 'Spinneys', 'Metro', 'Alfa Market', 
            'Oscar', 'Seoudi Market', 'Fresh Market'
        ]
        
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        category_urls = [
            '/category/fresh-produce',
            '/category/fruits-vegetables',
            '/category/dairy-eggs',
            '/category/meat-poultry-seafood',
            '/category/bakery',
            '/category/pantry',
            '/category/beverages',
            '/category/frozen',
            '/category/snacks-confectionery',
            '/category/health-beauty',
            '/category/household-cleaning'
        ]
        
        return [self.make_absolute_url(url) for url in category_urls]
    
    async def setup_location_and_store(self):
        """Set location and select preferred stores."""
        try:
            # Set delivery location to Cairo
            location_btn = await self.page.query_selector('[data-cy="location-button"], .location-selector')
            if location_btn:
                await location_btn.click()
                await asyncio.sleep(2)
                
                # Look for Cairo option or input field
                location_input = await self.page.query_selector('input[placeholder*="location"], input[placeholder*="address"]')
                if location_input:
                    await location_input.fill("New Cairo, Cairo, Egypt")
                    await asyncio.sleep(1)
                    
                    # Press Enter or click confirm
                    await self.page.keyboard.press('Enter')
                    await asyncio.sleep(3)
            
            # Try to select stores (if store selection is available)
            store_selector_btn = await self.page.query_selector('[data-cy="store-selector"], .store-filter')
            if store_selector_btn:
                await store_selector_btn.click()
                await asyncio.sleep(2)
                
                # Select target stores
                for store in self.target_stores:
                    store_option = await self.page.query_selector(f'[data-store="{store.lower()}"], [data-cy="store-{store.lower()}"]')
                    if store_option:
                        await store_option.click()
                        await asyncio.sleep(0.5)
                
                # Close store selector
                close_btn = await self.page.query_selector('[data-cy="apply-stores"], .apply-button')
                if close_btn:
                    await close_btn.click()
                    await asyncio.sleep(2)
            
            logger.info("Location and store setup completed for Instashop")
            
        except Exception as e:
            logger.warning(f"Could not setup location/stores for Instashop: {e}")
    
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """Scrape products from Instashop."""
        if category_urls is None:
            category_urls = await self.get_category_urls()
        
        # Setup location and stores first
        await self.navigate_to_url(self.base_url)
        await self.setup_location_and_store()
        
        all_products = []
        pages_scraped = 0
        
        for category_url in category_urls:
            try:
                logger.info(f"Scraping Instashop category: {category_url}")
                
                if not await self.navigate_to_url(category_url):
                    self.errors.append(f"Failed to navigate to {category_url}")
                    continue
                
                # Wait for products to load
                try:
                    await self.page.wait_for_selector(self.product_grid_selector, timeout=20000)
                except PlaywrightTimeoutError:
                    logger.warning(f"No products found in {category_url}")
                    continue
                
                # Handle infinite scroll and pagination
                await self.handle_pagination()
                
                # Extract products from all loaded content
                products = await self.extract_products_from_page()
                all_products.extend(products)
                pages_scraped += 1
                
                logger.info(f"Found {len(products)} products in {category_url}")
                
                # Random delay between categories
                await self.random_delay()
                
            except Exception as e:
                error_msg = f"Error scraping Instashop category {category_url}: {e}"
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
    
    async def handle_pagination(self):
        """Handle pagination and infinite scroll."""
        try:
            page_count = 0
            max_pages = 5  # Limit to prevent infinite loops
            
            while page_count < max_pages:
                # Scroll to bottom to trigger infinite scroll
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
                
                # Check for "Load More" button
                load_more_btn = await self.page.query_selector('[data-cy="load-more"], .load-more-btn, .pagination-next')
                if load_more_btn:
                    try:
                        await load_more_btn.click()
                        await asyncio.sleep(3)
                        page_count += 1
                        continue
                    except:
                        break
                
                # Check for pagination numbers
                next_page_btn = await self.page.query_selector('.pagination-next, [data-cy="next-page"]')
                if next_page_btn and await next_page_btn.is_enabled():
                    try:
                        await next_page_btn.click()
                        await asyncio.sleep(3)
                        page_count += 1
                        continue
                    except:
                        break
                
                # If no more pagination, break
                break
                
        except Exception as e:
            logger.warning(f"Error during Instashop pagination: {e}")
    
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
                    logger.warning(f"Error extracting Instashop product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting product elements from Instashop: {e}")
        
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
            
            # Extract original price (if discounted)
            original_price = None
            original_price_element = await element.query_selector(self.original_price_selector)
            if original_price_element:
                original_price_text = await original_price_element.text_content()
                original_price = self.clean_price(original_price_text)
                if original_price <= price:
                    original_price = None
            
            # Extract store name (Instashop aggregates multiple stores)
            store_name = None
            store_element = await element.query_selector(self.store_selector)
            if store_element:
                store_name = await store_element.text_content()
                store_name = self.clean_text(store_name)
            
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
            
            if not external_id:
                # Try data attributes
                external_id = (await element.get_attribute('data-product-id') or 
                             await element.get_attribute('data-id') or 
                             await element.get_attribute('data-cy'))
            
            # Determine category
            category = self.extract_category_from_url()
            
            # Extract weight/size information
            weight_value, weight_unit = self.extract_weight_info(name)
            
            # Extract brand
            brand = self.extract_brand_from_name(name)
            
            # Add store name to description if available
            description = None
            if store_name:
                description = f"Available at {store_name}"
            
            product = ScrapedProduct(
                name=name,
                price=price,
                original_price=original_price,
                category=category,
                brand=brand,
                description=description,
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
            logger.warning(f"Error extracting Instashop product from element: {e}")
            return None
    
    def extract_category_from_url(self) -> str:
        """Extract category from current URL."""
        try:
            current_url = self.page.url
            if '/category/' in current_url:
                category_slug = current_url.split('/category/')[-1].split('/')[0]
                
                category_mapping = {
                    'fresh-produce': 'vegetables',
                    'fruits-vegetables': 'vegetables',
                    'dairy-eggs': 'dairy',
                    'meat-poultry-seafood': 'meat',
                    'bakery': 'bakery',
                    'pantry': 'pantry',
                    'beverages': 'beverages',
                    'frozen': 'frozen',
                    'snacks-confectionery': 'snacks',
                    'health-beauty': 'personal-care',
                    'household-cleaning': 'household'
                }
                
                return category_mapping.get(category_slug, 'pantry')
        except:
            pass
        
        return 'pantry'
    
    def extract_brand_from_name(self, name: str) -> Optional[str]:
        """Extract brand name from product name."""
        if not name:
            return None
        
        # Common brands available through Instashop
        known_brands = [
            'Almarai', 'Juhayna', 'Domty', 'Beyti', 'Nada', 'Americana',
            'McCain', 'Green Land', 'Panda', 'El Rashidi El Mizan',
            'Molto', 'Chipsy', 'Tiger', 'Baraka', 'Gondola'
        ]
        
        name_upper = name.upper()
        for brand in known_brands:
            if brand.upper() in name_upper:
                return brand
        
        # Extract first word as potential brand
        words = name.split()
        if len(words) > 1 and len(words[0]) > 2 and not words[0].lower() in ['fresh', 'organic', 'premium']:
            return words[0]
        
        return None
    
    def generate_keywords(self, name: str) -> List[str]:
        """Generate keywords from product name."""
        if not name:
            return []
        
        words = name.lower().replace(',', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ').split()
        keywords = []
        
        stop_words = {'the', 'and', 'or', 'with', 'from', 'per', 'pack', 'piece', 'pieces', 'each', 'ea'}
        
        for word in words:
            word = word.strip()
            if len(word) > 2 and word not in stop_words and not word.isdigit():
                keywords.append(word)
        
        return keywords[:8]
    
    async def extract_product_data(self) -> Optional[ScrapedProduct]:
        """Extract product data from current page (single product page)."""
        try:
            # For detailed product page scraping
            return None
        except Exception as e:
            logger.error(f"Error extracting Instashop product data: {e}")
            return None