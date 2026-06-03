-- ============================================================
-- 博德之门 3 交互式地图 - 数据库初始化脚本
--
-- 创建 bg3_map 数据库及四张核心业务表：
--   1. users      用户表 (含管理员标识)
--   2. regions    区域/章节表
--   3. categories 标记分类表
--   4. markers    地图标记点表 (关联区域和分类，支持传送目标)
--
-- 同时插入初始种子数据。
-- ============================================================

-- 创建数据库，使用 utf8mb4 字符集
CREATE DATABASE IF NOT EXISTS bg3_map
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE bg3_map;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,     -- bcrypt 哈希
  avatar VARCHAR(255),
  is_admin TINYINT(1) DEFAULT 0,           -- 0=普通用户, 1=管理员
  created_at DATETIME DEFAULT NOW()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 区域表 — 游戏章节与瓦片地图配置
CREATE TABLE IF NOT EXISTS regions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  tile_url VARCHAR(255),                   -- Leaflet 瓦片 URL 模板 ({z}/{y}/{x})
  sort_order INT DEFAULT 0,                -- 排序序号
  created_at DATETIME DEFAULT NOW()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 标记分类表 — 传送点/怪物/道具等
CREATE TABLE IF NOT EXISTS categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  icon VARCHAR(255),                       -- SVG 图标 URL
  color VARCHAR(7),                        -- 标记颜色 (如 #FF4444)
  sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 标记点表 — 地图上的兴趣点，支持截图和传送跳转
CREATE TABLE IF NOT EXISTS markers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  region_id INT NOT NULL,                  -- 所属区域
  category_id INT NOT NULL,                -- 标记分类
  name VARCHAR(200) NOT NULL,
  description TEXT,
  x_coord DECIMAL(10, 2) NOT NULL,        -- 地图横坐标
  y_coord DECIMAL(10, 2) NOT NULL,        -- 地图纵坐标
  screenshot TEXT,                         -- JSON 数组，存储截图 URL 列表
  map_name VARCHAR(100) DEFAULT '',        -- 所属子地图
  target_region_id INT DEFAULT NULL,       -- 传送目标区域
  target_map_name VARCHAR(100) DEFAULT '', -- 传送目标子地图
  target_x DECIMAL(10, 2) DEFAULT NULL,    -- 传送目标 X
  target_y DECIMAL(10, 2) DEFAULT NULL,    -- 传送目标 Y
  created_at DATETIME DEFAULT NOW(),
  FOREIGN KEY (region_id) REFERENCES regions(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 初始种子数据
-- ============================================================

-- 五个游戏章节区域
INSERT INTO regions (name, description, tile_url, sort_order) VALUES
  ('序章', '鹦鹉螺式魔法船', '/TileMap/chapter0/{z}/{y}/{x}.png', 0),
  ('第一章', '林地、地精营地、幽暗地域等', '/TileMap/chapter1/{z}/{y}/{x}.png', 1),
  ('第二章', '伊雷珂养育间', '/TileMap/chapter2/{z}/{y}/{x}.png', 2),
  ('第三章', '月出之塔、暗夜之歌监狱等', '/TileMap/chapter3/{z}/{y}/{x}.png', 3),
  ('第四章', '博德之门', '/TileMap/chapter4/{z}/{y}/{x}.png', 4);

-- 三种标记分类
INSERT INTO categories (name, icon, color, sort_order) VALUES
  ('传送点', '/icons/waypoint.svg', '#00BFFF', 0),
  ('怪物', '/icons/monster.svg', '#FF4444', 1),
  ('道具', '/icons/item.svg', '#FFD700', 2);
