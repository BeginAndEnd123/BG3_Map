# 开发跟踪文档

> 最后更新: 2026-06-02

## 项目状态总览

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 环境搭建 | 100% | Python 依赖、MySQL 数据库、种子数据就绪 |
| 后端 API | 80% | 核心完成，缺静态文件挂载和权限系统 |
| 前端页面 | 50% | 框架完整，缺路由守卫、CRUD-UI、组件整合 |
| 地图数据 | 100% | 97 张源图，瓦片已全部切片 |
| 切图工具 | 100% | 支持全量/增量/多进程 |

---

## 环境配置记录

| 项目 | 值 | 备注 |
|------|-----|------|
| MySQL 路径 | `E:\SQLDB\mysql\` | 服务已运行 |
| MySQL 账号 | `root` / `root` | 端口 3306 |
| 数据库名 | `bg3_map` | utf8mb4 |
| 后端配置 | `backend/.env` | 密码已更正为 `root` |
| 管理员账号 | `admin` / `admin123` | bcrypt 加密 |
| bcrypt 版本 | 4.2.1 | 降级以兼容 passlib（5.0 API 不兼容） |
| Navicat | `E:\navicat170_premium_cs_x64\navicat.exe` | 已安装 |
| GitHub 仓库 | `git@github.com:BeginAndEnd123/BG3_Map.git` | SSH |
| SSH 密钥 | `~/.ssh/id_rsa` (私钥) / `~/.ssh/id_rsa.pub` (公钥) | 需在 GitHub Settings 添加公钥 |

### SSH 公钥（添加到 GitHub）

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDROCWwvjS/gMchxRqf6chPXNm9OU+YAFDMzC1HhS+uOC/5bZeeaHgjh+am9r1CFQKSzZ0tEJNKScP27RR2DRBLTC/96pKFm0rhxIaPXvIK7FLMegAEXsAoMnRGESkAFr4bBsisk9ecAPxnz4b7NRnbgK3z1gRIklaVEKZciAVX2NOX6dv1KPLrJddZtME4RzfF972VsKRw7EVGSH8lCA7rTMEbaxD/sQBfZQT0xYNZ4nwtCGu2A2xGMJCzFoYj/6XMip53oTFIf4tYP2g6wOjBKC9LCVsvlWhXlRAKBZ4ezPV1UqR2yIKN3uZ/nEZsh6kkRX+hlxouF8KwL/BXJhG41wODTwsgRX7oW2XRY1gZL/ghzkc098wpu1DBcFgTlRfuT4WJcabeSM785mCKI0ufRu5/MGq0A5WuK7tnTQEchC+yHO0HMBAPp4+0g1HfalksUxvWJlfZeQtOwQHw4ju3/0YfOJn5ep8uw3EGZarI4YeynQXwwivG6LLo4QpsyUM= 2759919162@qq.com
```

> 私钥 `id_rsa` 位于 `~/.ssh/` 目录，切勿提交到 Git。

---

## 任务清单

### 第一轮：打通核心链路

- [ ] **1. 后端挂载 TileMap 静态文件**
  - 文件: `backend/app/main.py`
  - 内容: 添加 `app.mount("/TileMap", StaticFiles(directory="..."), name="tilemap")`
  - 目的: 让 Leaflet 能加载瓦片图片

- [ ] **2. 前端路由鉴权守卫**
  - 文件: `frontend/src/router/index.js`
  - 内容: `router.beforeEach` 检查 token，未登录跳 `/login`
  - 目的: 保护主页不被未登录用户访问

- [ ] **3. 应用启动时恢复用户登录态**
  - 文件: `frontend/src/App.vue`
  - 内容: `onMounted` 时调用 `authStore.fetchUser()`
  - 目的: 刷新页面后保持登录状态

- [ ] **4. 添加 favicon 和基础静态资源**
  - 文件: `frontend/public/favicon.ico`
  - 内容: 放入 32x32 地图图标
  - 目的: 消除浏览器 404 报错

### 第二轮：重构组件架构

- [ ] **5. 重构 HomeView 使用 MapContainer 组件**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 删除内联 `L.map()` 逻辑，改用 `<MapContainer>` 并通过 props/events 通信
  - 目的: 消除重复代码，统一地图逻辑

- [ ] **6. 重构 HomeView 使用 MarkerPopup 组件**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 将 `marker.bindPopup(htmlString)` 改为组件化弹窗
  - 目的: 支持截图展示、结构化布局

- [ ] **7. 重构 HomeView 使用 SidePanel 组件**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 将 `.sidebar` 内联 HTML 移入 `<SidePanel>` slot
  - 目的: 组件职责分离，便于维护

### 第三轮：补充业务功能

