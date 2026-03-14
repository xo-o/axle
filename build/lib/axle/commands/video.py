"""
Video utility commands.
Each command does exactly one thing.
"""
import typer
import json
import subprocess
import os
from rich import print
from typing_extensions import Annotated, Optional

app = typer.Typer(help="Video manipulation utilities")


def _run(cmd: str):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg error")


@app.command()
def trim(
    input_file: Annotated[str, typer.Option("--input", "-i", help="Input video file path")],
    output_file: Annotated[str, typer.Option("--output", "-o", help="Output video file path")],
    start: Annotated[str, typer.Option("--start", "-s", help="Start timestamp (e.g. 00:00:10)")],
    end: Annotated[Optional[str], typer.Option("--end", "-e", help="End timestamp")] = None,
    duration: Annotated[Optional[str], typer.Option("--duration", "-d", help="Duration instead of end timestamp")] = None,
):
    """Trim a video between start and end timestamps."""
    cmd = f'ffmpeg -i "{input_file}" -ss {start}'
    if end:
        cmd += f' -to {end}'
    elif duration:
        cmd += f' -t {duration}'
    cmd += f' -c copy "{output_file}" -y'

    try:
        _run(cmd)
        print(f"[green][video:trim][/green] Done.")
        print(json.dumps({"path": output_file}))
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def split(
    input_file: Annotated[str, typer.Option("--input", "-i", help="Input video file path")],
    at: Annotated[str, typer.Option("--at", "-a", help="Timestamp to split at (e.g. 00:00:30)")],
    output_a: Annotated[str, typer.Option("--outputA", help="Output path for the first part")],
    output_b: Annotated[str, typer.Option("--outputB", help="Output path for the second part")],
):
    """Split a video into two parts at a given timestamp."""
    cmd_a = f'ffmpeg -i "{input_file}" -to {at} -c copy "{output_a}" -y'
    cmd_b = f'ffmpeg -i "{input_file}" -ss {at} -c copy "{output_b}" -y'

    try:
        _run(cmd_a)
        _run(cmd_b)
        print(f"[green][video:split][/green] Done.")
        print(json.dumps({"partA": output_a, "partB": output_b}))
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
