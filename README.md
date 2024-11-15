# 1. 動作確認手順

このドキュメントは、Text-to-SQL PoCアプリケーションのセットアップおよび動作確認方法をまとめたものです。

## 1.1. 依存関係のインストール

まず、Poetryを使って必要な依存関係をインストールします。

```bash
poetry install
```

## 1.2. 環境変数の設定

OpenAI APIキーがある場合は、以下のように環境変数として設定します。

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 1.3. データベースの初期化

このPoCでは、[Sakilaデータセット](https://github.com/jOOQ/sakila)を使用します。`sample.db`にSakilaデータベースをセットアップするには、以下の手順に従います。

1. Sakila用のSQLファイルが`data/`ディレクトリにあることを確認します。

```bash
ls data/
# 出力例:
# sample.db  sqlite-sakila-schema.sql  sqlite-sakila-insert-data.sql
```

initialize_sakila.shスクリプトを実行して、sample.dbにデータベースを初期化します。

```bash
bash
コードをコピーする
chmod +x initialize_sakila.sh
./initialize_sakila.sh
```

このスクリプトは、既存のsample.dbを削除してから新しいデータベースを作成し、Sakilaのスキーマとデータをインポートします。

3. 初期化が完了したら、SQLiteを使ってデータベースが正しく設定されているか確認できます。

```bash
sqlite3 data/sample.db
.tables  # テーブル一覧の確認
SELECT * FROM customer LIMIT 5;  # 顧客テーブルのデータ表示
```

## 1.4. プロンプトおよびスキーマファイルの確認

`prompts/generate_sql_prompt.txt` と `schema/tables_schema.json` が存在するか確認します。

- **プロンプトファイル**: `prompts/generate_sql_prompt.txt` は、SQLクエリ生成に使われるプロンプトを含みます。
- **スキーマファイル**: `schema/tables_schema.json` は、テーブルのスキーマ情報を含んでおり、SQL生成に利用されます。

## 1.5. アプリケーションの実行方法

アプリケーションは以下のコマンドで実行します。`--question`オプションで自然言語の質問を、`--dialect`オプションでSQLの方言を指定します。

```bash
poetry run python -m my_text_to_sql_poc --question "2023年の売上合計は？" --dialect "SQLite"
```

## 1.6. ログレベルの指定

デバッグ情報の出力レベルを制御するために、`--log-level`オプションを使用できます。

- `--log-level "INFO"` : 通常の情報のみを表示
- `--log-level "DEBUG"` : 詳細なデバッグ情報を表示
- `--log-level "ERROR"` : エラーメッセージのみを表示

### 1.6.1. 実行例

#### 1.6.1.1. text2sqlアプリver1の実行

```bash
poetry run python -m my_text_to_sql_poc.app.generate_sql_query_ver1 --question "各年の売り上げの推移を知りたい" --dialect "DuckDB" --log-level "DEBUG"
```

#### テーブルスキーマファイルと、サンプルクエリファイルを要約するオフラインバッチの実行

差分更新

```bash
poetry run python -m my_text_to_sql_poc.app.generate_summary_batch \
    --schema-dir data/schema \
    --sample-queries-dir data/sample_queries \
    --output-schema-dir data/summarized_schema \
    --output-queries-dir data/summarized_sample_queries
```

全更新

```bash
poetry run python -m my_text_to_sql_poc.app.generate_summary_batch \
    --schema-dir data/schema \
    --sample-queries-dir data/sample_queries \
    --output-schema-dir data/summarized_schema \
    --output-queries-dir data/summarized_sample_queries \
    --full-refresh
```

#### テーブル要約とクエリ要約を埋め込み表現に変換して、ベクトルストアに保存するオフラインバッチの実行

```bash
poetry run python -m my_text_to_sql_poc.app.embed_summaries_batch \
    --table-summary-dir data/summarized_schema \
    --query-summary-dir data/summarized_sample_queries \
    --vectorstore-file sample_vectorstore.duckdb
```

#### Text2SQLアプリケーションの実行(RAGによるcontext constructionを活用するver)

```bash
% poetry run python -m my_text_to_sql_poc.app.generate_sql_query_ver2 --question "直近2週間の各カテゴリのCTRの推移を知りたい" --dialect "Redshift" 
```

#### GUIアプリケーションの起動

```bash
poetry run streamlit run src/my_text_to_sql_poc/presentation/streamlit_gui.py
```
