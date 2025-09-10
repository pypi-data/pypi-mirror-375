from . import server, models, database
import asyncio
import argparse
import os
from dotenv import load_dotenv
import logfire


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description="BigQuery MCP Server with Pydantic")
    parser.add_argument("--project", help="BigQuery project ID", required=False)
    parser.add_argument(
        "--location", help="BigQuery location (e.g., us-central1)", required=False
    )
    parser.add_argument(
        "--dataset",
        help="BigQuery dataset to include (can be specified multiple times)",
        required=False,
        action="append",
    )
    parser.add_argument("--env-file", help="Path to .env file", required=False)
    parser.add_argument(
        "--log-level",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        default="INFO",
        required=False,
    )

    args = parser.parse_args()

    # Load environment variables
    if args.env_file:
        load_dotenv(args.env_file)
    else:
        load_dotenv()

    # Initialize logfire
    logfire_token = os.getenv("LOGFIRE_TOKEN")
    if logfire_token:
        logfire.configure(token=logfire_token)
        logfire.info("Logfire initialized with token")
    else:
        logfire.configure()
        logfire.warning(
            "Logfire initialized without token. Logs may not be sent to logfire.ai"
        )

    # Set log level for logfire - using a different approach since set_log_level is not available
    # The current version of logfire might not have this method
    # logfire.set_log_level(args.log_level.upper())

    # Run the server
    datasets_filter = args.dataset if args.dataset else []
    # Don't use asyncio.run here, let the server handle its own asyncio setup
    # This avoids the "Already running asyncio in this thread" error
    try:
        # Create a new event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the server
        loop.run_until_complete(
            server.main(args.project, args.location, datasets_filter, args.env_file)
        )
    except Exception as e:
        logfire.error("Error running server", exception=e)
        raise


# Expose important items at package level
__all__ = ["main", "server", "models", "database"]
