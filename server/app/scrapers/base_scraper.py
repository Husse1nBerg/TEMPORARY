from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
import asyncio
import random
import re
import logging
from urllib.parse import urljoin, urlparse

from server.app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ScrapedProduct:
    """Data class for scraped product information."""
    name: str
    price: float
    original_price: Optional[float] = None
    price_per_kg: Optional[float] = None
    pack_size: Optional[str] = None
    pack_unit: Optional[str] = None
    weight_value: Optional[float] = None
    weight_unit: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    external_id: Optional[str] = None
    is_available: bool = True
    is_discounted: bool = False
    is_on_sale: bool = False
    discount_percentage: Optional[float] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        
        # Calculate discount percentage if not provided
        if self.original_price and self.price and not self.discount_percentage:
            self.discount_percentage = ((self.original_price - self.price) / self.original_price) * 100
            self.is_discounted = self.discount_percentage > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'price': self.price,
            'original_price': self.original_price,
            'price_per_kg': self.price_per_kg,
            'pack_size': self.pack_size,
            'pack_unit': self.pack_unit,
            'weight_value': self.weight_value,
            'weight_unit': self.weight_unit,
            'brand': self.brand,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'external_id': self.external_id,
            'is_available': self.is_available,
            'is_discounted': self.is_discounted,
            'is_on_sale': self.is_on_sale,
            'discount_percentage': self.discount_percentage,
            'keywords': self.keywords,
        }


@dataclass
class ScraperResult:
    """Result of a scraping operation."""
    success: bool
    products: List[ScrapedProduct]
    errors: List[str]
    duration_seconds: float
    pages_scraped: int = 0
    total_products_found: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.total_products_found == 0:
            self.total_products_found = len(self.products)


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class ScraperTimeoutError(ScraperError):
    """Scraper timeout exception."""
    pass


class ScraperNavigationError(ScraperError):
    """Scraper navigation exception."""
    pass


