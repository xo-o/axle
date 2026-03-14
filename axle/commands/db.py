import typer
from rich import print
from typing_extensions import Annotated
from axle.lib.db import init_db

app = typer.Typer(help="Database operations")

@app.command()
def init():
    """Initialize the Turso database schema (projects and segments tables)."""
    print("Initializing database...")
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"[red]Error:[/red] Failed to initialize database: {e}")
        raise typer.Exit(code=1)
