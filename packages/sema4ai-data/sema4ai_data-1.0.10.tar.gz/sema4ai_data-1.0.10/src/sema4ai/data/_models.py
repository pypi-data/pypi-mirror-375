import json

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


def parse_json_string(v) -> dict | None:
    if isinstance(v, str):
        return json.loads(v)
    return v


class SourceInfo(BaseModel):
    name: Annotated[str, Field(description="The name of the data source", alias="NAME")]
    type: Annotated[str, Field(description="The type of the data source", alias="TYPE")]
    engine: Annotated[
        str | None, Field(description="The engine of the data source", alias="ENGINE")
    ] = None
    connection_data: Annotated[
        dict | None,
        BeforeValidator(parse_json_string),
        Field(
            description="The connection data of the data source",
            alias="CONNECTION_DATA",
        ),
    ] = None


class TableInfo(BaseModel, extra="allow"):
    table_schema: Annotated[
        str, Field(description="The schema of the table", alias="TABLE_SCHEMA")
    ]
    table_name: Annotated[
        str, Field(description="The name of the table", alias="TABLE_NAME")
    ]
    table_type: Annotated[
        str, Field(description="The type of the table", alias="TABLE_TYPE")
    ]
    engine: Annotated[
        str | None, Field(description="The engine of the table", alias="ENGINE")
    ] = None
    version: Annotated[
        int | None, Field(description="The version of the table", alias="VERSION")
    ] = None
    table_rows: Annotated[
        int, Field(description="The estimated number of rows", alias="TABLE_ROWS")
    ]
    create_time: Annotated[
        str, Field(description="The creation timestamp", alias="CREATE_TIME")
    ]
    update_time: Annotated[
        str, Field(description="The last update timestamp", alias="UPDATE_TIME")
    ]


class ColumnInfo(BaseModel):
    column_name: Annotated[
        str, Field(description="The name of the column", alias="COLUMN_NAME")
    ]
    data_type: Annotated[
        str, Field(description="The data type of the column", alias="DATA_TYPE")
    ]


class KnowledgeBaseInfo(BaseModel):
    name: Annotated[
        str, Field(description="The name of the knowledge base", alias="NAME")
    ]
    project: Annotated[
        str, Field(description="The project of the knowledge base", alias="PROJECT")
    ]
    embedding_model: Annotated[
        dict | None,
        BeforeValidator(parse_json_string),
        Field(
            description="The embedding model of the knowledge base",
            alias="EMBEDDING_MODEL",
        ),
    ] = None
    reranking_model: Annotated[
        dict | None,
        BeforeValidator(parse_json_string),
        Field(
            description="The reranking model of the knowledge base",
            alias="RERANKING_MODEL",
        ),
    ] = None
    storage: Annotated[
        str | None,
        Field(description="The storage of the knowledge base", alias="STORAGE"),
    ] = None
    metadata_columns: Annotated[
        list[str] | None,
        BeforeValidator(parse_json_string),
        Field(
            description="The metadata columns of the knowledge base",
            alias="METADATA_COLUMNS",
        ),
    ] = None
    content_columns: Annotated[
        list[str] | None,
        BeforeValidator(parse_json_string),
        Field(
            description="The content columns of the knowledge base",
            alias="CONTENT_COLUMNS",
        ),
    ] = None
    id_column: Annotated[
        str | None,
        Field(description="The id column of the knowledge base", alias="ID_COLUMN"),
    ] = None
    parameters: Annotated[
        dict | None,
        BeforeValidator(parse_json_string),
        Field(
            description="The knowledge base parameters",
            alias="PARAMS",
        ),
    ] = None
