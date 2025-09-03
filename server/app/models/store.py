from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from server.app.database import Base


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    url = Column(String, nullable=False)
    type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    scraper_class = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="idle")
    scraping_interval_hours = Column(Integer, default=24)
    success_rate = Column(Float, default=0.0)
    total_scrapes = Column(Integer, default=0)
    failed_scrapes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    products = relationship("Product", back_populates="store")
    prices = relationship("Price", back_populates="store")
    
    def __repr__(self):
        return f"<Store(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def success_percentage(self):
        if self.total_scrapes == 0:
            return 0.0
        return ((self.total_scrapes - self.failed_scrapes) / self.total_scrapes) * 100