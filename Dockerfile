# 公式のuv入りベースイメージ！Python 3.11 + uv がセットになってて便利✨
FROM ghcr.io/astral-sh/uv:0.6.14-python3.13-bookworm-slim

# 作業ディレクトリを作成
WORKDIR /app

# poetryと同じノリで依存解決するために必要なファイルをコピー
COPY pyproject.toml uv.lock README.md ./

# 依存関係インストール！速い！シンプル！
RUN uv sync --frozen

# アプリのコードをコピー
COPY src/ ./src/

# MCPサーバーのエントリーポイントを起動
CMD ["uv", "--directory", ".", "run", "src/my_text_to_sql_poc/app/text2sql/text2sql_mcp_server.py"]
