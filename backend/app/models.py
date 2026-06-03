"""
SQLAlchemy ORM 数据模型定义

定义用户、区域、分类和标记点四张核心表及其关联关系。
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """用户表 — 存储注册用户和管理员信息"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255))
    is_admin = Column(Integer, default=0)         # 0=普通用户, 1=管理员
    created_at = Column(DateTime, default=datetime.now)


class Region(Base):
    """区域表 — 游戏章节与对应瓦片地图配置"""
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tile_url = Column(String(255))                # Leaflet 瓦片加载 URL 模板
    sort_order = Column(Integer, default=0)       # 排序序号 (序章=0, 第一章=1 ...)
    created_at = Column(DateTime, default=datetime.now)

    markers = relationship("Marker", back_populates="region")


class Category(Base):
    """分类表 — 标记点类别，如传送点、怪物、道具"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(255))                    # 分类图标 SVG 路径
    color = Column(String(7))                     # 标记点颜色，十六进制格式
    sort_order = Column(Integer, default=0)

    markers = relationship("Marker", back_populates="category")


class Marker(Base):
    """标记点表 — 地图上的兴趣点，支持传送跳转和多截图"""
    __tablename__ = "markers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    x_coord = Column(DECIMAL(10, 2), nullable=False)      # 地图横坐标
    y_coord = Column(DECIMAL(10, 2), nullable=False)      # 地图纵坐标
    screenshot = Column(Text)                              # JSON 数组存储截图 URL 列表
    map_name = Column(String(100), default='')             # 所属子地图名称
    target_region_id = Column(Integer, nullable=True)      # 传送目标区域 ID
    target_map_name = Column(String(100), default='')      # 传送目标子地图名称
    target_x = Column(DECIMAL(10, 2), nullable=True)       # 传送目标 X 坐标
    target_y = Column(DECIMAL(10, 2), nullable=True)       # 传送目标 Y 坐标
    created_at = Column(DateTime, default=datetime.now)

    region = relationship("Region", back_populates="markers")
    category = relationship("Category", back_populates="markers")
