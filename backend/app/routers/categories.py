"""
分类路由 — 分类列表查询 + 管理员新增/删除
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category, Marker
from ..schemas import CategoryResponse, CategoryCreate, CategoryUpdate
from ..auth import require_admin

router = APIRouter(prefix="/api/categories", tags=["分类"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """获取所有标记分类列表"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """管理员新增标记分类"""
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """管理员删除标记分类（无标记引用的分类才能删除）"""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    marker_count = db.query(Marker).filter(Marker.category_id == category_id).limit(1).count()
    if marker_count > 0:
        raise HTTPException(status_code=400, detail="该分类下存在标记，无法删除")
    db.delete(cat)
    db.commit()


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """管理员修改标记分类"""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    if data.name is not None:
        existing = db.query(Category).filter(Category.name == data.name, Category.id != category_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="分类名称已存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat
