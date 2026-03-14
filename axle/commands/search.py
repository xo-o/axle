"""
Search commands.
Each command does exactly one thing.
"""
import typer
import json
from rich import print
from typing_extensions import Annotated, Optional

app = typer.Typer(help="Search operations")


@app.command()
def asset(
    query: Annotated[str, typer.Option("--query", "-q", help="Natural language search query")],
    db_url: Annotated[str, typer.Option("--db", "-d", help="Database connection string")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum number of results to return")] = 1,
    asset_type: Annotated[Optional[str], typer.Option("--type", "-t", help="Filter by asset type: video or image")] = None,
):
    """Semantically search the video RAG database for matching clips (stub — embed and vector search to be implemented)."""
    print(f"[search:asset] Searching for \"{query}\" (limit: {limit}) in database")
    # TODO: embed query, run vector similarity search, return top results as JSON
    # Output shape: Array of VisualBroll { url, duration, type, time, ... }
    print(json.dumps([]))
