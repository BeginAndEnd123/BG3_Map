# 开发跟踪文档

> 最后更新: 2026-06-08

## 项目状态总览

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 后端 API | 100% | 全部完成，含权限系统、静态文件挂载 |
| 前端页面 | 100% | 全部完成，路由守卫、CRUD-UI、组件整合均就绪 |
| 地图数据 | 100% | 97 张源图，瓦片已全部切片 |
| 切图工具 | 100% | 支持全量/增量/多进程 |

---

## 任务清单

### 第一轮：打通核心链路

- [x] **1. 后端挂载 TileMap 静态文件**
  - 文件: `backend/app/main.py:24-26`
  - 内容: 添加 `app.mount("/TileMap", StaticFiles(directory="..."), name="tilemap")`
  - 目的: 让 Leaflet 能加载瓦片图片

- [x] **2. 前端路由鉴权守卫**
  - 文件: `frontend/src/router/index.js:27-36`
  - 内容: `router.beforeEach` 检查 token，白名单 `['login', 'register']`，未登录跳 `/login`
  - 目的: 保护主页不被未登录用户访问

- [x] **3. 应用启动时恢复用户登录态**
  - 文件: `frontend/src/App.vue:20-21`
  - 内容: `onMounted` 时调用 `authStore.fetchUser()`
  - 目的: 刷新页面后保持登录状态

- [x] **4. 添加 favicon 和基础静态资源**
  - 文件: `frontend/public/favicon.svg` (地图定位标记 SVG 图标)
  - 内容: 放入 32x32 地图图标
  - 目的: 消除浏览器 404 报错

### 第二轮：重构组件架构

- [x] **5. 重构 HomeView 使用 MapContainer 组件**
  - 文件: `frontend/src/views/HomeView.vue:93-104`
  - 内容: 删除内联 `L.map()` 逻辑，改用 `<MapContainer>` 并通过 props/events 通信
  - 目的: 消除重复代码，统一地图逻辑

- [x] **6. 重构 HomeView 使用 MarkerPopup 组件**
  - 文件: `frontend/src/views/HomeView.vue:117-128`
  - 内容: 将 `marker.bindPopup(htmlString)` 改为组件化弹窗，支持截图展示和管理员操作
  - 目的: 支持截图展示、结构化布局

- [x] **7. 重构 HomeView 使用 SidePanel 组件**
  - 文件: `frontend/src/views/HomeView.vue:3-90`
  - 内容: 将 `.sidebar` 内联 HTML 移入 `<SidePanel>` slot
  - 目的: 组件职责分离，便于维护

### 第三轮：补充业务功能

- [x] **8. 添加管理员角色系统**
  - 文件: `backend/app/models.py` (User 加 `is_admin` 字段)
  - 文件: `backend/app/auth.py:68-75` (加 `require_admin` 依赖)
  - 文件: `backend/app/routers/markers.py` (CRUD 端点改用 `require_admin`)
  - 文件: `backend/app/seed.py` (admin 用户设 `is_admin=True`)
  - 文件: `sql/init.sql` (users 表加 `is_admin` 字段)
  - 目的: 区分普通用户和管理员权限

- [x] **9. 标记 CRUD 前端界面**
  - 文件: `frontend/src/stores/map.js:41-57` (加 `addMarker`/`editMarker`/`removeMarker` action)
  - 文件: `frontend/src/components/MarkerForm.vue` (新增/编辑表单弹窗，支持截图上传、传送目标配置)
  - 文件: `frontend/src/views/HomeView.vue` (集成新增/编辑/删除操作)
  - 目的: 管理员可在前端管理标记数据

- [x] **10. 登出功能 + 用户信息展示**
  - 文件: `frontend/src/App.vue` (加导航栏/顶栏)
  - 文件: `frontend/src/components/NavBar.vue` (显示品牌名、用户名、管理员徽章、登出按钮)
  - 内容: 显示用户名 + 登出按钮
  - 目的: 完善用户体验闭环

- [x] **11. 加载状态和错误处理**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 添加 loading spinner + try-catch 错误提示（含 403 权限提示）
  - 目的: 避免静默崩溃，提升用户体验

### 第四轮：收尾完善

- [x] **12. Alembic 初始化迁移**
  - 文件: `backend/alembic/versions/15a5faf78b3d_initial.py`
  - 目的: 建立正式的数据库迁移链

- [x] **13. 404 页面**
  - 文件: `frontend/src/views/NotFoundView.vue`
  - 文件: `frontend/src/router/index.js:16` (加 `/:pathMatch(.*)*` 路由)
  - 目的: 处理无效路由

