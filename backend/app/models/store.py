"""
Store model
Path: backend/app/models/store.py
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    url = Column(String, nullable=False)
    type = Column(String)  # Online Basket, Talabat App, etc.
    scraper_class = Column(String)  # Name of the scraper class to use
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True))
    status = Column(String, default="idle")  # idle, scraping, online, offline
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())