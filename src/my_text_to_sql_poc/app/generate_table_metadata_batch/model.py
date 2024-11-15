from pydantic import BaseModel


class ColumnMetadataSchema(BaseModel):
    column_name: str
    column_type: str
    column_description: str


class TableMetadataSchema(BaseModel):
    table_name: str
    table_description: str
    columns: list[ColumnMetadataSchema]
