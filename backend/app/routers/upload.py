"""
文件上传路由 — 接收截图文件并保存到 static/screenshots 目录

支持 JPG/PNG/GIF/WebP 格式，大小限制 5MB，通过文件头魔数校验真实类型。
SVG 文件上传前自动移除 script/事件处理器等危险标签。
"""

import uuid
import re
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from ..auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["上传"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "screenshots"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
MAX_SIZE = 5 * 1024 * 1024

# 文件头魔数签名映射：前 N 字节 -> 期望 Content-Type 前缀
MAGIC_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
}

_SVG_DANGEROUS = re.compile(
    r'<script[^>]*>.*?</script>|'
    r'on\w+\s*=\s*["\'][^"\']*["\']|'
    r'<foreignObject[^>]*>.*?</foreignObject>',
    re.IGNORECASE | re.DOTALL,
)


def _validate_magic(content: bytes, claimed_type: str) -> bool:
    if claimed_type == "image/webp":
        return content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    if claimed_type == "image/svg+xml":
        return content[:5] == b"<?xml" or content[:4] == b"<svg" or content[:10] == b"<svg xmlns"
    for magic, mime_type in MAGIC_SIGNATURES.items():
        if content.startswith(magic):
            return mime_type == claimed_type
    return False


def _sanitize_svg(content: bytes) -> bytes:
    """移除 SVG 中的 script 标签和事件处理器，防止 XSS"""
    text = content.decode("utf-8", errors="replace")
    text = _SVG_DANGEROUS.sub("", text)
    return text.encode("utf-8")


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

    if file.content_type == "image/svg+xml":
        content = _sanitize_svg(content)

    ext = "png"
    if file.filename and "." in file.filename:
        raw_ext = file.filename.rsplit(".", 1)[-1].lower()
        if re.match(r'^[a-z0-9]+$', raw_ext) and len(raw_ext) <= 5:
            ext = raw_ext
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: filepath.write_bytes(content))

    return {"url": f"/static/screenshots/{filename}"}
