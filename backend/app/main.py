"""
博德之门3 交互式地图 — FastAPI 应用入口

挂载静态资源、注册路由模块并配置 CORS 跨域支持。
"""

import logging
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import auth, regions, categories, markers, maps, upload
from .config import CORS_ORIGINS

logger = logging.getLogger("bg3map")

app = FastAPI(title="博德之门3 交互式地图", version="1.0.0")

# 缺失瓦片的透明 PNG 占位图
_TILE_PLACEHOLDER = bytes([
    0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,
    0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,
    0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,0x54,0x78,0x9C,0x63,0xF8,0x0F,0x00,0x00,
    0x01,0x01,0x00,0x05,0x18,0xD8,0x4E,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,
    0x42,0x60,0x82
])


@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info("%s %s → %s (%.0fms)", request.method, request.url.path, response.status_code, duration)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("未捕获的异常: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )

# 中间件按注册顺序执行
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 瓦片地图 — 自定义路由，缺失瓦片返回透明占位图避免 404 日志刷屏
_tile_dir = Path(__file__).resolve().parent.parent.parent / "TileMap"

@app.get("/TileMap/{rest:path}")
async def serve_tile(rest: str):
    path = (_tile_dir / rest).resolve()
    if not str(path).startswith(str(_tile_dir.resolve())):
        raise StarletteHTTPException(403)
    if path.is_file():
        return Response(content=path.read_bytes(), media_type="image/png")
    return Response(content=_TILE_PLACEHOLDER, media_type="image/png", status_code=200)

# 注册各功能模块路由
app.include_router(auth.router)
app.include_router(regions.router)
app.include_router(categories.router)
app.include_router(markers.router)
app.include_router(maps.router)
app.include_router(upload.router)

# 挂载截图上传静态目录
static_dir = Path(__file__).resolve().parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def root():
    """API 根路径，返回欢迎信息"""
    return {"message": "博德之门3 交互式地图 API"}
