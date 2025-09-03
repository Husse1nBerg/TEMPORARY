# In server/app/api/scraper.py

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

# Note: These are dependencies you will need to create
from app.database import get_db
from app.tasks.scraping_tasks import scrape_store_task, scrape_all_stores_task
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/trigger")
async def trigger_scraping_endpoint(
    background_tasks: BackgroundTasks,
    store_id: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """Trigger scraping for a specific store or all stores."""
    if store_id:
        background_tasks.add_task(scrape_store_task, store_id)
        return {"message": f"Scraping initiated for store ID: {store_id}"}
    
    background_tasks.add_task(scrape_all_stores_task)
    return {"message": "Scraping initiated for all active stores"}