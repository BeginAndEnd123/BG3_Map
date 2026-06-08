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
| `docs/DEVELOPMENT.md` | 完成任务、修复审计问题 → 更新任务勾选和审计问题表；新增技术债务 → 追加到备忘 |
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

默认管理员账号: `admin`，密码从环境变量 `ADMIN_PASSWORD` 读取或自动生成随机密码（运行 `python -m app.seed` 时输出）

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
├── ISSUES.md                        # 问题清单
├── docs/                            # 说明类文档
│   ├── DEVELOPMENT.md               # 开发跟踪（22 个任务全部已完成）
│   ├── PRD.md                       # 产品需求文档
│   ├── PROJECT.md                   # 项目详解
│   ├── ISSUES.md                    # 问题清单
│   └── 数据流程说明.md               # 注册数据流详解
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
│       ├── seed.py                  # 种子数据: 从环境变量 ADMIN_PASSWORD 读取管理员密码
│       ├── services/
│       │   └── marker_service.py    # 标记点业务逻辑层 (CRUD/筛选/文件安全删除)
│       └── routers/
│           ├── auth.py              # /api/auth/register, login, me (返回 is_admin)
│           ├── regions.py           # /api/regions CRUD
│           ├── categories.py        # /api/categories
│           ├── markers.py           # /api/markers CRUD + user-submit + review (CUD 需 require_admin, 审核需管理员)
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
│       │   ├── index.js             # axios 实例, baseURL=/api, JWT 拦截器 + 401 防重复
│       │   └── markers.js           # getMarkers, getPendingCount, createMarker, userSubmitMarker, updateMarker, deleteMarker, reviewMarker
│       ├── composables/
│       │   ├── useMapNavigation.js  # 区域/地图切换 + 传送跳转
│       │   ├── useMarkerSearch.js   # 搜索防抖 + 结果选中
│       │   ├── useRecentMarkers.js  # 最新标记列表 + 分页
│       │   ├── usePickMode.js       # 管理员坐标拾取
│       │   └── useMarkerForm.js     # 表单提交/编辑/删除 (支持管理员/普通用户两种提交模式)
│       ├── stores/
│       │   ├── auth.js              # user, token, fetchUser(), logout()
│       │   └── map.js               # regions, maps, categories, markers, addMarker/editMarker/removeMarker/submitUserMarker/approveMarker/rejectMarker
│       ├── router/
│       │   └── index.js             # 路由: /home /login /register /404; beforeEach 鉴权守卫
│       ├── views/
│       │   ├── HomeView.vue         # 主地图页: composable 驱动 + 审核面板 (useMapNavigation/Search/Recent/Pick/Form + 审核管理)
│       │   ├── LoginView.vue
│       │   ├── RegisterView.vue
│       │   ├── NotFoundView.vue     # 404 页面
│       │   └── auth.css             # 登录/注册共享样式
│       └── components/
│           ├── MapContainer.vue     # Leaflet 地图封装 (CRS.Simple, 瓦片层, 标记渲染含待审核橙色边框, 点击事件)
│           ├── MarkerPopup.vue      # 标记详情弹窗 (描述/截图/坐标/状态标签/提交者/管理操作)
│           ├── MarkerForm.vue       # 新增/编辑标记表单 (含截图上传、传送目标配置, 修复 removeImage bug)
│           ├── NavBar.vue           # 顶栏: 品牌名, 用户名, 管理员徽章, 登出
│           └── SidePanel.vue        # 侧边面板: 区域/地图选择, 分类筛选, 搜索, 统计, 审核管理
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
- **权限模型**: User 表用 `is_admin` (Integer, 0/1) 区分角色，`require_admin` 依赖注入保护 CUD 和审核端点；普通用户通过 `/api/markers/user-submit` 提交标记，自动设为 `pending` 状态
- **认证流**: JWT token 存储在 localStorage，登录时返回；`get_current_user` 从 Authorization header 解码，捕获 JWTError/ValueError/TypeError
- **配置安全**: JWT_SECRET_KEY / DATABASE_URL 无默认值，缺失启动报错；JWT_ALGORITHM 白名单校验；CORS origins 自动 strip 空格
- **API 前缀**: 所有 API 路由带 `/api` 前缀
- **数据填充**: `python -m app.seed` 管理员密码从环境变量 `ADMIN_PASSWORD` 读取，未设置生成随机密码
- **文件安全**: `_safe_delete_file()` resolve 后校验路径前缀防遍历；delete_marker 先 commit 再删文件
- **Alembic**: 只有一个初始迁移版本 `15a5faf78b3d_initial.py`，env.py 从环境变量读取 DB URL

