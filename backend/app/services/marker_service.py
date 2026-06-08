"""
MarkerService — 标记点业务逻辑层

将筛选、CRUD、文件管理从路由中抽离，路由只做 HTTP 关注点。
"""

import json
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from ..models import Marker
from ..schemas import MarkerCreate, MarkerUpdate, MarkerResponse, parse_images

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "screenshots"
_RESOLVED_UPLOAD_DIR = UPLOAD_DIR.resolve()


class MarkerService:

    # ── 筛选辅助 ──

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    @staticmethod
    def _parse_category_ids(raw: Optional[str]) -> list[int]:
        if not raw:
            return []
        ids = []
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        return ids

    @staticmethod
    def _apply_filters(query, region_id, category_id, keyword, map_name):
        if region_id is not None:
            query = query.filter(Marker.region_id == region_id)
        if category_id is not None:
            ids = MarkerService._parse_category_ids(category_id)
            if ids:
                query = query.filter(Marker.category_id.in_(ids))
        if keyword:
            escaped = MarkerService._escape_like(keyword)
            pattern = f"%{escaped}%"
            query = query.filter(
                Marker.name.like(pattern, escape="\\") |
                Marker.description.like(pattern, escape="\\")
            )
        if map_name:
            query = query.filter(Marker.map_name == map_name)
        return query

    # ── 响应构建 ──

    @staticmethod
    def to_response(marker: Marker) -> MarkerResponse:
        """显式字段映射，告别 __table__.columns 魔数"""
        return MarkerResponse(
            id=marker.id,
            region_id=marker.region_id,
            category_id=marker.category_id,
            name=marker.name,
            description=marker.description,
            x_coord=float(marker.x_coord),
            y_coord=float(marker.y_coord),
            images=parse_images(marker.screenshot),
            map_name=marker.map_name or '',
            target_region_id=marker.target_region_id,
            target_map_name=marker.target_map_name or '',
            target_x=float(marker.target_x) if marker.target_x is not None else None,
            target_y=float(marker.target_y) if marker.target_y is not None else None,
            created_at=marker.created_at,
            region=marker.region,
            category=marker.category,
        )

    # ── 文件操作 ──

    @staticmethod
    def _safe_delete_file(url: str) -> None:
        if not url:
            return
        filename = url.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        filepath = (UPLOAD_DIR / filename).resolve()
        if filepath.parent != _RESOLVED_UPLOAD_DIR:
            return
        if filepath.exists():
            filepath.unlink()

    # ── 查询 ──

    @staticmethod
    def list_markers(
        db: Session,
        region_id=None, category_id=None, keyword=None,
        map_name=None, sort_by=None, limit=None, offset=None,
    ) -> list[MarkerResponse]:
        query = db.query(Marker).options(
            joinedload(Marker.region),
            joinedload(Marker.category),
        )
        query = MarkerService._apply_filters(query, region_id, category_id, keyword, map_name)
        if sort_by == "created_at":
            query = query.order_by(Marker.created_at.desc())
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return [MarkerService.to_response(m) for m in query.all()]

    @staticmethod
    def count_markers(
        db: Session, region_id=None, category_id=None,
        keyword=None, map_name=None,
    ) -> int:
        query = MarkerService._apply_filters(
            db.query(Marker), region_id, category_id, keyword, map_name,
        )
        return query.count()

    @staticmethod
    def get_marker(db: Session, marker_id: int) -> MarkerResponse:
        marker = db.query(Marker).options(
            joinedload(Marker.region),
            joinedload(Marker.category),
        ).filter(Marker.id == marker_id).first()
        if not marker:
            return None
        return MarkerService.to_response(marker)

    # ── 写操作 ──

    @staticmethod
    def create_marker(db: Session, data: MarkerCreate) -> MarkerResponse:
        payload = data.model_dump(exclude={'images'})
        marker = Marker(**payload, screenshot=json.dumps(data.images, ensure_ascii=False))
        db.add(marker)
        db.commit()
        db.refresh(marker)
        return MarkerService.to_response(marker)

    @staticmethod
    def update_marker(db: Session, marker_id: int, data: MarkerUpdate) -> MarkerResponse:
        marker = db.query(Marker).options(
            joinedload(Marker.region),
            joinedload(Marker.category),
        ).filter(Marker.id == marker_id).first()
        if not marker:
            return None
        for key, value in data.model_dump(exclude={'images'}, exclude_unset=True).items():
            setattr(marker, key, value)
        to_delete = set()
        if data.images is not None:
            old_urls = set(parse_images(marker.screenshot))
            new_urls = set(data.images)
            to_delete = old_urls - new_urls
            marker.screenshot = json.dumps(data.images, ensure_ascii=False)
        db.commit()
        db.refresh(marker)
        for url in to_delete:
            MarkerService._safe_delete_file(url)
        return MarkerService.to_response(marker)

    @staticmethod
    def delete_marker(db: Session, marker_id: int) -> list[str]:
        marker = db.query(Marker).filter(Marker.id == marker_id).first()
        if not marker:
            return None
        urls = parse_images(marker.screenshot)
        db.delete(marker)
        db.commit()
        for url in urls:
            MarkerService._safe_delete_file(url)
        return urls
