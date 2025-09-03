from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, String, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from server.app.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    price_per_kg = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    
    pack_size = Column(String, nullable=True)
    pack_unit = Column(String, nullable=True)
    
    is_available = Column(Boolean, default=True)
    is_discounted = Column(Boolean, default=False)
    
    change_type = Column(String, nullable=True)  # 'increase', 'decrease', 'new', 'unavailable'
    change_amount = Column(Float, nullable=True)
    change_percentage = Column(Float, nullable=True)
    
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="price_history")
    store = relationship("Store")
    
    __table_args__ = (
        Index('idx_product_history_date', 'product_id', 'recorded_at'),
        Index('idx_store_history_date', 'store_id', 'recorded_at'),
        Index('idx_product_store_history', 'product_id', 'store_id', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, store_id={self.store_id}, price={self.price}, recorded_at={self.recorded_at})>"
    
    @property
    def is_price_drop(self):
        return self.change_type == 'decrease' and self.change_percentage and self.change_percentage > 5
    
    @property
    def significant_change(self):
        return abs(self.change_percentage or 0) > 10