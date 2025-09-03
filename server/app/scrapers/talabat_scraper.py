from typing import List, Optional
import logging
import asyncio
import json
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult

logger = logging.getLogger(__name__)


class TalabatScraper(BaseScraper):
    """Scraper for Talabat delivery service (food and grocery)."""
    
    def __init__(self):
        super().__init__(
            store_name="Talabat",
            base_url="https://www.talabat.com/egypt/"
        )
        
        # Talabat-specific selectors
        self.product_grid_selector = '.product-item, .dish-item, [data-testid="product-item"]'
        self.product_title_selector = '.product-name, .dish-name, [data-testid="product-name"]'
        self.product_price_selector = '.price, .product-price, [data-testid="product-price"]'
        self.original_price_selector = '.old-price, .strike-price, .was-price'
        self.product_link_selector = 'a'
        self.product_image_selector = 'img'
        self.out_of_stock_selector = '.unavailable, .out-of-stock, [data-testid="unavailable"]'
        self.sale_badge_selector = '.discount, .offer, .promo'
        self.restaurant_selector = '.restaurant-name, .vendor-name'
        
        # Talabat requires location setup
        self.default_location = "Cairo, Egypt"
        
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        # Talabat focuses on restaurants and some grocery stores
        category_urls = [
            '/restaurants/grocery',
            '/restaurants/supermarket',
            '/restaurants/convenience',
            '/restaurants/pharmacy',
            '/restaurants/bakery',
            '/restaurants/butcher',
            '/restaurants/fruits-vegetables',
            '/restaurants/beverages',
            '/restaurants/desserts',
            '/restaurants/healthy-food'
        ]
        
        return [self.make_absolute_url(url) for url in category_urls]
    
    async def setup_talabat_location(self):
        """Setup location for Talabat delivery."""
        try:
            # Look for location button or modal
            location_btn = await self.page.query_selector('[data-testid="location-button"], .location-selector, .address-input')
            if location_btn:
                await location_btn.click()
                await asyncio.sleep(2)
                
                # Enter Cairo as delivery location
                location_input = await self.page.query_selector('input[placeholder*="address"], input[placeholder*="location"]')
                if location_input:
                    await location_input.fill(self.default_location)
                    await asyncio.sleep(1)
                    
                    # Press Enter or click first suggestion
                    await self.page.keyboard.press('Enter')
                    await asyncio.sleep(2)
                    
                    # Click confirm if needed
                    confirm_btn = await self.page.query_selector('[data-testid="confirm-location"], .confirm-btn')
                    if confirm_btn:
                        await confirm_btn.click()
                        await asyncio.sleep(2)
            
            logger.info("Location setup completed for Talabat")
            
        except Exception as e:
            logger.warning(f"Could not setup location for Talabat: {e}")
    
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """Scrape products from Talabat."""
        if category_urls is None:
            category_urls = await self.get_category_urls()
        
        # Setup location first
        await self.navigate_to_url(self.base_url)
        await self.setup_talabat_location()
        
        all_products = []
        pages_scraped = 0
        
        for category_url in category_urls:
            try:
                logger.info(f"Scraping Talabat category: {category_url}")
                
                if not await self.navigate_to_url(category_url):
                    self.errors.append(f"Failed to navigate to {category_url}")
                    continue
                
                # Wait for restaurant/store listings
                try:
                    await self.page.wait_for_selector('.restaurant-card, .vendor-card, [data-testid="restaurant-card"]', timeout=15000)
                except PlaywrightTimeoutError:
                    logger.warning(f"No restaurants found in {category_url}")
                    continue
                
                # Get restaurant/store links
                restaurant_links = await self.get_restaurant_links()
                
                # Visit each restaurant and scrape products
                for restaurant_url in restaurant_links[:5]:  # Limit to 5 restaurants per category
                    try:
                        restaurant_products = await self.scrape_restaurant_products(restaurant_url)
                        all_products.extend(restaurant_products)
                        await self.random_delay()
                    except Exception as e:
                        logger.warning(f"Error scraping restaurant {restaurant_url}: {e}")
                        continue
                
                pages_scraped += 1
                logger.info(f"Found {len(all_products)} total products so far")
                
            except Exception as e:
                error_msg = f"Error scraping Talabat category {category_url}: {e}"
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
    
    async def get_restaurant_links(self) -> List[str]:
        """Get links to restaurants/stores from category page."""
        restaurant_links = []
        
        try:
            # Get restaurant/store cards
            restaurant_cards = await self.page.query_selector_all('.restaurant-card, .vendor-card, [data-testid="restaurant-card"]')
            
            for card in restaurant_cards:
                link_element = await card.query_selector('a')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        restaurant_links.append(self.make_absolute_url(href))
            
            logger.info(f"Found {len(restaurant_links)} restaurants/stores")
            
        except Exception as e:
            logger.error(f"Error getting restaurant links: {e}")
        
        return restaurant_links
    
    async def scrape_restaurant_products(self, restaurant_url: str) -> List[ScrapedProduct]:
        """Scrape products from a specific restaurant/store."""
        products = []
        
        try:
            if not await self.navigate_to_url(restaurant_url):
                return products
            
            # Wait for menu/products to load
            await self.page.wait_for_selector(self.product_grid_selector, timeout=10000)
            
            # Get restaurant name for context
            restaurant_name = await self.get_restaurant_name()
            
            # Scroll to load more products
            await self.handle_menu_scrolling()
            
            # Extract products
            product_elements = await self.page.query_selector_all(self.product_grid_selector)
            
            for element in product_elements:
                try:
                    product = await self.extract_product_from_element(element)
                    if product:
                        # Add restaurant context
                        if restaurant_name:
                            product.description = f"Available at {restaurant_name}" + (f" - {product.description}" if product.description else "")
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error extracting Talabat product: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} products from {restaurant_name or 'restaurant'}")
            
        except PlaywrightTimeoutError:
            logger.warning(f"No products found in restaurant: {restaurant_url}")
        except Exception as e:
            logger.error(f"Error scraping restaurant products: {e}")
        
        return products
    
    async def get_restaurant_name(self) -> Optional[str]:
        """Get restaurant/store name."""
        try:
            name_element = await self.page.query_selector('.restaurant-name, .vendor-name, [data-testid="restaurant-name"]')
            if name_element:
                name = await name_element.text_content()
                return self.clean_text(name)
        except:
            pass
        return None
    
    async def handle_menu_scrolling(self):
        """Handle scrolling to load menu items."""
        try:
            # Scroll down to load all menu items
            last_height = await self.page.evaluate("document.body.scrollHeight")
            
            for _ in range(3):  # Maximum 3 scrolls
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during menu scrolling: {e}")
    
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
                    logger.warning(f"Error extracting Talabat product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting product elements from Talabat: {e}")
        
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
            
            # Extract product URL (usually the current page for Talabat)
            product_url = self.page.url
            
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
            
            # Generate external ID from name and price
            external_id = f"talabat_{hash(name + str(price))}"
            
            # Determine category (food delivery focus)
            category = self.extract_category_from_url()
            
            # Extract weight/size information
            weight_value, weight_unit = self.extract_weight_info(name)
            
            # Extract brand/restaurant from context
            brand = await self.get_restaurant_name()
            
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
            logger.warning(f"Error extracting Talabat product from element: {e}")
            return None
    
    def extract_category_from_url(self) -> str:
        """Extract category from current URL."""
        try:
            current_url = self.page.url
            
            if 'grocery' in current_url or 'supermarket' in current_url:
                return 'pantry'
            elif 'pharmacy' in current_url:
                return 'health'
            elif 'bakery' in current_url:
                return 'bakery'
            elif 'butcher' in current_url:
                return 'meat'
            elif 'fruits-vegetables' in current_url:
                return 'vegetables'
            elif 'beverages' in current_url:
                return 'beverages'
            elif 'desserts' in current_url:
                return 'snacks'
            else:
                return 'food'  # Default for restaurant items
        except:
            pass
        
        return 'food'
    
    def generate_keywords(self, name: str) -> List[str]:
        """Generate keywords from product name."""
        if not name:
            return []
        
        words = name.lower().replace(',', ' ').replace('-', ' ').split()
        keywords = []
        
        stop_words = {'the', 'and', 'or', 'with', 'from', 'per', 'piece', 'talabat'}
        
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
            logger.error(f"Error extracting Talabat product data: {e}")
            return None