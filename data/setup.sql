-- data/setup.sql

-- 既存のテーブルを削除
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS show_events;
DROP TABLE IF EXISTS tap_events;
DROP TABLE IF EXISTS purchase_events;

-- 売上情報を管理するテーブル
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount REAL,
    sale_date TEXT
);

-- 顧客情報を管理するテーブル
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

-- 商品表示イベントを管理するテーブル
CREATE TABLE show_events (
    event_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    event_type TEXT,
    timestamp TEXT,
    product_id INTEGER
);

-- 商品タップイベントを管理するテーブル
CREATE TABLE tap_events (
    event_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    event_type TEXT,
    timestamp TEXT,
    product_id INTEGER
);

-- 購入イベントを管理するテーブル
CREATE TABLE purchase_events (
    event_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    timestamp TEXT,
    product_id INTEGER,
    purchase_amount REAL
);

-- サンプルデータ挿入

-- 顧客データ
INSERT INTO customers (name, email) VALUES 
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

-- 売上データ
INSERT INTO sales (customer_id, amount, sale_date) VALUES 
    (1, 100.5, '2023-01-15'),
    (2, 250.0, '2023-02-20'),
    (1, 300.0, '2023-03-10');

-- 商品表示イベントデータ
INSERT INTO show_events (customer_id, event_type, timestamp, product_id) VALUES 
    (1, 'show', '2023-01-15 10:00:00', 101),
    (2, 'show', '2023-01-20 14:30:00', 102),
    (3, 'show', '2023-01-25 16:45:00', 103);

-- 商品タップイベントデータ
INSERT INTO tap_events (customer_id, event_type, timestamp, product_id) VALUES 
    (1, 'tap', '2023-01-15 10:05:00', 101),
    (2, 'tap', '2023-01-20 14:35:00', 102),
    (3, 'tap', '2023-01-25 16:50:00', 103);

-- 購入イベントデータ
INSERT INTO purchase_events (customer_id, timestamp, product_id, purchase_amount) VALUES 
    (1, '2023-01-15 10:10:00', 101, 150.0),
    (2, '2023-01-20 14:40:00', 102, 200.0),
    (3, '2023-01-25 16:55:00', 103, 350.0);
