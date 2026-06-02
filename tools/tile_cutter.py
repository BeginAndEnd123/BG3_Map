"""
瓦片地图切图工具
将 Map/ 目录下的 PNG 源图按章节切割为 Leaflet CRS.Simple 瓦片。
图片尺寸不足时会居中补全透明像素，使其达到 2^n × 256 标准尺寸后再切片。
支持多进程并行处理。
"""

import argparse
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install Pillow")
    sys.exit(1)

Image.MAX_IMAGE_PIXELS = None

TILE_SIZE = 256


def calc_zoom(width: int, height: int) -> int:
    max_dim = max(width, height)
    z = math.ceil(math.log2(max_dim / TILE_SIZE))
    return max(z, 1)


def pad_to_canvas(img: Image.Image, canvas_size: int) -> Image.Image:
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    x_offset = (canvas_size - img.width) // 2
    y_offset = (canvas_size - img.height) // 2
    canvas.paste(img, (x_offset, y_offset))
    return canvas


def slice_image(canvas: Image.Image, zoom: int, output_dir: Path) -> int:
    grid_size = 2 ** zoom
    tile_size = TILE_SIZE
    count = 0
    for y in range(grid_size):
        y_dir = output_dir / str(zoom) / str(y)
        y_dir.mkdir(parents=True, exist_ok=True)
        for x in range(grid_size):
            left = x * tile_size
            upper = y * tile_size
            tile = canvas.crop((left, upper, left + tile_size, upper + tile_size))
            tile.save(y_dir / f"{x}.png", "PNG", optimize=True)
            count += 1
    return count


def _process_one(args_tuple: tuple) -> tuple:
    """进程池工作函数 (独立函数以支持 pickle)"""
    src_path_str, chapter, base_output_str, min_zoom = args_tuple
    src_path = Path(src_path_str)
    base_output = Path(base_output_str)
    map_name = src_path.stem

    img = Image.open(src_path).convert("RGBA")
    w, h = img.size
    z = calc_zoom(w, h)
    canvas_size = TILE_SIZE * (2 ** z)

    canvas = pad_to_canvas(img, canvas_size)
    img.close()

    out_dir = base_output / chapter / map_name
    total_tiles = 0

    for zoom_level in range(min_zoom, z + 1):
        scale = 2 ** (zoom_level - z)
        if scale == 1:
            scaled_canvas = canvas
        else:
            new_size = int(canvas_size * scale)
            scaled_canvas = canvas.resize((new_size, new_size), Image.LANCZOS)
        count = slice_image(scaled_canvas, zoom_level, out_dir)
        total_tiles += count
        if scale != 1:
            scaled_canvas.close()

    canvas.close()
    return map_name, z, total_tiles


def main():
    parser = argparse.ArgumentParser(description="BG3 地图瓦片切图工具")
    parser.add_argument("--input", "-i", default=str(Path(__file__).parent.parent / "Map"), help="源图目录")
    parser.add_argument("--output", "-o", default=str(Path(__file__).parent.parent / "TileMap"), help="输出目录")
    parser.add_argument("--min-zoom", type=int, default=1, help="最小 zoom 级别 (默认: 1)")
    parser.add_argument("--chapter", "-c", type=str, default=None, help="只处理指定章节")
    parser.add_argument("--workers", "-w", type=int, default=None, help="并行进程数 (默认: CPU 核数)")
    parser.add_argument("--skip-existing", action="store_true", help="跳过已有瓦片目录的地图")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        sys.exit(1)

    chapters = sorted(
        d for d in input_dir.iterdir()
        if d.is_dir() and d.name.startswith("chapter") and (
            args.chapter is None or d.name == args.chapter
        )
    )
    if not chapters:
        print("错误: 未找到章节目录 (chapter0 ~ chapter4)")
        sys.exit(1)

    tasks = []
    skipped = 0
    for chapter_dir in chapters:
        chapter = chapter_dir.name
        for src_path in sorted(chapter_dir.glob("*.png")):
            map_name = src_path.stem
            if args.skip_existing and (output_dir / chapter / map_name).exists():
                skipped += 1
                continue
            tasks.append((str(src_path), chapter, str(output_dir), args.min_zoom))

    if skipped:
        print(f"跳过 {skipped} 张已存在的地图")

    if not tasks:
        print("没有需要处理的任务")
        return

    total_images = len(tasks)
    print(f"源图目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"待处理: {total_images} 张地图, {args.workers or 'auto'} 进程并行")
    print(f"缩放范围: zoom {args.min_zoom} ~ auto")
    print("=" * 60)

    workers = args.workers or min(os.cpu_count() or 4, total_images)
    grand_tiles = 0
    completed = 0

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_process_one, t): t for t in tasks}
        for future in as_completed(futures):
            try:
                name, z, tiles = future.result()
                completed += 1
                grand_tiles += tiles
                print(f"  [{completed}/{total_images}] {name} (zoom=1~{z}, {tiles} tiles)")
            except Exception as e:
                src = Path(futures[future][0])
                print(f"  [{completed+1}/{total_images}] 错误: {src.name} - {e}")
                completed += 1

    print(f"\n{'=' * 60}")
    print(f"全部完成! {completed} 张地图, 共 {grand_tiles} 张瓦片")


if __name__ == "__main__":
    main()
