# uv公式のベースイメージを使用しておく
FROM ghcr.io/astral-sh/uv:0.6.14-python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

# 依存関係のみをinstall
# レイヤーを分けておいた方が、コード変更時に依存関係インストールをやり直さなくて済むので
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY src/ ./src/

# プロジェクトをinstall
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

CMD ["uv", "--directory", ".", "run", "src/my_text_to_sql_poc/app/text2sql/text2sql_mcp_server.py"]
