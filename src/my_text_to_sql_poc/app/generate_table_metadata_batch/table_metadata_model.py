from pydantic import BaseModel, Field


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
