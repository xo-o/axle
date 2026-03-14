"""
Voice commands.
Each command does exactly one thing.
"""
import typer
import os
import json
from rich import print
from typing_extensions import Annotated, Optional
from axle.lib.audio_service import AudioService

app = typer.Typer(help="Voice and audio tasks")


def _get_audio_service(model_default: str = "eleven_multilingual_v2") -> AudioService:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    base_url = os.environ.get("ELEVENLABS_URL", "https://api.elevenlabs.io")
    model_id = os.environ.get("ELEVENLABS_MODEL", model_default)

    if not api_key:
        print("[red]Error:[/red] ELEVENLABS_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)

    return AudioService(url=base_url, api_key=api_key, model=model_id)


@app.command()
def clone(
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the new cloned voice")],
    audio: Annotated[str, typer.Option("--audio", "-a", help="Path to the source audio file")],
    description: Annotated[Optional[str], typer.Option("--description", "-d", help="Optional description for the cloned voice")] = None,
):
    """Clone a voice from an audio sample via ElevenLabs."""
    print(f"[voice:clone] Cloning voice \"{name}\" from {audio}")
    service = _get_audio_service()
    try:
        with open(audio, "rb") as f:
            audio_bytes = f.read()
        filename = audio.split('/')[-1] if '/' in audio else audio
        voice_id = service.clone_voice(name, audio_bytes, filename, description)
        print(f"[green][voice:clone][/green] Cloned! Voice ID: {voice_id}")
        print(json.dumps({"name": name, "voiceId": voice_id}))
    except Exception as e:
        print(f"[red]Error:[/red] Voice cloning failed: {e}")
        raise typer.Exit(code=1)
