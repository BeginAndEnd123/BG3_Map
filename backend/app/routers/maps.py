"""
地图路由 — 从 TileMap 目录扫描子地图列表及其最大缩放级别
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/maps", tags=["地图"])

# TileMap 瓦片根目录
TILE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "TileMap"

# 章节名称映射
CHAPTER_MAP = {
    "chapter0": "序章",
    "chapter1": "第一章",
    "chapter2": "第二章",
    "chapter3": "第三章",
    "chapter4": "第四章",
}


@router.get("")
def list_maps(chapter: str = ""):
    """获取子地图列表

    若指定 chapter 参数则只返回该章节的地图；否则返回全部章节分组。
    通过扫描瓦片目录自动计算每个子地图的最大 zoom 级别。
    """
    if not TILE_DIR.is_dir():
        return {} if not chapter else []

    if chapter:
        chapter = os.path.basename(chapter)
        if chapter not in CHAPTER_MAP:
            raise HTTPException(status_code=400, detail="无效的章节参数")
        dir_path = TILE_DIR / chapter
        if not dir_path.is_dir():
            raise HTTPException(404, "章节不存在")
        maps = []
        for d in sorted(dir_path.iterdir()):
            if d.is_dir():
                zooms = [int(p.name) for p in d.iterdir() if p.is_dir() and p.name.isdigit()]
                maps.append({
                    "name": d.name,
                    "tile_url": f"/TileMap/{chapter}/{d.name}/{{z}}/{{y}}/{{x}}.png",
                    "max_zoom": max(zooms) if zooms else 6,
                })
        return maps

    # 返回全部章节分组
    result = {}
    for ch in sorted(TILE_DIR.iterdir()):
        if ch.is_dir() and ch.name in CHAPTER_MAP:
            maps = []
            for d in sorted(ch.iterdir()):
                if d.is_dir():
                    zooms = [int(p.name) for p in d.iterdir() if p.is_dir() and p.name.isdigit()]
                    maps.append({
                        "name": d.name,
                        "tile_url": f"/TileMap/{ch.name}/{d.name}/{{z}}/{{y}}/{{x}}.png",
                        "max_zoom": max(zooms) if zooms else 6,
                    })
            result[ch.name] = {
                "chapter_name": CHAPTER_MAP.get(ch.name, ch.name),
                "maps": maps,
            }
    return result
