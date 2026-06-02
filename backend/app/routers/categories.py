from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category
from ..schemas import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["分类"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.sort_order).all()
    return [CategoryResponse.model_validate(c) for c in categories]
