from pathlib import Path

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway

PROMPT_TEMPLATE = """
あなたはSQLテーブルの良質なメタデータを生成するデータアナリストです。

以下のテーブルのメタデータを推定して。

===テーブル名
{table_name}

===テーブルが利用されている過去のSQLクエリの実行ログ
{audit_logs}

===テーブルやカラムの説明を記述したドキュメント
{reffered_doc}

===応答ガイドライン

- テーブルやカラムの説明文は日本語で記載してください
- 提供された情報に基づいてメタデータを生成してください。
- 低cardinalityの場合はカラムの値の種類も推定・記載してください。
- 過去のSQLクエリの実行ログを参考に、テーブルの利用例を示すサンプルクエリを記載してください。
- サンプルクエリには、他テーブルとjoinして使う例も必ず2つは含めてください。
- サンプルSQLクエリは以下の文化に則って可読性を重視してください。
  - クエリ内のキーワードは全て小文字で記述すること。
  - クエリ内のテーブル名、カラム名は適切なエイリアスを使用すること。
  - シンプルな例の場合は必ずしもCTEを使用する必要はない。もしクエリ内でCTEを使う場合は、適切にインデントすること。
  - CTEの名前は必ずprefixとして_を付与すること。
  - 基本的にはサブクエリよりもCTEを使用すること。
  - 可読性を重視して積極的に改行 & インデントを行うこと。
  - 積極的にコメントを使用してCTEやクエリの目的を説明すること。
"""


class ColumnMetadataSchema(BaseModel):
    column_name: str = Field(description="カラム名")
    column_type: str = Field(description="カラムのデータ型")
    summary: str = Field(description="カラムの概要。低cardinalityの場合はカラムの値の種類も記載して")


class SampleQuerySchema(BaseModel):
    query: str = Field(description="テーブルの使用方法の例を示すサンプルクエリ")
    summary: str = Field(description="サンプルクエリの概要")


class TableMetadataSchema(BaseModel):
    table_name: str = Field(description="テーブル名")
    summary: str = Field(description="テーブルの概要")
    columns: list[ColumnMetadataSchema] = Field(description="カラム情報")
    sample: list[SampleQuerySchema] = Field(
        description="テーブルの使用方法の例を示すサンプルクエリ達。他テーブルとjoinして使う例も必ず1つは含めて。最低4つ以上。"
    )


def generate_table_metadata(
    table_name: str,
    related_queries: list[str] = [],
    reffered_doc: str = "",
) -> TableMetadataSchema:
    """対象テーブルを利用してるサンプルクエリ達と、関連ドキュメントを元にテーブルのメタデータを生成する"""
    prompt_template_str = PROMPT_TEMPLATE
    prompt_template = PromptTemplate(
        template=prompt_template_str,
        input_variables=["table_name", "audit_logs", "reffered_doc"],
    )

    formatted_prompt = prompt_template.format(
        table_name=table_name,
        audit_logs="\n\n".join(related_queries),
        reffered_doc=reffered_doc,
    )

    return ModelGateway().generate_response_with_structured_output(formatted_prompt, TableMetadataSchema)


if __name__ == "__main__":
    # Arrange
    table_name = "for_analysis_kikuchi_subscribe_all_list_comp_with_full_data"
    sample_queries_dir = Path("data/sample_queries")
    reffered_doc_path = Path(f"data/kikuchi_table_docs/{table_name}.csv")
    sample_queris = [file.read_text() for file in sample_queries_dir.glob("*.sql")]
    related_queries = [query for query in sample_queris if table_name in query]
    print(related_queries)
    reffered_doc = reffered_doc_path.read_text()
    print(reffered_doc)

    # Act
    table_metadata = generate_table_metadata(
        table_name,
        related_queries[0:100],  # input tokenのサイズ制限のため、100件までにしておく
        reffered_doc,
    )

    # Assert
    metadata_json = table_metadata.model_dump_json(indent=2)
    print(metadata_json)
    Path(f"temp_table_metadata_{table_name}.json").write_text(metadata_json)
