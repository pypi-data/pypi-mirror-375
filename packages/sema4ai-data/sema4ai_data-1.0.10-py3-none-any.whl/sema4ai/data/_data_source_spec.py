import typing
from pathlib import Path
from typing import Any, Literal, Optional

_global_internal_data_server_datasources_spec_instances: list["DataSourceSpec"] = []


JSONValue = typing.Union[
    dict[str, "JSONValue"], list["JSONValue"], list[str], str, int, float, bool, None
]


def _get_datasource_metadata_from_annotation_args(tp) -> dict[str, Any]:
    from sema4ai.actions._exceptions import ActionsCollectError

    error_message = """
Invalid DataSource annotation found.

The DataSource must always be annotated with a DataSourceSpec:
(i.e.: `Annotated[DataSource, DataSourceSpec(name="datasource_name", engine="postgres")]`) 
"""
    annotation_args = typing.get_args(tp)
    if not annotation_args or len(annotation_args) != 2:
        raise ActionsCollectError(error_message)

    datasource_spec = annotation_args[1]
    if datasource_spec.__class__.__name__ != "DataSourceSpec":
        raise ActionsCollectError(
            f"Second parameter in Annotation of DataSource is not a DataSourceSpec.\n{error_message}"
        )

    return datasource_spec.get_metadata()


_CUSTOM_ENGINE_NAMES = (
    "prediction:lightwood",  # Special use case: we know this maps to a lightwood prediction model
    "custom",  # Anything we don't really expect (that can be configured with custom SQL) should be here
    "mindsdb",  # Special use case: we know this maps to the `mindsdb` pre-configured project.
    # All the other engines are supported by the data server and are queried with:
    # SHOW HANDLERS WHERE type = 'data'
)

_DATASOURCES_ENGINE_NAMES = (
    "access",
    "aerospike",
    "airtable",
    "altibase",
    "apache_doris",
    "aqicn",
    "athena",
    "aurora",
    "bigquery",
    "binance",
    "cassandra",
    "chromadb",
    "ckan",
    "clickhouse",
    "cloud_spanner",
    "cloud_sql",
    "cockroachdb",
    "coinbase",
    "confluence",
    "couchbasevector",
    "couchbase",
    "crate",
    "d0lt",
    "databend",
    "databricks",
    "astra",
    "db2",
    "derby",
    "discord",
    "dockerhub",
    "documentdb",
    "dremio",
    "druid",
    "duckdb",
    "dummy_data",
    "dynamodb",
    "edgelessdb",
    "elasticsearch",
    "email",
    "empress",
    "eventbrite",
    "eventstoredb",
    "faunadb",
    "files",
    "financial_modeling_prep",
    "firebird",
    "frappe",
    "gcs",
    "github",
    "gitlab",
    "gmail",
    "google_analytics",
    "google_books",
    "google_calendar",
    "google_content_shopping",
    "google_fit",
    "google_search",
    "greptimedb",
    "hackernews",
    "hana",
    "hive",
    "hsqldb",
    "hubspot",
    "ignite",
    "impala",
    "influxdb",
    "informix",
    "ingres",
    "instatus",
    "intercom",
    "jira",
    "kinetica",
    "lancedb",
    "libsql",
    "lightdash",
    "lindorm",
    "luma",
    "mariadb",
    "materialize",
    "matrixone",
    "maxdb",
    "mediawiki",
    "mendeley",
    "milvus",
    "monetdb",
    "mongodb",
    "mssql",
    "teams",
    "mysql",
    "newsapi",
    "notion",
    "npm",
    "nuo_jdbc",
    "oceanbase",
    "oilpriceapi",
    "openbb",
    "opengauss",
    "openstreetmap",
    "oracle",
    "orioledb",
    "paypal",
    "pgvector",
    "phoenix",
    "pinecone",
    "pinot",
    "pirateweather",
    "plaid",
    "planet_scale",
    "postgres",
    "pypi",
    "qdrant",
    "questdb",
    "quickbooks",
    "reddit",
    "redshift",
    "rocket_chat",
    "rockset",
    "s3",
    "salesforce",
    "sap_erp",
    "scylladb",
    "sendinblue",
    "serpstack",
    "sharepoint",
    "sheets",
    "shopify",
    "singlestore",
    "slack",
    "snowflake",
    "solace",
    "solr",
    "sqlany",
    "sqlite",
    "sqreamdb",
    "starrocks",
    "strapi",
    "strava",
    "stripe",
    "supabase",
    "surrealdb",
    "symbl",
    "tdengine",
    "teradata",
    "tidb",
    "timescaledb",
    "trino",
    "tripadvisor",
    "twilio",
    "twitter",
    "vertica",
    "vitess",
    "weaviate",
    "webz",
    "web",
    "whatsapp",
    "xata",
    "youtube",
    "yugabyte",
    "zendesk",
    "zipcodebase",
    "zotero",
    "sema4_knowledge_base",
)

