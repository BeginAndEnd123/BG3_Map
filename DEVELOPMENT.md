# 开发跟踪文档

> 最后更新: 2026-06-02

## 项目状态总览

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 环境搭建 | 100% | Python 依赖、MySQL 数据库、种子数据就绪 |
| 后端 API | 100% | 全部路由实现，含静态文件挂载、管理员权限、Alembic 迁移 |
| 前端页面 | 100% | 全部视图和组件完成，含路由鉴权、CRUD、标记选取、地图选择 |
| 地图数据 | 100% | 97 张源图，瓦片已全部切片，含子地图选择器 |
| 切图工具 | 100% | 支持全量/增量/多进程 |

---

## 环境配置记录

| 项目 | 值 | 备注 |
|------|-----|------|
| MySQL 路径 | `E:\SQLDB\mysql\` | 服务已运行 |
| MySQL 账号 | `root` / `root` | 端口 3306 |
| 数据库名 | `bg3_map` | utf8mb4 |
| 后端配置 | `backend/.env` | `DATABASE_URL=mysql+pymysql://root:root@localhost:3306/bg3_map` |
| JWT 密钥 | `JWT_SECRET_KEY=your-secret-key-change-in-production` | 生产环境必须更换 |
| JWT 算法 | `HS256` | 过期时间 1440 分钟 (24h) |
| 管理员账号 | `admin` / `admin123` | `is_admin=1`，仅管理员可 CRUD 标记 |
| bcrypt 版本 | `4.0.1` | 降级以兼容 passlib 1.7.4（5.x/4.2.x API 不兼容） |
| passlib 版本 | `1.7.4` | 密码哈希库 |
| Python 版本 | 3.13+ | scoop 安装 |
| FastAPI | `0.115.0` | 后端框架 |
| Vue | `3.5+` | 前端框架 |
| Leaflet | `1.9.4` | 地图引擎，CRS.Simple 投影 |
| Navicat | `E:\navicat170_premium_cs_x64\navicat.exe` | 已安装 |
| GitHub 仓库 | `git@github.com:BeginAndEnd123/BG3_Map.git` | SSH，已配置 Git LFS |
| Git LFS | 97 个对象，共 1.9 GB | 管理 Map 目录下的大 PNG 源图 |
| SSH 密钥 | `~/.ssh/id_rsa` (私钥) / `~/.ssh/id_rsa.pub` (公钥) | 需在 GitHub Settings 添加公钥 |
| bcrypt 降级原因 | passlib 1.7.4 的 `_load_backend_mixin` 通过 `bcrypt.__about__.__version__` 读取版本，bcrypt≥4.1 移除了 `__about__` | 固定到 4.0.1 |

### SSH 公钥（添加到 GitHub）

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDROCWwvjS/gMchxRqf6chPXNm9OU+YAFDMzC1HhS+uOC/5bZeeaHgjh+am9r1CFQKSzZ0tEJNKScP27RR2DRBLTC/96pKFm0rhxIaPXvIK7FLMegAEXsAoMnRGESkAFr4bBsisk9ecAPxnz4b7NRnbgK3z1gRIklaVEKZciAVX2NOX6dv1KPLrJddZtME4RzfF972VsKRw7EVGSH8lCA7rTMEbaxD/sQBfZQT0xYNZ4nwtCGu2A2xGMJCzFoYj/6XMip53oTFIf4tYP2g6wOjBKC9LCVsvlWhXlRAKBZ4ezPV1UqR2yIKN3uZ/nEZsh6kkRX+hlxouF8KwL/BXJhG41wODTwsgRX7oW2XRY1gZL/ghzkc098wpu1DBcFgTlRfuT4WJcabeSM785mCKI0ufRu5/MGq0A5WuK7tnTQEchC+yHO0HMBAPp4+0g1HfalksUxvWJlfZeQtOwQHw4ju3/0YfOJn5ep8uw3EGZarI4YeynQXwwivG6LLo4QpsyUM= 2759919162@qq.com
```

> 私钥 `id_rsa` 位于 `~/.ssh/` 目录，切勿提交到 Git。

---

## 数据库参数

| 表名 | 字段 | 说明 |
|------|------|------|
| `users` | `id, username, password_hash, avatar, is_admin, created_at` | `is_admin=TINYINT(1) DEFAULT 0`，管理员标记 |
| `regions` | `id, name, description, tile_url, sort_order, created_at` | 5 个区域（序章~第四章） |
| `categories` | `id, name, icon, color, sort_order` | 3 个分类（传送点、怪物、道具），图标存 SVG 路径 |
| `markers` | `id, region_id(FK), category_id(FK), name, description, x_coord, y_coord, screenshot, created_at` | 标记点，关联区域和分类 |

### 瓦片数据结构

```
TileMap/
├── chapterX/              # X = 0~4 对应序章~第四章
│   └── 地图名称/           # 各章节子地图（共 97 张）
│       └── {z}/{y}/{x}.png  # z=缩放层级，y=行，x=列
```

- URL 格式: `/TileMap/{chapter}/{map_name}/{z}/{y}/{x}.png`
- Leaflet CRS.Simple，`minZoom=1, maxZoom=6`
- 瓦片通过后端 `app.mount("/TileMap", StaticFiles(...))` 挂载
- Vite 代理 `http://127.0.0.1:8000` 转发（注意：必须用 IPv4 地址，`localhost` 会解析到 IPv6 `::1` 导致连接失败）

