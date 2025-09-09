from pathlib import Path
from typing import Any, Callable, Optional, overload

from robocorp import log

from ._data_server_connection import DataServerConnection
from ._data_source import DataSource
from ._data_source_spec import DataSourceSpec
from ._models import ColumnInfo, KnowledgeBaseInfo, SourceInfo, TableInfo
from ._result_set import ResultSet
from ._snowflake import get_snowflake_connection_details

__version__ = "1.0.9"
version_info = [int(x) for x in __version__.split(".")]


@overload
def query(func: Callable) -> Callable: ...


@overload
def query(
    *, is_consequential: Optional[bool] = None, display_name: Optional[str] = None
) -> Callable: ...


def query(*args, **kwargs):
    """
    Decorator for queries which can be executed by `sema4ai.actions`.

    i.e.:

    If a file such as actions.py has the contents below:

    ```python
    from sema4ai.data import query, DataSource

    @query
    def query_invoices(date: str, datasource: DataSource) -> list[str]:
        ...
    ```

    Note that a query needs sema4ai actions to be executed.
    The command line to execute it is:

    python -m sema4ai.actions run actions.py -a query_invoices

    Args:
        func: A function which is a query to `sema4ai.data`.
        is_consequential: Whether the action is consequential or not.
            This will add `x-openai-isConsequential: true` to the action
            metadata and shown in OpenApi spec.
        display_name: A name to be displayed for this action.
            If given will be used as the openapi.json summary for this action.
    """
    from sema4ai.actions import action

    kwargs["kind"] = "query"
    return action(*args, **kwargs)


@overload
def predict(
    *, is_consequential: Optional[bool] = None, display_name: Optional[str] = None
) -> Callable: ...


@overload
def predict(func: Callable) -> Callable: ...


def predict(*args, **kwargs):
    """
    Decorator for predictions based on data models which can be executed by `sema4ai.actions`.

    i.e.:

    If a file such as actions.py has the contents below:

    ```python
    from sema4ai.data import predict, DataSource

    @predict
    def cashflow_prediction(scenario: str, datasource: DataSource) -> list[str]:
        ...
    ```

    Note that a prediction needs sema4ai actions to be executed.
    The command line to execute it is:

    python -m sema4ai.actions run actions.py -a cashflow_prediction

    Args:
        func: A function which is a prediction to `sema4ai.data`.
        is_consequential: Whether the action is consequential or not.
            This will add `x-openai-isConsequential: true` to the action
            metadata and shown in OpenApi spec.
        display_name: A name to be displayed for this action.
            If given will be used as the openapi.json summary for this action.
    """
    from sema4ai.actions import action

    log.warn("The @predict decorator is deprecated. Use `@query` or `@action` instead.")
    kwargs["kind"] = "predict"
    return action(*args, **kwargs)


def metadata(package_root: Path) -> dict:
    """
    Returns something like this:
    {
        // This is added by sema4ai-data
        'data_spec_version': 'v2',
        'data': {
            'datasources': [
                {
                    'name': 'datasource-name',
                    'engine': 'sqlite',
                    'description': 'description of the datasource',
                    'setup_sql': ['sql-to-execute'],
                    'defined_at': {
                        'file': 'relative/path/to/definition_file.py',
                        'line': 123,
                    },

                    # Only for files engine
                    'file': 'path/to/definition_file.py',  # Relative to package root.
                    'created_table': 'name-of-created-table',

                    # Only if a model is created (prediction engine or custom engine)
                    'model_name': 'name-of-model',

                },
                ...
            ]
        },
    }
    """
    from sema4ai.data._data_source_spec import (
        _global_internal_data_server_datasources_spec_instances,
    )

    ret: dict[str, Any] = {}
    datasources: list[dict[str, Any]] = []
    for (
        dataserver_datasource_spec
    ) in _global_internal_data_server_datasources_spec_instances:
        datasources.append(dataserver_datasource_spec.get_metadata(package_root))

    ret["data"] = {"datasources": datasources}
    ret["data_spec_version"] = "v2"
    return ret


def get_connection() -> "DataServerConnection":
    """
    Returns a connection to the data server.

    Usually it's recommended to use the `DataSource` as a parameter in the @query/@predict,
    but if needed, this method can also be used to get the configured connection.
    """
    from sema4ai.data._data_source import ConnectionNotSetupError

    from ._data_source import _ConnectionHolder

    try:
        return _ConnectionHolder.connection()
    except ConnectionNotSetupError as e:
        # Let's see if we can auto-setup the connection now.

        # This is not public for external use, but from internal use it's ok for now.
        from sema4ai.actions._action import get_current_requests_contexts

        ctx = get_current_requests_contexts()
        if not ctx:
            # We can't auto-setup the connection if there's no context.
            raise e

        data_context = ctx.data_context
        if data_context:
            DataSource.setup_connection_from_data_context(data_context)
            try:
                return _ConnectionHolder.connection()
            except ConnectionNotSetupError:
                pass

        # If it's still not setup, try to setup from env vars.
        DataSource.setup_connection_from_env_vars()
        try:
            return _ConnectionHolder.connection()
        except ConnectionNotSetupError:
            pass

        # Unable to auto-setup the connection, just raise the original error.
        raise e


__all__ = [
    "query",
    "predict",
    "metadata",
    "DataSource",
    "ResultSet",
    "DataSourceSpec",
    "get_connection",
    "get_snowflake_connection_details",
    "SourceInfo",
    "TableInfo",
    "ColumnInfo",
    "KnowledgeBaseInfo",
]
