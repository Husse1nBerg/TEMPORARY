"""
Price schemas for request/response validation
Path: backend/app/schemas/price.py
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class PriceBase(BaseModel):
    product_id: int
    store_id: int
    price: float
    original_price: Optional[float] = None
    price_per_kg: Optional[float] = None
    pack_size: Optional[str] = None
    pack_unit: Optional[str] = None
    is_available: bool = True
    is_discounted: bool = False
    product_url: Optional[str] = None
    image_url: Optional[str] = None

class PriceCreate(PriceBase):
    pass

class PriceResponse(PriceBase):
    id: int
    product_name: Optional[str] = None
    store_name: Optional[str] = None
    price_change: Optional[float] = 0
    price_change_percent: Optional[float] = 0
    scraped_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PriceTrend(BaseModel):
    date: str
    store_id: int
    price: float
    price_per_kg: Optional[float] = None
    is_available: bool