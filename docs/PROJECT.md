# 交互式地图 — 项目详解

## 一、项目概述

一个 Web 端交互式游戏地图系统。玩家可以浏览《博德之门3》的 97 张游戏地图，查看传送点/怪物/道具等标记，搜索定位并传送跳转；管理员可进行标记的增删改查。

**架构**: Vue 3 (前端) + FastAPI (后端) + MySQL 8.0 (数据库) + Leaflet.js (地图引擎) + JWT 认证，前后端完全分离。

---

## 二、整体架构与数据流

```
┌──────────────────────────────────────────────────────────────┐
│                        浏览器                                 │
│  ┌──────────┐  请求/响应    ┌──────────┐    静态文件请求      │
│  │ Vue 前端  │ ◄──────────► │ FastAPI   │ ◄───────────────    │
│  │ :5173    │    /api/*     │ 后端 :8000 │    /TileMap/*       │
│  └──────────┘               └────┬─────┘    /static/*         │
│                                   │                            │
│                            SQLAlchemy ORM                      │
│                                   │                            │
│                              ┌────┴─────┐                     │
│                              │  MySQL 8  │                     │
│                              └──────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

### 核心数据流

```
用户操作 → Vue组件 → Pinia Store → Axios API调用
                                         │
                                    FastAPI路由
                                         │
                                    SQLAlchemy查询
                                         │
                                      MySQL
                                         │
                                    返回JSON
                                         │
                              Pinia更新响应式状态
                                         │
                             Vue组件自动重新渲染
