from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from server.app.database import Base


class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    price_per_kg = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    
    pack_size = Column(String, nullable=True)
    pack_unit = Column(String, nullable=True)
    weight_value = Column(Float, nullable=True)
    weight_unit = Column(String, nullable=True)
    
    is_available = Column(Boolean, default=True)
    is_discounted = Column(Boolean, default=False)
    is_on_sale = Column(Boolean, default=False)
    
    product_url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", back_populates="prices")
    store = relationship("Store", back_populates="prices")
    
    __table_args__ = (
        Index('idx_product_store_date', 'product_id', 'store_id', 'scraped_at'),
        Index('idx_store_scraped', 'store_id', 'scraped_at'),
    )
    
    def __repr__(self):
        return f"<Price(id={self.id}, product_id={self.product_id}, store_id={self.store_id}, price={self.price})>"
    
    @property
    def discount_amount(self):
        if self.original_price and self.price < self.original_price:
            return self.original_price - self.price
        return 0.0
    
    @property
    def is_good_deal(self):
        return self.is_discounted and self.discount_percentage and self.discount_percentage > 15