---
name: bg3-map-dev
description: |
  博德之门3 交互式地图项目开发上下文。当用户在 G:\BG3_map 项目中工作时自动使用此技能——包括修改后端 API、前端 Vue 组件、数据库模型、瓦片地图、切图工具，或讨论该项目的任何功能、bug、重构。提供完整的架构概览、启动命令、文件索引和已完成的开发状态，确保新会话能无缝衔接。
---

# BG3 交互式地图 — 项目开发上下文

## 项目概述

为《博德之门3》开发的 Web 端交互式地图系统。用户可以浏览游戏地图、查看标记点（NPC、传送点、怪物、道具等）、搜索定位、收藏标记。前后端分离架构，地图使用 Leaflet CRS.Simple 渲染预切片瓦片。

## 开发守则

**每次修改代码后，必须同步更新以下三份文档**：

| 文档 | 更新时机 |
|------|----------|
| `README.md` | 新增/删除/重命名文件 → 更新项目结构树；修改启动方式、数据库字段、API 接口 → 更新对应章节 |
| `DEVELOPMENT.md` | 完成任务、修复审计问题 → 更新任务勾选和审计问题表；新增技术债务 → 追加到备忘 |
| `.opencode/skills/bg3-map-dev/SKILL.md` | 上述内容变更导致项目上下文改变 → 同步更新技能中的架构说明、文件索引、约定、状态等 |

这三份文档是项目的唯一真相来源，不同步会导致新会话产生错误认知。

## 启动项目

三个步骤，顺序启动：

```powershell
# 1. 确保 MySQL 运行 → 2. 启动后端 → 3. 启动前端
# 后端
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'G:\BG3_map\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"

# 前端
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'G:\BG3_map\frontend'; npm run dev"
```

| 服务 | 地址 |
|------|------|
| 后端 API | http://127.0.0.1:8000 |
| Swagger 文档 | http://127.0.0.1:8000/docs |
| 前端页面 | http://localhost:5173 |

默认管理员: `admin` / `admin123`

前端 Vite 配置了代理：`/api`、`/TileMap`、`/static` 自动转发到后端 8000 端口。

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
| 认证 | JWT (python-jose + passlib, bcrypt) | - |

## 项目结构（关键文件索引）

```
G:\BG3_map/
├── README.md                        # 完整项目文档
├── DEVELOPMENT.md                   # 开发跟踪（14 个任务全部已完成）
├── PRD.md                           # 产品需求文档
├── ISSUES.md                        # 问题清单
│
├── backend/
│   ├── .env                         # DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/versions/15a5faf78b3d_initial.py  # 初始迁移（唯一的迁移版本）
│   ├── venv/                        # Python 虚拟环境（已创建）
│   ├── static/screenshots/          # 用户上传的标记截图
│   └── app/
│       ├── main.py                  # FastAPI 入口，含 CORS、路由注册、TileMap 静态挂载
│       ├── config.py                # 从 .env 读取配置
│       ├── database.py              # SQLAlchemy engine + SessionLocal
│       ├── models.py                # ORM: User(含 is_admin), Region, Category, Marker
│       ├── schemas.py               # Pydantic: 请求/响应模型，UserResponse 含 is_admin
│       ├── auth.py                  # JWT 创建/验证, get_current_user, require_admin 依赖
│       ├── rate_limit.py            # 请求频率限制
│       ├── seed.py                  # 种子数据: admin 账号, 区域, 分类 (每次运行覆盖)
│       └── routers/
│           ├── auth.py              # /api/auth/register, login, me (返回 is_admin)
│           ├── regions.py           # /api/regions CRUD
│           ├── categories.py        # /api/categories
│           ├── markers.py           # /api/markers CRUD (CUD 需 require_admin)
│           ├── maps.py              # /api/maps 地图列表
│           └── upload.py            # /api/upload 截图上传
│
├── frontend/
│   ├── index.html                   # Leaflet CSS 从 unpkg CDN 加载
│   ├── vite.config.js               # 端口 5173, proxy /api /TileMap /static → 8000
│   ├── package.json                 # vue 3.5, pinia 2.2, vue-router 4.4, axios 1.7, leaflet 1.9
│   ├── public/
│   │   ├── favicon.svg              # 地图定位标记图标
│   │   └── icons/                   # waypoint.svg, monster.svg, item.svg
│   └── src/
│       ├── main.js                  # 创建 app, 挂载 router + pinia
│       ├── App.vue                  # 根组件: <NavBar> + <RouterView>, onMounted 调用 fetchUser()
│       ├── style.css                # 全局样式
│       ├── api/
│       │   ├── index.js             # axios 实例, baseURL=/api, JWT 拦截器 (401→window.location.href)
│       │   ├── auth.js              # login, register, getMe
│       │   ├── regions.js           # getRegions, getRegion
│       │   ├── categories.js        # getCategories
│       │   ├── markers.js           # getMarkers, getMarker, createMarker, updateMarker, deleteMarker
│       │   └── maps.js              # getMaps
│       ├── stores/
│       │   ├── auth.js              # user, token, fetchUser(), logout()
│       │   └── map.js               # regions, maps, categories, markers, addMarker/removeMarker/editMarker
│       ├── router/
│       │   └── index.js             # 路由: /home /login /register /404; beforeEach 鉴权守卫
│       ├── views/
│       │   ├── HomeView.vue         # 主地图页: 集成 MapContainer+SidePanel+MarkerPopup+MarkerForm
│       │   ├── LoginView.vue
│       │   ├── RegisterView.vue
│       │   └── NotFoundView.vue     # 404 页面
│       └── components/
│           ├── MapContainer.vue     # Leaflet 地图封装 (CRS.Simple, 瓦片层, 标记渲染, 点击事件)
│           ├── MarkerPopup.vue      # 标记详情弹窗 (描述/截图/坐标/管理操作)
│           ├── MarkerForm.vue       # 新增/编辑标记表单 (含截图上传、传送目标配置)
│           ├── NavBar.vue           # 顶栏: 品牌名, 用户名, 管理员徽章, 登出
│           └── SidePanel.vue        # 侧边面板: 区域/地图选择, 分类筛选, 搜索, 统计
│
├── Map/                             # 源图 PNG (97 张, chapter0-4)
├── TileMap/                         # 切好的瓦片 (~68,548 tiles), URL: /TileMap/{chapter}/{map}/{z}/{y}/{x}.png
├── tools/
│   ├── tile_cutter.py               # 瓦片切图工具
│   ├── fix_admin_pw.py              # 管理员密码修复
│   └── mysql_mcp_server.py          # MySQL MCP 服务器
└── sql/
    └── init.sql                     # 数据库初始化脚本
```

