import os
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
import json
import logfire

from .database import BigQueryDatabase
from .models import (
    QueryParams,
    TableInfo,
    QueryResult,
    TableSchema,
    ErrorResponse,
    ToolResponse,
)
from .custom_server import CustomFastMCP

# Environment variables will be loaded in main()

logfire.info("Starting MCP BigQuery Server with Pydantic")

# Create CustomFastMCP server to avoid asyncio conflicts
server = CustomFastMCP("BigQuery Server")

# Global database instance
db = None


def validate_config(
    project: Optional[str] = None, location: Optional[str] = None
) -> tuple:
    """Validate configuration parameters.

    Args:
        project: Optional project ID from command line
        location: Optional location from command line

    Returns:
        Tuple of (project, location)
    """
    # Try command line args first, then environment variables
    project = project or os.getenv("BIGQUERY_PROJECT")
    location = location or os.getenv("BIGQUERY_LOCATION")

    if not project:
        raise ValueError(
            "Project ID is required. Provide it via --project argument or BIGQUERY_PROJECT environment variable."
        )
    if not location:
        raise ValueError(
            "Location is required. Provide it via --location argument or BIGQUERY_LOCATION environment variable."
        )

    return project, location


@server.tool()
async def execute_query(query: str) -> str:
    """Execute a SELECT query on the BigQuery database.

    Args:
        query: SQL query to execute using BigQuery dialect

    Returns:
        Query results as a formatted string
    """
    logfire.debug("Tool called: execute_query", query=query)

    try:
        # Validate that db is initialized
        if not db:
            logfire.error("Database not initialized")
            return json.dumps(
                ErrorResponse(
                    error="Database not initialized",
                    details="Server was not properly initialized with project and location",
                ).dict()
            )

        # Create query params and execute
        params = QueryParams(query=query)
        result = await db.execute_query(params)

        logfire.info("Query executed successfully", query=query)

        # Return formatted result
        return json.dumps(result.dict(), indent=2)

    except Exception as e:
        logfire.error("Error executing query", exception=e, query=query)
        return json.dumps(ErrorResponse.from_exception(e).dict())


@server.tool()
async def list_tables() -> str:
    """List all tables in the BigQuery database.

    Returns:
        List of tables as a formatted string
    """
    logfire.debug("Tool called: list_tables")

    try:
        # Validate that db is initialized
        if not db:
            logfire.error("Database not initialized")
            return json.dumps(
                ErrorResponse(
                    error="Database not initialized",
                    details="Server was not properly initialized with project and location",
                ).dict()
            )

        # Get tables
        tables = await db.list_tables()

        # Convert to dict for JSON serialization
        tables_dict = [table.dict() for table in tables]

        logfire.info("Tables listed successfully", table_count=len(tables_dict))

        # Return formatted result
        return json.dumps(tables_dict, indent=2)

    except Exception as e:
        logfire.error("Error listing tables", exception=e)
        return json.dumps(ErrorResponse.from_exception(e).dict())


@server.tool()
async def describe_table(table_name: str) -> str:
    """Get the schema information for a specific table.

    Args:
        table_name: Name of the table to describe (e.g. my_dataset.my_table)

    Returns:
        Table schema as a formatted string
    """
    logfire.debug("Tool called: describe_table", table_name=table_name)

    try:
        # Validate that db is initialized
        if not db:
            logfire.error("Database not initialized")
            return json.dumps(
                ErrorResponse(
                    error="Database not initialized",
                    details="Server was not properly initialized with project and location",
                ).dict()
            )

        # Get table schema
        schema = await db.describe_table(table_name)

        logfire.info("Table schema retrieved successfully", table_name=table_name)

        # Return formatted result
        return json.dumps(schema.dict(), indent=2)

    except Exception as e:
        logfire.error("Error describing table", exception=e, table_name=table_name)
        return json.dumps(ErrorResponse.from_exception(e).dict())


async def main(
    project: Optional[str] = None,
    location: Optional[str] = None,
    datasets_filter: List[str] = None,
    env_file: Optional[str] = None,
):
    """Main entry point for the server.

    Args:
        project: Optional project ID from command line
        location: Optional location from command line
        datasets_filter: Optional list of datasets to filter by
        env_file: Optional path to .env file
    """
    global db

    try:
        logfire.info("Initializing BigQuery MCP Server")

        # Load environment variables
        if env_file:
            logfire.info("Loading environment variables", env_file=env_file)
            load_dotenv(env_file)
        else:
            logfire.info("Loading environment variables from default .env file")
            load_dotenv()

        # Validate configuration
        project, location = validate_config(project, location)
        logfire.info("Configuration validated", project=project, location=location)

        if datasets_filter:
            logfire.info("Using dataset filter", datasets=datasets_filter)

        # Initialize database
        db = BigQueryDatabase(project, location, datasets_filter)
        logfire.info("Database initialized")

        # Run server
        logfire.info("Starting server", project=project, location=location)
        # The current version of logfire might not have the Context class
        # with logfire.Context(project=project, location=location):
        server.run()

    except Exception as e:
        logfire.error("Error starting server", exception=e)
        raise
