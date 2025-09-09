import typing
from pathlib import Path
from typing import Optional

from sema4ai.actions import Row
from sema4ai.data._models import ColumnInfo, KnowledgeBaseInfo, SourceInfo, TableInfo

if typing.TYPE_CHECKING:
    from sema4ai.data._result_set import ResultSet
    from sema4ai_http import ResponseWrapper

from robocorp import log


class _HttpConnectionHelper:
    """
    Helper class to manage connections to the http server.
    """

    def __init__(self, http_url: str, http_user: str, http_password: str) -> None:
        self._http_url = http_url
        self._http_user = http_user
        self._http_password = http_password
        self._session_headers: dict[str, str] = {}

    def login(self) -> None:
        import time
        from http.cookies import SimpleCookie

        import sema4ai_http

        login_url = f"{self._http_url}/api/login"

        login_response = sema4ai_http.post(
            login_url,
            json={"password": self._http_password, "username": self._http_user},
        )

        if login_response.status != 200:
            # 401 is Unauthorized (bad or expired credentials, no need to retry)
            if login_response.status != 401:
                # Retry once in case of another unexpected error
                time.sleep(0.2)
                login_response = sema4ai_http.post(
                    login_url,
                    json={"password": self._http_password, "username": self._http_user},
                )

            if login_response.status != 200:
                raise Exception(
                    f"Failed to login. Status: {login_response.status}. Data: {login_response.data.decode('utf-8', errors='backslashreplace')}"
                )

        cookies = SimpleCookie()
        session_cookies = {}
        if "set-cookie" in login_response.headers:
            cookies.load(login_response.headers["set-cookie"])
            session_cookies = {key: morsel.value for key, morsel in cookies.items()}
        cookie_header = "; ".join([f"{k}={v}" for k, v in session_cookies.items()])
        self._session_headers = {"Cookie": cookie_header}

    def _is_login_info_available(self) -> bool:
        return bool(self._http_user and self._http_password)

    def _login_if_needed(self) -> None:
        if not self._session_headers and self._is_login_info_available():
            self.login()

    def _execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute an operation with retry logic.

        Args:
            operation: The callable to execute
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            The result of the operation

        Raises:
            Exception: If the operation fails and login info is not available
        """
        self._login_if_needed()
        try:
            return operation(*args, **kwargs)
        except Exception:
            if not self._is_login_info_available():
                raise

            # Retry once with a new session
            self._session_headers = {}
            self._login_if_needed()
            return operation(*args, **kwargs)

    def upload_file(self, file_path: Path, table_name: str) -> None:
        self._execute_with_retry(self._upload_file, file_path, table_name)

    def _get_datasource_info(self, database_name: str) -> "ResponseWrapper":
        import sema4ai_http

        url = self._http_url + f"/api/databases/{database_name}"
        result = sema4ai_http.get(url, headers=self._session_headers)
        return result

    def _get_datasource_info_with_retry(self, database_name: str) -> "ResponseWrapper":
        return self._execute_with_retry(self._get_datasource_info, database_name)

    def _run_sql_with_retry(
        self, sql: str, database: str | None = None
    ) -> "ResponseWrapper":
        import time

        import sema4ai_http

        url = self._http_url + "/api/sql/query"

        result = sema4ai_http.post(
            url,
            json={"query": sql, "context": {"db": database or ""}},
            headers=self._session_headers,
        )

        if result.status != 200:
            if result.status == 401:  # Unauthorized (bad or expired credentials)
                # Try to login again
                self._session_headers = {}
                self._login_if_needed()
            else:
                # Another unexpected error (sleep a bit and retry)
                time.sleep(0.2)

            # Retry the request (once)
            result = sema4ai_http.post(
                url,
                json={"query": sql, "context": {"db": database or ""}},
                headers=self._session_headers,
            )

        return result

    def run_sql(
        self, sql: str, database: str | None = None
    ) -> tuple[list[str], list[Row]] | None:
        """
        Args:
            sql: The SQL query to execute.
            database: The database to use.

        Returns:
            A tuple of columns and rows or None if a table was not returned.
        """
        from sema4ai.actions import ActionError

        self._login_if_needed()

        result = self._run_sql_with_retry(sql, database)

        if result.status != 200:
            raise Exception(
                f"Failed to run sql. Status: {result.status}. Data: {result.data.decode('utf-8', errors='backslashreplace')}"
            )

        data = result.json()
        data_type = data["type"]
        if data_type == "table":
            columns: list[str] = [x for x in data["column_names"]]
            rows: list[Row] = data["data"]
            return columns, rows
        if data_type == "ok":
            return None
        if data_type == "error":
            log.critical(
                f"There was an error running the SQL query: {sql}.\n"
                f"Error: {data['error_message']}"
            )
            raise ActionError(
                f"There was an error running the query SQL. Error: {data['error_message']}"
            )

        log.critical(f"Unexpected sql result type: {data_type}")
        return None

    def _upload_file(self, file_path: Path, table_name: str) -> None:
        import json

        import sema4ai_http

        file_name = file_path.name
        data = file_path.read_bytes()
        result = sema4ai_http.put(
            f"{self._http_url}/api/files/{table_name}",
            fields={
                "file": (file_name, data),
                "data": json.dumps(
                    {
                        "original_file_name": file_name,
                        "name": table_name,
                        "source_type": "file",
                    }
                ).encode("utf-8"),
            },
            headers=self._session_headers,
        )
        if result.status != 200:
            raise Exception(
                f"Failed to upload file. Status: {result.status}. Data: {result.data.decode('utf-8', errors='backslashreplace')}"
            )


class DataServerConnection:
    def __init__(
        self,
        http_url: str,
        http_user: Optional[str],
        http_password: Optional[str],
        mysql_host: str,
        mysql_port: int,
        mysql_user: Optional[str],
        mysql_password: Optional[str],
    ):
        """
        Creates a connection to the data server.
        """
        # Not using mysql connection for now (had issues with pymysql not giving
        # errors when the connection was closed by the server).
        self._http_connection = _HttpConnectionHelper(
            http_url, http_user or "", http_password or ""
        )

    def query(
        self,
        query: str,
        params: Optional[dict[str, str | int | float] | list[str | int | float]] = None,
    ) -> "ResultSet":
        """
        API to execute a query and get the result set.

        Args:
            query: The SQL to execute.
            params: The parameters to pass to the query.

                If a list is provided, the parameters are used as positional parameters
                and `?` is used as placeholder.

                If a dict is provided, the parameters are used as named parameters
                and names such as `$key` are used as placeholders.

                Note: the parameters can only be used in the SQL for the replacement of regular variables,
                not for the datasource name (i.e.: it works when the escaping single or double quotes,
                but for datasource names must be escaped with backticks).

                Note: It's expected that the SQL is always using the full data source name (i.e.: `datasource_name.table_name`)
                and not just the table name (i.e.: `table_name`).

        Returns:
            The result set from the query.

        Example:
            result_set = datasource.query("SELECT * FROM `datasource_name`.my_table WHERE id = ?", [1])
            return Response(result=result_set.to_table())

            result_set = datasource.query("SELECT * FROM `datasource_name`.my_table WHERE id = $id", {"id": 1})
            return Response(result=result_set.to_table())
        """

        result = self.execute_sql(query, params)
        if result is None:
            raise RuntimeError(
                "Unexpected result from the data server (expected table but received just 'ok')"
            )
        return result

    def native_query(
        self,
        datasource_name: str,
        query: str,
        params: Optional[list[str | int | float] | dict[str, str | int | float]] = None,
    ) -> "ResultSet":
        """
        API to execute a query in a data source using the native SQL syntax for that data source and get the result set.

        Args:
            datasource_name: The name of the data source to use.
            query: The SQL to execute.
            params: The parameters to pass to the query.

                If a list is provided, the parameters are used as positional parameters
                and `?` is used as placeholder.

                If a dict is provided, the parameters are used as named parameters
                and names such as `$key` are used as placeholders.

                Note: the parameters can only be used in the SQL for the replacement of regular variables,
                not for the datasource name (i.e.: it works when the escaping single or double quotes,
                but for datasource names must be escaped with backticks).

                Note: It's expected that the SQL is always using the full data source name (i.e.: `datasource_name.table_name`)
                and not just the table name (i.e.: `table_name`).

        Returns:
            The result set from the query.

        Important:
            The escaping of the parameters is done by putting parameters in single quotes and escaping any
            single quotes in the parameters for `''` (i.e.: a string such as `O'Neill` would become `O''Neill`).
            If the native SQL syntax requires a different escaping, parameters should not be used and the SQL
            should be written without them.

        Example:
            result_set = datasource.native_query("datasource_name", "SELECT * FROM my_table WHERE id = ?", [1])
            return Response(result=result_set.to_table())

            result_set = datasource.native_query("datasource_name", "SELECT * FROM my_table WHERE id = $id", {"id": 1})
            return Response(result=result_set.to_table())
        """
        new_query = f"SELECT * FROM `{datasource_name}` ({query})"
        return self.query(new_query, params)

    def predict(
        self,
        query: str,
        params: Optional[dict[str, str | int | float] | list[str | int | float]] = None,
    ) -> "ResultSet":
        """
        API to execute a prediction and get the result set.

        Args:
            query: The SQL to execute.
            params: The parameters to pass to the query.

                If a list is provided, the parameters are used as positional parameters
                and `?` is used as placeholder.

                If a dict is provided, the parameters are used as named parameters
                and names such as `$key` are used as placeholders.

                Note: the parameters can only be used in the SQL for the replacement of regular variables,
                not for the datasource name (i.e.: it works when the escaping single or double quotes,
                but for datasource names must be escaped with backticks).

                Note: It's expected that the SQL is always using the full data source name (i.e.: `datasource_name.table_name`)
                and not just the table name (i.e.: `table_name`).

        Returns:
            The result set from the prediction.

        Example:
            result_set = datasource.predict("SELECT * FROM `datasource_name`.my_table WHERE id = ?", [1])
            return Response(result=result_set.to_table())

            result_set = datasource.predict("SELECT * FROM `datasource_name`.my_table WHERE id = $id", {"id": 1})
            return Response(result=result_set.to_table())

        Note: the only difference between `query()` and `predict()` is that `predict()` is expected to be used when
        querying a model.
        """

        log.warn("The `predict` method is deprecated. Use `query` instead.")
        return self.query(query, params)

    def execute_sql(
        self,
        sql: str,
        params: Optional[dict[str, str | int | float] | list[str | int | float]] = None,
    ) -> "ResultSet | None":
        """
        API to execute some SQL. Either it can return a result set (if it was a query) or None
        (if it was some other SQL command).

        Args:
            sql: The SQL to execute.
            params: The parameters to pass to the query.

                If a list is provided, the parameters are used as positional parameters
                and `?` is used as placeholder.

                If a dict is provided, the parameters are used as named parameters
                and names such as `$key` are used as placeholders.

                Note: the parameters can only be used in the SQL for the replacement of regular variables,
                not for the datasource name (i.e.: it works when the escaping single or double quotes,
                but for datasource names must be escaped with backticks).

                Note: It's expected that the SQL is always using the full data source name (i.e.: `datasource_name.table_name`)
                and not just the table name (i.e.: `table_name`).

        Returns:
            The result set if the SQL was a query or None if it was some other SQL command.

        Example:
            datasource.run_sql("UPDATE `datasource_name`.my_table SET name = 'John' WHERE id = 1")
        """
        from sema4ai.data._result_set import ResultSet
        from sema4ai.data._sql_handling import (
            build_query_from_dict_params,
            build_query_from_list_params,
        )

        if isinstance(params, list):
            query = build_query_from_list_params(sql, params)
        else:
            query = build_query_from_dict_params(sql, params)

        # For now, we don't support database names (scope is always global and
        # users need to specify the full data source name + table name in the
        # SQL being executed).
        database_name = ""
        result = self._http_connection.run_sql(query, database_name)
        if result is None:
            return None

        columns, rows = result
        return ResultSet(columns, rows)

    def list_data_sources(self) -> list[SourceInfo]:
        """
        List the data sources available to query.

        Returns:
            A table of the databases available to query.
        """

        result = self.query("select * from information_schema.databases;")

        return result.build_list(SourceInfo)

    def list_tables(self, database_name: str) -> list[TableInfo]:
        """
        List the tables available to query.

        Args:
            database_name: The name of the database

        Returns:
            A table of the tables available to query.
        """
        sql = """
            select * from information_schema.tables
            where table_schema = $database_name;
        """

        result = self.query(sql, params={"database_name": database_name})

        return result.build_list(TableInfo)

    def list_columns(self, database_name: str, table_name: str) -> list[ColumnInfo]:
        """
        List the columns in a table.

        Args:
            database_name: The name of the database
            table_name: The name of the table
        Returns:
            Json representation of the columns
        """
        sql = """
            select COLUMN_NAME, DATA_TYPE
            from information_schema.columns
            where table_name = $table_name
            and table_schema = $database_name
        """

        result = self.query(
            sql, params={"table_name": table_name, "database_name": database_name}
        )

        return result.build_list(ColumnInfo)

    def list_knowledge_bases(self) -> list[KnowledgeBaseInfo]:
        """
        Get all the knowledge bases that we know about.

        Returns:
            The knowledge bases.
        """

        result = self.query("select * from information_schema.knowledge_bases;")

        return result.build_list(KnowledgeBaseInfo)

    def list_vector_databases(self) -> list[SourceInfo]:
        """
        Get the vector databases that we know about.

        Returns:
            Table: The vector databases
        """

        sql = """
            select * from information_schema.databases
            where engine in ('pgvector', 'pinecone', 'chromadb');
        """

        result = self.query(sql)

        return result.build_list(SourceInfo)

    def _get_datasource_info(self, database_name: str) -> dict:
        """
        Get the datasource info for a database.

        Args:
            database_name: The name of the database

        Returns:
            The datasource info for the database.

        Raises:
            Exception: If the datasource info is not found.
        """
        response = self._http_connection._get_datasource_info_with_retry(database_name)
        if response.status_code != 200:
            raise Exception(
                f"Failed to datasource info. Status: {response.status}. Data: {response.data.decode('utf-8', errors='backslashreplace')}"
            )

        return response.json()
