from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class StoreStatus(str, Enum):
    IDLE = "idle"
    SCRAPING = "scraping"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class StoreType(str, Enum):
    SUPERMARKET = "supermarket"
    GROCERY = "grocery"
    PHARMACY = "pharmacy"
    CONVENIENCE = "convenience"
    ONLINE = "online"


class StoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., description="Store website URL")
    type: Optional[StoreType] = None
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = None
    scraper_class: str = Field(..., description="Python class name for the scraper")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class StoreCreate(StoreBase):
    is_active: bool = True
    scraping_interval_hours: int = Field(24, ge=1, le=168)


class StoreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = None
    type: Optional[StoreType] = None
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[StoreStatus] = None
    scraping_interval_hours: Optional[int] = Field(None, ge=1, le=168)


class StoreResponse(StoreBase):
    id: int
    is_active: bool
    status: StoreStatus
    last_scraped: Optional[datetime] = None
    scraping_interval_hours: int
    success_rate: float
    total_scrapes: int
    failed_scrapes: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Store(StoreResponse):
    pass


class StoreStats(BaseModel):
    id: int
    name: str
    total_products: int
    active_products: int
    avg_price: Optional[float] = None
    last_update: Optional[datetime] = None
    status: StoreStatus
    success_rate: float
    
    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    stores: List[StoreResponse]
    total: int
    page: int
    page_size: int


class ScrapingResult(BaseModel):
    store_id: int
    success: bool
    products_scraped: int = 0
    errors: List[str] = []
    duration_seconds: Optional[float] = None
    timestamp: datetime