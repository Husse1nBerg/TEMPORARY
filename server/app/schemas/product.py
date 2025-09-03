from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProductCategory(str, Enum):
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    DAIRY = "dairy"
    MEAT = "meat"
    BAKERY = "bakery"
    GRAINS = "grains"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    FROZEN = "frozen"
    PANTRY = "pantry"


class ProductUnit(str, Enum):
    KG = "kg"
    GRAM = "g"
    LITER = "l"
    ML = "ml"
    PIECE = "piece"
    PACK = "pack"
    BOX = "box"
    BOTTLE = "bottle"


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    category: ProductCategory
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    unit: Optional[ProductUnit] = None
    weight: Optional[float] = Field(None, gt=0)
    brand: Optional[str] = Field(None, max_length=200)
    is_organic: bool = False
    keywords: List[str] = Field(default_factory=list)
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 keywords allowed')
        return [keyword.lower().strip() for keyword in v if keyword.strip()]


class ProductCreate(ProductBase):
    store_id: int = Field(..., gt=0)
    external_id: Optional[str] = Field(None, max_length=200)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[ProductCategory] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    unit: Optional[ProductUnit] = None
    weight: Optional[float] = Field(None, gt=0)
    brand: Optional[str] = Field(None, max_length=200)
    is_organic: Optional[bool] = None
    is_active: Optional[bool] = None
    keywords: Optional[List[str]] = None


class ProductResponse(ProductBase):
    id: int
    store_id: int
    external_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    current_price: Optional[float] = None
    
    class Config:
        from_attributes = True


class Product(ProductResponse):
    pass


class ProductWithPrices(ProductResponse):
    prices: List[Dict[str, Any]] = []
    price_history: List[Dict[str, Any]] = []


class ProductSearch(BaseModel):
    query: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[ProductCategory] = None
    store_id: Optional[int] = None
    is_organic: Optional[bool] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    is_available: Optional[bool] = None
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int


class ProductStats(BaseModel):
    id: int
    name: str
    category: ProductCategory
    avg_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_trend: Optional[str] = None  # 'up', 'down', 'stable'
    availability_rate: float = 0.0
    store_count: int = 0
    
    class Config:
        from_attributes = True