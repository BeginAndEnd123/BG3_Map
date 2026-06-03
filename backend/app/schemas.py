import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tile_url: Optional[str] = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int

    model_config = {"from_attributes": True}


class MarkerCreate(BaseModel):
    region_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    x_coord: float
    y_coord: float
    images: list[str] = []


class MarkerUpdate(BaseModel):
    region_id: Optional[int] = None
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    images: Optional[list[str]] = None


def parse_images(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [raw]


class MarkerResponse(BaseModel):
    id: int
    region_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    x_coord: float
    y_coord: float
    images: list[str] = []
    created_at: datetime
    region: Optional[RegionResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}
