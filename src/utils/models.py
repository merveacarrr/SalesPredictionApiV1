from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from src.utils.db import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False, unique=True, index=True)

    # İlişkiler
    order_details = relationship("OrderDetail", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    order_date = Column(Date, nullable=False)

    
    order_details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "order_details"

    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")
