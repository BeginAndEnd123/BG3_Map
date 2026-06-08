"""
文件上传路由 — 接收截图文件并保存到 static/screenshots 目录

支持 JPG/PNG/GIF/WebP 格式，大小限制 5MB，通过文件头魔数校验真实类型。
"""

import uuid
import re
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from ..auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["上传"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "screenshots"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024

# 文件头魔数签名映射：前 N 字节 -> 期望 Content-Type 前缀
MAGIC_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
}


def _validate_magic(content: bytes, claimed_type: str) -> bool:
    if claimed_type == "image/webp":
        return content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    for magic, mime_type in MAGIC_SIGNATURES.items():
        if content.startswith(magic):
            return mime_type == claimed_type
    return False


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    _=Depends(get_current_user),
):
    """上传截图文件，返回可访问的静态 URL (需登录)"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    if not _validate_magic(content, file.content_type):
        raise HTTPException(status_code=400, detail="文件内容与声称的类型不符")

    ext = "png"
    if file.filename and "." in file.filename:
        raw_ext = file.filename.rsplit(".", 1)[-1].lower()
        if re.match(r'^[a-z0-9]+$', raw_ext) and len(raw_ext) <= 5:
            ext = raw_ext
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(content)

    return {"url": f"/static/screenshots/{filename}"}
