-- 创建数据库
CREATE DATABASE IF NOT EXISTS bg3_map
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE bg3_map;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  avatar VARCHAR(255),
  is_admin TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT NOW()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 区域表
CREATE TABLE IF NOT EXISTS regions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  tile_url VARCHAR(255),
  sort_order INT DEFAULT 0,
  created_at DATETIME DEFAULT NOW()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 标记分类表
CREATE TABLE IF NOT EXISTS categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  icon VARCHAR(255),
  color VARCHAR(7),
  sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 标记点表
CREATE TABLE IF NOT EXISTS markers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  region_id INT NOT NULL,
  category_id INT NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  x_coord DECIMAL(10, 2) NOT NULL,
  y_coord DECIMAL(10, 2) NOT NULL,
  screenshot TEXT,
  map_name VARCHAR(100) DEFAULT '',
  created_at DATETIME DEFAULT NOW(),
  FOREIGN KEY (region_id) REFERENCES regions(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 初始数据
INSERT INTO regions (name, description, tile_url, sort_order) VALUES
  ('序章', '鹦鹉螺式魔法船', '/TileMap/chapter0/{z}/{y}/{x}.png', 0),
  ('第一章', '林地、地精营地、幽暗地域等', '/TileMap/chapter1/{z}/{y}/{x}.png', 1),
  ('第二章', '伊雷珂养育间', '/TileMap/chapter2/{z}/{y}/{x}.png', 2),
  ('第三章', '月出之塔、暗夜之歌监狱等', '/TileMap/chapter3/{z}/{y}/{x}.png', 3),
  ('第四章', '博德之门', '/TileMap/chapter4/{z}/{y}/{x}.png', 4);

INSERT INTO categories (name, icon, color, sort_order) VALUES
  ('传送点', '/icons/waypoint.svg', '#00BFFF', 0),
  ('怪物', '/icons/monster.svg', '#FF4444', 1),
  ('道具', '/icons/item.svg', '#FFD700', 2);
