"""
Storyboard commands — the main container for a video project.
A storyboard has: title, script, aspectRatio, segments, voice, visuals, etc.

Segment operations are included here since segments belong to a storyboard.
Each command does exactly one thing.
"""
import typer
import uuid
import json
from rich import print
from typing_extensions import Annotated, Optional
from axle.lib.db import get_db

app = typer.Typer(help="Manage storyboards and their segments")

# ---------------------------------------------------------------------------
# Storyboard CRUD
# ---------------------------------------------------------------------------

@app.command()
def create(
    title: Annotated[str, typer.Option("--title", "-t", help="Storyboard title")],
    aspect_ratio: Annotated[str, typer.Option("--aspectRatio", "-a", help="Aspect ratio: 9:16, 16:9, 1:1, 11")] = "9:16",
    script: Annotated[Optional[str], typer.Option("--script", "-s", help="Full script text")] = None,
    description: Annotated[Optional[str], typer.Option("--description", "-d", help="Optional description")] = None,
    storyboard_type: Annotated[Optional[str], typer.Option("--type", help="Type: narrative-video, product-video-ad, ugc-video-ad")] = None,
    pacing: Annotated[Optional[str], typer.Option("--pacing", help="Pacing: fast, slow, regular, dynamic, relaxed")] = None,
    quality: Annotated[Optional[str], typer.Option("--quality", help="Quality: regular, high")] = "regular",
):
    """Create a new storyboard."""
    storyboard_id = str(uuid.uuid4())
    data = {
        "aspectRatio": aspect_ratio,
        "script": script or "",
        "type": storyboard_type,
        "pacing": pacing,
        "quality": quality,
        "caption": {"id": "default", "name": "Default", "position": "bottom", "size": "medium"},
        "visuals": {"style": "cinematic", "type": storyboard_type or "narrative-video"},
        "voice": {"name": "Default"},
        "segments": [],
        "tags": [],
    }
    try:
        db = get_db()
        db.execute(
            "INSERT INTO storyboards (id, title, description, data) VALUES (?, ?, ?, ?)",
            (storyboard_id, title, description or "", json.dumps(data))
        )
        db.commit()
        print(f"Storyboard created. ID: [bold]{storyboard_id}[/bold]")
        print(json.dumps({"id": storyboard_id, "title": title}))
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)



@app.command()
def list():
    """List all storyboards."""
    try:
        db = get_db()
        rows = db.execute(
            "SELECT id, title, description, createdAt FROM storyboards ORDER BY createdAt DESC"
        ).fetchall()
        if not rows:
            print("No storyboards found.")
            return
        for row in rows:
            print(f"- {row[1]} ({row[0]}) — {row[3]}")
        print(json.dumps([{"id": r[0], "title": r[1], "description": r[2], "createdAt": r[3]} for r in rows]))
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def get(
    storyboard_id: Annotated[str, typer.Argument(help="Storyboard ID")],
):
    """Get a storyboard with all its segments."""
    try:
        db = get_db()
        row = db.execute("SELECT id, title, description, data FROM storyboards WHERE id = ?", (storyboard_id,)).fetchone()
        if not row:
            print(f"[red]Error:[/red] Storyboard {storyboard_id} not found.")
            raise typer.Exit(code=1)

        schema = {
            **json.loads(row[3]),
            "id": row[0],
            "title": row[1],
            "description": row[2],
        }
        print(json.dumps(schema, indent=2))
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def delete(
    storyboard_id: Annotated[str, typer.Argument(help="Storyboard ID to delete")],
):
    """Delete a storyboard."""
    try:
        db = get_db()
        db.execute("DELETE FROM storyboards WHERE id = ?", (storyboard_id,))
        db.commit()
        print(f"Storyboard [bold]{storyboard_id}[/bold] deleted.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def validate(
    schema_file: Annotated[str, typer.Option("--schema", "-f", help="Path to storyboard JSON file")],
):
    """Validate a storyboard JSON against the required schema fields."""
    try:
        with open(schema_file, "r") as f:
            data = json.load(f)

        required = ["voice", "visuals", "caption", "aspectRatio"]
        missing = [k for k in required if k not in data]

        if missing:
            print(f"[red]Validation failed:[/red] Missing: {', '.join(missing)}")
            raise typer.Exit(code=1)

        print("[green]Storyboard schema is valid.[/green]")
        print(json.dumps({"valid": True}))
    except typer.Exit:
        raise
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Segment operations (now modifying the JSON blob)
# ---------------------------------------------------------------------------

