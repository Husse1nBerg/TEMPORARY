"""
Product schemas for request/response validation
Path: backend/app/schemas/product.py
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str  # A or B
    keywords: Optional[List[str]] = []
    description: Optional[str] = None
    is_organic: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    is_organic: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True