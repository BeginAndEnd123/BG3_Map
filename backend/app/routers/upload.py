"""
文件上传路由 — 接收截图文件并保存到 static/screenshots 目录

支持 JPG/PNG/GIF/WebP 格式，大小限制 5MB。
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/api/upload", tags=["上传"])

# 截图存储目录
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "screenshots"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的图片 MIME 类型
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
# 单文件最大 5MB
MAX_SIZE = 5 * 1024 * 1024


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """上传截图文件，返回可访问的静态 URL"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    # 用 UUID 重命名文件，防止文件名冲突
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(content)

    return {"url": f"/static/screenshots/{filename}"}
