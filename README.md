# 交互式游戏地图 — 课程设计

## AI 开发声明

本项目的代码由 AI 生成，包括但不限于：
- 后端路由、数据模型、认证逻辑的框架代码
- 前端组件、状态管理、路由配置的基础结构
- 瓦片切图工具的核心逻辑
- 架构图与文档模板

人工编写与审核的部分：
- 项目需求分析与数据库设计
- API 接口设计规范
- 代码审查与功能调试
- 配置与环境适配（Windows 兼容性、依赖版本锁定）

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

## 功能需求

### 用户故事

| 角色 | 需求 | 目的 |
|------|------|------|
| 游客 | 浏览地图（无需登录） | 未登录即可查看地图、搜索标记、切换区域 |
| 玩家 | 浏览游戏地图 | 查看各区域地形与地标 |
| 玩家 | 查找标记点 | 快速定位 NPC、传送点、怪物、道具位置 |
| 玩家 | 搜索标记 | 按名称模糊匹配找到目标点 |
| 玩家 | 提交标记 | 向地图贡献新的标记点 |
| 管理员 | 管理标记数据 | 新增、编辑、删除标记点信息 |
| 管理员 | 管理分类 | 新增、编辑、删除标记分类和图标 |
| 管理员 | 审核标记 | 审核玩家提交的标记，通过或拒绝 |

### 用户系统
- 用户注册 / 登录（JWT 认证）
- 个人信息查看
- 游客模式：无需登录即可浏览地图、搜索标记、查看详情
  - 登录/注册页底部提供「游客模式 — 直接浏览」入口
  - 首页「登录后即可提交新标记」按钮引导游客登录

### 地图浏览
- 瓦片地图加载与渲染（Leaflet CRS.Simple）
- 鼠标拖拽平移、滚轮缩放（缩放控件暗黑主题金边风格）
- 多区域/章节地图切换
- 按分类筛选标记点（默认全选，跨区域保持）
- 地图标记悬停显示名称提示
- 最新标记列表悬停预览（透明弹窗贴合侧边栏，动态防遮挡，不移动视角）

### 标记系统
- 标记点展示（图标 + 名称 + 坐标）
- 标记分类：传送点、怪物、道具、商人
- 点击标记显示详情弹窗（描述、坐标、所属区域、状态标签、提交者，支持拖拽）
- 标记搜索（按名称模糊匹配）
- 普通用户提交标记（需管理员审核通过后显示）
- 管理员审核面板（分页审核，10 条/页，通过/拒绝操作）
- 管理员新增/编辑/删除标记
- 传送点绑定：从已有传送点选择目标，管理员点击弹出传送/编辑/删除选项
- 通用传送点：未绑定目标的传送点标记为「通用传送点」
- 待审核标记以橙色边框标识，弹窗显示状态标签

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
| is_admin | BOOLEAN DEFAULT FALSE | 是否管理员 |
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
| screenshot | TEXT | 截图 JSON 数组 |
| map_name | VARCHAR(100) | 所属子地图名称 |
| target_region_id | INT | 传送目标区域 ID |
| target_map_name | VARCHAR(100) | 传送目标子地图名 |
| target_x | DECIMAL(10,2) | 传送目标 X 坐标 |
| target_y | DECIMAL(10,2) | 传送目标 Y 坐标 |
| status | VARCHAR(20) DEFAULT 'approved' | 审核状态 (pending/approved/rejected) |
| submitted_by | INT FK → users.id | 提交者 ID (管理员直接添加为 null) |
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
| POST | `/api/categories` | 新增分类（需管理员） |
| PUT | `/api/categories/{id}` | 编辑分类（需管理员） |
| DELETE | `/api/categories/{id}` | 删除分类（需管理员，有关联标记时不可删） |

### 标记模块 `/api/markers`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/markers` | 查询标记（支持 `region_id` `category_id`(逗号多选) `keyword` `map_name` `status` `sort_by` 筛选，`limit`≤1000，默认只返回已审核） |
| GET | `/api/markers/count` | 统计已审核标记总数 |
| GET | `/api/markers/pending/count` | 统计待审核标记数量 |
| GET | `/api/markers/{id}` | 获取标记详情（含提交者信息） |
| POST | `/api/markers` | 管理员直接新增标记（自动通过，需管理员） |
| POST | `/api/markers/user-submit` | 普通用户提交标记（需登录，自动设为待审核） |
| POST | `/api/markers/{id}/review` | 审核标记（需管理员，action=approve/reject） |
| PUT | `/api/markers/{id}` | 编辑标记（需管理员） |
| DELETE | `/api/markers/{id}` | 删除标记（需管理员） |

### 地图模块 `/api/maps`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/maps` | 获取子地图列表（支持 `chapter` 筛选） |

### 上传模块 `/api/upload`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传截图/图标（需登录，JPG/PNG/GIF/WebP/SVG，≤5MB） |

## 项目结构

> 项目文件有新增时请同步更新此结构树。