## 架构决策与约定

### 后端
- **权限模型**: User 表用 `is_admin` (Integer, 0/1) 区分角色，`require_admin` 依赖注入保护 CUD 端点
- **认证流**: JWT token 存储在 localStorage，登录时返回；`get_current_user` 从 Authorization header 解码
- **API 前缀**: 所有 API 路由带 `/api` 前缀
- **数据填充**: `python -m app.seed` 每次运行会检查是否存在再插入（覆盖模式），安全可重复执行
- **Alembic**: 只有一个初始迁移版本 `15a5faf78b3d_initial.py`，`alembic.ini` 中硬编码了数据库 URL（与 .env 可能不一致）

### 前端
- **路由守卫**: 白名单 `['login', 'register']`，已登录用户访问登录页自动跳转首页
- **登录态恢复**: `App.vue` onMounted 调用 `authStore.fetchUser()` 用 localStorage token 验证
- **401 处理**: axios 拦截器 401 时用 `window.location.href = '/login'` 硬刷新（非 router.push）
- **Leaflet**: CSS 从 unpkg CDN 加载，地图用 CRS.Simple 非地理坐标系统
- **图标渲染**: MapContainer 优先 `L.icon` 加载 SVG 图标，无图标时回退 `L.divIcon` 纯色圆点
- **分类图标路径**: `public/icons/` (waypoint.svg, monster.svg, item.svg)，seed.py 中预设了 `/icons/xxx.svg` 路径

### 数据库
- 连接字符串: `mysql+pymysql://root:root@localhost:3306/bg3_map`
- 表: `users`(含 is_admin), `regions`, `categories`, `markers`(外键 region_id, category_id, x_coord/y_coord)
- 坐标系统: map 的 bounds 在 maps 表中定义 `[[-4096,0],[4096,8192]]`，坐标在标记中以像素为单位

### 瓦片地图
- 源图放 `Map/chapterX/地图名.png`，输出到 `TileMap/chapterX/地图名/{z}/{y}/{x}.png`
- 切图工具: `python tools/tile_cutter.py --skip-existing` 增量切图
- 后端 `main.py` 挂载 TileMap 为静态目录到 `/TileMap` 路径

## 当前开发状态

DEVELOPMENT.md 中 **14 个任务全部已完成**：

| 轮次 | 任务 | 状态 |
|------|------|------|
| 第一轮 | 1. TileMap 静态挂载, 2. 路由鉴权, 3. 登录态恢复, 4. favicon | ✅ |
| 第二轮 | 5. MapContainer, 6. MarkerPopup, 7. SidePanel 组件重构 | ✅ |
| 第三轮 | 8. 管理员权限, 9. CRUD 前端, 10. 登出+用户信息, 11. 加载状态 | ✅ |
| 第四轮 | 12. Alembic 迁移, 13. 404 页面, 14. 分类图标 | ✅ |

项目处于 **功能完整、可正常运行** 状态。

## 技术债务

| 问题 | 严重度 | 说明 |
|------|--------|------|
| `alembic.ini` 硬编码 DB URL | 中 | 与 .env 不一致，需改为从环境变量读取 |
| Leaflet CSS CDN 依赖 | 中 | CDN 不可用时地图无法渲染 |
| 无 TypeScript | 低 | 全部 JS，按需逐步迁移 |
| 401 用 window.location.href | 低 | 应改为 `router.push('/login')` |
| Vite 代理依赖后端 | 低 | 生产环境需 nginx |

## 常见操作

```powershell
# 后端: 激活虚拟环境 + 启动
G:\BG3_map\backend\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# 填充种子数据 (admin 账号)
python -m app.seed

# 前端: 安装依赖 + 启动
cd G:\BG3_map\frontend
npm install
npm run dev

# 切图 (增量模式)
python tools/tile_cutter.py --skip-existing

# 数据库初始化
mysql -u root -p < sql/init.sql

# 查看端口占用
netstat -ano | findstr ":8000"
netstat -ano | findstr ":5173"

# 杀掉进程
taskkill /PID <pid> /F
```
