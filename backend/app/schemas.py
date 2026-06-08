"""
Pydantic 数据校验与序列化 Schema

定义 API 请求体和响应体的数据结构，提供从 JSON 字符串解析图片列表的工具函数。
"""

import json
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    password: str
    confirm_password: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("用户名至少需要2个字符")
        if len(v) > 50:
            raise ValueError("用户名不能超过50个字符")
        if not re.match(r'^[\w\u4e00-\u9fff]+$', v):
            raise ValueError("用户名只允许字母、数字、下划线和中文")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码至少需要6个字符")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: Optional[str], info) -> Optional[str]:
        if v is not None and "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    avatar: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT 令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegionResponse(BaseModel):
    """区域信息响应"""
    id: int
    name: str
    description: Optional[str] = None
    tile_url: Optional[str] = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    """分类信息响应"""
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int

    model_config = {"from_attributes": True}


class MarkerCreate(BaseModel):
    """创建标记点请求"""
    region_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    x_coord: float
    y_coord: float
    images: list[str] = []                            # 截图 URL 列表
    map_name: str = ''                                # 所属子地图名
    target_region_id: Optional[int] = None            # 传送目标区域
    target_map_name: str = ''
    target_x: Optional[float] = None
    target_y: Optional[float] = None

    @field_validator("x_coord", "y_coord")
    @classmethod
    def coords_valid(cls, v: float) -> float:
        if v < -100000 or v > 100000:
            raise ValueError("坐标值必须在 -100000 到 100000 之间")
        return v


class MarkerUpdate(BaseModel):
    """更新标记点请求，所有字段可选"""
    region_id: Optional[int] = None
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    images: Optional[list[str]] = None
    map_name: Optional[str] = None
    target_region_id: Optional[int] = None
    target_map_name: Optional[str] = None
    target_x: Optional[float] = None
    target_y: Optional[float] = None


def parse_images(raw: Optional[str]) -> list[str]:
    """将数据库中存储的 JSON 字符串解析为图片 URL 列表

    兼容两种格式：JSON 数组和纯字符串。处理 null 值返回空列表。
    """
    if not raw:
        return []
    try:
        result = json.loads(raw)
        if result is None:
            return []
        return result
    except (json.JSONDecodeError, TypeError):
        return [raw]


class MarkerResponse(BaseModel):
    """标记点响应，包含关联的区域和分类信息"""
    id: int
    region_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    x_coord: float
    y_coord: float
    images: list[str] = []
    map_name: str = ''
    target_region_id: Optional[int] = None
    target_map_name: str = ''
    target_x: Optional[float] = None
    target_y: Optional[float] = None
    created_at: datetime
    status: str = 'approved'
    submitted_by: Optional[int] = None
    submitter_name: Optional[str] = None
    region: Optional[RegionResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}


class MarkerReview(BaseModel):
    """审核操作请求"""
    action: str  # approve / reject
