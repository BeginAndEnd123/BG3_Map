"""
应用配置模块

从 .env 文件和系统环境变量中加载配置项。
JWT_SECRET_KEY 无默认值，部署时必须在 .env 中设置。
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# MySQL 数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("错误: 未设置 DATABASE_URL 环境变量", file=sys.stderr)
    sys.exit(1)

# JWT 签名密钥 (生产环境务必替换)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    print("错误: 未设置 JWT_SECRET_KEY 环境变量", file=sys.stderr)
    sys.exit(1)

# JWT 加密算法
_ALLOWED_ALGORITHMS = frozenset({"HS256", "HS384", "HS512"})
_raw_algo = os.getenv("JWT_ALGORITHM", "HS256")
if _raw_algo not in _ALLOWED_ALGORITHMS:
    print(f"错误: JWT_ALGORITHM '{_raw_algo}' 不在允许的白名单中", file=sys.stderr)
    sys.exit(1)
JWT_ALGORITHM = _raw_algo
# JWT 过期时间，默认 24 小时 (分钟)
try:
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
except ValueError:
    print("错误: JWT_EXPIRE_MINUTES 必须是整数", file=sys.stderr)
    sys.exit(1)
# CORS 允许的来源，逗号分隔
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
