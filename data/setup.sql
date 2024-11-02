-- data/setup.sql

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

-- サンプルデータ挿入
INSERT INTO customers (name, email) VALUES 
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

INSERT INTO sales (customer_id, amount, sale_date) VALUES 
    (1, 100.5, '2023-01-15'),
    (2, 250.0, '2023-02-20'),
    (1, 300.0, '2023-03-10');
