from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import auth, regions, categories, markers

app = FastAPI(title="博德之门3 交互式地图", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tile_dir = Path(__file__).resolve().parent.parent.parent / "TileMap"
app.mount("/TileMap", StaticFiles(directory=str(tile_dir)), name="tilemap")

app.include_router(auth.router)
app.include_router(regions.router)
app.include_router(categories.router)
app.include_router(markers.router)


@app.get("/")
def root():
    return {"message": "博德之门3 交互式地图 API"}