### 前端
- **路由守卫**: 白名单 `['login', 'register', 'not-found']`，已登录用户访问登录页自动跳转首页
- **登录态恢复**: `App.vue` onMounted 调用 `authStore.fetchUser()` 用 localStorage token 验证
- **401 处理**: axios 拦截器 `isRedirecting` 防重复标志，防止并发 401 多次跳转
- **表单防护**: LoginView / RegisterView 均有 `submitting` 状态防重复提交
- **全局错误**: App.vue 中 `onErrorCaptured` + hasError 遮罩 UI
- **Leaflet**: CSS 从 unpkg CDN 加载，地图用 CRS.Simple 非地理坐标系统
- **图标渲染**: MapContainer 优先 `L.icon` 加载 SVG 图标，无图标时回退 `L.divIcon` 纯色圆点；待审核标记用橙色边框区分
- **分类图标路径**: `public/icons/` (waypoint.svg, monster.svg, item.svg)，seed.py 中预设了 `/icons/xxx.svg` 路径
- **无障碍**: 搜索/弹窗/列表支持 ARIA 属性和键盘导航 (Esc/Enter/Space)

### 数据库
- 连接字符串: `mysql+pymysql://root:root@localhost:3306/bg3_map`
- 表: `users`(含 is_admin), `regions`, `categories`, `markers`(外键 region_id, category_id, submitted_by, 含 status/坐标等)
- 坐标系统: map 的 bounds 在 maps 表中定义 `[[-4096,0],[4096,8192]]`，坐标在标记中以像素为单位

### 瓦片地图
- 源图放 `Map/chapterX/地图名.png`，输出到 `TileMap/chapterX/地图名/{z}/{y}/{x}.png`
- 切图工具: `python tools/tile_cutter.py --skip-existing` 增量切图
- 后端 `main.py` 挂载 TileMap 为静态目录到 `/TileMap` 路径

## 当前开发状态

`docs/DEVELOPMENT.md` 中 **25 个任务全部已完成**：

| 轮次 | 任务 | 状态 |
|------|------|------|
| 第一轮 | 1-4: TileMap 挂载, 路由鉴权, 登录态恢复, favicon | ✅ |
| 第二轮 | 5-7: MapContainer, MarkerPopup, SidePanel 组件重构 | ✅ |
| 第三轮 | 8-11: 管理员权限, CRUD 前端, 登出, 加载状态 | ✅ |
| 第四轮 | 12-14: Alembic 迁移, 404 页面, 分类图标 | ✅ |
| 第五轮 | 15-22: 安全加固, Bug修复, 组件优化, 无障碍 | ✅ |
| 第六轮 | 23-25: 用户提交标记, 管理员审核, 状态展示 | ✅ |

项目处于 **功能完整、含用户提交与审核工作流、安全强化、可正常运行** 状态。

## 技术债务

| 问题 | 严重度 | 说明 |
|------|--------|------|
| Leaflet CSS CDN 依赖 | 中 | CDN 不可用时地图无法渲染 |
| rate_limit.py 内存限流 | 中 | 多 worker 时各进程独立，生产需 Redis |
| 无 TypeScript | 低 | 全部 JS，按需逐步迁移 |
| is_admin 用 Integer | 低 | SQLAlchemy 原生支持 Boolean 类型 |
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
