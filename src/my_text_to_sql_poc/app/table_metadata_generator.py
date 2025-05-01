import typer
from langchain_core.prompts import PromptTemplate
from loguru import logger
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway
from my_text_to_sql_poc.service.repository import (
    DuckDBSampleQueryRepository,
    DuckDBTableMetadataRepository,
    SampleQueryRepositoryInterface,
    TableMetadataRepositoryInterface,
)

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


class TableMetadataGenerator:
    def __init__(
        self,
        table_metadata_repo: TableMetadataRepositoryInterface = DuckDBTableMetadataRepository(
            "/tmp/table_metadata_store.duckdb"
        ),
        sample_query_repo: SampleQueryRepositoryInterface = DuckDBSampleQueryRepository(
            "/tmp/sample_query_store.duckdb"
        ),
    ):
        self._table_metadata_repo = table_metadata_repo
        self._sample_query_repo = sample_query_repo
        self._prompt_template = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["table_name", "audit_logs", "reffered_doc"],
        )

    def generate_table_metadata(
        self,
        table_name: str,
        reffered_doc: str | None = None,
    ) -> None:
        """
        対象テーブルを利用してるサンプルクエリ達と、関連ドキュメントを元にテーブルのメタデータを生成し、DuckDBに保存する
        """
        reffered_query_map = self._sample_query_repo.retrieve_by_table_name(table_name)
        logger.info(
            f"""
            対象テーブル {table_name} を利用しているサンプルクエリが {len(reffered_query_map)} 件見つかりました。
            (LLM呼び出しのtoken数制限に引っかかるのを避けるため、サンプルクエリは最大100件までプロンプトに含めます)
            """
        )

        reffered_querys = list(reffered_query_map.values())[0:100]
        formatted_prompt = self._prompt_template.format(
            table_name=table_name,
            audit_logs="\n\n".join(reffered_querys),
            reffered_doc=reffered_doc,
        )

        table_metadata = ModelGateway().generate_response_with_structured_output(
            formatted_prompt,
            TableMetadataSchema,
        )
        logger.info(f"Generated table metadata: {table_metadata.model_dump_json(indent=2)}")

        self._table_metadata_repo.put(table_name, table_metadata.model_dump_json(indent=2))


app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def main(
    target_table: list[str] = typer.Option(
        ...,
        help="""
        LLMにSQLクエリ履歴からメタデータを生成させたいテーブル名を指定する。複数テーブルを同時に指定可能。
        指定方法: --target-table table_name1 --target-table table_name2 --target-table table_name3
        """,
    ),
):
    table_metadata_generator = TableMetadataGenerator()
    for table_name in target_table:
        logger.info(f"=============={table_name}のテーブルメタデータを生成します=================")
        table_metadata_generator.generate_table_metadata(table_name=table_name)
        logger.info(f"=============={table_name}のテーブルメタデータを生成しました===============")


if __name__ == "__main__":
    app()
