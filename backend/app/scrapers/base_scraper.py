"""
Base Scraper Class
Handles common scraping functionality using Playwright
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import asyncio
import re
from decimal import Decimal
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import json

logger = logging.getLogger(__name__)

class ProductData:
    """Data class for scraped product information"""
    def __init__(self):
        self.name: str = ""
        self.brand: Optional[str] = None
        self.price: Decimal = Decimal("0")
        self.original_price: Optional[Decimal] = None
        self.pack_size: str = ""
        self.pack_unit: str = ""
        self.price_per_kg: Optional[Decimal] = None
        self.is_available: bool = True
        self.is_organic: bool = False
        self.is_discounted: bool = False
        self.category: str = ""
        self.image_url: Optional[str] = None
        self.product_url: Optional[str] = None
        self.scraped_at: datetime = datetime.utcnow()
        self.store_name: str = ""
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "brand": self.brand,
            "price": float(self.price) if self.price else 0,
            "original_price": float(self.original_price) if self.original_price else None,
            "pack_size": self.pack_size,
            "pack_unit": self.pack_unit,
            "price_per_kg": float(self.price_per_kg) if self.price_per_kg else None,
            "is_available": self.is_available,
            "is_organic": self.is_organic,
            "is_discounted": self.is_discounted,
            "category": self.category,
            "image_url": self.image_url,
            "product_url": self.product_url,
            "scraped_at": self.scraped_at.isoformat(),
            "store_name": self.store_name
        }

class BaseScraper(ABC):
    """Abstract base class for all store scrapers"""
    
    def __init__(self, store_name: str, base_url: str):
        self.store_name = store_name
        self.base_url = base_url
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.products_to_track = self._load_products_list()
        
    def _load_products_list(self) -> List[Dict]:
        """Load the list of products to track from configuration"""
        # These come from the Excel file - Categories A & B
        return [
            # Category A
            {"name": "Cucumbers", "category": "A", "keywords": ["cucumber", "خيار"]},
            {"name": "Tomatoes", "category": "A", "keywords": ["tomato", "tomatoes", "طماطم"]},
            {"name": "Cherry Tomatoes", "category": "A", "keywords": ["cherry tomato", "طماطم كرزية"]},
            {"name": "Capsicum Red and Yellow Mix", "category": "A", "keywords": ["capsicum mix", "pepper mix"]},
            {"name": "Capsicum Red", "category": "A", "keywords": ["red capsicum", "red pepper", "فلفل أحمر"]},
            {"name": "Capsicum Yellow", "category": "A", "keywords": ["yellow capsicum", "yellow pepper", "فلفل أصفر"]},
            {"name": "Chili Pepper", "category": "A", "keywords": ["chili", "hot pepper", "فلفل حار"]},
            {"name": "Arugula", "category": "A", "keywords": ["arugula", "rocket", "جرجير"]},
            {"name": "Parsley", "category": "A", "keywords": ["parsley", "بقدونس"]},
            {"name": "Coriander", "category": "A", "keywords": ["coriander", "cilantro", "كزبرة"]},
            {"name": "Mint", "category": "A", "keywords": ["mint", "نعناع"]},
            {"name": "Tuscan Kale", "category": "A", "keywords": ["tuscan kale", "lacinato kale", "dinosaur kale"]},
            {"name": "Italian Basil", "category": "A", "keywords": ["basil", "italian basil", "ريحان"]},
            
            # Category B
            {"name": "Colored Cherry Tomatoes", "category": "B", "keywords": ["colored cherry", "rainbow tomatoes"]},
            {"name": "Capsicum Green", "category": "B", "keywords": ["green capsicum", "green pepper", "فلفل أخضر"]},
            {"name": "Italian Arugula", "category": "B", "keywords": ["italian arugula", "wild arugula"]},
            {"name": "Chives", "category": "B", "keywords": ["chives", "ثوم معمر"]},
            {"name": "Curly Kale", "category": "B", "keywords": ["curly kale", "kale"]},
            {"name": "Batavia Lettuce", "category": "B", "keywords": ["batavia", "batavia lettuce"]},
            {"name": "Ice Berg Lettuce", "category": "B", "keywords": ["iceberg", "iceberg lettuce", "خس آيسبرغ"]},
            {"name": "Oak Leaf Lettuce", "category": "B", "keywords": ["oak leaf", "oakleaf lettuce"]},
            {"name": "Romain Lettuce", "category": "B", "keywords": ["romaine", "romain lettuce", "خس روماني"]}
        ]
    
    async def initialize_browser(self, headless: bool = True):
        """Initialize Playwright browser"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = await context.new_page()
            logger.info(f"Browser initialized for {self.store_name}")
        except Exception as e:
            logger.error(f"Failed to initialize browser for {self.store_name}: {e}")
            raise
    
    async def close_browser(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            logger.info(f"Browser closed for {self.store_name}")
    
    async def wait_for_page_load(self, timeout: int = 30000):
        """Wait for page to fully load"""
        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
        except PlaywrightTimeout:
            logger.warning(f"Page load timeout for {self.store_name}")
    
    def calculate_price_per_kg(self, price: Decimal, size: str, unit: str) -> Optional[Decimal]:
        """Calculate price per kilogram"""
        try:
            # Extract numeric value from size
            size_match = re.search(r'(\d+(?:\.\d+)?)', size)
            if not size_match:
                return None
            
            size_value = Decimal(size_match.group(1))
            
            # Convert to kg based on unit
            if unit.lower() in ['kg', 'كجم', 'كيلو']:
                return price / size_value
            elif unit.lower() in ['g', 'جم', 'جرام', 'gram']:
                return price / (size_value / 1000)
            elif unit.lower() in ['lb', 'pound']:
                return price / (size_value * Decimal('0.453592'))
            elif unit.lower() in ['piece', 'pcs', 'قطعة']:
                # For pieces, we can't calculate per kg
                return None
            else:
                return None
        except Exception as e:
            logger.error(f"Error calculating price per kg: {e}")
            return None
    
    def detect_organic(self, text: str) -> bool:
        """Detect if product is organic"""
        organic_keywords = ['organic', 'bio', 'عضوي', 'اورجانيك']
        return any(keyword in text.lower() for keyword in organic_keywords)
    
    def clean_price(self, price_text: str) -> Decimal:
        """Extract and clean price from text"""
        try:
            # Remove currency symbols and text
            price_text = re.sub(r'[^\d.,]', '', price_text)
            # Replace comma with dot for decimal
            price_text = price_text.replace(',', '.')
            # Remove multiple dots except the last one
            parts = price_text.split('.')
            if len(parts) > 2:
                price_text = ''.join(parts[:-1]) + '.' + parts[-1]
            return Decimal(price_text)
        except Exception as e:
            logger.error(f"Error cleaning price '{price_text}': {e}")
            return Decimal("0")
    
    def match_product(self, product_text: str) -> Optional[Dict]:
        """Match scraped product with tracked products list"""
        product_text_lower = product_text.lower()
        
        for product in self.products_to_track:
            for keyword in product['keywords']:
                if keyword.lower() in product_text_lower:
                    return product
        return None
    
    @abstractmethod
    async def search_product(self, product_name: str) -> List[ProductData]:
        """Search for a specific product - must be implemented by each scraper"""
        pass
    
    @abstractmethod
    async def scrape_all_products(self) -> List[ProductData]:
        """Scrape all tracked products - must be implemented by each scraper"""
        pass
    
    async def scrape(self) -> List[ProductData]:
        """Main scraping method"""
        try:
            await self.initialize_browser()
            logger.info(f"Starting scrape for {self.store_name}")
            
            # Navigate to the website
            await self.page.goto(self.base_url, wait_until='domcontentloaded')
            await self.wait_for_page_load()
            
            # Scrape all products
            products = await self.scrape_all_products()
            
            logger.info(f"Scraped {len(products)} products from {self.store_name}")
            return products
            
        except Exception as e:
            logger.error(f"Scraping error for {self.store_name}: {e}")
            return []
        finally:
            await self.close_browser()
    
    async def handle_cookies_popup(self):
        """Handle cookie consent popups if they appear"""
        try:
            # Common cookie consent button selectors
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("I Agree")',
                'button:has-text("OK")',
                '[id*="cookie-accept"]',
                '[class*="cookie-accept"]',
                '[class*="consent-accept"]'
            ]
            
            for selector in cookie_selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=3000)
                    if button:
                        await button.click()
                        logger.info(f"Clicked cookie consent for {self.store_name}")
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"No cookie popup found for {self.store_name}")
    
    async def scroll_to_load_more(self, max_scrolls: int = 5):
        """Scroll page to load more products (for infinite scroll)"""
        for i in range(max_scrolls):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)  # Wait for content to load
            
    async def take_screenshot(self, filename: str = None):
        """Take a screenshot for debugging"""
        if not filename:
            filename = f"{self.store_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await self.page.screenshot(path=f"screenshots/{filename}")
        logger.info(f"Screenshot saved: {filename}")