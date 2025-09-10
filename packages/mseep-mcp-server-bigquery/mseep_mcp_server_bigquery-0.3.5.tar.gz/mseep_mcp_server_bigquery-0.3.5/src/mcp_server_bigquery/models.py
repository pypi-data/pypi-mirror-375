from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union


class QueryParams(BaseModel):
    """Parameters for executing a SQL query on BigQuery."""

    query: str = Field(..., description="SQL query to execute using BigQuery dialect")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate that the query is not empty and is a SELECT query."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        if not v.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed for security reasons")
        return v


class TableInfo(BaseModel):
    """Information about a BigQuery table."""

    dataset_id: str = Field(..., description="Dataset ID")
    table_id: str = Field(..., description="Table ID")
    full_name: str = Field(..., description="Full table name in format dataset.table")

    @classmethod
    def from_ids(cls, dataset_id: str, table_id: str) -> "TableInfo":
        """Create a TableInfo instance from dataset and table IDs."""
        return cls(
            dataset_id=dataset_id,
            table_id=table_id,
            full_name=f"{dataset_id}.{table_id}",
        )


class QueryResult(BaseModel):
    """Result of a BigQuery query."""

    rows: List[Dict[str, Any]] = Field(
        default_factory=list, description="Query result rows"
    )
    row_count: int = Field(0, description="Number of rows returned")

    @classmethod
    def from_rows(cls, rows: List[Dict[str, Any]]) -> "QueryResult":
        """Create a QueryResult instance from a list of rows."""
        return cls(rows=rows, row_count=len(rows))


class TableSchema(BaseModel):
    """Schema information for a BigQuery table."""

    table_name: str = Field(..., description="Table name")
    ddl: str = Field(..., description="DDL statement for the table")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

    @classmethod
    def from_exception(cls, e: Exception) -> "ErrorResponse":
        """Create an ErrorResponse from an exception."""
        return cls(error=str(e), details=repr(e) if hasattr(e, "__repr__") else None)


class ToolResponse(BaseModel):
    """Response model for MCP tools."""

    content: Union[
        str, List[Dict[str, Any]], List[TableInfo], TableSchema, ErrorResponse
    ]
    is_error: bool = False
