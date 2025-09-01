"""
Price history model for tracking price changes
Path: backend/app/models/price_history.py
"""

from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    
    price = Column(Float, nullable=False)
    price_per_kg = Column(Float)
    
    is_available = Column(Boolean, default=True)
    
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    product = relationship("Product", backref="price_history")
    store = relationship("Store", backref="price_history")