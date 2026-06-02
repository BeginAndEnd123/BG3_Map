from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255))
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tile_url = Column(String(255))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    markers = relationship("Marker", back_populates="region")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(255))
    color = Column(String(7))
    sort_order = Column(Integer, default=0)

    markers = relationship("Marker", back_populates="category")


class Marker(Base):
    __tablename__ = "markers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    x_coord = Column(DECIMAL(10, 2), nullable=False)
    y_coord = Column(DECIMAL(10, 2), nullable=False)
    screenshot = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

    region = relationship("Region", back_populates="markers")
    category = relationship("Category", back_populates="markers")
