"""Routes for the Datascribe API.

This module defines the API endpoints and their corresponding models for the Datascribe API.
"""

from datascribe_api.models import (
    DataTableColumns,
    DataTableMetadata,
    DataTableRows,
    DataTableRowsCount,
    DataTables,
)

ROUTES = {
    "get_data_tables": ("/data-tables", DataTables, []),
    "get_data_table": ("/data-table", DataTableRows, ["tableName"]),
    "get_data_tables_for_user": ("/data-tables-for-user", DataTables, []),
    "get_data_table_rows": ("/data-table-rows", DataTableRows, ["tableName", "columns"]),
    "get_data_table_columns": ("/data-table-columns", DataTableColumns, ["tableName"]),
    "get_data_table_metadata": ("/data-table-metadata", DataTableMetadata, ["tableName"]),
    "get_data_table_rows_count": ("/data-table-rows-count", DataTableRowsCount, ["tableName"]),
}