---

## 任务清单

### 第一轮：打通核心链路 ✅

- [x] **1. 后端挂载 TileMap 静态文件**
  - 文件: `backend/app/main.py`
  - 内容: `app.mount("/TileMap", StaticFiles(directory=...))` + `pathlib` 路径解析
  - 目的: 让 Leaflet 能加载瓦片图片

- [x] **2. 前端路由鉴权守卫**
  - 文件: `frontend/src/router/index.js`
  - 内容: `router.beforeEach` 检查 token，白名单 `['login', 'register']`，未登录跳 `/login`
  - 注意: `router.beforeEach` 必须在 `createRouter()` 之后注册，否则报 `Cannot access 'router' before initialization`
  - 目的: 保护主页不被未登录用户访问

- [x] **3. 应用启动时恢复用户登录态**
  - 文件: `frontend/src/App.vue`
  - 内容: `onMounted` 时调用 `authStore.fetchUser()`
  - 目的: 刷新页面后保持登录状态

- [x] **4. 添加 favicon 和基础静态资源**
  - 文件: `frontend/public/favicon.svg` (SVG 格式)
  - 内容: 金色地图标记 SVG 图标
  - 目的: 消除浏览器 404 报错

### 第二轮：重构组件架构 ✅

- [x] **5. 重构 HomeView 使用 MapContainer 组件**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 删除内联 `L.map()` 逻辑，改用 `<MapContainer>` 并通过 props/events 通信
  - 目的: 消除重复代码，统一地图逻辑

- [x] **6. 重构 HomeView 使用 MarkerPopup 组件**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: MarkerPopup 改为浮动详情卡片，支持 actions 插槽（编辑/删除按钮）
  - 目的: 支持截图展示、结构化布局

- [x] **7. 重构 HomeView 使用 SidePanel 组件**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 侧栏内容移入 `<SidePanel>` slot
  - 目的: 组件职责分离，便于维护

### 第三轮：补充业务功能 ✅

- [x] **8. 添加管理员角色系统**
  - 文件: `backend/app/models.py` (User 加 `is_admin` 字段，`Integer default=0`)
  - 文件: `backend/app/auth.py` (加 `require_admin` 依赖，检查 `current_user.is_admin`)
  - 文件: `backend/app/routers/markers.py` (CRUD 端点改用 `require_admin`，普通用户只能查询)
  - 文件: `backend/app/seed.py` (admin 用户设 `is_admin=1`)
  - 文件: `sql/init.sql` (users 表加 `is_admin TINYINT(1) DEFAULT 0`)
  - 数据库: `ALTER TABLE users ADD COLUMN is_admin TINYINT(1) DEFAULT 0`
  - 目的: 区分普通用户和管理员权限

- [x] **9. 标记 CRUD 前端界面**
  - 文件: `frontend/src/stores/map.js` (加 `addMarker`/`editMarker`/`removeMarker` action)
  - 文件: 新建 `frontend/src/components/MarkerForm.vue` (新增/编辑表单弹窗，支持地图拖拽选坐标)
  - 文件: `frontend/src/components/MapContainer.vue` (新增 `pickMode`/`tempMarker` prop + `map-pick` emit)
  - 文件: `frontend/src/views/HomeView.vue` (集成新增/编辑/删除操作，支持地图点选 + 拖动定位)
  - 新增标记流程: 点"新增"→拖动标记→"确认位置"→填表单→提交
  - 目的: 管理员可在前端管理标记数据

- [x] **10. 登出功能 + 用户信息展示**
  - 文件: `frontend/src/App.vue` (加导航栏/顶栏)
  - 文件: 新建 `frontend/src/components/NavBar.vue`
  - 内容: 显示用户名 + 管理员标签 + 登出按钮
  - 目的: 完善用户体验闭环

- [x] **11. 加载状态和错误处理**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: loading 动画 (spinner) + try-catch 错误提示
  - 目的: 避免静默崩溃，提升用户体验

### 第四轮：收尾完善 ✅

- [x] **12. Alembic 初始化迁移**
  - 命令: `cd backend && alembic revision --autogenerate -m "initial"`
  - 注意: `alembic.ini` 中数据库 URL 从 `123456` 修正为 `root`
  - 目的: 建立正式的数据库迁移链

- [x] **13. 404 页面**
  - 文件: 新建 `frontend/src/views/NotFoundView.vue`
  - 文件: `frontend/src/router/index.js` (加 `/:pathMatch(.*)*` 路由)
  - 目的: 处理无效路由

