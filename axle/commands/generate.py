import typer
from rich import print
import os
import json
from axle.lib.audio_service import AudioService
from typing_extensions import Annotated
from axle.lib.image_generator import ImageGenerator, AspectRatioType

app = typer.Typer(help="Generate varied assets using AI")

@app.command()
def image(
    prompt: Annotated[str, typer.Option("--prompt", "-p", help="The prompt for image generation")],
    output: Annotated[str, typer.Option("--output", "-o", help="Output file path to write the generated image")],
    model: Annotated[str, typer.Option("--model", "-m", help="Gemini model to use")] = "gemini-3.1-flash-image-preview",
    aspect_ratio: Annotated[str, typer.Option("--aspectRatio", "-a", help="Aspect ratio: 1:1, 9:16, 16:9")] = "9:16",
):
    """Generate an image using Gemini and save it to a file."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"[green][generate:image][/green] Generating image with model: {model}")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[red]Error:[/red] GEMINI_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)

    try:
        ar = AspectRatioType(aspect_ratio)
    except ValueError:
        print(f"[red]Error:[/red] Invalid aspect ratio '{aspect_ratio}'. Use: 1:1, 9:16, 16:9")
        raise typer.Exit(code=1)

    try:
        generator = ImageGenerator(api_key=api_key, model=model)
        success = generator.generate_to_file(prompt, output, aspect_ratio=ar)

        if not success:
            raise RuntimeError("No image data returned from Gemini.")

        print(f"[green][generate:image][/green] Saved to {output}")
        print(json.dumps({"path": output}))
    except Exception as e:
        print(f"[red]Error:[/red] Image generation failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def tts(
    text: Annotated[str, typer.Option("--text", "-t", help="The script text to convert to speech")],
    voice_id: Annotated[str, typer.Option("--voiceId", "-v", help="Voice ID to use for the TTS provider (ElevenLabs)")],
    output: Annotated[str, typer.Option("--output", "-o", help="Path or filename to write the generated audio file")],
):
    """Generate a Text-to-Speech (TTS) audio file from a script."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"[green][generate:tts][/green] Generating audio with voice \"{voice_id}\" -> {output}")
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    base_url = os.environ.get("ELEVENLABS_URL", "https://api.elevenlabs.io")
    model_id = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

    if not api_key:
        print("[red]Error:[/red] ELEVENLABS_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)

    service = AudioService(url=base_url, api_key=api_key, model=model_id)
    try:
        success, buffer = service.synthesize(text, voice_id)
        if not success:
            print("[red]Error:[/red] Failed to generate speech.")
            raise typer.Exit(code=1)

        with open(output, "wb") as f:
            f.write(buffer)
            
        print(f"[green][generate:tts][/green] Audio saved to {output}")
        
        tts_data = {
            "refId": voice_id,
            "src": output,
            "duration": 0
        }
        print(json.dumps(tts_data))
    except Exception as e:
        print(f"[red]Error:[/red] TTS generation failed: {e}")
        raise typer.Exit(code=1)

@app.command()
def s2s(
    audio: Annotated[str, typer.Option("--audio", "-a", help="Path to the source audio file")],
    voice_id: Annotated[str, typer.Option("--voiceId", "-v", help="Voice ID to use for the target voice (ElevenLabs)")],
    output: Annotated[str, typer.Option("--output", "-o", help="Path or filename to write the generated audio file")],
):
    """Generate a Speech-to-Speech (S2S) voice cloned audio file from a source audio file."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"[green][generate:s2s][/green] Converting audio {audio} to voice \"{voice_id}\" -> {output}")
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    base_url = os.environ.get("ELEVENLABS_URL", "https://api.elevenlabs.io")
    model_id = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_sts_v2")

    if not api_key:
        print("[red]Error:[/red] ELEVENLABS_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)

    service = AudioService(url=base_url, api_key=api_key, model=model_id)
    try:
        with open(audio, "rb") as f:
            audio_buffer = f.read()
            
        filename = audio.split('/')[-1] if '/' in audio else audio

        success, buffer = service.speech_to_speech(voice_id, audio_buffer, filename)
        if not success:
            print("[red]Error:[/red] Failed to generate speech-to-speech.")
            raise typer.Exit(code=1)

        with open(output, "wb") as f:
            f.write(buffer)
            
        print(f"[green][generate:s2s][/green] Audio saved to {output}")
        
        s2s_data = {
            "refId": voice_id,
            "src": output,
            "duration": 0
        }
        print(json.dumps(s2s_data))
    except Exception as e:
        print(f"[red]Error:[/red] S2S generation failed: {e}")
        raise typer.Exit(code=1)

@app.command()
def stt(
    audio: Annotated[str, typer.Option("--audio", "-a", help="URL or local path to the audio file to transcribe")],
    output: Annotated[str, typer.Option("--output", "-o", help="Path to write the transcript JSON output")],
    language: Annotated[str, typer.Option("--language", "-l", help="Target language for transcription (e.g. 'en'). Omit for auto-detection.")] = None,
    model: Annotated[str, typer.Option("--model", "-m", help="Deepgram model to use")] = "nova-3",
    segment_id: Annotated[str, typer.Option("--segmentId", "-s", help="Segment ID to update with the STT result")] = None,
):
    """Generate a Speech-to-Text (STT) transcript from an audio file using Deepgram. Populates the SpeechToText object in a Segment."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"[green][generate:stt][/green] Transcribing: {audio} -> {output}")
    
    from axle.lib.stt import transcribe
    
    try:
        result = transcribe(
            url=audio,
            language=language,
            model=model,
            smart_format=True,
            paragraphs=True
        )
        
        duration = result.get('duration', 0.0)
        
        with open(output, "w", encoding="utf8") as f:
            json.dump(result, f, indent=2)
            
        print(f"[green][generate:stt][/green] Done. Duration: {duration}s")
        
        # Original TS generated a UUID for some results but STT result.id might be missing since deepgram-to-combo drops it, returning main data.
        # Deepgram response has metadata.request_id, but the TS used result.id or similar.
        # Fallback to a new UUID if no refId available.
        import uuid
        stt_data = {
            "duration": duration,
            "refId": str(uuid.uuid4()), 
            "src": output
        }
        
        if segment_id:
            try:
                from axle.lib.db import get_db
                db = get_db()
                row = db.execute("SELECT data FROM segments WHERE id = ?", (segment_id,))
                result_row = row.fetchone()
                
                if result_row:
                    segment_data = json.loads(result_row[0])
                    segment_data['speechToText'] = stt_data
                    
                    db.execute("UPDATE segments SET data = ? WHERE id = ?", (json.dumps(segment_data), segment_id))
                    print(f"[green][generate:stt][/green] Database updated for segment {segment_id}")
            except Exception as e:
                print(f"[yellow]Warning:[/yellow] Failed to update database: {e}")
                
        print(json.dumps(stt_data))
    except Exception as e:
        print(f"[red]Error:[/red] STT generation failed: {e}")
        raise typer.Exit(code=1)


