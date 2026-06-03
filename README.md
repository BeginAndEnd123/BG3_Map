# 交互式游戏地图 — 课程设计

## 项目背景

为《博德之门3》开发的 Web 端交互式地图系统。用户可以浏览游戏地图、查看各类标记点（NPC、传送点、怪物、道具等）、搜索定位、标记收藏。

## 技术栈

| 层面 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | Python 3.10+ |
| 数据库 | MySQL | 8.0 |
| ORM | SQLAlchemy 2.0 + Alembic | - |
| 前端框架 | Vue 3 | Composition API |
| 构建工具 | Vite | 5.x |
| 状态管理 | Pinia | 2.x |
| 路由 | Vue Router | 4.x |
| HTTP 客户端 | Axios | 1.x |
| 地图引擎 | Leaflet.js (CRS.Simple) | 1.9 |
| 认证 | JWT (python-jose + passlib) | - |


## 系统架构

```mermaid
graph TB
    subgraph 前端["前端 — Vue 3 SPA (Port 5173)"]
        Router["路由 Vue Router"]
        Store["状态管理 Pinia"]
        Components["组件层"]
        MapContainer["MapContainer.vue<br/>Leaflet CRS.Simple"]
        SidePanel["SidePanel.vue<br/>筛选/搜索/统计"]
        MarkerPopup["MarkerPopup.vue<br/>详情弹窗"]
        MarkerForm["MarkerForm.vue<br/>创建/编辑表单"]
        NavBar["NavBar.vue<br/>用户信息/登出"]
        API["API 层 Axios<br/>(JWT Bearer Token)"]
        Components --- MapContainer
        Components --- SidePanel
        Components --- MarkerPopup
        Components --- MarkerForm
        Components --- NavBar
    end

    subgraph 后端["后端 — FastAPI (Port 8000)"]
        Auth["JWT 认证层<br/>登录校验 / 管理员权限"]
        Routers["路由层"]
        AuthRouter["auth.py<br/>注册/登录/me"]
        RegionsRouter["regions.py<br/>区域查询"]
        CategoriesRouter["categories.py<br/>分类查询"]
        MarkersRouter["markers.py<br/>标记 CRUD"]
        MapsRouter["maps.py<br/>地图列表"]
        UploadRouter["upload.py<br/>截图上传"]
        ORM["ORM SQLAlchemy"]
        StaticFiles["静态文件挂载"]
        TileMap["/TileMap<br/>瓦片地图"]
        Static["/static<br/>上传截图"]
        Routers --- AuthRouter
        Routers --- RegionsRouter
        Routers --- CategoriesRouter
        Routers --- MarkersRouter
        Routers --- MapsRouter
        Routers --- UploadRouter
    end

    subgraph 存储["存储层"]
        DB[("MySQL 8.0<br/>bg3_map")]
        FS1["文件系统<br/>TileMap/ (97 张地图, 68,548 tiles)"]
        FS2["文件系统<br/>static/screenshots/ (上传图片)"]
    end

    前端 -->|"Axios HTTP (代理 /api /TileMap /static)"| 后端
    AuthRouter -->|"验证登录"--> Auth
    MarkersRouter -.->|"需管理员权限"--> Auth
    UploadRouter -.->|"需登录"--> Auth
    后端 --> ORM
    ORM --> DB
    TileMap --> FS1
    Static --> FS2
```

## 功能需求

### 用户故事

| 角色 | 需求 | 目的 |
|------|------|------|
| 玩家 | 浏览游戏地图 | 查看各区域地形与地标 |
| 玩家 | 查找标记点 | 快速定位 NPC、传送点、怪物、道具位置 |
| 玩家 | 搜索标记 | 按名称模糊匹配找到目标点 |
| 管理员 | 管理标记数据 | 新增、编辑、删除标记点信息 |

### 用户系统
- 用户注册 / 登录（JWT 认证）
- 个人信息查看

### 地图浏览
- 瓦片地图加载与渲染（Leaflet CRS.Simple）
- 鼠标拖拽平移、滚轮缩放
- 多区域/章节地图切换
- 按分类筛选标记点（显示/隐藏）

### 标记系统
- 标记点展示（图标 + 名称 + 坐标）
- 标记分类：传送点、怪物、道具
- 点击标记显示详情弹窗（描述、坐标、所属区域）
- 标记搜索（按名称模糊匹配）
- 管理员新增/编辑/删除标记

### 数据面板
- 各类标记数量统计
- 最新添加的标记

### 边界
- 本项目不涉及实时多人协作编辑
- 不涉及移动端适配（仅桌面端）
- 地图瓦片为预切片，不支持运行时动态切图

## 非功能性需求

