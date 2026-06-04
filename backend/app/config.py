"""
应用配置模块

从 .env 文件和系统环境变量中加载配置项，提供默认值用于本地开发。
"""

import os
from dotenv import load_dotenv

load_dotenv()

# MySQL 数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/bg3_map")
# JWT 签名密钥 (生产环境务必替换)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
# JWT 加密算法
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
# JWT 过期时间，默认 24 小时 (分钟)
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
# CORS 允许的来源，逗号分隔
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