@app.command()
def add_segment(
    storyboard_id: Annotated[str, typer.Option("--storyboardId", "-b", help="Storyboard ID")],
    data: Annotated[str, typer.Option("--data", "-d", help="JSON string of segment data")],
    order: Annotated[Optional[int], typer.Option("--order", "-n", help="Order index")] = None,
):
    """Add a segment to a storyboard."""
    try:
        db = get_db()
        row = db.execute("SELECT data FROM storyboards WHERE id = ?", (storyboard_id,)).fetchone()
        if not row:
            print(f"[red]Error:[/red] Storyboard {storyboard_id} not found.")
            raise typer.Exit(code=1)

        storyboard_data = json.loads(row[0])
        segment = json.loads(data)
        if not segment.get("id"):
            segment["id"] = str(uuid.uuid4())

        segments = storyboard_data.get("segments", [])
        
        if order is not None:
            segments.insert(order, segment)
        else:
            segments.append(segment)
            
        storyboard_data["segments"] = segments

        db.execute(
            "UPDATE storyboards SET data = ? WHERE id = ?",
            (json.dumps(storyboard_data), storyboard_id)
        )
        db.commit()
        print(f"Segment added. ID: [bold]{segment['id']}[/bold]")
        print(json.dumps({"id": segment["id"], "storyboardId": storyboard_id}))
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def update_segment(
    storyboard_id: Annotated[str, typer.Option("--storyboardId", "-b", help="Storyboard ID")],
    segment_id: Annotated[str, typer.Argument(help="Segment ID to update")],
    data: Annotated[str, typer.Option("--data", "-d", help="JSON to merge into segment")],
    order: Annotated[Optional[int], typer.Option("--order", "-n", help="New order index")] = None,
):
    """Update a segment's data inside a storyboard."""
    try:
        db = get_db()
        row = db.execute("SELECT data FROM storyboards WHERE id = ?", (storyboard_id,)).fetchone()
        if not row:
            print(f"[red]Error:[/red] Storyboard {storyboard_id} not found.")
            raise typer.Exit(code=1)

        storyboard_data = json.loads(row[0])
        segments = storyboard_data.get("segments", [])
        
        found = False
        for i, seg in enumerate(segments):
            if seg.get("id") == segment_id:
                merged = {**seg, **json.loads(data)}
                segments[i] = merged
                if order is not None:
                    segments.pop(i)
                    segments.insert(order, merged)
                found = True
                break
        
        if not found:
            print(f"[red]Error:[/red] Segment {segment_id} not found in storyboard {storyboard_id}.")
            raise typer.Exit(code=1)

        storyboard_data["segments"] = segments
        db.execute("UPDATE storyboards SET data = ? WHERE id = ?", (json.dumps(storyboard_data), storyboard_id))
        db.commit()
        print(f"Segment [bold]{segment_id}[/bold] updated.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def delete_segment(
    storyboard_id: Annotated[str, typer.Option("--storyboardId", "-b", help="Storyboard ID")],
    segment_id: Annotated[str, typer.Argument(help="Segment ID to delete")],
):
    """Delete a segment from a storyboard."""
    try:
        db = get_db()
        row = db.execute("SELECT data FROM storyboards WHERE id = ?", (storyboard_id,)).fetchone()
        if not row:
            print(f"[red]Error:[/red] Storyboard {storyboard_id} not found.")
            raise typer.Exit(code=1)

        storyboard_data = json.loads(row[0])
        segments = storyboard_data.get("segments", [])
        
        new_segments = [s for s in segments if s.get("id") != segment_id]
        
        if len(new_segments) == len(segments):
            print(f"[red]Error:[/red] Segment {segment_id} not found.")
            raise typer.Exit(code=1)

        storyboard_data["segments"] = new_segments
        db.execute("UPDATE storyboards SET data = ? WHERE id = ?", (json.dumps(storyboard_data), storyboard_id))
        db.commit()
        print(f"Segment [bold]{segment_id}[/bold] deleted.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