_VALID_ENGINE_NAMES = _CUSTOM_ENGINE_NAMES + _DATASOURCES_ENGINE_NAMES


class DataSourceSpec:
    def __init__(
        self,
        *,
        engine: str,
        name: Optional[
            Literal[
                "prediction:lightwood",  # Special use case: we know this maps to a lightwood prediction model
                "custom",  # Anything we don't really expect (that can be configured with custom SQL) should be here
                "models",  # Special use case: we know this maps to the `models` pre-configured data source.
                "files",  # Special use case: we know this maps to the `files` pre-configured data source.
                # All the other engines are supported by the data server and are queried with:
                # SHOW HANDLERS WHERE type = 'data'
                "access",
                "aerospike",
                "airtable",
                "altibase",
                "apache_doris",
                "aqicn",
                "athena",
                "aurora",
                "bigquery",
                "binance",
                "cassandra",
                "chromadb",
                "ckan",
                "clickhouse",
                "cloud_spanner",
                "cloud_sql",
                "cockroachdb",
                "coinbase",
                "confluence",
                "couchbasevector",
                "couchbase",
                "crate",
                "d0lt",
                "databend",
                "databricks",
                "astra",
                "db2",
                "derby",
                "discord",
                "dockerhub",
                "documentdb",
                "dremio",
                "druid",
                "duckdb",
                "dummy_data",
                "dynamodb",
                "edgelessdb",
                "elasticsearch",
                "email",
                "empress",
                "eventbrite",
                "eventstoredb",
                "faunadb",
                "financial_modeling_prep",
                "firebird",
                "frappe",
                "gcs",
                "github",
                "gitlab",
                "gmail",
                "google_analytics",
                "google_books",
                "google_calendar",
                "google_content_shopping",
                "google_fit",
                "google_search",
                "greptimedb",
                "hackernews",
                "hana",
                "hive",
                "hsqldb",
                "hubspot",
                "ignite",
                "impala",
                "influxdb",
                "informix",
                "ingres",
                "instatus",
                "intercom",
                "jira",
                "kinetica",
                "lancedb",
                "libsql",
                "lightdash",
                "lindorm",
                "luma",
                "mariadb",
                "materialize",
                "matrixone",
                "maxdb",
                "mediawiki",
                "mendeley",
                "milvus",
                "monetdb",
                "mongodb",
                "mssql",
                "teams",
                "mysql",
                "newsapi",
                "notion",
                "npm",
                "nuo_jdbc",
                "oceanbase",
                "oilpriceapi",
                "openbb",
                "opengauss",
                "openstreetmap",
                "oracle",
                "orioledb",
                "paypal",
                "pgvector",
                "phoenix",
                "pinecone",
                "pinot",
                "pirateweather",
                "plaid",
                "planet_scale",
                "postgres",
                "pypi",
                "qdrant",
                "questdb",
                "quickbooks",
                "reddit",
                "redshift",
                "rocket_chat",
                "rockset",
                "s3",
                "salesforce",
                "sap_erp",
                "scylladb",
                "sendinblue",
                "serpstack",
                "sharepoint",
                "sheets",
                "shopify",
                "singlestore",
                "slack",
                "snowflake",
                "solace",
                "solr",
                "sqlany",
                "sqlite",
                "sqreamdb",
                "starrocks",
                "strapi",
                "strava",
                "stripe",
                "supabase",
                "surrealdb",
                "symbl",
                "tdengine",
                "teradata",
                "tidb",
                "timescaledb",
                "trino",
                "tripadvisor",
                "twilio",
                "twitter",
                "vertica",
                "vitess",
                "weaviate",
                "webz",
                "web",
                "whatsapp",
                "xata",
                "youtube",
                "yugabyte",
                "zendesk",
                "zipcodebase",
                "zotero",
                "sema4_knowledge_base",
            ]
        ] = None,
        created_table: Optional[str] = None,
        model_name: Optional[str] = None,
        file: Optional[str] = None,
        description: str = "",
        setup_sql: Optional[str | list[str]] = None,
        setup_sql_files: Optional[str | list[str]] = None,
    ):
        import sys

        if not engine:
            raise ValueError(
                "'engine' of the datasource must be set (some common values: 'postgres', 'files', 'prediction:lightwood', 'redshift')"
            )

        if engine == "files":
            if not name:
                name = "files"

        if engine.startswith("prediction:") or name == "custom":
            if not name:
                name = "models"

        self.name = name
        self.engine = engine
        self.created_table = created_table
        self.model_name = model_name
        self.file = file
        self.description = description
        self.setup_sql = setup_sql
        frame = sys._getframe(1)
        self.__defined_at_file = frame.f_code.co_filename
        self.__defined_at_line = frame.f_lineno
        self.setup_sql_files = setup_sql_files

        self._validate()

        _global_internal_data_server_datasources_spec_instances.append(self)

    def _validate(self):
        import os.path

        if not self.name:
            raise ValueError("'name' of the datasource must be set")

        if not self.engine:
            raise ValueError(
                "'engine' of the datasource must be set (some common values: 'postgres', 'files', 'prediction:lightwood', 'redshift')"
            )

        if not self.description:
            raise ValueError("'description' of the datasource must be set")

        if self.engine == "files":
            if self.name != "files":
                raise ValueError("'name' must be 'files' for the 'files' engine")

            if not self.created_table:
                raise ValueError("'created_table' must be set for the 'files' engine")

            if not self.file:
                raise ValueError("'file' must be set for the 'files' engine")

            if os.path.isabs(self.file):
                raise ValueError("'file' must be a relative path")

        if self.engine not in _VALID_ENGINE_NAMES:
            raise ValueError(
                f"Invalid engine: {self.engine} (note: consider using 'custom' if it's not a pre-defined supported engine and it's configured with SQL). Valid engines are: {_VALID_ENGINE_NAMES}"
            )

        if self.engine in _CUSTOM_ENGINE_NAMES:
            if not self.setup_sql and not self.setup_sql_files:
                raise ValueError(
                    f"The engine: {self.engine} requires a 'sql' to be set (which will be executed to create the datasource/table)"
                )
            if self.setup_sql and self.setup_sql_files:
                raise ValueError(
                    "It's not possible to use both 'setup_sql' and 'setup_sql_files' parameters together"
                )

            if self.setup_sql_files:
                if not isinstance(self.setup_sql_files, list):
                    raise ValueError(
                        f"'setup_sql_files' must be a list of file paths (relative to the package root). Found: {type(self.setup_sql_files)}"
                    )

                for setup_sql_file in self.setup_sql_files:
                    if os.path.isabs(setup_sql_file):
                        raise ValueError(
                            f"'setup_sql_files' must contain relative paths (relative to the package root). Found absolute path: {setup_sql_file}"
                        )
        else:
            if self.setup_sql or self.setup_sql_files:
                raise ValueError(
                    f"The engine: {self.engine} does not support the 'sql' parameter (only {_CUSTOM_ENGINE_NAMES} engines support it)"
                )

        if self.engine.startswith("prediction:"):
            if not self.model_name:
                raise ValueError(
                    f"The engine: {self.engine} requires a 'model_name' to be set"
                )

        if self.created_table:
            for char in ["'", '"', "`", ";"]:
                if char in self.created_table:
                    raise ValueError(
                        f"created_table name must not contain character: {char}"
                    )
        if self.model_name:
            for char in ["'", '"', "`", ";"]:
                if char in self.model_name:
                    raise ValueError(f"model_name must not contain character: {char}")

    def get_metadata(self, package_root: Path) -> dict[str, JSONValue]:
        try:
            defined_at_file = (
                Path(self.__defined_at_file).relative_to(package_root).as_posix()
            )
        except Exception:
            defined_at_file = Path(self.__defined_at_file).as_posix()

        ret: dict[str, JSONValue] = {
            "name": self.name,
            "engine": self.engine,
            "description": self.description,
            "defined_at": {
                "file": defined_at_file,
                "line": self.__defined_at_line,
            },
        }
        if self.created_table:
            ret["created_table"] = self.created_table
        if self.model_name:
            ret["model_name"] = self.model_name
        if self.file:
            ret["file"] = self.file
        if self.setup_sql:
            if isinstance(self.setup_sql, str):
                ret["setup_sql"] = [self.setup_sql]
            else:
                assert isinstance(self.setup_sql, list)
                ret["setup_sql"] = self.setup_sql
        if self.setup_sql_files:
            # If we have a setup_sql_files, we'll read those files and use the content as setup_sql
            sqls: list[str] = []
            for setup_sql_file in self.setup_sql_files:
                setup_sql_files_path = package_root / setup_sql_file
                try:
                    sqls.append(Path(setup_sql_files_path).read_text(encoding="utf-8"))
                except Exception:
                    raise ValueError(
                        f"Failed to read setup_sql_files content from: {setup_sql_file} -- resolved path: {setup_sql_files_path}"
                    )
            ret["setup_sql"] = sqls

        return ret
