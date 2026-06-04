"""
标记点路由 — CRUD 操作，支持多条件筛选、分页和截图关联删除
"""

import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from ..database import get_db
from ..models import Marker, Region, Category
from ..schemas import MarkerCreate, MarkerUpdate, MarkerResponse, parse_images
from ..auth import require_admin

router = APIRouter(prefix="/api/markers", tags=["标记"])

# 截图文件存储目录
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "screenshots"


def _to_response(marker: Marker) -> dict:
    """将 ORM Marker 对象转换为可用于 MarkerResponse 校验的字典

    处理 screenshot 字段 (JSON 字符串 -> URL 列表) 并附加关联的 region/category 对象。
    """
    data = {c.name: getattr(marker, c.name) for c in marker.__table__.columns}
    data['images'] = parse_images(data.pop('screenshot', None))
    data['region'] = marker.region
    data['category'] = marker.category
    return data


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _parse_category_ids(raw: Optional[str]) -> list[int]:
    if not raw:
        return []
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return ids


@router.get("", response_model=list[MarkerResponse])
def list_markers(
    region_id: Optional[int] = Query(None),
    category_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    map_name: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """查询标记点列表，支持按区域/分类(多选逗号分隔)/关键词/地图名筛选，以及分页和排序"""
    query = db.query(Marker).options(
        joinedload(Marker.region),
        joinedload(Marker.category),
    )
    if region_id is not None:
        query = query.filter(Marker.region_id == region_id)
    if category_id is not None:
        ids = _parse_category_ids(category_id)
        if ids:
            query = query.filter(Marker.category_id.in_(ids))
    if keyword:
        escaped = _escape_like(keyword)
        pattern = f"%{escaped}%"
        query = query.filter(
            Marker.name.like(pattern, escape="\\") |
            Marker.description.like(pattern, escape="\\")
        )
    if map_name:
        query = query.filter(Marker.map_name == map_name)
    if sort_by == "created_at":
        query = query.order_by(Marker.created_at.desc())
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)
    markers = query.all()
    return [MarkerResponse.model_validate(_to_response(m)) for m in markers]


@router.get("/count")
def count_markers(
    region_id: Optional[int] = Query(None),
    category_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    map_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """统计满足筛选条件的标记点总数 (用于分页)"""
    query = db.query(Marker)
    if region_id is not None:
        query = query.filter(Marker.region_id == region_id)
    if category_id is not None:
        ids = _parse_category_ids(category_id)
        if ids:
            query = query.filter(Marker.category_id.in_(ids))
    if keyword:
        escaped = _escape_like(keyword)
        pattern = f"%{escaped}%"
        query = query.filter(
            Marker.name.like(pattern, escape="\\") |
            Marker.description.like(pattern, escape="\\")
        )
    if map_name:
        query = query.filter(Marker.map_name == map_name)
    return {"total": query.count()}


@router.get("/{marker_id}", response_model=MarkerResponse)
def get_marker(marker_id: int, db: Session = Depends(get_db)):
    """获取单个标记点详情"""
    marker = db.query(Marker).options(
        joinedload(Marker.region),
        joinedload(Marker.category),
    ).filter(Marker.id == marker_id).first()
    if not marker:
        raise HTTPException(status_code=404, detail="标记不存在")
    return MarkerResponse.model_validate(_to_response(marker))


@router.post("", response_model=MarkerResponse, status_code=201)
def create_marker(
    data: MarkerCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """创建新标记点 (需要管理员权限)

    images 列表序列化为 JSON 字符串存入 screenshot 字段。
    """
    payload = data.model_dump(exclude={'images'})
    marker = Marker(**payload, screenshot=json.dumps(data.images, ensure_ascii=False))
    db.add(marker)
    db.commit()
    db.refresh(marker)
    return MarkerResponse.model_validate(_to_response(marker))


@router.put("/{marker_id}", response_model=MarkerResponse)
def update_marker(
    marker_id: int,
    data: MarkerUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """更新标记点 (需要管理员权限)

    若更新了 images 字段，会自动清理不再引用的旧截图文件。
    """
    marker = db.query(Marker).options(
        joinedload(Marker.region),
        joinedload(Marker.category),
    ).filter(Marker.id == marker_id).first()
    if not marker:
        raise HTTPException(status_code=404, detail="标记不存在")
    for key, value in data.model_dump(exclude={'images'}, exclude_unset=True).items():
        setattr(marker, key, value)
    if data.images is not None:
        old_urls = set(parse_images(marker.screenshot))
        new_urls = set(data.images)
        # 删除被移除的旧截图文件
        for url in old_urls - new_urls:
            filename = url.rsplit("/", 1)[-1]
            filepath = UPLOAD_DIR / filename
            if filepath.exists():
                filepath.unlink()
        marker.screenshot = json.dumps(data.images, ensure_ascii=False)
    db.commit()
    db.refresh(marker)
    return MarkerResponse.model_validate(_to_response(marker))


def _delete_image_files(marker: Marker):
    """辅助函数：删除标记点关联的所有截图文件"""
    urls = parse_images(marker.screenshot)
    for url in urls:
        filename = url.rsplit("/", 1)[-1]
        filepath = UPLOAD_DIR / filename
        if filepath.exists():
            filepath.unlink()


@router.delete("/{marker_id}", status_code=204)
def delete_marker(
    marker_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """删除标记点 (需要管理员权限)

    同时删除关联的截图文件，释放磁盘空间。
    """
    marker = db.query(Marker).filter(Marker.id == marker_id).first()
    if not marker:
        raise HTTPException(status_code=404, detail="标记不存在")
    _delete_image_files(marker)
    db.delete(marker)
    db.commit()
