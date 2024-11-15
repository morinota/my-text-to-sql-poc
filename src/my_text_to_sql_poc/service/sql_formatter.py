from typing import Optional

import sqlfluff
from sqlfluff.core.config import FluffConfig


# SQLクエリをフォーマットする関数
def format_sql_query(
    sql_query: str,
    dialect: str,
    custom_config: Optional[dict] = None,
) -> str:
    # 改行コードを変換
    linebroken_sql_query = sql_query.replace("\n", " ")

    # デフォルトの設定
    default_config = {
        "core": {"dialect": dialect.lower()},
        "layout": {"type": {"comma": {"line_position": "trailing"}}},
        "indentation": {"indented_joins": False, "indented_using_on": True, "template_blocks_indent": False},
        # "capitalisation": {"keywords": "lower", "identifiers": "lower", "functions": "lower"},
    }
    if custom_config:
        default_config.update(custom_config)

    # FluffConfigオブジェクトを作成
    fluff_config = FluffConfig(configs=default_config)
    print(fluff_config.get("dialect"))

    # SQLフォーマッターを実行
    formatted_sql = sqlfluff.fix(
        linebroken_sql_query,
        config=fluff_config,
    )
    return formatted_sql
