"""
数据库种子脚本

用于首次部署时自动创建表结构并填充初始数据 (区域、分类、管理员账号)。
可通过 ``python -m app.seed`` 直接运行。
"""

from .database import SessionLocal, engine
from .models import Base, Region, Category, User
from .auth import hash_password


def seed():
    """执行种子数据填充

    如果 regions 表已有数据则跳过，避免重复填充。
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Region).count() > 0:
            print("数据已存在，跳过填充")
            return

    # 五个游戏章节区域
    regions = [
        Region(name="序章", description="鹦鹉螺式魔法船", sort_order=0, tile_url="/TileMap/chapter0/{z}/{y}/{x}.png"),
        Region(name="第一章", description="林地、地精营地、幽暗地域等", sort_order=1, tile_url="/TileMap/chapter1/{z}/{y}/{x}.png"),
        Region(name="第二章", description="伊雷珂养育间", sort_order=2, tile_url="/TileMap/chapter2/{z}/{y}/{x}.png"),
        Region(name="第三章", description="月出之塔、暗夜之歌监狱等", sort_order=3, tile_url="/TileMap/chapter3/{z}/{y}/{x}.png"),
        Region(name="第四章", description="博德之门", sort_order=4, tile_url="/TileMap/chapter4/{z}/{y}/{x}.png"),
    ]
    db.add_all(regions)

    # 三种标记分类
    categories = [
        Category(name="传送点", icon="/icons/waypoint.svg", color="#00BFFF", sort_order=0),
        Category(name="怪物", icon="/icons/monster.svg", color="#FF4444", sort_order=1),
        Category(name="道具", icon="/icons/item.svg", color="#FFD700", sort_order=2),
    ]
    db.add_all(categories)

    # 默认管理员账号 (首次登录后建议修改密码)
    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        is_admin=1,
    )
    db.add(admin)

        db.commit()
        print("初始数据填充完成")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
