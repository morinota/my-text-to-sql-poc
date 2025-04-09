# 1. 動作確認手順

このドキュメントは、Text-to-SQL PoCアプリケーションのセットアップおよび動作確認方法をまとめたものです。

## 1.1. 依存関係のインストール

まず、uvを使って必要な依存関係をインストールします。

```bash
brew install uv
uv sync
```

## 1.2. 環境変数の設定

OpenAI APIキーがある場合は、以下のように環境変数として設定します。

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 1.3. 実行例

### 1.3.1. 自動でテーブルメタデータを生成するオフラインのバッチジョブを実行

全更新 (すでにテーブルメタデータがある場合は、上書きされます)

```bash
uv run python -m my_text_to_sql_poc.app.generate_table_metadata_batch \
    --sample-queries-dir data/sample_queries \
    --table-metadata-dir data/table_metadata \
    --full-refresh \
    --target-tables for_analysis_kikuchi_subscribe_all_list_comp_with_full_data \
    --target-tables allocation_settings \
    --target-tables tap_article_events \
    --target-tables show_article_events \
    --target-tables dynamodb.news
```

差分更新 (すでにテーブルメタデータがある場合は、スキップされます)

```bash
uv run python -m my_text_to_sql_poc.app.generate_table_metadata_batch \
    --sample-queries-dir data/sample_queries \
    --table-metadata-dir data/table_metadata \
    --target-tables for_analysis_kikuchi_subscribe_all_list_comp_with_full_data \
    --target-tables allocation_settings \
    --target-tables tap_article_events \
    --target-tables show_article_events \
    --target-tables dynamodb.news
```

### 1.3.2. 　テーブルメタデータとサンプルクエリファイルを要約するオフラインバッチの実行

差分更新

```bash
uv run python -m my_text_to_sql_poc.app.generate_summary_batch \
    --table-metadata-dir data/table_metadata \
    --sample-queries-dir data/sample_queries \
    --output-table-summary-dir data/summarized_table \
    --output-query-summary-dir data/summarized_sample_query
```

全更新

```bash
uv run python -m my_text_to_sql_poc.app.generate_summary_batch \
    --table-metadata-dir data/table_metadata \
    --sample-queries-dir data/sample_queries \
    --output-table-summary-dir data/summarized_table \
    --output-query-summary-dir data/summarized_sample_query \
    --full-refresh
```

### 1.3.3. テーブル要約とクエリ要約を埋め込み表現に変換して、ベクトルストアに保存するオフラインバッチの実行

```bash
uv run python -m my_text_to_sql_poc.app.embed_summaries_batch \
    --table-summary-dir data/summarized_table \
    --query-summary-dir data/summarized_sample_query \
    --vectorstore-file sample_vectorstore.duckdb
```

### 1.3.4. Text2SQLアプリケーションの実行

```bash
uv run python src/my_text_to_sql_poc/presentation/text2sql_cli.py \
    --question "2023年の売上合計を知りたい" \
    --dialect SQLite \
    --log-level INFO
```

### 1.3.5. GUIアプリケーションの起動

```bash
uv run streamlit run src/my_text_to_sql_poc/presentation/streamlit_gui.py
```
