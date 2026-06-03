"""
数据库连接模块

创建 SQLAlchemy 引擎和会话工厂，提供 FastAPI 依赖注入式的数据库会话获取函数。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

# SQLAlchemy 引擎实例
engine = create_engine(DATABASE_URL)
# 会话工厂，关闭自动提交和自动刷新，由业务逻辑显式控制事务
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ORM 模型基类
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：为每个请求创建一个独立的数据库会话，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
