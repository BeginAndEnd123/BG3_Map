import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/maps", tags=["地图"])

TILE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "TileMap"

CHAPTER_MAP = {
    "chapter0": "序章",
    "chapter1": "第一章",
    "chapter2": "第二章",
    "chapter3": "第三章",
    "chapter4": "第四章",
}


@router.get("")
def list_maps(chapter: str = ""):
    if chapter:
        dir_path = TILE_DIR / chapter
        if not dir_path.is_dir():
            raise HTTPException(404, "章节不存在")
        maps = []
        for d in sorted(dir_path.iterdir()):
            if d.is_dir():
                maps.append({
                    "name": d.name,
                    "tile_url": f"/TileMap/{chapter}/{d.name}/{{z}}/{{y}}/{{x}}.png",
                })
        return maps

    result = {}
    for ch in sorted(TILE_DIR.iterdir()):
        if ch.is_dir() and ch.name in CHAPTER_MAP:
            maps = []
            for d in sorted(ch.iterdir()):
                if d.is_dir():
                    maps.append({
                        "name": d.name,
                        "tile_url": f"/TileMap/{ch.name}/{d.name}/{{z}}/{{y}}/{{x}}.png",
                    })
            result[ch.name] = {
                "chapter_name": CHAPTER_MAP.get(ch.name, ch.name),
                "maps": maps,
            }
    return result
