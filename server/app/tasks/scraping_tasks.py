# In server/app/tasks/scraping_tasks.py
import asyncio
from celery.utils.log import get_task_logger
from app.database import SessionLocal
from app.models.store import Store
from app.scrapers import SCRAPER_MAP # Assuming SCRAPER_MAP is defined in scrapers/__init__.py
from .celery_app import celery_app

logger = get_task_logger(__name__)

@celery_app.task
def scrape_store_task(store_id: int):
    """Celery task to scrape a single store."""
    logger.info(f"Starting scrape for store_id: {store_id}")
    db = SessionLocal()
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        logger.error(f"Store with id {store_id} not found.")
        db.close()
        return

    scraper_class = SCRAPER_MAP.get(store.scraper_class)
    if not scraper_class:
        logger.error(f"Scraper class {store.scraper_class} not found.")
        db.close()
        return
        
    scraper = scraper_class()
    
    try:
        scraped_data = asyncio.run(scraper.scrape_all_products())
        # Here you would add logic to save the scraped_data to the database
        logger.info(f"Successfully scraped {len(scraped_data)} items from {store.name}")
    except Exception as e:
        logger.error(f"Failed to scrape {store.name}: {e}")
    finally:
        db.close()