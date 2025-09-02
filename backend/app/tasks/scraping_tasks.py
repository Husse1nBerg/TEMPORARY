"""
Celery tasks for web scraping
Path: backend/app/tasks/scraping_tasks.py
"""

from celery import shared_task
from celery.schedules import crontab
from datetime import datetime
import logging
import asyncio
from typing import List

from app.database import SessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.price import Price
from app.models.price_history import PriceHistory
from app.scrapers import (
    GourmetScraper,
    RDNAScraper,
    MetroScraper,
    SpinneysScraper,
    RabbitScraper,
    TalabatScraper,
    InstashopScraper,
    BreadfastScraper
)

logger = logging.getLogger(__name__)

# Map store names to scraper classes
SCRAPER_MAP = {
    "GourmetScraper": GourmetScraper,
    "RDNAScraper": RDNAScraper,
    "MetroScraper": MetroScraper,
    "SpinneysScraper": SpinneysScraper,
    "RabbitScraper": RabbitScraper,
    "TalabatScraper": TalabatScraper,
    "InstashopScraper": InstashopScraper,
    "BreadfastScraper": BreadfastScraper
}

def setup_periodic_tasks():
    """Setup periodic scraping tasks"""
    from app.tasks.celery_app import celery_app
    
    # Schedule scraping every 6 hours
    celery_app.conf.beat_schedule = {
        'scrape-all-stores': {
            'task': 'app.tasks.scraping_tasks.scrape_all_stores_task',
            'schedule': crontab(hour='*/6'),  # Every 6 hours
        },
    }

@shared_task
def scrape_store_task(store_id: int):
    """Scrape a specific store"""
    db = SessionLocal()
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            logger.error(f"Store {store_id} not found")
            return
        
        # Get scraper class
        scraper_class = SCRAPER_MAP.get(store.scraper_class)
        if not scraper_class:
            logger.error(f"Scraper class {store.scraper_class} not found")
            store.status = "offline"
            db.commit()
            return
        
        # Update store status
        store.status = "scraping"
        db.commit()
        
        # Run scraper
        scraper = scraper_class()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        products_data = loop.run_until_complete(scraper.scrape())
        loop.close()
        
        # Save scraped data
        save_scraped_data(db, store_id, products_data)
        
        # Update store status
        store.status = "online"
        store.last_scraped = datetime.utcnow()
        db.commit()
        
        logger.info(f"Successfully scraped {len(products_data)} products from {store.name}")
        
    except Exception as e:
        logger.error(f"Error scraping store {store_id}: {e}")
        if store:
            store.status = "offline"
            db.commit()
    finally:
        db.close()

@shared_task
def scrape_all_stores_task():
    """Scrape all active stores"""
    db = SessionLocal()
    try:
        stores = db.query(Store).filter(Store.is_active == True).all()
        
        for store in stores:
            scrape_store_task.delay(store.id)
        
        logger.info(f"Initiated scraping for {len(stores)} stores")
        
    except Exception as e:
        logger.error(f"Error initiating scraping: {e}")
    finally:
        db.close()

def save_scraped_data(db, store_id: int, products_data: List):
    """Save scraped product data to database"""
    try:
        # Get all products
        products = db.query(Product).all()
        product_map = {p.name.lower(): p for p in products}
        
        for data in products_data:
            # Find matching product
            product = product_map.get(data.name.lower())
            if not product:
                # Create new product if not exists
                product = Product(
                    name=data.name,
                    category=data.category or "A",
                    is_organic=data.is_organic
                )
                db.add(product)
                db.flush()
            
            # Check if price already exists
            existing_price = db.query(Price).filter(
                Price.product_id == product.id,
                Price.store_id == store_id
            ).order_by(Price.scraped_at.desc()).first()
            
            # Save new price
            new_price = Price(
                product_id=product.id,
                store_id=store_id,
                price=float(data.price),
                original_price=float(data.original_price) if data.original_price else None,
                price_per_kg=float(data.price_per_kg) if data.price_per_kg else None,
                pack_size=data.pack_size,
                pack_unit=data.pack_unit,
                is_available=data.is_available,
                is_discounted=data.is_discounted,
                product_url=data.product_url,
                image_url=data.image_url
            )
            db.add(new_price)
            
            # Add to price history
            history = PriceHistory(
                product_id=product.id,
                store_id=store_id,
                price=float(data.price),
                price_per_kg=float(data.price_per_kg) if data.price_per_kg else None,
                is_available=data.is_available
            )
            db.add(history)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error saving scraped data: {e}")
        db.rollback()
        raise

def trigger_scraping(db):
    """Trigger scraping for all stores (called from API)"""
    stores = db.query(Store).filter(Store.is_active == True).all()
    
    for store in stores:
        scrape_store_task.delay(store.id)
    
    return len(stores)