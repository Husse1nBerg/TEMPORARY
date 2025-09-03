from typing import List, Optional
import logging
import asyncio
import json
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult

logger = logging.getLogger(__name__)


class BreadfastScraper(BaseScraper):
    """Scraper for Breadfast delivery service."""
    
    def __init__(self):
        super().__init__(
            store_name="Breadfast",
            base_url="https://breadfast.com/"
        )
        
        # Breadfast-specific selectors
        self.product_grid_selector = '.product-card, .item-card, [data-testid="product-item"]'
        self.product_title_selector = '.product-title, .item-name, h3, .product-name'
        self.product_price_selector = '.price, .current-price, [data-testid="price"]'
        self.original_price_selector = '.original-price, .old-price, .was-price'
        self.product_link_selector = 'a'
        self.product_image_selector = 'img'
        self.out_of_stock_selector = '.out-of-stock, .unavailable, [data-testid="out-of-stock"]'
        self.sale_badge_selector = '.sale, .discount, .offer-badge'
        self.category_selector = '.category-nav a, .categories a'
        
        # Breadfast uses location-based delivery
        self.default_location = "New Cairo, Egypt"
        
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        category_urls = [
            '/categories/bakery-bread',
            '/categories/fresh-fruits-vegetables',
            '/categories/dairy-eggs',
            '/categories/beverages',
            '/categories/snacks-sweets',
            '/categories/frozen-foods',
            '/categories/pantry-essentials',
            '/categories/personal-care',
            '/categories/household-cleaning'
        ]
        
        return [self.make_absolute_url(url) for url in category_urls]
    
    async def setup_location(self):
        """Set delivery location for Breadfast."""
        try:
            # Look for location selector
            location_selector = await self.page.query_selector('.location-selector, [data-testid="location-button"]')
            if location_selector:
                await location_selector.click()
                await asyncio.sleep(2)
                
                # Try to set Cairo/New Cairo as location
                location_input = await self.page.query_selector('input[placeholder*="location"], input[placeholder*="address"]')
                if location_input:
                    await location_input.fill(self.default_location)
                    await asyncio.sleep(1)
                    
                    # Click on first suggestion or confirm button
                    confirm_btn = await self.page.query_selector('.confirm-location, [data-testid="confirm-location"]')
                    if confirm_btn:
                        await confirm_btn.click()
                        await asyncio.sleep(2)
                
            logger.info("Location setup completed for Breadfast")
            
        except Exception as e:
            logger.warning(f"Could not set location for Breadfast: {e}")
    
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """Scrape products from Breadfast."""
        if category_urls is None:
            category_urls = await self.get_category_urls()
        
        # Setup location first
        await self.navigate_to_url(self.base_url)
        await self.setup_location()
        
        all_products = []
        pages_scraped = 0
        
        for category_url in category_urls:
            try:
                logger.info(f"Scraping Breadfast category: {category_url}")
                
                if not await self.navigate_to_url(category_url):
                    self.errors.append(f"Failed to navigate to {category_url}")
                    continue
                
                # Wait for products to load
                try:
                    await self.page.wait_for_selector(self.product_grid_selector, timeout=15000)
                except PlaywrightTimeoutError:
                    logger.warning(f"No products found in {category_url}")
                    continue
                
                # Handle lazy loading
                await self.handle_lazy_loading()
                
                # Extract products from category page
                products = await self.extract_products_from_page()
                all_products.extend(products)
                pages_scraped += 1
                
                logger.info(f"Found {len(products)} products in {category_url}")
                
                # Random delay between categories
                await self.random_delay()
                
            except Exception as e:
                error_msg = f"Error scraping Breadfast category {category_url}: {e}"
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
    
    async def handle_lazy_loading(self):
        """Handle lazy loading by scrolling and clicking load more buttons."""
        try:
            # Scroll to load more products
            last_height = await self.page.evaluate("document.body.scrollHeight")
            
            for _ in range(3):  # Maximum 3 scrolls
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                # Check for "Load More" button
                load_more_btn = await self.page.query_selector('.load-more, [data-testid="load-more"], .show-more')
                if load_more_btn:
                    try:
                        await load_more_btn.click()
                        await asyncio.sleep(3)
                    except:
                        pass
                
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during lazy loading: {e}")
    
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
                    logger.warning(f"Error extracting Breadfast product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting product elements from Breadfast: {e}")
        
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
            
            # Extract product ID from URL or data attributes
            external_id = None
            if product_url:
                external_id = self.extract_product_id(product_url)
            
            if not external_id:
                # Try data-id attribute
                external_id = await element.get_attribute('data-id') or await element.get_attribute('data-product-id')
            
            # Determine category
            category = self.extract_category_from_url()
            
            # Extract weight/size information
            weight_value, weight_unit = self.extract_weight_info(name)
            
            # Extract brand from name (if available)
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
            logger.warning(f"Error extracting Breadfast product from element: {e}")
            return None
    
    def extract_category_from_url(self) -> str:
        """Extract category from current URL."""
        try:
            current_url = self.page.url
            if '/categories/' in current_url:
                category_slug = current_url.split('/categories/')[-1].split('/')[0]
                
                category_mapping = {
                    'bakery-bread': 'bakery',
                    'fresh-fruits-vegetables': 'vegetables',
                    'dairy-eggs': 'dairy',
                    'beverages': 'beverages',
                    'snacks-sweets': 'snacks',
                    'frozen-foods': 'frozen',
                    'pantry-essentials': 'pantry',
                    'personal-care': 'personal-care',
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
        
        # Common brand patterns in Breadfast
        known_brands = [
            'Almarai', 'Juhayna', 'Domty', 'Beyti', 'Nada', 'Molto',
            'Panda', 'El Rashidi El Mizan', 'Americana', 'McCain'
        ]
        
        name_upper = name.upper()
        for brand in known_brands:
            if brand.upper() in name_upper:
                return brand
        
        # Try to extract first word as potential brand
        words = name.split()
        if len(words) > 1 and len(words[0]) > 2:
            return words[0]
        
        return None
    
    def generate_keywords(self, name: str) -> List[str]:
        """Generate keywords from product name."""
        if not name:
            return []
        
        # Clean and split name
        words = name.lower().replace(',', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ').split()
        keywords = []
        
        stop_words = {'the', 'and', 'or', 'with', 'from', 'per', 'pack', 'piece', 'pieces'}
        
        for word in words:
            word = word.strip()
            if len(word) > 2 and word not in stop_words and not word.isdigit():
                keywords.append(word)
        
        return keywords[:8]  # Limit to 8 keywords
    
    async def extract_product_data(self) -> Optional[ScrapedProduct]:
        """Extract product data from current page (single product page)."""
        try:
            # This would be used for detailed product page scraping
            # Currently we extract from category pages
            return None
        except Exception as e:
            logger.error(f"Error extracting Breadfast product data: {e}")
            return None