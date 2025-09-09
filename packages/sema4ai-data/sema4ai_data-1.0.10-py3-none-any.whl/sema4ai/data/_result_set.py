import typing
from typing import Any, Iterator

from sema4ai.actions import Row, RowValue, Table

if typing.TYPE_CHECKING:
    import pandas as pd


T = typing.TypeVar("T")


class ResultSet:
    """
    The `ResultSet` is the result of a query.

    The preferred approach is to do a query and then use the `ResultSet`
    to create the structured response that is returned to the LLM by using
    `build_list`.

    Example:

        ```python
        from pydantic import BaseModel
        from sema4ai.actions import Response
        from sema4ai.data import query
        from data_sources import MyDataSource

        class User(BaseModel):
            id: int
            name: str
            email: str

        @query
        def query_users(datasource: MyDataSource) -> Response[list[User]]:
            result_set = datasource.query("SELECT * FROM users")
            return Response(result=result_set.build_list(User))
        ```

    If filtering is required, one can either improve the SQL to filter the data
    (preferred) or filter the result set after it's been returned from the data source
    by iterating over the result set and filtering the rows.

    Example:

        ```python
        from pydantic import BaseModel
        from sema4ai.actions import Response
        from sema4ai.data import query
        from data_sources import MyDataSource

        class User(BaseModel):
            id: int
            name: str
            email: str

        @query
        def query_users(datasource: MyDataSource) -> Response[list[User]]:
            result_set = datasource.query("SELECT * FROM users")
            users_list = [User(**row) for row in result_set if "John" in row["name"]]
            return Response(result=users_list)
        ```

    Another alternative if the shape of the return is not known is to use the `Table`
    class to return a generic structured response.

    Example:

        ```python
        from sema4ai.actions import Response, Table
        from sema4ai.data import query
        from data_sources import MyDataSource


        @query
        def query_users(datasource: MyDataSource) -> Response[Table]:
            result_set = datasource.query("SELECT * FROM users")
            return Response(result=result_set.to_table())
        ```

    The class also has other utility methods to convert the result set to a pandas
    DataFrame (for deeper analysis if needed) or a markdown table (for inspecting
    the result set in the console).

    Note: many methods when converting to a new data type may not really copy the
    data, but rather return a new object that references the same data. This means
    that changing the original result set after it's been converted to a new data type
    may also change the new data type and vice-versa.
    """

    def __init__(self, columns: list[str], rows: list[Row]):
        self._columns = columns
        self._data = rows

    def to_dataframe(self) -> "pd.DataFrame":
        """
        Converts the result set to a pandas DataFrame.

        It's usually not recommended to use this method, unless analysis
        from pandas are actually required (for just returning a value to the
        LLM, it's better to use `build_list` with a structure class -- if the
        shape of the return is known or `to_table` for a generic structured response)
        """
        import pandas as pd

        return pd.DataFrame(self._data, columns=self._columns)

    # Alias for backwards compatibility
    as_dataframe = to_dataframe

    def to_markdown(self) -> str:
        """
        Converts the result set to a markdown table.

        Note: in general it's not recommended to return a markdown table to the LLM,
        instead use the `Table` class for a generic structured response
        (as it allows further structured processing).

        Ideally though, it's recommended to create a custom class and use
        `build_list` to build a list of objects from the result set.
        """
        # Note: str(Table) is expected to return a markdown table!
        return str(self.to_table())

    def __len__(self) -> int:
        """
        Returns the number of rows in the result set.
        """
        return len(self._data)

    def __iter__(self) -> Iterator[dict[str, RowValue]]:
        """
        Iterates over the result set as a list of dictionaries.
        """
        return self.iter_as_dicts()

    def to_table(self) -> Table:
        """
        Converts the result set to a Table.

        Note: changing the columns or rows of the result set after it's been
        converted to a Table will affect the Table and vice-versa.
        """
        return Table(columns=self._columns, rows=self._data)

    def iter_as_dicts(self) -> Iterator[dict[str, RowValue]]:
        """
        Iterates over the result set as a list of dictionaries.

        Note: each dictionary is a row in the result set where
        the keys are the column names and the values are the row values.
        """
        for row in self._data:
            yield dict(zip(self._columns, row))

    def to_dict_list(self) -> list[dict[str, RowValue]]:
        """
        Converts the result set to a list of dictionaries

        Note: each dictionary is a row in the result set where
        the keys are the column names and the values are the row values.
        """
        return list(self.iter_as_dicts())

    def iter_as_tuples(self) -> Iterator[tuple[Any, ...]]:
        """
        Iterates over the result set values as a list of tuples.
        """
        for row in self._data:
            yield tuple(row)

    def build_list(self, item_class: type[T]) -> list[T]:
        """
        Builds a list of objects of the given class from the result set.

        Args:
            item_class: The class to build the list of.

        Returns:
            A list of objects of the given class.

        Note: The class must have a constructor that accepts each item in the
        result set as keyword arguments.

        Example:

            ```python
            from pydantic import BaseModel
            from sema4ai.actions import Response
            from sema4ai.data import query
            from data_sources import MyDataSource

            class User(BaseModel):
                id: int
                name: str
                email: str

            @query
            def query_users(datasource: MyDataSource) -> Response[list[User]]:
                result_set = datasource.query("SELECT * FROM users")
                return Response(result=result_set.build_list(User))
            ```
        """
        return [item_class(**row) for row in self]