- [x] **14. 标记分类图标**
  - 目录: `frontend/public/icons/` (waypoint.svg / monster.svg / item.svg)
  - 内容: 传送点/怪物/道具的 SVG 图标
  - 文件: `frontend/src/components/MapContainer.vue:100-113` (优先使用 `L.icon` 加载 SVG 图标，回退 `L.divIcon`)
  - 目的: 用图标替代纯色圆点，视觉更丰富
  - 备注: 图标实际位于 `public/icons/` 而非 `src/assets/icons/`，功能正常

### 第五轮：安全加固 & Bug 修复 (2026-06-08)

- [x] **15. JWT 密钥安全加固**
  - 文件: `backend/app/config.py`
  - 内容: JWT_SECRET_KEY / DATABASE_URL 去掉默认值，缺失时 `sys.exit(1)`；JWT_ALGORITHM 白名单校验；CORS origins strip 空格
  - 目的: 防止弱密钥和配置错误

- [x] **16. 管理员密码安全**
  - 文件: `backend/app/seed.py`
  - 内容: 管理员密码从环境变量 `ADMIN_PASSWORD` 读取，未设置则生成随机密码
  - 目的: 消除硬编码弱密码

- [x] **17. 认证防御加固**
  - 文件: `backend/app/auth.py` — `get_current_user` 中 `int()` 转换纳入 try/except 范围
  - 文件: `backend/app/routers/upload.py` — 上传接口添加 `Depends(get_current_user)` 认证
  - 目的: 防止非整数 JWT payload 导致 500，上传需登录

- [x] **18. 路径遍历防护**
  - 文件: `backend/app/routers/markers.py`
  - 内容: 新增 `_safe_delete_file()` 函数，`resolve()` 后检查路径前缀；delete_marker 先 commit 再删文件
  - 目的: 防止 Windows 反斜杠路径遍历；事务一致性

- [x] **19. 参数校验 + 代码质量**
  - 文件: `backend/app/schemas.py` — username 正则校验、parse_images null 处理
  - 文件: `backend/app/routers/markers.py` — limit 加 `le=1000`、抽取 `_apply_marker_filters()` 消除重复
  - 文件: `backend/app/routers/regions.py` — HTTPException import 移至顶部
  - 文件: `backend/app/routers/maps.py` — TILE_DIR 不存在时返回空结果
  - 文件: `backend/app/routers/upload.py` — 扩展名正则清洗

- [x] **20. 前端安全与体验修复**
  - 文件: `frontend/src/api/index.js` — 401 跳转 `isRedirecting` 防重复
  - 文件: `frontend/src/views/RegisterView.vue` — 添加 `submitting` 状态防重复提交
  - 文件: `frontend/src/views/LoginView.vue` — 登录按钮 loading 状态
  - 文件: `frontend/src/stores/map.js` — addMarker/editMarker/removeMarker 加 try/catch
  - 文件: `frontend/src/stores/auth.js` — fetchUser 非 401 错误记录日志
  - 文件: `frontend/src/App.vue` — hasError 死代码激活为全局错误遮罩

- [x] **21. 组件优化**
  - 文件: `frontend/src/components/MarkerForm.vue` — submitting 改为 prop、AbortController 防泄漏、图片 key 改用 url
  - 文件: `frontend/src/views/HomeView.vue` — 抽取 `switchToRegion()` 消除三段重复；请求序列号防竞态
  - 文件: `frontend/src/stores/map.js` — 导出 `CHAPTER_KEYS` 给 MarkerForm 复用

- [x] **22. 无障碍改进**
  - 搜索框/分页/弹窗/地图容器添加 ARIA 属性 (role/aria-label/aria-modal)
  - 搜索结果和最新标记列表支持键盘导航 (tabindex/Enter/Space)
  - 弹窗/MarkerPopup/MarkerForm 支持 Esc 键关闭
  - 关闭按钮添加 aria-label

---

## 审计问题（已全部解决）