- [ ] **8. 添加管理员角色系统**
  - 文件: `backend/app/models.py` (User 加 `is_admin` 字段)
  - 文件: `backend/app/auth.py` (加 `require_admin` 依赖)
  - 文件: `backend/app/routers/markers.py` (CRUD 端点改用 `require_admin`)
  - 文件: `backend/app/seed.py` (admin 用户设 `is_admin=True`)
  - 文件: `sql/init.sql` (users 表加 `is_admin` 字段)
  - 目的: 区分普通用户和管理员权限

- [ ] **9. 标记 CRUD 前端界面**
  - 文件: `frontend/src/stores/map.js` (加 `createMarker`/`updateMarker`/`deleteMarker` action)
  - 文件: 新建 `frontend/src/components/MarkerForm.vue` (新增/编辑表单弹窗)
  - 文件: `frontend/src/views/HomeView.vue` (集成新增/编辑/删除操作)
  - 目的: 管理员可在前端管理标记数据

- [ ] **10. 登出功能 + 用户信息展示**
  - 文件: `frontend/src/App.vue` (加导航栏/顶栏)
  - 文件: 新建 `frontend/src/components/NavBar.vue`
  - 内容: 显示用户名 + 登出按钮
  - 目的: 完善用户体验闭环

- [ ] **11. 加载状态和错误处理**
  - 文件: `frontend/src/views/HomeView.vue`
  - 内容: 添加 loading 动画 + try-catch 错误提示
  - 目的: 避免静默崩溃，提升用户体验

### 第四轮：收尾完善

- [ ] **12. Alembic 初始化迁移**
  - 命令: `cd backend && alembic revision --autogenerate -m "initial"`
  - 目的: 建立正式的数据库迁移链

- [ ] **13. 404 页面**
  - 文件: 新建 `frontend/src/views/NotFoundView.vue`
  - 文件: `frontend/src/router/index.js` (加 `/:pathMatch(.*)*` 路由)
  - 目的: 处理无效路由

- [ ] **14. 标记分类图标**
  - 目录: `frontend/src/assets/icons/`
  - 内容: 传送点/怪物/道具的 SVG 图标
  - 文件: `frontend/src/components/MapContainer.vue` (改用 `L.icon` 替代 `L.divIcon`)
  - 目的: 用图标替代纯色圆点，视觉更丰富

---

## 审计发现的问题汇总

| # | 类别 | 问题 | 严重度 | 对应任务 |
|---|------|------|--------|----------|
| 1 | 后端 | TileMap 静态文件未挂载，瓦片无法访问 | 高 | 任务 1 |
| 2 | 后端 | User 表无 role 字段，任何登录用户都能 CRUD | 高 | 任务 8 |
| 3 | 后端 | Alembic 未初始化，无迁移版本 | 中 | 任务 12 |
| 4 | 前端 | 路由无鉴权守卫，主页可未登录访问 | 高 | 任务 2 |
| 5 | 前端 | MapContainer/MarkerPopup/SidePanel 三组件未被使用 | 中 | 任务 5/6/7 |
| 6 | 前端 | 标记 CRUD 无前端界面 | 中 | 任务 9 |
| 7 | 前端 | 无登出功能，无用户信息展示 | 中 | 任务 10 |
| 8 | 前端 | 应用启动时未调用 fetchUser 恢复登录态 | 中 | 任务 3 |
| 9 | 前端 | favicon 和图标资源缺失 | 低 | 任务 4/14 |
| 10 | 前端 | HomeView 无错误处理和加载状态 | 低 | 任务 11 |
| 11 | 前端 | 404 页面缺失 | 低 | 任务 13 |
| 12 | 前端 | Map Store 中 selectedCategory 未被使用 | 低 | 任务 7 |

---

## 技术债务备忘

| 项目 | 说明 | 建议操作 |
|------|------|----------|
| `alembic.ini` 硬编码数据库 URL | 与实际 .env 配置不一致 | 改为从环境变量读取 |
| Leaflet CSS 依赖 unpkg CDN | CDN 不可用时地图无法渲染 | 改为 npm 引入或本地文件 |
| 前端无 TypeScript | 全部 JS，无类型安全 | 按需逐步迁移 |
| `window.location.href` 跳转 | API 401 拦截器用硬刷新代替路由跳转 | 改为 `router.push('/login')` |
| Vite 代理转发 TileMap | 开发环境依赖后端同时在线 | 生产部署需 nginx 配置 |

---

## 变更日志

| 日期 | 内容 |
|------|------|
| 2026-06-02 | 项目审计完成，生成 14 项任务清单，4 轮迭代计划 |
| 2026-06-02 | 切图工具 `tools/tile_cutter.py` 完成，97 张源图全部切片 (68,548 tiles) |
| 2026-06-02 | MySQL 数据库初始化：`init.sql` 执行、4 表创建、5 区域 + 3 分类种子数据 |
| 2026-06-02 | Python 依赖安装 + bcrypt 兼容性修复 (5.0.0 → 4.2.1) |
| 2026-06-02 | admin 用户创建：`admin` / `admin123` |
| 2026-06-02 | `.env` 密码更正：`123456` → `root` |
