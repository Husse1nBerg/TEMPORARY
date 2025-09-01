"""
Price model for current prices
Path: backend/app/models/price.py
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # If discounted
    price_per_kg = Column(Float)
    
    pack_size = Column(String)
    pack_unit = Column(String)
    
    is_available = Column(Boolean, default=True)
    is_discounted = Column(Boolean, default=False)
    
    product_url = Column(Text)
    image_url = Column(Text)
    
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", backref="prices")
    store = relationship("Store", backref="prices")