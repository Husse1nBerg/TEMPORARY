from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class PriceChangeType(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    NEW = "new"
    UNAVAILABLE = "unavailable"
    STABLE = "stable"


class PriceBase(BaseModel):
    product_id: int = Field(..., gt=0)
    store_id: int = Field(..., gt=0)
    price: float = Field(..., gt=0, description="Current selling price")
    original_price: Optional[float] = Field(None, gt=0, description="Original price before discount")
    price_per_kg: Optional[float] = Field(None, gt=0, description="Price per kilogram")
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    pack_size: Optional[str] = Field(None, max_length=50)
    pack_unit: Optional[str] = Field(None, max_length=20)
    weight_value: Optional[float] = Field(None, gt=0)
    weight_unit: Optional[str] = Field(None, max_length=20)
    is_available: bool = True
    is_discounted: bool = False
    is_on_sale: bool = False
    product_url: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=2000)
    
    @validator('discount_percentage')
    def validate_discount(cls, v, values):
        if v is not None and 'original_price' in values and values['original_price'] is not None:
            if 'price' in values and values['price'] is not None:
                calculated_discount = ((values['original_price'] - values['price']) / values['original_price']) * 100
                if abs(calculated_discount - v) > 1:  # Allow 1% tolerance
                    raise ValueError('Discount percentage does not match price difference')
        return v


class PriceCreate(PriceBase):
    pass


class PriceUpdate(BaseModel):
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None
    is_discounted: Optional[bool] = None
    is_on_sale: Optional[bool] = None


class PriceResponse(PriceBase):
    id: int
    product_name: Optional[str] = None
    store_name: Optional[str] = None
    product_category: Optional[str] = None
    product_brand: Optional[str] = None
    price_change_percent: Optional[float] = None
    scraped_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Price(PriceResponse):
    pass


class PriceHistory(BaseModel):
    id: int
    product_id: int
    store_id: int
    price: float
    original_price: Optional[float] = None
    is_available: bool
    change_type: Optional[PriceChangeType] = None
    change_amount: Optional[float] = None
    change_percentage: Optional[float] = None
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class PriceTrend(BaseModel):
    date: date
    price: float
    original_price: Optional[float] = None
    is_available: bool = True


class PriceComparison(BaseModel):
    product_id: int
    product_name: str
    prices: List[Dict[str, Any]]
    lowest_price: float
    highest_price: float
    avg_price: float
    best_deal_store: Optional[str] = None


class PriceAlert(BaseModel):
    id: int
    user_id: int
    product_id: int
    target_price: float
    condition: str  # 'below', 'above', 'equal'
    is_active: bool = True
    created_at: datetime


class PriceStats(BaseModel):
    total_prices: int
    avg_price: float
    min_price: float
    max_price: float
    price_range: float
    discounted_count: int
    available_count: int
    last_updated: datetime


class PriceListResponse(BaseModel):
    prices: List[PriceResponse]
    total: int
    page: int
    page_size: int


class PriceFilter(BaseModel):
    product_id: Optional[int] = None
    store_id: Optional[int] = None
    category: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    is_available: Optional[bool] = None
    is_discounted: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v