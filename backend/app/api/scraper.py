"""
Scraper API endpoints
Path: backend/app/api/scraper.py
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.store import Store
from app.api.auth import get_current_user
from app.tasks.scraping_tasks import scrape_store_task, scrape_all_stores_task

router = APIRouter()

@router.post("/trigger")
async def trigger_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    store_id: Optional[int] = None
):
    """Trigger scraping for all stores or specific store"""
    if store_id:
        # Scrape specific store
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        if not store.is_active:
            raise HTTPException(status_code=400, detail="Store is not active")
        
        # Update status
        store.status = "scraping"
        db.commit()
        
        # Add to background tasks
        background_tasks.add_task(scrape_store_task, store_id)
        
        return {
            "message": f"Scraping initiated for {store.name}",
            "store_id": store_id
        }
    else:
        # Scrape all active stores
        stores = db.query(Store).filter(Store.is_active == True).all()
        
        if not stores:
            raise HTTPException(status_code=404, detail="No active stores found")
        
        # Update all statuses
        for store in stores:
            store.status = "scraping"
        db.commit()
        
        # Add to background tasks
        background_tasks.add_task(scrape_all_stores_task)
        
        return {
            "message": "Scraping initiated for all stores",
            "stores_count": len(stores)
        }

@router.get("/status")
def get_scraping_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current scraping status for all stores"""
    stores = db.query(Store).all()
    
    status = {
        "total_stores": len(stores),
        "active_stores": len([s for s in stores if s.is_active]),
        "scraping": len([s for s in stores if s.status == "scraping"]),
        "online": len([s for s in stores if s.status == "online"]),
        "offline": len([s for s in stores if s.status == "offline"]),
        "idle": len([s for s in stores if s.status == "idle"]),
        "stores": [
            {
                "id": store.id,
                "name": store.name,
                "status": store.status,
                "last_scraped": store.last_scraped,
                "is_active": store.is_active
            }
            for store in stores
        ]
    }
    
    return status

@router.post("/stop")
def stop_scraping(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Stop all ongoing scraping tasks"""
    stores = db.query(Store).filter(Store.status == "scraping").all()
    
    for store in stores:
        store.status = "idle"
    
    db.commit()
    
    return {
        "message": "Scraping stopped",
        "affected_stores": len(stores)
    }