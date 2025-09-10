"""DataScribe CLI - A command-line interface for interacting with the DataScribe API."""

import re
from typing import Annotated

import typer
from rich import print as pretty_print
from rich.panel import Panel

from datascribe_api import DataScribeClient
from datascribe_api.filter import Filter

app = typer.Typer(help="DataScribe CLI - Interact with the DataScribe API.", pretty_exceptions_show_locals=False)


def handle_error(e: Exception) -> None:
    """Handle errors by printing them to the console.

    Args:
        e (Exception): The exception to handle.
    """
    pretty_print(Panel(renderable=f"{e}", title="Error", title_align="left", border_style="red"))


def parse_filter_string(filter_str: str) -> Filter:
    """Parse a filter string into a Filter object."""
    m = re.match(r"^(\w+)\s+(is not null|is null)$", filter_str, re.IGNORECASE)
    if m:
        col, op = m.groups()
        if op.lower() == "is null":
            return Filter(col).is_null()
        else:
            return Filter(col).is_not_null()

    m = re.match(r"^(\w+)\s+(not in|in)\s+([\w.,-]+)$", filter_str, re.IGNORECASE)
    if m:
        col, op, values = m.groups()
        values_list = [v.strip() for v in values.split(",") if v.strip()]
        if op.lower() == "in":
            return Filter(col).in_(values_list)
        else:
            return Filter(col).not_in(values_list)

    m = re.match(r"^(\w+)\s+(ilike|like)\s+(.+)$", filter_str, re.IGNORECASE)
    if m:
        col, op, val = m.groups()
        if op.lower() == "like":
            return Filter(col).like(val)
        elif op.lower() == "ilike":
            return Filter(col).ilike(val)

    m = re.match(r"^(\w+)(==|=|!=|>=|<=|>|<)(.+)$", filter_str)
    if m:
        col, op, val = m.groups()
        val = val.strip()
        if op in ("==", "="):
            return Filter(col) == val
        elif op == "!=":
            return Filter(col) != val
        elif op == ">":
            return Filter(col) > val
        elif op == ">=":
            return Filter(col) >= val
        elif op == "<":
            return Filter(col) < val
        elif op == "<=":
            return Filter(col) <= val
    raise ValueError(f"Invalid filter syntax: {filter_str}")


@app.command("data-tables")
def data_tables(
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display all available data tables."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            for table in client.get_data_tables():
                if json:
                    typer.echo(table.model_dump_json())
                else:
                    pretty_print(table)
    except Exception as e:
        handle_error(e)


@app.command("data-table")
def data_table(
    table_name: Annotated[str, typer.Argument(help="Name of the data table.", show_default=False)],
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    starting_row: Annotated[int, typer.Option("--starting-row", "-s", help="Starting row index for pagination.")] = 0,
    num_rows: Annotated[int, typer.Option("--num-rows", "-n", help="Number of rows to retrieve.")] = 100,
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display a specific data table."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            table = client.get_data_table(tableName=table_name, startingRow=starting_row, numRows=num_rows)
            if json:
                typer.echo(table.model_dump_json())
            else:
                pretty_print(table)
    except Exception as e:
        handle_error(e)


@app.command("data-tables-for-user")
def data_tables_for_user(
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display all data tables that the authenticated user has access to."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            for table in client.get_data_tables_for_user():
                if json:
                    typer.echo(table.json())
                else:
                    pretty_print(table)
    except Exception as e:
        handle_error(e)


@app.command("data-table-rows")
def data_table_rows(
    table_name: Annotated[str, typer.Argument(help="Name of the data table.", show_default=False)],
    columns: Annotated[str, typer.Argument(help="Comma-separated list of columns.")],
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    starting_row: Annotated[int, typer.Option("--starting-row", "-s", help="Starting row index for pagination.")] = 0,
    num_rows: Annotated[int, typer.Option("--num-rows", "-n", help="Number of rows to retrieve.")] = 100,
    filter_: Annotated[list[str], typer.Option("--filter", help="Filter expression. Can be used multiple times.")] = [],
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display rows from a specified data table, allowing you to specify which columns to include. Filtering is supported using --filter."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            cols = columns.split(",")
            filters = [parse_filter_string(f) for f in filter_] if filter_ else None
            for row in client.get_data_table_rows(
                tableName=table_name, columns=cols, startingRow=starting_row, numRows=num_rows, filters=filters
            ):
                if json:
                    typer.echo(row.model_dump_json())
                else:
                    pretty_print(row)
    except Exception as e:
        handle_error(e)


@app.command("data-table-columns")
def data_table_columns(
    table_name: Annotated[str, typer.Argument(help="Name of the data table.", show_default=False)],
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display the columns of a specified data table."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            columns = client.get_data_table_columns(tableName=table_name)
            if json:
                typer.echo(columns.model_dump_json())
            else:
                pretty_print(columns)
    except Exception as e:
        handle_error(e)


@app.command("data-table-metadata")
def data_table_metadata(
    table_name: Annotated[str, typer.Argument(help="Name of the data table.", show_default=False)],
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display metadata for a specified data table."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            metadata = client.get_data_table_metadata(tableName=table_name)
            if json:
                typer.echo(metadata.model_dump_json())
            else:
                pretty_print(metadata)
    except Exception as e:
        handle_error(e)


@app.command("data-table-rows-count")
def data_table_rows_count(
    table_name: Annotated[str, typer.Argument(help="Name of the data table.", show_default=False)],
    api_key: Annotated[str, typer.Option(envvar="DATASCRIBE_API_TOKEN", show_default=False, help="Your DataScribe API key.")],
    filter_: Annotated[list[str], typer.Option("--filter", help="Filter expression. Can be used multiple times.")] = [],
    json: Annotated[bool | None, typer.Option("--json", help="Output in JSON format.")] = None,
) -> None:
    """Retrieve and display the number of rows in a specified data table. Filtering is supported using --filter."""
    try:
        with DataScribeClient(api_key=api_key) as client:
            filters = [parse_filter_string(f) for f in filter_] if filter_ else None
            count = client.get_data_table_rows_count(tableName=table_name, filters=filters)
            if json:
                typer.echo(count.model_dump_json())
            else:
                pretty_print(count)
    except Exception as e:
        handle_error(e)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Default command that displays the help message."""
    typer.echo(ctx.get_help())


if __name__ == "__main__":
    app(prog_name="datascribe-cli")
