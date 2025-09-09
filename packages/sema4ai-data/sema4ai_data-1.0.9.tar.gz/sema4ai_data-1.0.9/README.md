# ⚡️ sema4ai-data

Python library to develop data packages for Sema4.ai. Build powerful data-driven actions that can query databases and work with various data sources.
This library is designed to work with `Sema4.ai Data Server`, which is included in the [Sema4.ai Data Access](https://marketplace.visualstudio.com/items?itemName=sema4ai.sema4ai-data-access) VSCode extension.


## Installation

```bash
pip install sema4ai-data
```

## Quick Start

```python
from typing import Annotated
from sema4ai.data import query, DataSource, DataSourceSpec
from sema4ai.actions import Response, Table

# Define a data source
PostgresDataSource = Annotated[DataSource, DataSourceSpec(
    name="my_postgres_db",
    engine="postgres",
    description="Main PostgreSQL database"
)]

# Create a data query
@query
def get_users(datasource: PostgresDataSource, limit: int = 10) -> Response[Table]:
    """Get users from the database."""
    result = datasource.query("SELECT * FROM `my_postgres_db`.users LIMIT 5", [limit])
    return Response(result=result.to_table())
```

## Core Concepts

### DataSource

The `DataSource` class is the main interface for executing queries against configured data sources. It's automatically injected by the framework when you use the `@query` decorator.

**Key Methods:**
- `query(sql, params=None)` - Execute SQL queries with optional parameters
- `native_query(sql, params=None)` - Execute engine-specific queries
- `connection()` - Get the underlying data server connection

### DataSourceSpec

Used to specify the configuration of a data source through type annotations:

```python
from typing import Annotated
from sema4ai.data import DataSource, DataSourceSpec

# Database data source
DatabaseSource = Annotated[DataSource, DataSourceSpec(
    name="my_database",
    engine="postgres",  # or "mysql", "sqlite", etc.
    description="Production database"
)]

# File-based data source
FileSource = Annotated[DataSource, DataSourceSpec(
    engine="files",
    file="data/customers.csv",
    created_table="customers",
    description="Customer data from CSV"
)]

# Knowledge base for semantic search
KnowledgeBaseSource = Annotated[DataSource, DataSourceSpec(
    name="company_kb",
    engine="sema4_knowledge_base",
    description="Company knowledge base for semantic search"
)]
```

**Parameters:**
- `engine` (required) - The data source engine type
- `name` - Name of the data source
- `description` - Human-readable description
- `file` - File path for file-based sources
- `created_table` - Table name created from files
- `setup_sql` - SQL commands to run on setup
- `setup_sql_files` - SQL files to execute on setup

## Decorators

### @query

The main decorator for creating data queries that can be executed by sema4ai actions:

```python
from sema4ai.data import query
from sema4ai.actions import Response, Table

@query
def get_countries(datasource: PostgresCustomersDataSource) -> str:
    sql = """
        SELECT distinct(country)
        FROM public_demo.demo_customers
        LIMIT 100;
    """

    result = datasource.query(sql)
    return result.to_markdown()
```

**Parameters:**
- `is_consequential` - Whether the action has side effects or updates a resource (default: False)
- `display_name` - Custom display name for the action

### @predict ⚠️ **DEPRECATED**

**Note**: The `@predict` decorator is deprecated as of version 1.0.3. Use `@query` instead for all operations including predictions.

```python
# OLD (deprecated):
@predict
def predict_something(datasource: SomeDataSource):
    pass

# NEW (recommended):
@query
def predict_something(datasource: SomeDataSource):
    pass
```

### ResultSet

The `ResultSet` class represents query results and provides various methods to work with the data:

```python
# Convert to different formats
result = datasource.query("SELECT * FROM `my_database`.users")

# As a table for actions
table = result.to_table()

# As a list of dictionaries
dicts = result.to_dict_list()

# As structured objects
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

users = result.build_list(User)

# Iterate over results
for row_dict in result.iter_as_dicts():
    print(row_dict)

for row_tuple in result.iter_as_tuples():
    print(row_tuple)
```

#### Basic Database Query

```python
from typing import Annotated
from pydantic import BaseModel
from sema4ai.data import query, DataSource, DataSourceSpec
from sema4ai.actions import Response

class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str

ProductDB = Annotated[DataSource, DataSourceSpec(
    name="products",
    engine="postgres",
    description="Product catalog database"
)]

@query
def search_products(
    category: str,
    max_price: float,
    datasource: ProductDB
) -> Response[list[Product]]:
    """Search products by category and price."""
    result = datasource.query(
        """
        SELECT id, name, price, category
        FROM products.products
        WHERE category = ? AND price <= ?
        ORDER BY price ASC
        """,
        [category, max_price]
    )
    return Response(result=result.build_list(Product))
```

#### File-based Data Source

```python
SalesData = Annotated[DataSource, DataSourceSpec(
    engine="files",
    file="data/sales_2024.csv",
    created_table="sales",
    description="Sales data for 2024"
)]

@query
def monthly_sales_report(
    month: int,
    datasource: SalesData
) -> Response[Table]:
    """Generate monthly sales report."""
    result = datasource.query(
        """
        SELECT
            product_category,
            SUM(amount) as total_sales,
            COUNT(*) as transaction_count
        FROM files.sales
        WHERE MONTH(sale_date) = ?
        GROUP BY product_category
        ORDER BY total_sales DESC
        """,
        [month]
    )
    return Response(result=result.to_table())
```

#### Knowledge Base Search

```python
KnowledgeBase = Annotated[DataSource, DataSourceSpec(
    name="company_kb",
    engine="sema4_knowledge_base",
    description="Company knowledge base for semantic search"
)]

@query
def search_knowledge(
    query_text: str,
    relevance_threshold: float = 0.7,
    datasource: KnowledgeBase
) -> Response[Table]:
    """Search company knowledge base."""
    result = datasource.query(
        """
        SELECT chunk_content, relevance_score, document_name
        FROM company_kb
        WHERE content = ? AND relevance_threshold = ?
        ORDER BY relevance_score DESC
        LIMIT 5
        """,
        [query_text, relevance_threshold]
    )
    return Response(result=result.to_table())
```

#### Using native_query for Engine-Specific Syntax

```python
@query
def get_user_by_id(
    user_id: int,
    datasource: MyDataSource
) -> Response[Table]:
    """Get user using native SQL syntax."""
    # Uses engine-specific syntax, automatically wrapped
    result = datasource.native_query(
        "SELECT * FROM user_info WHERE id = $id",
        {"id": user_id}
    )
    return Response(result=result.to_table())
```

## API Reference

### Functions

#### `query(func=None, *, is_consequential=None, display_name=None)`
Decorator for creating query actions.

#### `predict(func=None, *, is_consequential=None, display_name=None)` ⚠️ **DEPRECATED**
**Deprecated**: Use `@query` instead. This decorator is deprecated as of version 1.0.3.

#### `get_connection() -> DataServerConnection`
Get a connection to the data server.

#### `metadata(package_root: Path) -> dict`
Get metadata about data sources in a package.

#### `get_snowflake_connection_details()`
Get Snowflake-specific connection configuration.

### Classes

#### `DataSource`
Main interface for executing queries against data sources.

**Methods:**
- `query(sql: str, params: list = None) -> ResultSet`
- `native_query(sql: str, params: dict = None) -> ResultSet`
- `connection() -> DataServerConnection`

**Properties:**
- `datasource_name: str` - Name of the data source

#### `DataSourceSpec`
Configuration specification for data sources.

#### `ResultSet`
Container for query results with conversion methods.

**Methods:**
- `to_table() -> Table` - Convert to sema4ai Table
- `to_dict_list() -> list[dict]` - Convert to list of dictionaries
- `build_list(item_class: type[T]) -> list[T]` - Build typed object list
- `iter_as_dicts() -> Iterator[dict]` - Iterate as dictionaries
- `iter_as_tuples() -> Iterator[tuple]` - Iterate as tuples
- `to_pandas_df() -> pd.DataFrame` - Convert to pandas DataFrame
- `to_markdown_table() -> str` - Convert to markdown table

### Data Models

#### `SourceInfo`
Information about a data source configuration.

#### `TableInfo`
Metadata about database tables.

#### `ColumnInfo`
Information about table columns.

#### `KnowledgeBaseInfo`
Metadata about knowledge base configurations.

## Changelog

## Unreleased

## 1.0.9 - 2025-09-08

- Implement `_get_datasource_info` private method on `DataServerConnection` class

## 1.0.8 - 2025-08-21

- CVE updates
- Expose the underlying SQL error when running an query

## 1.0.7 - 2025-07-28

- Improve readme and add changelog when publishing to pypi

## 1.0.6 - 2025-06-18

- Simplify error message on `run_sql` function call.

## 1.0.5 - 2025-05-20

- Allow extra fields in `sf-auth.json` without changing behaviour of `get_snowflake_connection_details`.

## 1.0.4 - 2025-05-13

- Add `sema4_knowledge_base` engine to support knowledge base as a data source

## 1.0.3 - 2025-04-24

- Add deprecation warning for `@predict` decorator and `DataServerConnection.predict` method as Lightwood is being
  phased out for data server predictions. Use `@query` or `connection.query()` instead.
- Update to latest `sema4ai-actions` version

## 1.0.2 - 2025-03-06

- Fix Snowflake local auth file path for Windows

## 1.0.1 - 2025-02-28

- Fix to the private key passphrase hanling

## 1.0.0 - 2025-02-25

- Add `private_key_file_pwd` to snowflake connection details when it exists in auth config file
- `SnowflakeAuthenticationError` now inherits from `ActionError`.

## 0.1.0 - 2025-02-18

- Added `native_query()` method which will automatically wrap the query in a `SELECT * FROM <datasource_name> (<query>)` clause
  so that the query can be executed in the native SQL syntax of the data source instead of the syntax required by
  the data server.
- If no parameters are provided, the query is returned as is (even if parameters are detected in the query -- added so that
  the user can do the escaping themselves if needed if the SQL syntax accepts the parameters in a different way).

## 0.0.9 - 2025-02-14

- Correct the local authentication JSON file path for Snowflake in get_snowflake_connection_details

## 0.0.8 - 2025-02-14

- Add `get_snowflake_connection_details` helper function to get the connection details for Snowflake.

## 0.0.7 - 2025-02-06

- Corrected typo in `ColumInfo`.
- Updated `list_knowledge_bases` method to return `KnowledgeBaseInfo`.

## 0.0.6 - 2025-01-31

- Add data utilitary methods to `DataServerConnection`

## 0.0.5 - 2024-12-20

- Added `execute_sql()` to the `DataSource` class.

## 0.0.4 - 2024-12-19

- New utility methods for the `ResultSet` class:
  - `to_dataframe()` (alias for `as_dataframe`)
  - `to_table()` (creates a `Table` object that can be used to build a structured response)
  - `to_dict_list()` (returns a list of dictionaries)
  - `__iter__()` (same as `iter_as_dicts`)
  - `__len__()`
- Retry login if the server returns a 401 error.
- Retry SQL requests (once) if the server returns an unexpected error (as it may be a transient error).
- Added `sema4ai.data.get_connection()` to get the configured connection to the data server.
- **Backward incompatible change**: The queries/predictions must always use the full data source name to access a table and not just the table name
  regardless of the data source name configured in the `DataSourceSpec`.
  i.e.: SQL like `SELECT * FROM my_datasource.my_table` is required instead of `SELECT * FROM my_table`.

## 0.0.3 - 2024-11-27

- Using REST API instead of PyMySQL.
- ResultSet APIs (provisional):
  - `iter_as_dicts()` (new in 0.0.3)
  - `iter_as_tuples()` (new in 0.0.3)
  - `as_dataframe()` (new in 0.0.1)
  - `build_list(item_class)` (new in 0.0.1)
  - `to_markdown()` (new in 0.0.1)

## 0.0.2 - 2024-11-25

- Changed metadata format to have `_` instead of `-` in names.
- Made `defined_at/file` in metadata relative.
- Added support for `setup_sql_files` in `DataSourceSpec`.
- Default datasource named `models` is used for custom and prediction engines.

## 0.0.1 - 2024-11-18

- Initial release
- Added API:
  - `from sema4ai.data import query` to mark function as `@query`
  - `from sema4ai.data import predict` to mark function as `@predict`
  - `from sema4ai.data import DataSource` to define a data source
  - `from sema4ai.data import DataSourceSpec` to define a data source specification using an `Annotated` type

## License

See [LICENSE](LICENSE) - Sema4.ai End User License Agreement