| # | 类别 | 问题 | 严重度 | 状态 |
|---|------|------|--------|------|
| 1 | 后端 | TileMap 静态文件未挂载，瓦片无法访问 | 高 | ✅ 已解决 |
| 2 | 后端 | User 表无 role 字段，任何登录用户都能 CRUD | 高 | ✅ 已解决 |
| 3 | 后端 | Alembic 未初始化，无迁移版本 | 中 | ✅ 已解决 |
| 4 | 前端 | 路由无鉴权守卫，主页可未登录访问 | 高 | ✅ 已解决 |
| 5 | 前端 | MapContainer/MarkerPopup/SidePanel 三组件未被使用 | 中 | ✅ 已解决 |
| 6 | 前端 | 标记 CRUD 无前端界面 | 中 | ✅ 已解决 |
| 7 | 前端 | 无登出功能，无用户信息展示 | 中 | ✅ 已解决 |
| 8 | 前端 | 应用启动时未调用 fetchUser 恢复登录态 | 中 | ✅ 已解决 |
| 9 | 前端 | favicon 和图标资源缺失 | 低 | ✅ 已解决 |
| 10 | 前端 | HomeView 无错误处理和加载状态 | 低 | ✅ 已解决 |
| 11 | 前端 | 404 页面缺失 | 低 | ✅ 已解决 |
| 12 | 前端 | Map Store 中 selectedCategory 未被使用 | 低 | ✅ 已解决 |

---

## 技术债务备忘

| 项目 | 说明 | 建议操作 |
|------|------|----------|
| ~~`alembic.ini` 硬编码数据库 URL~~ | 已改为占位符，env.py 从环境变量读取 | ✅ 已解决 |
| Leaflet CSS 依赖 unpkg CDN | CDN 不可用时地图无法渲染 | 改为 npm 引入或本地文件 |
| 前端无 TypeScript | 全部 JS，无类型安全 | 按需逐步迁移 |
| ~~`window.location.href` 跳转~~ | 已添加 `isRedirecting` 防重复标志 | ✅ 已缓解 |
| Vite 代理转发 TileMap | 开发环境依赖后端同时在线 | 生产部署需 nginx 配置 |
| rate_limit.py 多 worker 不共享 | 内存字典，多进程各自独立 | 生产环境改用 Redis |
| is_admin 用 Integer 而非 Boolean | SQLAlchemy 原生支持 Boolean 类型 | 按需重构 |

---

## 2026-06-05 全面审计 — 待修复问题

| # | 类别 | 问题 | 严重度 | 对应 ISSUES # |
|---|------|------|--------|---------------|
| 1 | 后端 | config.py int() 环境变量解析崩溃 | ~~高~~ ✅ 已修复 | #21 |
| 2 | 后端 | maps.py 路径遍历漏洞 | ~~高~~ ✅ 已修复 | #22 |
| 3 | 后端 | upload.py file.filename 为 None 崩溃 | ~~高~~ ✅ 已修复 | #23 |
| 4 | 后端 | seed.py 数据库会话泄漏 | ~~高~~ ✅ 已修复 | #24 |
| 5 | 后端 | database.py 连接池未配置 | ~~高~~ ✅ 已修复 | #25 |
| 6 | 后端 | main.py 缺少全局异常处理 | ~~高~~ ✅ 已修复 | #26 |
| 7 | 前端 | MapContainer.vue 地图实例内存泄漏 | ~~高~~ ✅ 已修复 | #27 |
| 8 | 前端 | HomeView.vue Promise rejection 未处理 | ~~高~~ ✅ 已修复 | #28 |
| 9 | 前端 | MarkerForm.vue 文件上传无前端验证 | ~~高~~ ✅ 已修复 | #29 |
| 10 | 前端 | stores/map.js fetchRegions/fetchCategories 无错误处理 | ~~高~~ ✅ 已修复 | #30 |
| 11 | 后端 | auth.py user_id 类型不安全 | ~~中~~ ✅ 已修复 | #31 |
| 12 | 后端 | rate_limit.py 反向代理 IP 错误 | ~~中~~ ✅ 已修复 | #32 |
| 13 | 后端 | rate_limit.py 字典内存泄漏 | ~~中~~ ✅ 已修复 | #33 |
| 14 | 后端 | markers.py 文件删除与事务不一致 | ~~中~~ ✅ 已修复 | #34 |
| 15 | 后端 | models.py datetime.now 无时区 | ~~中~~ ✅ 已修复 | #35 |
| 16 | 前端 | stores/auth.js 网络错误误触发登出 | ~~中~~ ✅ 已修复 | #36 |
| 17 | 前端 | HomeView.vue 搜索请求竞态 | ~~中~~ ✅ 已修复 | #37 |
| 18 | 前端 | HomeView.vue setTimeout 未清理 | ~~中~~ ✅ 已修复 | #38 |
| 19 | 前端 | MarkerForm.vue try/catch emit 无效 | ~~中~~ ✅ 已修复 | #39 |
| 20 | 前端 | App.vue 缺少全局错误边界 | ~~中~~ ✅ 已修复 | #40 |
| 21 | 前端 | 未登录用户无法看到 404 页面 | ~~低~~ ✅ 已修复 | #41 |
| 22 | 前端 | MapContainer.vue flyTo 缩放不准确 | ~~低~~ ✅ 已修复 | #42 |