```
BG3_map/
├── .gitattributes
├── .gitignore
├── README.md
├── docs/                           # 说明类文档
│   ├── PRD.md                      # 产品需求文档
│   ├── DEVELOPMENT.md              # 开发跟踪文档
│   ├── PROJECT.md                  # 项目详解
│   ├── ISSUES.md                   # 问题清单 (90项)
│   ├── DEPLOYMENT.md               # 生产环境部署指南
│   └── 数据流程说明.md              # 注册数据流详解
├── backend/
│   ├── .env                        # 环境变量
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── alembic/                    # 数据库迁移
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 15a5faf78b3d_initial.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 应用入口
│   │   ├── config.py               # 配置（数据库连接、JWT密钥等）
│   │   ├── database.py             # 数据库连接与 Session 管理
│   │   ├── models.py               # SQLAlchemy ORM 模型
│   │   ├── schemas.py              # Pydantic 请求/响应模型
│   │   ├── auth.py                 # JWT 认证与密码哈希
│   │   ├── rate_limit.py           # 请求频率限制
│   │   ├── seed.py                 # 初始数据填充（从 ADMIN_PASSWORD 环境变量读取管理员密码）
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── marker_service.py    # 标记点业务逻辑层 (CRUD/筛选/文件管理)
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py             # 认证路由
│   │       ├── regions.py          # 区域路由
│   │       ├── categories.py       # 分类路由
│   │       ├── markers.py          # 标记路由
│   │       ├── maps.py             # 地图列表路由
│   │       └── upload.py           # 截图上传路由
│   └── static/                     # 用户上传文件
│       └── screenshots/            # 标记截图
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons/
│   │       ├── waypoint.svg
│   │       ├── monster.svg
│   │       ├── item.svg
│   │       └── merchant.svg
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── api/
│       │   ├── index.js            # axios 实例（JWT 拦截器 + 401 防重复跳转）
│       │   └── markers.js          # 标记 CRUD API
│       ├── composables/
│       │   ├── useMapNavigation.js # 区域/地图切换 + 传送跳转
│       │   ├── useMarkerSearch.js  # 搜索防抖 + 结果列表
│       │   ├── useRecentMarkers.js # 最新标记 + 分页
│       │   ├── usePickMode.js      # 坐标拾取模式
│       │   └── useMarkerForm.js    # 标记表单提交/删除
│       ├── components/
│       │   ├── AuthForm.vue          # 登录/注册共享表单组件
│       │   ├── MapContainer.vue     # 地图容器
│       │   ├── MarkerPopup.vue      # 标记详情弹窗
│       │   ├── MarkerForm.vue       # 标记新增/编辑表单
│       │   ├── ReviewModal.vue       # 审核拖拽弹窗
│       │   ├── CategoryManager.vue   # 分类增删改弹窗
│       │   ├── NavBar.vue           # 导航栏（用户信息+登出）
│       │   └── SidePanel.vue        # 侧边面板
│       ├── views/
│       │   ├── HomeView.vue         # 地图主页
│       │   ├── LoginView.vue        # 登录页
│       │   ├── RegisterView.vue     # 注册页
│       │   ├── NotFoundView.vue     # 404 页面
│       ├── stores/
│       │   ├── auth.js              # 认证状态 (Pinia)
│       │   └── map.js               # 地图状态 (Pinia)
│       └── router/
│           └── index.js
├── Map/                            # 各章节地图源图片 (PNG)
│   ├── chapter0/                   # 序章 — 鹦鹉螺号（2张）
│   ├── chapter1/                   # 第1章 — 林地、地精营地、幽暗地域（23张）
│   ├── chapter2/                   # 第1.5章 — 伊雷珂养育间（3张）
│   ├── chapter3/                   # 第2章 — 月出之塔、幽影诅咒之地（13张）
│   └── chapter4/                   # 第3章 — 博德之门（44张）
├── TileMap/                        # 瓦片地图（切图工具生成，68,548 tiles）
│   └── chapterX/地图名/{z}/{y}/{x}.png
├── tools/
│   ├── tile_cutter.py              # 瓦片切图工具
│   ├── fix_admin_pw.py             # 管理员密码修复脚本
│   └── mysql_mcp_server.py         # MySQL MCP 服务器
├── sql/
│   └── init.sql                    # 数据库初始化脚本
```

## 切图工具

> **注意**：`TileMap/`（约 68,548 张瓦片）已加入 `.gitignore`，不上传仓库。
> 克隆项目后运行一次切图工具即可生成本地瓦片。

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
# JWT_SECRET_KEY=your-strong-random-key

# 可选：设置管理员密码
# set ADMIN_PASSWORD=your-admin-password

# 填充初始数据（区域、分类、admin 账号）
python -m app.seed

# 启动服务
uvicorn app.main:app --reload --port 8000
```

管理员账号：`admin`，密码从环境变量 `ADMIN_PASSWORD` 读取，未设置则自动生成随机密码并输出到控制台。

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

> **首次使用**：克隆仓库后 `TileMap/` 和 `backend/venv/`、`frontend/node_modules/` 均不在仓库中，需依次执行步骤 2-4 完成环境搭建和瓦片切图。

