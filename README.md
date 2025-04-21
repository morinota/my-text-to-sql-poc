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
    --question "コンテンツごとの課金獲得数を知りたい" \
    --dialect SQLite \
    --log-level INFO
```

### 1.3.5. GUIアプリケーションの起動

```bash
uv run streamlit run src/my_text_to_sql_poc/presentation/streamlit_gui.py
```

### 1.3.6. DockerコンテナでText2SQL MCPサーバーを起動

以下の手順でDockerコンテナを使用してText2SQL MCPサーバーを起動できます。

1. Dockerイメージをビルドしておく。

```bash
cd path/to/my-text-to-sql-poc
docker build -t text2sql-mcp .
```

2. 環境変数 `OPENAI_API_KEY` を設定しておく(OpenAIの埋め込みモデルを利用するため。すでに設定済みの場合は不要)。

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

3. 一旦Dockerコンテナをrunできることを確認しておく

```bash
docker run -it --rm \
  -e OPENAI_API_KEY \
  -e AWS_PROFILE=newspicks-development \
  -v /Users/masato.morita/.aws:/root/.aws \
  text2sql-mcp
```

4. settings.jsonに必要な設定を追加します。

```json
"mcp": {
        "inputs": [],
        "servers": {
            // MCPサーバー名は任意の名前でOK
            "text2sql-docker-mcp-server": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "-e",
                    "OPENAI_API_KEY",
                    "-e",
                    "AWS_PROFILE=newspicks-development",
                    "-v", // ホストのAWS認証情報をコンテナにマウント
                    "/Users/masato.morita/.aws:/root/.aws",
                    "text2sql-mcp"
                ],
                "env": {}
            }
        }
    }
```

4. VSCodeのコマンドパレットやGUIなどから、startを実行して、MCPサーバーを起動します。
5. これでGihub Copilot Agentが、Text2SQL MCPサーバーを利用できるようになるはずです。

試しに、以下のような質問を投げてみてください。これでツール呼んでくれなかったらまた教えてください。

```text
#sym:text2sql-docker-mcp-server 各コンテンツ経由の課金獲得数を集計するSQLクエリ書いて!
```