---

## 2026-06-05 代码审查 — 待修复问题（✅ 全部已修复）

### 必须修复

| # | 类别 | 问题 | 对应 ISSUES # |
|---|------|------|---------------|
| 1 | 后端 | 全局异常处理器无日志，线上问题无法排查 | ~~#43~~ ✅ 已修复 |
| 2 | 后端 | JWT 默认密钥为弱密钥 | ~~#44~~ ✅ 已修复 |
| 3 | 前端 | MarkerForm.vue submitting 状态未正确控制 | ~~#45~~ ✅ 已修复 |
| 4 | 前端 | api/index.js 401 硬跳转竞态 | ~~#46~~ ✅ 已修复 |
| 5 | 前端 | HomeView.vue 快速切换请求竞态 | ~~#47~~ ✅ 已修复 |

### 建议修改

| # | 类别 | 问题 | 对应 ISSUES # |
|---|------|------|---------------|
| 6 | 后端 | 多 worker 下限流失效 | ~~#48~~ ✅ 已修复 |
| 7 | 后端 | 上传接口无认证、无限流 | ~~#49~~ ✅ 已修复 |
| 8 | 后端 | limit 参数无上限 | ~~#50~~ ✅ 已修复 |
| 9 | 后端 | delete_marker 先删文件后提交 | ~~#51~~ ✅ 已修复 |
| 10 | 后端 | list/count 筛选逻辑重复 | ~~#52~~ ✅ 已修复 |
| 11 | 后端 | username 缺少字符校验 | ~~#53~~ ✅ 已修复 |
| 12 | 前端 | fetchUser 静默吞非 401 错误 | ~~#54~~ ✅ 已修复 |
| 13 | 前端 | fetchMarkers 缺少错误处理 | ~~#55~~ ✅ 已修复 |
| 14 | 前端 | 文件上传缺少 AbortController | ~~#56~~ ✅ 已修复 |
| 15 | 前端 | HomeView 三段重复逻辑 | ~~#57~~ ✅ 已修复 |

### 仅供参考

| # | 类别 | 问题 | 对应 ISSUES # |
|---|------|------|---------------|
| 16 | 后端 | is_admin 用 Integer 而非 Boolean | #58 |
| 17 | 后端 | HTTPException import 位置 | ~~#59~~ ✅ 已修复 |
| 18 | 前端 | 认证页面样式重复 | #60 |
| 19 | 前端 | hasError 死代码 | ~~#61~~ ✅ 已修复 |
| 20 | 前端 | 登录按钮缺少 loading 状态 | ~~#62~~ ✅ 已修复 |

---

## 2026-06-08 代码审计 — 新增修复

| # | 类别 | 问题 | 严重度 | 对应 ISSUES # |
|---|------|------|--------|---------------|
| 1 | 后端 | seed.py 硬编码弱管理员密码 | 致命 | ~~#63~~ ✅ 已修复 |
| 2 | 后端 | auth.py int() 未捕获异常 | 高 | ~~#64~~ ✅ 已修复 |
| 3 | 后端 | markers.py Windows 反斜杠路径遍历 | 高 | ~~#65~~ ✅ 已修复 |
| 4 | 前端 | RegisterView 缺少重复提交防护 | 高 | ~~#66~~ ✅ 已修复 |
| 5 | 前端 | map.js 三个 action 无 try/catch | 高 | ~~#67~~ ✅ 已修复 |
| 6 | 前端 | MarkerForm 图片 key 使用索引 | 高 | ~~#68~~ ✅ 已修复 |
| 7 | 后端 | markers.py 批量赋值风险 | 中 | #69 |
| 8 | 后端 | parse_images null 处理不当 | 中 | ~~#70~~ ✅ 已修复 |
| 9 | 后端 | CORS 未 strip + JWT_ALGORITHM 无白名单 | 中 | ~~#71~~ ✅ 已修复 |
| 10 | 后端 | maps.py TILE_DIR 不存在未处理 | 中 | ~~#72~~ ✅ 已修复 |
| 11 | 前端 | CHAPTER_KEYS 常量重复定义 | 中 | ~~#73~~ ✅ 已修复 |
| 12 | 前端 | api/index.js isRedirecting 永不重置 | 中 | #74 |
| 13 | 前端 | 弹窗/MarkerForm 缺 Esc 键支持 | 低 | ~~#75~~ ✅ 已修复 |
| 14 | 前端 | 弹窗和地图容器缺 ARIA 属性 | 低 | ~~#76~~ ✅ 已修复 |
| 15 | 前端 | 搜索结果不可键盘导航 | 低 | ~~#77~~ ✅ 已修复 |
| 16 | 后端 | upload.py 扩展名未清理 | 低 | ~~#78~~ ✅ 已修复 |
| 17 | 前端 | 搜索空 catch 无日志 | 低 | ~~#79~~ ✅ 已修复 |