- [x] **14. 标记分类图标**
  - 目录: `frontend/public/icons/` (waypoint.svg, monster.svg, item.svg)
  - 文件: `frontend/src/components/MapContainer.vue` (优先使用 `L.icon` 加载分类图标，fallback 到 `L.divIcon`)
  - 目的: 用图标替代纯色圆点，视觉更丰富

---

## 审计发现的问题汇总（已全部修复）

| # | 类别 | 问题 | 严重度 | 状态 |
|---|------|------|--------|------|
| 1 | 后端 | TileMap 静态文件未挂载，瓦片无法访问 | 高 | ✅ 已修复 |
| 2 | 后端 | User 表无 role 字段，任何登录用户都能 CRUD | 高 | ✅ 已修复（`is_admin` + `require_admin`） |
| 3 | 后端 | Alembic 未初始化，无迁移版本 | 中 | ✅ 已修复 |
| 4 | 前端 | 路由无鉴权守卫，主页可未登录访问 | 高 | ✅ 已修复 |
| 5 | 前端 | MapContainer/MarkerPopup/SidePanel 三组件未被使用 | 中 | ✅ 已修复 |
| 6 | 前端 | 标记 CRUD 无前端界面 | 中 | ✅ 已修复 |
| 7 | 前端 | 无登出功能，无用户信息展示 | 中 | ✅ 已修复 |
| 8 | 前端 | 应用启动时未调用 fetchUser 恢复登录态 | 中 | ✅ 已修复 |
| 9 | 前端 | favicon 和图标资源缺失 | 低 | ✅ 已修复 |
| 10 | 前端 | HomeView 无错误处理和加载状态 | 低 | ✅ 已修复 |
| 11 | 前端 | 404 页面缺失 | 低 | ✅ 已修复 |
| 12 | 前端 | Map Store 中 selectedCategory 未被使用 | 低 | ✅ 已修复 |

---

## 技术债务备忘

| 项目 | 说明 | 建议操作 |
|------|------|----------|
| `alembic.ini` 硬编码数据库 URL | 密码与实际 `.env` 不一致（已手动改为 `root`） | 改为从环境变量读取 |
| Leaflet CSS 依赖 unpkg CDN | CDN 不可用时地图无法渲染 | 改为 npm 引入或本地文件 |
| 前端无 TypeScript | 全部 JS，无类型安全 | 按需逐步迁移 |
| `window.location.href` 跳转 | API 401 拦截器用硬刷新代替路由跳转 | 改为 `router.push('/login')` |
| Vite 代理 target 必须用 IP | `localhost` 解析到 IPv6 `::1` 但后端只监听 `127.0.0.1` | 保持 `http://127.0.0.1:8000` |
| 瓦片 URL 坐标顺序 | 目录结构 `{z}/{y}/{x}.png` 非 Leaflet 默认 `{z}/{x}/{y}.png` | maps API 已修正，tile_url 使用 `{z}/{y}/{x}.png` |
| 每章节多子地图 | 共 97 张子地图，原 tile_url 无法覆盖 | 已新增 maps API + 前端下拉选择器 |
| 新增标记流程 | 需拖动标记→确认位置→填写表单，不直接在地图点击 | 当前实现已满足 |
| Git LFS 锁定 API | 远程不支持 locking API | 已 `git config lfs.<url>/info/lfs.locksverify false` |

---

## 变更日志

| 日期 | 内容 |
|------|------|
| 2026-06-02 | 项目审计完成，生成 14 项任务清单，4 轮迭代计划 |
| 2026-06-02 | 切图工具 `tools/tile_cutter.py` 完成，97 张源图全部切片 (68,548 tiles) |
| 2026-06-02 | MySQL 数据库初始化：`init.sql` 执行、4 表创建、5 区域 + 3 分类种子数据 |
| 2026-06-02 | Python 依赖安装 + bcrypt 兼容性修复 (5.0.0 → 4.0.1) |
| 2026-06-02 | admin 用户创建：`admin` / `admin123` |
| 2026-06-02 | `.env` 密码更正：`123456` → `root` |
| 2026-06-02 | 第一轮完成：TileMap 挂载、路由鉴权、登录态恢复、favicon |
| 2026-06-02 | 第二轮完成：HomeView 重构使用 MapContainer/MarkerPopup/SidePanel |
| 2026-06-02 | 第三轮完成：管理员系统、CRUD 界面、NavBar、错误处理 |
| 2026-06-02 | 第四轮完成：Alembic 迁移、404 页面、分类图标 |
| 2026-06-02 | 修复 bcrypt 版本从 5.0.0 降级到 4.0.1（passlib 兼容性） |
| 2026-06-02 | 修复 Vite 代理 `localhost`→`127.0.0.1`（IPv6 解析问题） |
| 2026-06-02 | 修复瓦片渲染：新增 maps API + 子地图选择器，URL 格式 `{z}/{y}/{x}.png` |
| 2026-06-02 | 优化新增标记：点击添加→拖动定位→确认位置→填写表单 |
| 2026-06-02 | 地图容器背景改为黑色以匹配瓦片边缘 |
