import typer
from axle.commands import db, generate, storyboard, storage, video, voice, search

app = typer.Typer(
    help="Axle: A composable toolset for agentic video workflows",
    no_args_is_help=True,
)

app.add_typer(db.app, name="db", help="Database operations")
app.add_typer(generate.app, name="generate", help="Generate assets using AI")
app.add_typer(storyboard.app, name="storyboard", help="Manage storyboards and their segments")
app.add_typer(storage.app, name="storage", help="Upload and manage assets in storage")
app.add_typer(video.app, name="video", help="Video manipulation utilities")
app.add_typer(voice.app, name="voice", help="Voice and audio tasks")
app.add_typer(search.app, name="search", help="Search operations")

if __name__ == "__main__":
    app()
