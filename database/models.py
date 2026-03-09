from database.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    client = "client"
    courier = "courier"
    admin = "admin"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_progress = "in_progress"
    delivered = "delivered"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="client")
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="client", foreign_keys="Order.client_id")
    assignments = relationship("Assignment", back_populates="courier")


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    opening_hours = Column(String(100), nullable=True)

    products = relationship("Product", back_populates="market", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="market")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    name = Column(String(150), nullable=False)
    unit = Column(String(30), nullable=False, default="pièce")
    price = Column(Float, nullable=False, default=0.0)
    category = Column(String(80), nullable=True)
    image_url = Column(String(500), nullable=True)

    market = relationship("Market", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    notes = Column(Text, nullable=True)
    total_estimate = Column(Float, nullable=True)
    delivery_eta = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("User", back_populates="orders", foreign_keys=[client_id])
    market = relationship("Market", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    assignment = relationship("Assignment", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False, default=1)
    note = Column(String(255), nullable=True)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="assignment")
    courier = relationship("User", back_populates="assignments")


class TrendComment(Base):
    __tablename__ = "trend_comments"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True) # None = Anonymous
    author_name = Column(String(100), nullable=True) # "Anonyme" or User's name
    text = Column(Text, nullable=False)
    trend_type = Column(String(30), default="general") # e.g. 'price_up', 'price_down', 'general'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Note: We won't add a strict relationship back to users to keep it simple, but we could.
