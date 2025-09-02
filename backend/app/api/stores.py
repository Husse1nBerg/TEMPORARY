"""
Stores API endpoints
Path: backend/app/api/stores.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.store import Store
from app.models.price import Price
from app.schemas.store import StoreCreate, StoreResponse, StoreUpdate
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[StoreResponse])
def get_stores(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None
):
    """Get all stores"""
    query = db.query(Store)
    
    if is_active is not None:
        query = query.filter(Store.is_active == is_active)
    
    stores = query.offset(skip).limit(limit).all()
    
    # Add product counts
    results = []
    for store in stores:
        # Count total and available products
        total_products = db.query(Price).filter(Price.store_id == store.id).count()
        available_products = db.query(Price).filter(
            Price.store_id == store.id,
            Price.is_available == True
        ).count()
        
        store_dict = {
            "id": store.id,
            "name": store.name,
            "url": store.url,
            "type": store.type,
            "scraper_class": store.scraper_class,
            "is_active": store.is_active,
            "status": store.status,
            "last_scraped": store.last_scraped,
            "total_products": total_products,
            "available_products": available_products,
            "created_at": store.created_at,
            "updated_at": store.updated_at
        }
        results.append(store_dict)
    
    return results

@router.post("/", response_model=StoreResponse)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new store"""
    # Check if store exists
    existing = db.query(Store).filter(Store.name == store.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store already exists")
    
    db_store = Store(
        name=store.name,
        url=store.url,
        type=store.type,
        scraper_class=store.scraper_class,
        is_active=store.is_active
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific store by ID"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Add product counts
    total_products = db.query(Price).filter(Price.store_id == store.id).count()
    available_products = db.query(Price).filter(
        Price.store_id == store.id,
        Price.is_available == True
    ).count()
    
    store_dict = store.__dict__.copy()
    store_dict["total_products"] = total_products
    store_dict["available_products"] = available_products
    
    return store_dict

@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store_update: StoreUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update store"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    for field, value in store_update.dict(exclude_unset=True).items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    return store

@router.delete("/{store_id}")
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete store (soft delete)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    store.is_active = False
    db.commit()
    return {"message": "Store deleted successfully"}