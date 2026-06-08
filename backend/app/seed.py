"""
数据库种子脚本

用于首次部署时自动创建表结构并填充初始数据 (区域、分类、管理员账号)。
管理员密码从环境变量 ADMIN_PASSWORD 读取，未设置时生成随机密码输出到控制台。
可通过 ``python -m app.seed`` 直接运行。
"""

import os
import secrets
import logging
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
            Region(name="序章", description="鹦鹉螺式魔法船", sort_order=0),
            Region(name="第1章", description="林地、地精营地、幽暗地域", sort_order=1),
            Region(name="第1.5章", description="伊雷珂养育间", sort_order=2),
            Region(name="第2章", description="幽影诅咒之地、月出之塔", sort_order=3),
            Region(name="第3章", description="博德之门", sort_order=4),
        ]
        db.add_all(regions)

        # 四种标记分类
        categories = [
            Category(name="传送点", icon="/icons/waypoint.svg", sort_order=0),
            Category(name="怪物", icon="/icons/monster.svg", sort_order=1),
            Category(name="道具", icon="/icons/item.svg", sort_order=2),
            Category(name="商人", icon="/icons/merchant.svg", sort_order=3),
        ]
        db.add_all(categories)

        # 默认管理员账号：密码从环境变量读取，未设置则生成随机密码
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            admin_password = secrets.token_hex(8)
            logging.warning("未设置 ADMIN_PASSWORD，已生成随机管理员密码，请妥善保存: %s", admin_password)
        admin = User(
            username="admin",
            password_hash=hash_password(admin_password),
            is_admin=True,
        )
        db.add(admin)

        db.commit()
        print("初始数据填充完成")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
