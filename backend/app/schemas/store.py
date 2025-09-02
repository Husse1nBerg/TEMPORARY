"""
Store schemas for request/response validation
Path: backend/app/schemas/store.py
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class StoreBase(BaseModel):
    name: str
    url: str
    type: Optional[str] = None
    scraper_class: str

class StoreCreate(StoreBase):
    is_active: bool = True

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    scraper_class: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None

class StoreResponse(StoreBase):
    id: int
    is_active: bool
    status: str
    last_scraped: Optional[datetime] = None
    total_products: Optional[int] = 0
    available_products: Optional[int] = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True