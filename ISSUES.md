# 项目问题清单

> 审计日期：2026-06-04
> 审计范围：全项目代码、配置、安全

---

## 一、致命 (Critical)

### 1. 分类多选筛选 API 404 / 422 报错

**位置**：`backend/app/routers/markers.py:37` → `frontend/src/views/HomeView.vue:343`

**问题**：前端多选分类时将 ID 拼接为字符串 `"1,2,3"` 传给 `category_id` 参数，但后端定义为 `Optional[int]`，FastAPI 无法将 `"1,2,3"` 解析为 int，直接返回 422 Validation Error。

**影响**：用户勾选多个分类筛选标记时功能不可用。

**修复建议**：后端 `category_id` 改为 `Optional[str]`，内部自行拆分和校验。

---

### 2. alembic.ini 硬编码数据库密码

**位置**：`backend/alembic.ini:3`

```ini
sqlalchemy.url = mysql+pymysql://root:root@localhost:3306/bg3_map
```

**问题**：数据库用户名和密码以明文写在配置文件里，且该文件**未被 `.gitignore` 排除**。一旦推送至公开仓库，数据库凭据彻底暴露。

**影响**：严重安全漏洞。

**修复建议**：
- 将 `alembic.ini` 中的 `sqlalchemy.url` 改为引用环境变量
- 修改 `backend/alembic/env.py`，从 `.env` 读取 `DATABASE_URL`

---

### 3. JWT 密钥使用占位符弱值

**位置**：`backend/.env:2`

```
JWT_SECRET_KEY=your-secret-key-change-in-production
```

**问题**：虽然 `.env` 在 `.gitignore` 中，但实际运行时使用的是该弱密钥，攻击者可以轻易伪造任意用户的 JWT 令牌，完全绕过认证系统。

**修复建议**：生成高熵密钥：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 二、高危 (High)

### 4. 注册接口无密码验证

**位置**：`backend/app/schemas.py:15-16`

```python
class UserRegister(BaseModel):
    username: str
    password: str  # 无任何约束
```

**问题**：
- 密码无最小长度限制（可注册空密码）
- 无复杂度要求（允许纯数字、纯字母等弱密码）
- 前端也未做密码确认（无 confirm password 字段），用户输错后无法登录

**修复建议**：
- `password` 字段加 `min_length=6`
- 前端注册表单加"确认密码"输入框

---

### 5. 多处 async 函数调用缺少 await，存在竞态条件

**位置**：`frontend/src/views/HomeView.vue`

| 行号 | 代码 | 问题 |
|------|------|------|
| 362 | `loadMarkers()` | `fetchMaps()` 未完成时就开始加载标记 |
| 374 | `loadMarkers()` | 同上，`onMapChange` 中 |
| 478 | `fetchMaps()` | `onMounted` 中 `loadMarkers` 可能在 `fetchMaps` 完成前执行 |

**影响**：区域/地图切换时，标记请求可能携带尚未更新完毕的 `selectedMapName`，导致 UI 出现短暂旧数据闪烁或传参错误。

**修复建议**：所有调用均加 `await`。

---

### 6. 数据库密码默认值与实际配置不一致

| 位置 | 密码 |
|------|------|
| `backend/.env` | `root` |
| `backend/app/config.py:13` 硬编码 fallback | `123456` |
| `backend/alembic.ini:3` | `root` |
| `sql/init.sql` 注释说明 | `root` |

**问题**：当 `.env` 被误删或未加载（如 dotenv 未安装）时，`config.py` 回退到 `123456`，与数据库实际密码不一致，导致启动失败且排查困难。

**修复建议**：
- fallback 值统一为 `""`（空字符串），强制要求配置 `.env`
- 或 fallback 值与 `.env` 保持一致

---

## 三、中危 (Medium)

### 7. 统计数字含义不准确

**位置**：`frontend/src/views/HomeView.vue:57`

```html
<p>标记总数：{{ mapStore.markers.length }}</p>
```

**问题**：显示的是**当前筛选条件过滤后**的标记数量，但标签名是"标记总数"，语义严重误导。

**修复建议**：要么改标签名为"当前标记"，要么用 `/api/markers/count` 接口获取真实总数。

---

### 8. JWT Token 存储方式不安全

**位置**：`frontend/src/stores/auth.js:12`

```js
const token = ref(localStorage.getItem('token') || '')
```

**问题**：Token 存储在 `localStorage` 中，任何注入的恶意脚本（XSS）都能直接读取并窃取 token。

**修复建议**：改用 `httpOnly` + `Secure` Cookie 方案，或设置较短的过期时间作为缓解措施。

---

### 9. 路由守卫不验证 token 有效性

**位置**：`frontend/src/router/index.js:28-36`

```js
const token = localStorage.getItem('token')
if (WHITE_LIST.includes(to.name)) {
  if (token) return next({ name: 'home' })
  return next()
}
if (!token) return next({ name: 'login' })
next()
```

**问题**：只要 `localStorage` 中有 token 字符串就放行，不校验 token 是否过期或有效。结果是：
1. 过期 token 先跳到首页
2. 首页 API 调用触发 401
3. axios 拦截器再跳回登录页

用户看到一次不必要的闪烁跳转。

**修复建议**：在守卫中调用 `/api/auth/me` 验证 token 有效性，或在 store 维护一个 `isAuthenticated` 状态。

---

### 10. 登录和注册接口无频率限制

**位置**：`backend/app/routers/auth.py`

