"""
区域路由 — 按 sort_order 排序返回所有游戏区域
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Region
from ..schemas import RegionResponse

router = APIRouter(prefix="/api/regions", tags=["区域"])


@router.get("", response_model=list[RegionResponse])
def list_regions(db: Session = Depends(get_db)):
    """获取所有区域列表，按 sort_order 升序排列"""
    regions = db.query(Region).order_by(Region.sort_order).all()
    return [RegionResponse.model_validate(r) for r in regions]


@router.get("/{region_id}", response_model=RegionResponse)
def get_region(region_id: int, db: Session = Depends(get_db)):
    """根据 ID 获取单个区域详情"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")
    return RegionResponse.model_validate(region)
