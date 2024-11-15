import re
from pathlib import Path

import typer
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from loguru import logger

from my_text_to_sql_poc.app.generate_table_metadata_batch.model import TableMetadataSchema
from my_text_to_sql_poc.service.model_gateway import ModelGateway

app = typer.Typer()


# プロンプトの設定
METADATA_PROMPT_PATH = Path("prompts/generate_table_metadata_jp.txt")


def _find_related_queries(table_name: str, sample_queries_dir: Path) -> set[str]:
    """
    指定されたテーブルに関連するサンプルクエリを取得する関数。
    :param table_name: 関連クエリを検索するテーブル名
    :param sample_queries_dir: サンプルクエリのディレクトリ
    :return: 関連するクエリのリスト
    """
    related_queries = set()
    table_pattern = re.compile(rf"\b{table_name}\b", re.IGNORECASE)

    for query_file in sample_queries_dir.glob("*.sql"):
        query_str = query_file.read_text()
        if table_pattern.search(query_str):
            related_queries.add(query_str)

    return related_queries


def _generate_table_metadata(
    table_name: str,
    table_schema_dir: Path,
    sample_queries_dir: Path,
) -> str:
    """対象テーブルのスキーマ情報と、対象テーブルを利用してるサンプルクエリ達を元に、LLMにテーブルメタデータを生成させる"""
    logger.info(f"Processing table: {table_name}")
    related_sample_queries = _find_related_queries(table_name, sample_queries_dir)

    schema_data = (table_schema_dir / f"{table_name}.txt").read_text()

    output_parser = JsonOutputParser(pydantic_object=TableMetadataSchema)

    prompt_template_str = METADATA_PROMPT_PATH.read_text()
    prompt_template = PromptTemplate(
        template=prompt_template_str + "\n\n{format_instructions}",
        input_variables=["table_schema", "sample_queries"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    formatted_prompt = prompt_template.format(
        table_schema=schema_data,
        sample_queries="\n\n".join(related_sample_queries),
    )

    response_text = ModelGateway().generate_response(formatted_prompt)

    summary = response_text.replace("\\n", "\n")

    return summary


@app.command()
def main(
    table_schema_dir: Path = typer.Option(..., help="Directory containing the table schemas"),
    sample_queries_dir: Path = typer.Option(..., help="Directory containing sample queries"),
    table_metadata_dir: Path = typer.Option(..., help="Output directory for summarized table schemas"),
    full_refresh: bool = typer.Option(False, help="Force full refresh of all summaries"),
    log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
):
    # ログレベルを設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    # 出力ディレクトリが存在しない場合は作成
    if not table_metadata_dir.exists():
        table_metadata_dir.mkdir(parents=True)

    # 洗い替えモードの場合は、サマリ生成前にdocumentsの保存先を空にしておく
    logger.info(f"mode: {full_refresh=}")
    if full_refresh:
        for file in table_metadata_dir.glob("*.txt"):
            file.unlink()

    table_names = [f.stem for f in table_schema_dir.glob("*.txt")]
    for table_name in table_names:
        logger.info(f"Processing table: {table_name}")

        # 差分更新チェック: すでにサマリファイルが存在している場合はスキップ
        output_path = table_metadata_dir / f"{table_name}.txt"
        if not full_refresh and output_path.exists():
            logger.info(f"Summary for {table_name} already exists, skipping")
            continue

        table_metadata = _generate_table_metadata(
            table_name,
            table_schema_dir,
            sample_queries_dir,
        )
        output_path.write_text(table_metadata)


if __name__ == "__main__":
    app()
    # table_name = "show_article_events"
    # table_schema_dir = Path("data/schema")
    # sample_queries_dir = Path("data/sample_queries")
    # print(_generate_table_metadata(table_name, table_schema_dir, sample_queries_dir))