class BaseScraper(ABC):
    """Abstract base class for all store scrapers."""
    
    def __init__(self, store_name: str, base_url: str, **kwargs):
        self.store_name = store_name
        self.base_url = base_url
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Scraping configuration
        self.timeout = kwargs.get('timeout', settings.SCRAPING_TIMEOUT * 1000)  # Convert to ms
        self.delay_min = kwargs.get('delay_min', settings.SCRAPING_DELAY_MIN)
        self.delay_max = kwargs.get('delay_max', settings.SCRAPING_DELAY_MAX)
        self.max_retries = kwargs.get('max_retries', settings.SCRAPING_MAX_RETRIES)
        self.user_agent = kwargs.get('user_agent', settings.SCRAPING_USER_AGENT)
        
        # Results tracking
        self.scraped_count = 0
        self.error_count = 0
        self.errors = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def setup_browser(self):
        """Setup browser and page."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # Create page with context
            context = await self.browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.page = await context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(self.timeout)
            
            logger.info(f"Browser setup complete for {self.store_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup browser for {self.store_name}: {e}")
            await self.cleanup()
            raise ScraperError(f"Browser setup failed: {e}")
    
    async def cleanup(self):
        """Cleanup browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    async def random_delay(self):
        """Add random delay between requests."""
        delay = random.uniform(self.delay_min, self.delay_max)
        await asyncio.sleep(delay)
    
    async def navigate_to_url(self, url: str, retries: int = None) -> bool:
        """Navigate to URL with retry logic."""
        if retries is None:
            retries = self.max_retries
            
        for attempt in range(retries + 1):
            try:
                logger.info(f"Navigating to {url} (attempt {attempt + 1})")
                response = await self.page.goto(url, wait_until='domcontentloaded')
                
                if response and response.status < 400:
                    await self.random_delay()
                    return True
                else:
                    logger.warning(f"HTTP {response.status if response else 'unknown'} for {url}")
                    
            except PlaywrightTimeoutError:
                logger.warning(f"Timeout navigating to {url} (attempt {attempt + 1})")
                if attempt == retries:
                    raise ScraperTimeoutError(f"Navigation timeout after {retries + 1} attempts")
                    
            except Exception as e:
                logger.error(f"Navigation error for {url}: {e}")
                if attempt == retries:
                    raise ScraperNavigationError(f"Navigation failed: {e}")
            
            # Wait before retry
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    def clean_price(self, price_text: str) -> float:
        """Clean and convert price text to float."""
        if not price_text:
            return 0.0
            
        try:
            # Remove currency symbols, commas, and extra whitespace
            cleaned = re.sub(r'[^\d.,]', '', str(price_text).strip())
            
            # Handle different decimal separators
            if ',' in cleaned and '.' in cleaned:
                # Assume comma is thousands separator
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned and cleaned.count(',') == 1 and len(cleaned.split(',')[1]) <= 2:
                # Comma as decimal separator
                cleaned = cleaned.replace(',', '.')
            
            return round(float(cleaned), 2)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse price '{price_text}': {e}")
            return 0.0
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(str(text).strip().split())
        return cleaned
    
    def extract_weight_info(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        """Extract weight value and unit from text."""
        if not text:
            return None, None
            
        # Common weight patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|kilogram|g|gram|l|liter|ml|milliliter)s?',
            r'(\d+(?:\.\d+)?)\s*(oz|pound|lb)s?',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))
                unit = match.group(2)
                
                # Normalize units
                unit_mapping = {
                    'kilogram': 'kg', 'gram': 'g',
                    'liter': 'l', 'milliliter': 'ml',
                    'pound': 'lb', 'lb': 'lb', 'oz': 'oz'
                }
                
                return value, unit_mapping.get(unit, unit)
        
        return None, None
    
    def make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute URL."""
        if not url:
            return ""
        
        if url.startswith(('http://', 'https://')):
            return url
        
        return urljoin(self.base_url, url)
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from URL."""
        if not url:
            return None
        
        # Try to extract ID from URL patterns
        patterns = [
            r'/products?/(\d+)',
            r'/item/(\d+)',
            r'id=(\d+)',
            r'/(\d+)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @abstractmethod
    async def scrape_products(self, category_urls: List[str] = None) -> ScraperResult:
        """
        Scrape products from the store.
        
        Args:
            category_urls: List of category URLs to scrape. If None, scrape all categories.
            
        Returns:
            ScraperResult: Results of the scraping operation
        """
        pass
    
    @abstractmethod
    async def get_category_urls(self) -> List[str]:
        """Get list of category URLs to scrape."""
        pass
    
    async def scrape_product_page(self, product_url: str) -> Optional[ScrapedProduct]:
        """Scrape a single product page."""
        try:
            if not await self.navigate_to_url(product_url):
                return None
            
            return await self.extract_product_data()
            
        except Exception as e:
            logger.error(f"Error scraping product page {product_url}: {e}")
            self.errors.append(f"Product page error: {e}")
            return None
    
    @abstractmethod
    async def extract_product_data(self) -> Optional[ScrapedProduct]:
        """Extract product data from current page."""
        pass
    
    def validate_product(self, product: ScrapedProduct) -> bool:
        """Validate scraped product data."""
        if not product:
            return False
        
        # Required fields
        if not product.name or not product.name.strip():
            logger.warning("Product missing name")
            return False
        
        if product.price <= 0:
            logger.warning(f"Invalid price for product {product.name}: {product.price}")
            return False
        
        # Validate price logic
        if product.original_price and product.original_price < product.price:
            logger.warning(f"Original price less than current price for {product.name}")
            product.original_price = None
            product.is_discounted = False
        
        return True
    
    async def run_scraping(self, category_urls: List[str] = None) -> ScraperResult:
        """Run the complete scraping process."""
        start_time = datetime.now()
        
        try:
            result = await self.scrape_products(category_urls)
            
            # Validate products
            valid_products = []
            for product in result.products:
                if self.validate_product(product):
                    valid_products.append(product)
                else:
                    self.errors.append(f"Invalid product: {product.name if product else 'Unknown'}")
            
            result.products = valid_products
            result.errors.extend(self.errors)
            result.success = len(valid_products) > 0
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Scraping completed for {self.store_name}: "
                f"{len(valid_products)} products, "
                f"{len(result.errors)} errors, "
                f"{result.duration_seconds:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Scraping failed for {self.store_name}: {e}")
            return ScraperResult(
                success=False,
                products=[],
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )