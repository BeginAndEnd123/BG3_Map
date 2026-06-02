from .database import SessionLocal, engine
from .models import Base, Region, Category, User
from .auth import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Region).count() > 0:
        print("数据已存在，跳过填充")
        return

    regions = [
        Region(name="序章", description="鹦鹉螺式魔法船", sort_order=0, tile_url="/TileMap/chapter0/{z}/{x}/{y}.png"),
        Region(name="第一章", description="林地、地精营地、幽暗地域等", sort_order=1, tile_url="/TileMap/chapter1/{z}/{x}/{y}.png"),
        Region(name="第二章", description="伊雷珂养育间", sort_order=2, tile_url="/TileMap/chapter2/{z}/{x}/{y}.png"),
        Region(name="第三章", description="月出之塔、暗夜之歌监狱等", sort_order=3, tile_url="/TileMap/chapter3/{z}/{x}/{y}.png"),
        Region(name="第四章", description="博德之门", sort_order=4, tile_url="/TileMap/chapter4/{z}/{x}/{y}.png"),
    ]
    db.add_all(regions)

    categories = [
        Category(name="传送点", icon="/icons/waypoint.png", color="#00BFFF", sort_order=0),
        Category(name="怪物", icon="/icons/monster.png", color="#FF4444", sort_order=1),
        Category(name="道具", icon="/icons/item.png", color="#FFD700", sort_order=2),
    ]
    db.add_all(categories)

    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
    )
    db.add(admin)

    db.commit()
    print("初始数据填充完成")


if __name__ == "__main__":
    seed()