| 类别 | 要求 |
|------|------|
| 性能 | 首屏加载 ≤ 3s，瓦片加载无明显卡顿 |
| 可用性 | 界面简洁，操作直觉，无需培训即可使用 |
| 安全性 | 密码 bcrypt 加密存储；JWT 令牌过期自动失效；管理员接口需认证 |
| 兼容性 | 支持 Chrome / Edge / Firefox 最新版本 |
| 可维护性 | 前后端分离，RESTful API；数据库迁移由 Alembic 管理 |

## 数据库设计

### 用户表 `users`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) UNIQUE NOT NULL | 用户名 |
| password_hash | VARCHAR(255) NOT NULL | 密码哈希 (bcrypt) |
| avatar | VARCHAR(255) | 头像URL |
| created_at | DATETIME DEFAULT NOW() | 创建时间 |

### 区域表 `regions`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 区域ID |
| name | VARCHAR(100) NOT NULL | 区域名称 |
| description | TEXT | 区域描述 |
| tile_url | VARCHAR(255) | 瓦片地图URL模板 |
| sort_order | INT DEFAULT 0 | 排序 |
| created_at | DATETIME DEFAULT NOW() | 创建时间 |

### 标记分类表 `categories`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 分类ID |
| name | VARCHAR(50) NOT NULL | 分类名称 |
| icon | VARCHAR(255) | 分类图标URL |
| color | VARCHAR(7) | 标记颜色 (#RRGGBB) |
| sort_order | INT DEFAULT 0 | 排序 |

### 标记点表 `markers`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 标记ID |
| region_id | INT FK → regions.id | 所属区域 |
| category_id | INT FK → categories.id | 标记分类 |
| name | VARCHAR(200) NOT NULL | 标记名称 |
| description | TEXT | 详细描述 |
| x_coord | DECIMAL(10,2) NOT NULL | 地图X坐标 |
| y_coord | DECIMAL(10,2) NOT NULL | 地图Y坐标 |
| screenshot | VARCHAR(255) | 截图URL |
| created_at | DATETIME DEFAULT NOW() | 创建时间 |

## API 接口设计

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录，返回 JWT |
| GET | `/api/auth/me` | 获取当前用户信息 |

### 区域模块 `/api/regions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/regions` | 获取区域列表 |
| GET | `/api/regions/{id}` | 获取区域详情 |

### 分类模块 `/api/categories`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 获取标记分类列表 |

### 标记模块 `/api/markers`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/markers` | 查询标记（支持 `region_id` `category_id` `keyword` 筛选） |
| GET | `/api/markers/{id}` | 获取标记详情 |
| POST | `/api/markers` | 新增标记（需认证） |
| PUT | `/api/markers/{id}` | 编辑标记（需认证） |
| DELETE | `/api/markers/{id}` | 删除标记（需认证） |

## 项目结构

> 项目文件有新增时请同步更新此结构树。

```
BG3_map/
├── .gitattributes
├── .gitignore
├── DEVELOPMENT.md                 # 开发跟踪文档
├── PRD.md                         # 产品需求文档
├── README.md
├── origin_3845393_146764.png
├── backend/
│   ├── .env                       # 环境变量
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── alembic/                   # 数据库迁移
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 15a5faf78b3d_initial.py
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI 应用入口
│       ├── config.py               # 配置（数据库连接、JWT密钥等）
│       ├── database.py             # 数据库连接与 Session 管理
│       ├── models.py               # SQLAlchemy ORM 模型
│       ├── schemas.py              # Pydantic 请求/响应模型
│       ├── auth.py                 # JWT 认证与密码哈希
│       ├── seed.py                 # 初始数据填充（admin账号、区域、分类）
│       └── routers/
│           ├── __init__.py
│           ├── auth.py             # 认证路由
│           ├── regions.py          # 区域路由
│           ├── categories.py       # 分类路由
│           ├── markers.py          # 标记路由
│           ├── maps.py             # 地图列表路由
│           └── upload.py           # 截图上传路由
│   ├── static/                     # 用户上传文件
│   │   └── screenshots/            # 标记截图
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons/
│   │       ├── waypoint.svg        # 传送点图标
│   │       ├── monster.svg         # 怪物图标
│   │       └── item.svg            # 道具图标
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── api/
│       │   ├── index.js            # axios 实例（含 JWT 拦截器）
│       │   ├── auth.js             # 认证 API
│       │   ├── regions.js          # 区域 API
│       │   ├── categories.js       # 分类 API
│       │   ├── markers.js          # 标记 API
│       │   └── maps.js             # 地图列表 API
│       ├── assets/
│       │   └── icons/              # 资源图标（预留）
│       ├── components/
│       │   ├── MapContainer.vue     # 地图容器
│       │   ├── MarkerPopup.vue      # 标记详情弹窗
│       │   ├── MarkerForm.vue       # 标记新增/编辑表单
│       │   ├── NavBar.vue           # 导航栏（用户信息+登出）
│       │   └── SidePanel.vue        # 侧边面板
│       ├── views/
│       │   ├── HomeView.vue         # 地图主页
│       │   ├── LoginView.vue        # 登录页
│       │   ├── RegisterView.vue     # 注册页
│       │   └── NotFoundView.vue     # 404 页面
│       ├── stores/
│       │   ├── auth.js              # 认证状态 (Pinia)
│       │   └── map.js               # 地图状态 (Pinia)
│       └── router/
│           └── index.js
├── Map/                            # 各章节地图源图片 (PNG)
│   ├── chapter0/                   # 序章 — 鹦鹉螺号（2张）
│   ├── chapter1/                   # 第一章 — 林地、地精营地、幽暗地域（23张）
│   ├── chapter2/                   # 第二章 — 伊雷珂养育间（3张）
│   ├── chapter3/                   # 第三章 — 月出之塔、暗夜之歌监狱（13张）
│   └── chapter4/                   # 第四章 — 博德之门（44张）
├── TileMap/                        # 瓦片地图（切图工具生成，68,548 tiles）
│   └── chapterX/地图名/{z}/{y}/{x}.png
├── tools/
│   ├── tile_cutter.py              # 瓦片切图工具
│   └── fix_admin_pw.py             # 管理员密码修复脚本
├── sql/
│   └── init.sql                    # 数据库初始化脚本
```

## 切图工具

项目自带瓦片切图工具 `tools/tile_cutter.py`，用于将 `Map/` 下的 PNG 源图切割为 Leaflet CRS.Simple 格式的瓦片。

### 工作原理

1. 读取 PNG 源图，检测宽高
2. 计算刚好包住图片的最小 zoom 级别（画布 = 256 × 2^z px）
3. 将原图居中放置到透明画布上（不足尺寸自动补全透明像素）
4. 从 minZoom 到 maxZoom 逐级缩放画布并切片为 256×256 瓦片

### 使用方法

```bash
# 安装依赖
pip install Pillow

# 全量切图（所有章节）
python tools/tile_cutter.py

# 增量切图（仅处理新增地图）
python tools/tile_cutter.py --skip-existing

# 只处理指定章节
python tools/tile_cutter.py --chapter chapter1

# 自定义参数
python tools/tile_cutter.py -i Map/ -o TileMap/ --min-zoom 1 --workers 8
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 源图目录 | `Map/` |
| `-o, --output` | 输出目录 | `TileMap/` |
| `--min-zoom` | 最小 zoom 级别 | 1 |
| `-c, --chapter` | 指定章节 | 全部 |
| `-w, --workers` | 并行进程数 | CPU 核数 |
| `--skip-existing` | 跳过已有瓦片的地图 | 关闭 |

### 瓦片输出结构

```
TileMap/
├── chapter0/
│   └── 鹦鹉螺式魔法船（第一层）/
│       ├── 1/
│       │   ├── 0/           # y 坐标
│       │   │   ├── 0.png    # x 坐标
│       │   │   └── 1.png
│       │   └── 1/
│       │       └── ...
│       ├── 2/
│       ├── 3/
│       └── ...
```

URL 格式：`/TileMap/{chapter}/{map_name}/{z}/{y}/{x}.png`

### 新增地图流程

1. 将 PNG 图片放入对应 `Map/chapterX/` 目录
2. 运行增量切图：`python tools/tile_cutter.py --skip-existing`
3. 重新部署 TileMap 目录即可

## 环境要求

- Python 3.10+
- MySQL 8.0
- Node.js 18+
- npm / pnpm

## 快速开始

### 1. 数据库初始化

```bash
# 创建数据库并导入表结构
mysql -u root -p < sql/init.sql
```

### 2. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS / Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（编辑 .env）
# DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/bg3_map
# JWT_SECRET_KEY=your-secret-key-change-in-production

# 填充初始数据（区域、分类、admin 账号）
python -m app.seed

# 启动服务
uvicorn app.main:app --reload --port 8000
```

默认管理员账号：`admin` / `admin123`

### 3. 瓦片切图

```bash
# 在项目根目录执行
pip install Pillow
python tools/tile_cutter.py
```

### 4. 前端

```bash
cd frontend
npm install
npm run dev
```

## AI 开发声明

本项目的部分代码由 AI 辅助生成，包括但不限于：
- 后端路由、数据模型、认证逻辑的框架代码
- 前端组件、状态管理、路由配置的基础结构
- 瓦片切图工具的核心逻辑
- 架构图与文档模板

人工编写与审核的部分：
- 项目需求分析与数据库设计
- API 接口设计规范
- 代码审查与功能调试
- 配置与环境适配（Windows 兼容性、依赖版本锁定）

AI 生成代码均经过人工审查和测试，确保符合项目功能需求和代码质量要求。


