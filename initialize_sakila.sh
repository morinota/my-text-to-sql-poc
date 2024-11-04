#!/bin/bash

# データベースファイルのパス
db_file="data/sample.db"

# SQLiteスクリプトファイルのパス
schema_sql="data/sqlite-sakila-schema.sql"
insert_data_sql="data/sqlite-sakila-insert-data.sql"
drop_objects_sql="data/sqlite-sakila-drop-objects.sql"

# SakilaデータセットのURL
schema_url="https://github.com/jOOQ/sakila/raw/main/sqlite-sakila-db/sqlite-sakila-schema.sql"
insert_data_url="https://github.com/jOOQ/sakila/raw/main/sqlite-sakila-db/sqlite-sakila-insert-data.sql"

# データセットのSQLファイルが存在しない場合のみダウンロード
if [ ! -f "$schema_sql" ]; then
    echo "Downloading Sakila schema SQL..."
    curl -L -o "$schema_sql" "$schema_url"
fi

if [ ! -f "$insert_data_sql" ]; then
    echo "Downloading Sakila insert data SQL..."
    curl -L -o "$insert_data_sql" "$insert_data_url"
fi

# データベースファイルが既に存在する場合は削除
if [ -f "$db_file" ]; then
    echo "既存のデータベース $db_file を削除します..."
    rm "$db_file"
fi

# 空のデータベースを作成
echo "新しいデータベース $db_file を作成します..."
sqlite3 "$db_file" "VACUUM;"

# Sakilaスキーマのインポート
echo "Sakilaのスキーマをインポートします..."
sqlite3 "$db_file" < "$schema_sql"

# Sakilaデータの挿入
echo "Sakilaのデータを挿入します..."
sqlite3 "$db_file" < "$insert_data_sql"

echo "データベースの初期化が完了しました。"
