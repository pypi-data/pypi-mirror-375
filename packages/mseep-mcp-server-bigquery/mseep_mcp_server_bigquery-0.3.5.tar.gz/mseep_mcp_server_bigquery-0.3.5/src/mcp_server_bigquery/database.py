from google.cloud import bigquery
from typing import List, Dict, Any, Optional
import asyncio
from functools import wraps
import logfire

from .models import QueryParams, TableInfo, QueryResult, TableSchema, ErrorResponse


def async_wrap(func):
    """Decorator to convert a synchronous function to asynchronous."""

    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return run


class BigQueryDatabase:
    """Database class for interacting with BigQuery using Pydantic models."""

    def __init__(self, project: str, location: str, datasets_filter: List[str] = None):
        """Initialize a BigQuery database client with validation.

        Args:
            project: The GCP project ID
            location: The GCP location (e.g., 'us-central1')
            datasets_filter: Optional list of datasets to filter by
        """
        if not project:
            raise ValueError("Project is required")
        if not location:
            raise ValueError("Location is required")

        self.client = bigquery.Client(project=project, location=location)
        self.datasets_filter = datasets_filter or []
        self.project = project
        self.location = location

        logfire.info("Initialized BigQuery client", project=project, location=location)
        if self.datasets_filter:
            logfire.info("Filtering to datasets", datasets=self.datasets_filter)

    async def execute_query(self, params: QueryParams) -> QueryResult:
        """Execute a SQL query with proper validation and error handling.

        Args:
            params: QueryParams object containing the query and optional parameters

        Returns:
            QueryResult object containing the query results
        """
        logfire.debug("Executing query", query=params.query)

        try:
            # Convert parameters to BigQuery format if provided
            job_config = None
            if params.params:
                query_parameters = [
                    bigquery.ScalarQueryParameter(
                        name, self._get_param_type(value), value
                    )
                    for name, value in params.params.items()
                ]
                job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)

            # Execute query
            results = await self._execute_query(params.query, job_config)
            rows = [dict(row.items()) for row in results]

            logfire.debug("Query returned rows", count=len(rows))
            return QueryResult.from_rows(rows)

        except Exception as e:
            logfire.error("Error executing query", exception=e, query=params.query)
            raise

    async def list_tables(self) -> List[TableInfo]:
        """List all tables with proper typing.

        Returns:
            List of TableInfo objects
        """
        logfire.debug("Listing all tables")

        try:
            # Get datasets
            if self.datasets_filter:
                datasets = [
                    await self._get_dataset(dataset_id)
                    for dataset_id in self.datasets_filter
                ]
            else:
                datasets = await self._list_datasets()

            logfire.debug("Found datasets", count=len(datasets))

            # Get tables for each dataset
            tables = []
            for dataset in datasets:
                if not dataset:
                    continue

                dataset_tables = await self._list_tables(dataset.dataset_id)
                tables.extend(
                    [
                        TableInfo.from_ids(dataset.dataset_id, table.table_id)
                        for table in dataset_tables
                    ]
                )

            logfire.debug("Found tables", count=len(tables))
            return tables

        except Exception as e:
            logfire.error("Error listing tables", exception=e)
            raise

    async def describe_table(self, table_name: str) -> TableSchema:
        """Describe a table in the BigQuery database.

        Args:
            table_name: The table name in format 'dataset.table'

        Returns:
            TableSchema object containing the table schema
        """
        logfire.debug("Describing table", table_name=table_name)

        try:
            # Parse table name
            parts = table_name.split(".")
            if len(parts) != 2:
                error_msg = (
                    f"Invalid table name: {table_name}. Expected format: dataset.table"
                )
                logfire.error("Invalid table name format", table_name=table_name)
                raise ValueError(error_msg)

            dataset_id, table_id = parts

            # Get table schema
            query = f"""
                SELECT ddl
                FROM {dataset_id}.INFORMATION_SCHEMA.TABLES
                WHERE table_name = @table_name;
            """

            params = QueryParams(query=query, params={"table_name": table_id})

            result = await self.execute_query(params)

            if not result.rows:
                logfire.error("Table not found", table_name=table_name)
                raise ValueError(f"Table not found: {table_name}")

            logfire.info("Table schema retrieved", table_name=table_name)
            return TableSchema(table_name=table_name, ddl=result.rows[0].get("ddl", ""))

        except Exception as e:
            logfire.error("Error describing table", exception=e, table_name=table_name)
            raise

    @async_wrap
    def _execute_query(
        self, query: str, job_config: Optional[bigquery.QueryJobConfig] = None
    ):
        """Execute a BigQuery query synchronously (will be wrapped as async)."""
        job = self.client.query(query, job_config=job_config)
        return job.result()

    @async_wrap
    def _list_datasets(self):
        """List all datasets synchronously (will be wrapped as async)."""
        return list(self.client.list_datasets())

    @async_wrap
    def _get_dataset(self, dataset_id: str):
        """Get a dataset by ID synchronously (will be wrapped as async)."""
        try:
            return self.client.dataset(dataset_id)
        except Exception as e:
            logfire.error("Error getting dataset", exception=e, dataset_id=dataset_id)
            return None

    @async_wrap
    def _list_tables(self, dataset_id: str):
        """List tables in a dataset synchronously (will be wrapped as async)."""
        return list(self.client.list_tables(dataset_id))

    def _get_param_type(self, value: Any) -> str:
        """Get the BigQuery parameter type for a value."""
        if isinstance(value, str):
            return "STRING"
        elif isinstance(value, int):
            return "INT64"
        elif isinstance(value, float):
            return "FLOAT64"
        elif isinstance(value, bool):
            return "BOOL"
        else:
            return "STRING"  # Default to string for complex types
