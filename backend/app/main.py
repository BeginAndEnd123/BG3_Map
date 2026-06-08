"""
博德之门3 交互式地图 — FastAPI 应用入口

挂载静态资源、注册路由模块并配置 CORS 跨域支持。
"""

import logging
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .routers import auth, regions, categories, markers, maps, upload
from .config import CORS_ORIGINS

logger = logging.getLogger("bg3map")

app = FastAPI(title="博德之门3 交互式地图", version="1.0.0")


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

# 挂载瓦片地图静态资源目录
tile_dir = Path(__file__).resolve().parent.parent.parent / "TileMap"
if tile_dir.is_dir():
    app.mount("/TileMap", StaticFiles(directory=str(tile_dir)), name="tilemap")

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
