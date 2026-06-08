"""
标记点路由 — 薄 HTTP 层，业务逻辑委托给 MarkerService
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import MarkerCreate, MarkerUpdate, MarkerResponse, MarkerReview
from ..auth import get_current_user, require_admin
from ..models import User
from ..services.marker_service import MarkerService

router = APIRouter(prefix="/api/markers", tags=["标记"])


@router.get("", response_model=list[MarkerResponse])
def list_markers(
    region_id: Optional[int] = Query(None),
    category_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    map_name: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if status is not None and status != 'approved' and not current_user.is_admin:
        status = 'approved'
    return MarkerService.list_markers(
        db, region_id, category_id, keyword, map_name, sort_by, limit, offset, status,
    )


@router.get("/count")
def count_markers(
    region_id: Optional[int] = Query(None),
    category_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    map_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return {"total": MarkerService.count_markers(db, region_id, category_id, keyword, map_name)}


@router.get("/pending/count")
def count_pending_markers(db: Session = Depends(get_db)):
    return {"total": MarkerService.count_markers(db, status="pending")}


@router.get("/{marker_id}", response_model=MarkerResponse)
def get_marker(marker_id: int, db: Session = Depends(get_db)):
    result = MarkerService.get_marker(db, marker_id)
    if result is None:
        raise HTTPException(status_code=404, detail="标记不存在")
    return result


@router.post("", response_model=MarkerResponse, status_code=201)
def create_marker(
    data: MarkerCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return MarkerService.create_marker(db, data)


@router.post("/user-submit", response_model=MarkerResponse, status_code=201)
def user_submit_marker(
    data: MarkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MarkerService.user_submit_marker(db, data, current_user.id)


@router.post("/{marker_id}/review", response_model=MarkerResponse)
def review_marker(
    marker_id: int,
    data: MarkerReview,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        result = MarkerService.review_marker(db, marker_id, data.action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if result is None:
        raise HTTPException(status_code=404, detail="标记不存在")
    return result


@router.put("/{marker_id}", response_model=MarkerResponse)
def update_marker(
    marker_id: int,
    data: MarkerUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    result = MarkerService.update_marker(db, marker_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="标记不存在")
    return result


@router.delete("/{marker_id}", status_code=204)
def delete_marker(
    marker_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    result = MarkerService.delete_marker(db, marker_id)
    if result is None:
        raise HTTPException(status_code=404, detail="标记不存在")
