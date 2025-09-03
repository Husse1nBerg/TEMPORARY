from typing import List, Optional
import logging
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult

logger = logging.getLogger(__name__)


class SpinneysScraper(BaseScraper):
    """Scraper for Spinneys website."""
    
    def __init__(self):
        super().__init__(
            store_name="Spinneys",
            base_url="https://www.spinneys.com/"
        )
        
        # Spinneys-specific selectors
        self.product_grid_selector = '.product-item, .product-card, .grid-item'
        self.product_title_selector = '.product-name, .product-title, h3'
        self.product_price_selector = '.price, .current-price, .product-price'
        self.original_price_selector = '.old-price, .was-price, .compare-price'
        self.product_link_selector = 'a'
        self.product_image_selector = 'img'
        self.out_of_stock_selector = '.out-of-stock, .unavailable, .sold-out'
        self.sale_badge_selector = '.sale, .discount, .offer, .special'
    
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        category_urls = [
            '/fresh/fruits-vegetables',
            '/fresh/meat-poultry-seafood',
            '/dairy-chilled/dairy-products',
            '/dairy-chilled/eggs',
            '/bakery/bread-bakery',
            '/bakery/cakes-desserts',
            '/frozen/frozen-food',
            '/beverages/soft-drinks',
            '/beverages/juices-smoothies',
            '/pantry/breakfast-cereals',
            '/pantry/rice-pasta',
            '/snacks/chips-nuts',
            '/health-beauty/personal-care',
            '/household/cleaning-supplies'
        ]
        
        return [self.make_absolute_url(url) for url in category_urls]
    
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """Scrape products from Spinneys."""
        if category_urls is None:
            category_urls = await self.get_category_urls()
        
        all_products = []
        pages_scraped = 0
        
        for category_url in category_urls:
            try:
                logger.info(f"Scraping Spinneys category: {category_url}")
                
                if not await self.navigate_to_url(category_url):
                    self.errors.append(f"Failed to navigate to {category_url}")
                    continue
                
                # Wait for products to load
                try:
                    await self.page.wait_for_selector(self.product_grid_selector, timeout=15000)
                except PlaywrightTimeoutError:
                    logger.warning(f"No products found in {category_url}")
                    continue
                
                # Handle Spinneys pagination
                await self.handle_spinneys_pagination()
                
                # Extract products
                products = await self.extract_products_from_page()
                all_products.extend(products)
                pages_scraped += 1
                
                logger.info(f"Found {len(products)} products in {category_url}")
                await self.random_delay()
                
            except Exception as e:
                error_msg = f"Error scraping Spinneys category {category_url}: {e}"
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
    
    async def handle_spinneys_pagination(self):
        """Handle Spinneys pagination and loading."""
        try:\n            page_count = 0\n            max_pages = 4\n            \n            while page_count < max_pages:\n                # Scroll to bottom\n                await self.page.evaluate(\"window.scrollTo(0, document.body.scrollHeight)\")\n                await asyncio.sleep(2)\n                \n                # Look for \"View More\" or similar button\n                view_more_btn = await self.page.query_selector('.view-more, .load-more, .show-more')\n                if view_more_btn:\n                    try:\n                        await view_more_btn.click()\n                        await asyncio.sleep(3)\n                        page_count += 1\n                        continue\n                    except:\n                        break\n                \n                # Look for pagination arrows\n                next_page_btn = await self.page.query_selector('.pagination-next, .next-page, [aria-label=\"Next\"]')\n                if next_page_btn and await next_page_btn.is_enabled():\n                    try:\n                        await next_page_btn.click()\n                        await asyncio.sleep(3)\n                        page_count += 1\n                        continue\n                    except:\n                        break\n                \n                break\n                \n        except Exception as e:\n            logger.warning(f\"Error during Spinneys pagination: {e}\")\n    \n    async def extract_products_from_page(self) -> List[ScrapedProduct]:\n        \"\"\"Extract all products from current page.\"\"\"\n        products = []\n        \n        try:\n            product_elements = await self.page.query_selector_all(self.product_grid_selector)\n            logger.info(f\"Found {len(product_elements)} product elements\")\n            \n            for element in product_elements:\n                try:\n                    product = await self.extract_product_from_element(element)\n                    if product:\n                        products.append(product)\n                except Exception as e:\n                    logger.warning(f\"Error extracting Spinneys product: {e}\")\n                    continue\n                    \n        except Exception as e:\n            logger.error(f\"Error getting product elements from Spinneys: {e}\")\n        \n        return products\n    \n    async def extract_product_from_element(self, element) -> Optional[ScrapedProduct]:\n        \"\"\"Extract product data from a product element.\"\"\"\n        try:\n            # Extract name\n            name_element = await element.query_selector(self.product_title_selector)\n            if not name_element:\n                return None\n            \n            name = await name_element.text_content()\n            name = self.clean_text(name)\n            \n            if not name:\n                return None\n            \n            # Extract price\n            price_element = await element.query_selector(self.product_price_selector)\n            if not price_element:\n                return None\n            \n            price_text = await price_element.text_content()\n            price = self.clean_price(price_text)\n            \n            if price <= 0:\n                return None\n            \n            # Extract original price\n            original_price = None\n            original_price_element = await element.query_selector(self.original_price_selector)\n            if original_price_element:\n                original_price_text = await original_price_element.text_content()\n                original_price = self.clean_price(original_price_text)\n                if original_price <= price:\n                    original_price = None\n            \n            # Extract product URL\n            link_element = await element.query_selector(self.product_link_selector)\n            product_url = None\n            if link_element:\n                href = await link_element.get_attribute('href')\n                if href:\n                    product_url = self.make_absolute_url(href)\n            \n            # Extract image URL\n            image_element = await element.query_selector(self.product_image_selector)\n            image_url = None\n            if image_element:\n                src = await image_element.get_attribute('src') or await image_element.get_attribute('data-src')\n                if src:\n                    image_url = self.make_absolute_url(src)\n            \n            # Check availability\n            out_of_stock_element = await element.query_selector(self.out_of_stock_selector)\n            is_available = out_of_stock_element is None\n            \n            # Check if on sale\n            sale_element = await element.query_selector(self.sale_badge_selector)\n            is_on_sale = sale_element is not None\n            is_discounted = original_price is not None\n            \n            # Extract product ID\n            external_id = None\n            if product_url:\n                external_id = self.extract_product_id(product_url)\n            \n            # Determine category\n            category = self.extract_category_from_url()\n            \n            # Extract weight/size information\n            weight_value, weight_unit = self.extract_weight_info(name)\n            \n            # Extract brand\n            brand = self.extract_brand_from_name(name)\n            \n            product = ScrapedProduct(\n                name=name,\n                price=price,\n                original_price=original_price,\n                category=category,\n                brand=brand,\n                image_url=image_url,\n                product_url=product_url,\n                external_id=external_id,\n                is_available=is_available,\n                is_discounted=is_discounted,\n                is_on_sale=is_on_sale,\n                weight_value=weight_value,\n                weight_unit=weight_unit,\n                keywords=self.generate_keywords(name)\n            )\n            \n            return product\n            \n        except Exception as e:\n            logger.warning(f\"Error extracting Spinneys product from element: {e}\")\n            return None\n    \n    def extract_category_from_url(self) -> str:\n        \"\"\"Extract category from current URL.\"\"\"\n        try:\n            current_url = self.page.url\n            \n            if 'fruits-vegetables' in current_url:\n                return 'vegetables'\n            elif 'meat-poultry-seafood' in current_url:\n                return 'meat'\n            elif 'dairy-products' in current_url or 'eggs' in current_url:\n                return 'dairy'\n            elif 'bread-bakery' in current_url or 'cakes-desserts' in current_url:\n                return 'bakery'\n            elif 'frozen' in current_url:\n                return 'frozen'\n            elif 'beverages' in current_url or 'drinks' in current_url or 'juices' in current_url:\n                return 'beverages'\n            elif 'chips-nuts' in current_url:\n                return 'snacks'\n            elif 'personal-care' in current_url:\n                return 'personal-care'\n            elif 'cleaning' in current_url:\n                return 'household'\n            else:\n                return 'pantry'\n        except:\n            pass\n        \n        return 'pantry'\n    \n    def extract_brand_from_name(self, name: str) -> Optional[str]:\n        \"\"\"Extract brand name from product name.\"\"\"\n        if not name:\n            return None\n        \n        # Common brands at Spinneys\n        known_brands = [\n            'Spinneys', 'Almarai', 'Juhayna', 'Domty', 'Beyti', 'Nada',\n            'Americana', 'McCain', 'Green Land', 'Panda', 'Molto',\n            'Heinz', 'Kelloggs', 'Nestle', 'Unilever', 'Ariel'\n        ]\n        \n        name_upper = name.upper()\n        for brand in known_brands:\n            if brand.upper() in name_upper:\n                return brand\n        \n        # Try first word as brand\n        words = name.split()\n        if len(words) > 1 and len(words[0]) > 2:\n            return words[0]\n        \n        return None\n    \n    def generate_keywords(self, name: str) -> List[str]:\n        \"\"\"Generate keywords from product name.\"\"\"\n        if not name:\n            return []\n        \n        words = name.lower().replace(',', ' ').replace('-', ' ').split()\n        keywords = []\n        \n        stop_words = {'the', 'and', 'or', 'with', 'from', 'per', 'pack', 'spinneys'}\n        \n        for word in words:\n            word = word.strip()\n            if len(word) > 2 and word not in stop_words and not word.isdigit():\n                keywords.append(word)\n        \n        return keywords[:8]\n    \n    async def extract_product_data(self) -> Optional[ScrapedProduct]:\n        \"\"\"Extract product data from current page.\"\"\"\n        try:\n            return None\n        except Exception as e:\n            logger.error(f\"Error extracting Spinneys product data: {e}\")\n            return None