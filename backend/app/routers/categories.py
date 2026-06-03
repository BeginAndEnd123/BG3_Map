"""
分类路由 — 按 sort_order 排序返回标记分类列表
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category
from ..schemas import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["分类"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """获取所有标记分类列表"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    return [CategoryResponse.model_validate(c) for c in categories]
