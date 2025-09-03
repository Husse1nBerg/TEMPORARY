from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from server.app.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True)
    keywords = Column(Text)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    weight = Column(Float, nullable=True)
    brand = Column(String, nullable=True)
    is_organic = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    external_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    store = relationship("Store", back_populates="products")
    prices = relationship("Price", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, store={self.store.name if self.store else 'None'})>"
    
    @property
    def current_price(self):
        if self.prices:
            return max(self.prices, key=lambda p: p.updated_at)
        return None