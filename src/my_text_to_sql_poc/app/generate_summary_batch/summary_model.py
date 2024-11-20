from pydantic import BaseModel, Field


class TableSummary(BaseModel):
    name: str = Field(description="テーブル名")
    summary: str = Field(description="テーブルの概要")
    utilization: str = Field(
        description="テーブルの利用状況。そのテーブルがどのような質問に答えられるか、そのテーブルでどのような分析ができるか、など"
    )
    potential_usecases: str = Field(description="テーブルの潜在的な利用用途")


class SQLQuerySummary(BaseModel):
    purposes: str = Field(description="クエリの目的や意図を詳細に記載")
    selected_columns: str = Field(description="クエリ内で選択されてるカラムとその概要")
    input_tables: str = Field(description="クエリ内で使用されてるテーブルとその概要")
    detailed_transformation_logics: str = Field(description="クエリ内で行われてるデータ加工の詳細")
