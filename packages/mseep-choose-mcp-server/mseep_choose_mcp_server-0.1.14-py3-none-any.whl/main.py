import os
import json
import datetime
from typing import AsyncIterator
from dataclasses import dataclass
from contextlib import asynccontextmanager
from google.cloud import bigquery
from mcp.server.fastmcp import FastMCP, Context


PROJECT_ID = os.getenv("PROJECT_ID")
DATASETS = os.getenv("DATASETS").split(",") if os.getenv("DATASETS") else [os.getenv("DATASET")] 
DBT_MANIFEST_FILEPATH = os.getenv("DBT_MANIFEST_FILEPATH")


@dataclass
class AppContext:
    client: bigquery.Client


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    client = bigquery.Client(project=PROJECT_ID)
    yield AppContext(client=client)


mcp = FastMCP("Choose MCP Server", lifespan=app_lifespan)


@mcp.tool()
def load_documentation(ctx: Context) -> str:
    """
    Load the documentation of all tables.

    Returns:
        str: The full documentation of all tables. Key is the table name, value is the description.
    """
    if DBT_MANIFEST_FILEPATH:
        try:
            with open(DBT_MANIFEST_FILEPATH, "r") as fh:
                manifest = json.load(fh)
                nodes = manifest["nodes"]
                return json.dumps({f"{nodes[v]['schema']}.{v.split('.')[2]}": nodes[v]["description"] for _, v in enumerate(manifest["nodes"]) if nodes[v]["schema"] in DATASETS}, indent=2)
        except Exception as e:
            return f"Error: {str(e)}. Please check the DBT manifest file path and try again."
    else:
        return "No documentation found."


@mcp.tool()
def get_tables(ctx: Context) -> str:
    """
    Get the list of tables in the database.

    Returns:
        str: The list of tables in the database, prefixed by the dataset name.
    """
    client = ctx.request_context.lifespan_context.client

    tables = []

    for dataset in DATASETS:
        query = f"SELECT table_name FROM `{PROJECT_ID}.{dataset}.INFORMATION_SCHEMA.TABLES`"
        query_job = client.query(query)
        results = query_job.result()
        tables.extend([f"{dataset}.{row.table_name}" for row in results])
    
    return ", ".join(tables)


@mcp.tool()
def get_table_schema(ctx: Context, dataset: str, table: str) -> str:
    """
    Get the schema of a table in the database, along with the description of each available field.
    
    Args:
        dataset (str): The name of the dataset.
        table (str): The name of the table in the database, prefixed with the dataset.

    Returns:
        str: The schema of the table in the database.
    """
    client = ctx.request_context.lifespan_context.client
    query = f"SELECT ddl FROM `{PROJECT_ID}.{dataset}.INFORMATION_SCHEMA.TABLES` WHERE table_name = @table"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("table", "STRING", table)
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    for row in results:
        return row.ddl
    return f"Table {table} not found"


@mcp.tool()
def query(ctx: Context, query: str) -> str:
    """
    Execute a SQL query against BigQuery and get back the result as dict.
    Input to this tool is a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    If you encounter an issue with Unknown column 'xxxx' in 'field list', use get_table_schema to query the correct table fields.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        query_job = client.query(query)
        results = [dict(row.items()) for row in query_job.result()]
        return str(results)
    except Exception as e:
        return f"Error: Query failed. {str(e)}. Please rewrite the query, check the query, and try again."


@mcp.tool()
def fetch_current_time() -> str:
    """
    Fetch the current time in UTC.

    Returns:
        str: The current time in UTC.
    """
    return datetime.datetime.now().isoformat()


def run():
    """
    Run the MCP server.
    """
    mcp.run()


if __name__ == "__main__":
    run()