---

## 2026-06-05 架构审查 — 重构候选

> 详细报告见 `C:\Users\1\AppData\Local\Temp\architecture-review-20260605.html`
> 方法基于深度/局部性模型，术语见下文说明

### 模块术语

- **模块 (Module)**：任何有接口和实现的东西（函数、类、包、组件）
- **接口 (Interface)**：调用者需要知道的一切（类型、不变量、错误模式、顺序）
- **深度 (Depth)**：接口简单但背后逻辑复杂 → 高杠杆
- **浅度 (Shallow)**：接口几乎和实现一样复杂 → 低杠杆
- **Seam**：接口所在的位置，可以不修改原代码就改变行为的地方
- **局部性 (Locality)**：改动、bug、知识集中在一处的程度
- **删除测试 (Deletion Test)**：想象删除这个模块——复杂度消失(直通)还是重新出现在各处(有深度)

### 重构候选

#### P0 · Strong（高深度+高局部性，立即执行）

| # | 层面 | 候选 | 涉及文件 | 工作量 |
|---|------|------|----------|--------|
| 1 | 后端 | 抽取 MarkerRepository 层，消除 list/count 筛选重复 | `routers/markers.py` | 30min |
| 2 | 前端 | HomeView God Component 拆分为 5 个 composable | `views/HomeView.vue` | 2h |
| 3 | 前端 | Token 双源真实 → auth store 为唯一真实源 | `auth.js, router, api/index.js` | 30min |

**#1 细节**：`list_markers` 和 `count_markers` 中 20 行筛选代码完全复制。提取 `_apply_filters()` 公共函数，Router 只做 HTTP 关注点。首次实现了"修改 DB schema 不需要改 Router 代码"。

**#2 细节**：HomeView (684行) 承载 13 个职责：区域切换、地图选择、分类筛选、搜索防抖、分页、统计、标记CRUD、坐标拾取、传送跳转等。拆分为 `useMapNavigation`、`useMarkerSearch`、`useRecentMarkers`、`usePickMode`、`useMarkerForm` 五个 composable。抽 `RecentMarkersPanel`、`CategoryFilter`、`MarkerSearch` 三个独立组件。

**#3 细节**：JWT token 被 `stores/auth.js`、`router/index.js`、`api/index.js` 三个模块直接从 localStorage 读写。改成 auth store 是唯一真实源，其他模块通过 getter 访问。axios 401 拦截器改用 `authStore.logout()` + `router.push`，不再用 `window.location.href`。

#### P1 · Worth Exploring（中深度/高局部性）

| # | 层面 | 候选 | 涉及文件 |
|---|------|------|----------|
| 4 | 后端 | auth.py 拆分为 `core.py`(纯函数) + `dependencies.py`(FastAPI适配器) | `auth.py` |
| 5 | 前端 | API 浅模块合并：删除 4 个单行导出文件，store 直接调 axios | `api/regions.js, categories.js, maps.js, auth.js` |
| 6 | 后端 | 消除 CHAPTER_MAP(seed+map重复) 和 UPLOAD_DIR(marker+upload重复) | `seed.py, maps.py, markers.py, upload.py` |

#### P2 · Speculative（低深度/高局部性或反之）

| # | 层面 | 候选 | 涉及文件 |
|---|------|------|----------|
| 7 | 前端 | MapContainer 命令式耦合 → `focusCoords` prop 声明式驱动 | `MapContainer.vue, HomeView.vue` |
| 8 | 前端 | Props 瀑布 → MarkerForm/Popup 直连 `useMapStore()` | `HomeView.vue, MarkerForm.vue, MarkerPopup.vue` |
| 9 | 后端 | config.py + database.py 浅模块 → Pydantic BaseSettings | `config.py, database.py` |
| 10 | 前端 | SidePanel (19行空壳) → 用 CSS 类替代 | `SidePanel.vue` |

### 首选推荐

**#1 Repository 层**——改动在一个文件内，消除重复、开启可测试性、为后续所有数据层改进铺路。30 分钟工作量。
