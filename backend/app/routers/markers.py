from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import Marker, Region, Category
from ..schemas import MarkerCreate, MarkerUpdate, MarkerResponse
from ..auth import require_admin

router = APIRouter(prefix="/api/markers", tags=["标记"])


@router.get("", response_model=list[MarkerResponse])
def list_markers(
    region_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Marker)
    if region_id is not None:
        query = query.filter(Marker.region_id == region_id)
    if category_id is not None:
        query = query.filter(Marker.category_id == category_id)
    if keyword:
        query = query.filter(Marker.name.like(f"%{keyword}%"))
    markers = query.all()
    return [MarkerResponse.model_validate(m) for m in markers]


@router.get("/{marker_id}", response_model=MarkerResponse)
def get_marker(marker_id: int, db: Session = Depends(get_db)):
    marker = db.query(Marker).filter(Marker.id == marker_id).first()
    if not marker:
        raise HTTPException(status_code=404, detail="标记不存在")
    return MarkerResponse.model_validate(marker)


@router.post("", response_model=MarkerResponse, status_code=201)
def create_marker(
    data: MarkerCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    marker = Marker(**data.model_dump())
    db.add(marker)
    db.commit()
    db.refresh(marker)
    return MarkerResponse.model_validate(marker)


@router.put("/{marker_id}", response_model=MarkerResponse)
def update_marker(
    marker_id: int,
    data: MarkerUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    marker = db.query(Marker).filter(Marker.id == marker_id).first()
    if not marker:
        raise HTTPException(status_code=404, detail="标记不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(marker, key, value)
    db.commit()
    db.refresh(marker)
    return MarkerResponse.model_validate(marker)


@router.delete("/{marker_id}", status_code=204)
def delete_marker(
    marker_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    marker = db.query(Marker).filter(Marker.id == marker_id).first()
    if not marker:
        raise HTTPException(status_code=404, detail="标记不存在")
    db.delete(marker)
    db.commit()