```

### 地图瓦片加载流程

```
1. PNG源图 (Map/chapterX/*.png)
        │
2. tools/tile_cutter.py 切图
        │
3. TileMap/chapterX/地图名/{z}/{y}/{x}.png (68,548 tiles)
        │
4. FastAPI 挂载 /TileMap 静态目录
        │
5. Leaflet CRS.Simple 按需加载瓦片
```

---

## 三、目录结构

```
BG3_map/
│
├── backend/                          # 后端 — FastAPI
│   ├── .env                          # 环境变量（数据库URL、JWT密钥等）
│   ├── requirements.txt              # Python 依赖清单
│   ├── alembic.ini                   # Alembic 迁移配置（URL从环境变量读取）
│   ├── alembic/                      # 数据库迁移工具
│   │   ├── env.py                    #   迁移环境配置
│   │   ├── script.py.mako            #   迁移脚本模板
│   │   └── versions/                 #   迁移版本记录
│   │       └── 15a5faf78b3d_initial.py
│   ├── app/                          # 应用核心
│   │   ├── __init__.py               #   包标记（空文件）
│   │   ├── main.py                   #   FastAPI 入口：CORS、静态挂载、路由注册
│   │   ├── config.py                 #   配置模块：从 .env 加载所有配置项
│   │   ├── database.py               #   数据库引擎、会话工厂、Base模型基类
│   │   ├── models.py                 #   ORM 模型：User/Region/Category/Marker 四表
│   │   ├── schemas.py                #   Pydantic 校验：请求体/响应体模型
│   │   ├── auth.py                   #   认证：bcrypt哈希、JWT签发/验证、依赖注入
│   │   ├── rate_limit.py             #   频率限制：内存字典实现，防暴力破解
│   │   ├── seed.py                   #   种子数据：首次部署填充区域/分类/admin
│   │   └── routers/                  #   路由模块（每个文件一个路由前缀）
│   │       ├── __init__.py
│   │       ├── auth.py               #     /api/auth     注册/登录/获取当前用户
│   │       ├── regions.py            #     /api/regions  区域列表和详情
│   │       ├── categories.py         #     /api/categories  分类列表
│   │       ├── markers.py            #     /api/markers  CRUD + 多条件筛选 + 分页
│   │       ├── maps.py               #     /api/maps     扫描TileMap返回子地图列表
│   │       └── upload.py             #     /api/upload   截图上传（魔数校验）
│   ├── static/                       # 静态资源目录
│   │   └── screenshots/              #   用户上传的标记截图
│   └── venv/                         # Python 虚拟环境（不入版本库）
│
├── frontend/                         # 前端 — Vue 3 + Vite
│   ├── index.html                    # HTML 入口
│   ├── vite.config.js                # Vite 配置：端口5173、代理/api/TileMap到后端
│   ├── package.json                  # Node 依赖清单
│   ├── public/                       # 公共静态资源
│   │   ├── favicon.svg               #   网站图标
│   │   └── icons/                    #   标记分类图标
│   │       ├── waypoint.svg          #     传送点
│   │       ├── monster.svg           #     怪物
│   │       └── item.svg              #     道具
│   └── src/                          # 源代码
│       ├── main.js                   #   应用入口：创建Pinia/Router、挂载App
│       ├── App.vue                   #   根组件：NavBar + router-view
│       ├── style.css                 #   全局样式
│       ├── api/                      #   HTTP 请求层
│       │   ├── index.js              #     Axios实例：baseURL /api, JWT拦截器
│       │   ├── auth.js               #     认证API：login/register/getMe
│       │   ├── regions.js            #     区域API
│       │   ├── categories.js         #     分类API
│       │   ├── markers.js            #     标记CRUD API
│       │   └── maps.js               #     地图列表API
│       ├── stores/                   #   Pinia 状态管理
│       │   ├── auth.js               #     认证状态：user/token/login/register/logout
│       │   └── map.js                #     地图状态：regions/categories/markers/maps
│       ├── router/
│       │   └── index.js              #   路由配置 + 登录鉴权守卫
│       ├── components/               #   可复用组件
│       │   ├── NavBar.vue            #     顶部导航栏（用户名+登出）
│       │   ├── SidePanel.vue         #     侧边面板容器（280px）
│       │   ├── MapContainer.vue      #     Leaflet 地图（CRS.Simple瓦片渲染）
│       │   ├── MarkerPopup.vue       #     标记详情弹窗（截图画廊）
│       │   └── MarkerForm.vue        #     标记新增/编辑表单（含传送目标配置）
│       └── views/                    #   页面视图
│           ├── HomeView.vue          #     核心主页（地图+侧栏+弹窗+表单整合）
│           ├── LoginView.vue         #     登录页
│           ├── RegisterView.vue      #     注册页
│           └── NotFoundView.vue      #     404页面
│
├── Map/                              # 地图源图片（PNG，Git LFS管理，97张）
│   ├── chapter0/                     #   序章 — 鹦鹉螺号（2张）
│   ├── chapter1/                     #   第一章 — 林地、地精营地、幽暗地域（23张）
│   ├── chapter2/                     #   第二章 — 伊雷珂养育间（3张）
│   ├── chapter3/                     #   第三章 — 月出之塔、暗夜之歌监狱（13张）
│   └── chapter4/                     #   第四章 — 博德之门（44张）
│
├── TileMap/                          # 切图生成的瓦片（68,548个，不入版本库）
│   └── chapterX/地图名/{z}/{y}/{x}.png     # Leaflet CRS.Simple 瓦片格式
│
├── sql/
│   └── init.sql                      # 数据库初始化：建库/建表/索引/种子数据
│
├── tools/
│   ├── tile_cutter.py                # 瓦片切图工具：PNG→256x256瓦片，支持多进程
│   ├── fix_admin_pw.py               # 管理员密码重置脚本
│   └── mysql_mcp_server.py           # MySQL MCP Server（JSON-RPC协议）
│
├── .gitignore                        # Git 忽略规则
├── .gitattributes                    # Git LFS 配置（PNG文件）
├── README.md                         # 项目说明（快速开始、技术栈）
├── PRD.md                            # 产品需求文档
├── DEVELOPMENT.md                    # 开发跟踪文档
└── PROJECT.md                        # 本文档
```

---

## 四、核心文件详解

### 后端

| 文件 | 作用 |
|------|------|
| `main.py` | 创建 FastAPI 实例，配置 CORS（来源从环境变量读取），挂载 `/TileMap` 和 `/static` 静态目录，注册 6 个路由模块 |
| `config.py` | 用 `python-dotenv` 加载 `.env`，导出 DATABASE_URL、JWT_SECRET_KEY、JWT_ALGORITHM、JWT_EXPIRE_MINUTES、CORS_ORIGINS 五个配置项 |
| `database.py` | 创建 SQLAlchemy 引擎（`create_engine`），会话工厂 `SessionLocal`，模型基类 `Base`；`get_db()` 是 FastAPI 依赖注入，每个请求一个独立会话，请求结束自动关闭 |
| `models.py` | 定义 4 个 ORM 模型：`User`（含 is_admin）、`Region`（一对多 markers）、`Category`（一对多 markers）、`Marker`（含传送目标字段和截图JSON）；`markers` 表有联合索引 |
| `schemas.py` | 请求/响应的 Pydantic 模型：`UserRegister`（密码≥6位、用户名2-50位）、`MarkerCreate/Update`、`MarkerResponse` 等；`parse_images()` 将 JSON 字符串转列表 |
| `auth.py` | 密码 bcrypt 哈希/验证；JWT 令牌签发（含过期时间）和解析；`get_current_user` 从 Bearer Token 注入当前用户；`require_admin` 在用户基础上检查 is_admin |
| `rate_limit.py` | `RateLimiter` 类用内存字典按 IP 记录时间戳，超出 max_requests 次/窗口即返回 429，每 1000 次调用做全量过期清理 |
| `seed.py` | 建表后插入 5 个区域、3 个分类、admin 管理员账号（admin/admin123），已有数据则跳过 |

### 路由模块

| 文件 | 请求 | 说明 |
|------|------|------|
| `auth.py` | POST /register | 创建用户并返回 JWT（有频率限制） |
| | POST /login | 验证密码返回 JWT（有频率限制） |
| | GET /me | 返回当前用户信息 |
| `regions.py` | GET / | 按 sort_order 排序返回所有区域 |
| | GET /{id} | 根据 ID 获取单个区域 |
| `categories.py` | GET / | 按 sort_order 排序返回所有分类 |
| `markers.py` | GET / | 多条件筛选（region_id, category_id逗号分隔多选, keyword, map_name）+ 分页 + 排序 |
| | GET /count | 返回满足条件的标记总数 |
| | GET /{id} | 获取单个标记详情（含关联 region/category） |
| | POST / | 创建标记（需管理员），images 列表序列化为 JSON |
| | PUT /{id} | 更新标记（需管理员），移除的截图自动删文件 |
| | DELETE /{id} | 删除标记（需管理员），关联截图一并删除 |
| `maps.py` | GET / | 扫描 TileMap 目录返回子地图名、瓦片URL模板、max_zoom |
| `upload.py` | POST / | 上传截图：限制JPG/PNG/GIF/WebP，≤5MB，魔数校验，UUID重命名 |

### 前端

| 文件 | 作用 |
|------|------|
| `main.js` | 创建 Vue 应用，注册 Pinia 和 Router，导入 Leaflet CSS，挂载到 #app |
| `App.vue` | 根组件：顶部 NavBar + `<router-view>`；onMounted 时调用 fetchUser 恢复登录态 |
| `api/index.js` | Axios 实例：baseURL `/api`，10s 超时；请求拦截器自动注入 Bearer Token；响应拦截器处理 401 跳转登录 |
| `stores/auth.js` | 管理 user、token；login/register 成功后存 token 到 localStorage；logout 清除；fetchUser 从服务端恢复用户信息 |
| `stores/map.js` | 管理 regions、categories、markers、maps、currentRegion、currentMap；提供 fetch/add/edit/remove 异步操作；getChapterKey 将 sort_order 映射为章节目录名 |
| `router/index.js` | 4 条路由（/、/login、/register、404）；全局守卫：白名单已登录跳首页，其他未登录跳登录 |
| `HomeView.vue` | **核心页面（~680行）**：整合 SidePanel + MapContainer + MarkerPopup + MarkerForm；处理区域切换、地图切换、分类筛选、搜索、最新标记分页、传送跳转、管理员 CRUD、坐标拾取 |
| `MapContainer.vue` | 封装 Leaflet 地图：CRS.Simple 瓦片渲染、标记点渲染（自定义图标/颜色）、拾取模式（点击放置+拖动微调）、传送高亮脉冲动画；通过 defineExpose 暴露 flyTo/highlightMarker/resetView |
| `MarkerPopup.vue` | 标记详情弹窗：名称、分类标签、描述、坐标、截图画廊（点击放大）；actions 插槽接收编辑/删除按钮 |
| `MarkerForm.vue` | 新增/编辑表单：名称/分类/描述/坐标/多图上传/传送目标配置（目标区域+地图+坐标） |
| `NavBar.vue` | 顶部栏：品牌名 + 用户名 + 管理员徽章 + 登出按钮 |
| `SidePanel.vue` | 侧边面板容器（280px，滚动支持），通过 slot 接收内容 |

---

## 五、数据库设计

```
users                          regions
┌──────────────────┐          ┌──────────────────┐
│ id (PK)          │          │ id (PK)          │
│ username UNIQUE  │          │ name             │
│ password_hash    │          │ description      │
│ avatar           │          │ tile_url         │
│ is_admin         │          │ sort_order       │
│ created_at       │          │ created_at       │
└──────────────────┘          └────────┬─────────┘
                                       │ 1:N
                          ┌────────────┼────────────┐
                          │            │            │
                    markers            │       categories
              ┌──────────────────┐    │  ┌──────────────────┐
              │ id (PK)          │    │  │ id (PK)          │
              │ region_id (FK) ──┼────┘  │ name             │
              │ category_id(FK) ─┼────── │ icon             │
              │ name             │  N:1  │ color            │
              │ description      │       │ sort_order       │
              │ x_coord          │       └──────────────────┘
              │ y_coord          │
              │ screenshot (JSON)│
              │ map_name         │
              │ target_region_id │
              │ target_map_name  │
              │ target_x         │
              │ target_y         │
              │ created_at       │
              └──────────────────┘
              索引: (region_id, map_name, category_id)
              索引: (map_name)
```

---

## 六、用户角色与权限

| 操作 | 游客 | 普通用户 | 管理员 |
|------|------|----------|--------|
| 浏览地图 | ✓ | ✓ | ✓ |
| 查看标记 | ✓ | ✓ | ✓ |
| 搜索标记 | ✓ | ✓ | ✓ |
| 注册/登录 | ✓ | - | - |
| 新增标记 | ✗ | ✗ | ✓ |
| 编辑标记 | ✗ | ✗ | ✓ |
| 删除标记 | ✗ | ✗ | ✓ |

---

## 七、关键交互流程

### 地图浏览
```
用户选择区域 → onRegionChange() → fetchMaps() → loadMarkers() → 地图居中显示全部标记
用户选择地图 → onMapChange() → loadMarkers() → 地图居中显示全部标记
用户勾选分类 → loadMarkers() → 按分类筛选标记
用户输入搜索 → onSearchInput() → 实时搜索下拉列表
```

### 标记跳转（传送）
```
点击传送标记 → onMarkerTeleport() → 切换区域/地图 → loadMarkers（清除筛选）→ flyTo 目标坐标 → 高亮动画
从最新添加点击 → onRecentClick() → onSearchSelect() → 同上
从搜索结果点击 → onSearchSelect() → 同上
```

### 新增标记（管理员）
```
点击"新增标记" → pickMode开启 → 点击地图放置初始标记 → 拖动微调 → 确认位置 → 填写表单 → 提交
```

---

## 八、切图工具说明

`tools/tile_cutter.py` 将 Map/ 下的 PNG 源图切割为 Leaflet CRS.Simple 瓦片。

**原理**：
1. 读取 PNG，计算刚好包住图片的 zoom 级别（画布 = 256 × 2^z px）
2. 原图居中放在透明画布上
3. 从 minZoom 到 maxZoom 逐级缩放并切片为 256×256 PNG

**用法**：
```bash
python tools/tile_cutter.py                          # 全量
python tools/tile_cutter.py --skip-existing          # 增量
python tools/tile_cutter.py --chapter chapter1       # 指定章节
```