**问题**：`/api/auth/login` 和 `/api/auth/register` 无 rate limiting，攻击者可无限次尝试弱密码/撞库，也可批量注册垃圾账号。

**修复建议**：引入 `slowapi` 或自实现 IP 级别的速率限制（如每分钟最多 5 次尝试）。

---

### 11. 前端错误信息不友好

**位置**：多处

```js
// HomeView.vue:451-453
} catch {
  alert('操作失败，请检查权限')
}
```

**问题**：所有非 401 错误（网络故障、500 服务端错误）统一提示"请检查权限"，误导用户。服务端返回的具体错误信息也被丢弃。

**修复建议**：区分错误类型给出不同提示，或至少显示 `err.response?.data?.detail`。

---

## 四、低危 (Low)

### 12. PRD 文档与实际代码不一致

**位置**：`PRD.md`

| 字段 | PRD 描述 | 实际代码 |
|------|----------|----------|
| `users` 表 | 缺少 `is_admin` 字段 | `is_admin INT` |
| `markers.screenshot` | `VARCHAR(255)` 单图 | `TEXT` JSON 数组 |
| `markers` 表 | 缺少 `map_name` / `target_*` 字段 | 已实现但未文档化 |

**修复建议**：同步更新 PRD 或直接删除，避免两份文档不一致造成混淆。

---

### 13. 项目完全没有测试

**位置**：全局

**问题**：项目中没有任何测试文件（单元测试、API 集成测试、E2E 测试均为零）。每次改动只能依靠手工回归，极易引入新 Bug。

**修复建议**：至少为核心路由添加 API 测试（FastAPI 自带 `TestClient`），为关键组件添加 Vue Test Utils 测试。

---

### 14. markers 表外键缺少显式索引

**位置**：`backend/app/models.py:57-58`

```python
region_id = Column(Integer, ForeignKey("regions.id"))
category_id = Column(Integer, ForeignKey("categories.id"))
```

**问题**：`region_id` 和 `category_id` 是高频筛选条件（每次加载地图标记都按 region+map 过滤），但没有显式创建索引。虽然 InnoDB 对外键自动创建索引，但 `map_name` 字段（第64行）完全没有索引，会随数据量增长导致全表扫描。

**修复建议**：
- 为 `map_name` 添加索引
- 为 `(region_id, map_name, category_id)` 添加联合索引

---

### 15. 搜索未转义 LIKE 通配符

**位置**：`backend/app/routers/markers.py:54`

```python
query = query.filter(Marker.name.like(f"%{keyword}%"))
```

**问题**：如果用户输入包含 `%` 或 `_` 字符，会被 SQL LIKE 解释为通配符，导致搜索结果异常。并非安全漏洞（SQLAlchemy 参数化了），但是功能缺陷。

**修复建议**：搜索前对 `keyword` 中的 `%` 和 `_` 进行转义：
```python
escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
query = query.filter(Marker.name.like(f"%{escaped}%", escape="\\"))
```

---

### 16. models.py 缺少表级别的命名约定

**位置**：`backend/app/models.py`

**问题**：使用 `declarative_base()` 没有配置命名约定，Alembic 自动迁移时无法正确检测约束命名变更。

**修复建议**：在 `database.py` 中使用：
```python
from sqlalchemy import MetaData
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base = declarative_base(metadata=MetaData(naming_convention=convention))
```

---

### 17. 文件上传无文件类型深度校验

**位置**：`backend/app/routers/upload.py:26`

```python
if file.content_type not in ALLOWED_TYPES:
    raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")
```

**问题**：仅检查 `Content-Type` 头，攻击者可伪造该字段上传任意文件。未使用 Python 的 `imghdr` 或 `Pillow` 对文件内容做魔术字节校验。

**修复建议**：读取文件头部字节验证真实类型，或用 Pillow 尝试打开图片。

---

### 18. MarkerForm 直接使用原生 `api.post` 而非封装的 upload API

**位置**：`frontend/src/components/MarkerForm.vue:162`

```js
const res = await api.post('/upload', fd)
```

**问题**：上传直接硬编码路径 `/upload`，违背了封装原则。其他 API 调用通过 api 模块中转，上传却直接使用 axios 实例。

**修复建议**：在 `src/api/` 下新建 `upload.js`，统一管理上传接口。

---

## 五、改进建议 (Enhancement)

### 19. 地图瓦片 URL 中的 `{z}` 双花括号问题

**位置**：
- `backend/app/routers/maps.py:41`
- `sql/init.sql:75-79`

```python
"tile_url": f"/TileMap/{chapter}/{d.name}/{{z}}/{{y}}/{{x}}.png",
```

**问题**：Python f-string 中 `{{z}}` 转义为 `{z}` 的做法虽然正确，但极易被误改。如果某人将 `f""` 改为 `""` 或漏掉一层花括号，Leaflet 将无法正确加载瓦片。

**修复建议**：添加注释说明花括号转义，或改用 `.format()` / 字符串拼接提高可读性。

---

### 20. 缺少生产环境构建配置

**问题**：
- 前端无生产环境 Dockerfile 或 nginx 配置
- 后端无 gunicorn/多 worker 配置
- CORS `allow_origins` 硬编码 `localhost:5173`，生产环境需改代码

**修复建议**：将 CORS origins 和 proxy target 等提取为环境变量。

---

> **共计：20 个问题**
> - 致命: 3
> - 高危: 3
> - 中危: 5
> - 低危: 7
> - 改进建议: 2
