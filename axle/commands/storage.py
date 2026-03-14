"""
Storage commands.
Each command does exactly one thing.
"""
import typer
import os
import json
from rich import print
from typing_extensions import Annotated, Optional
from axle.lib.r2_storage import R2StorageService

app = typer.Typer(help="Upload and manage assets in storage")


def _get_storage_service() -> R2StorageService:
    bucket_name = os.environ.get("R2_BUCKET_NAME")
    access_key_id = os.environ.get("R2_ACCESS_KEY_ID")
    secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    account_id = os.environ.get("R2_ACCOUNT_ID")
    cdn = os.environ.get("R2_CDN")

    if not all([bucket_name, access_key_id, secret_access_key, account_id, cdn]):
        print("[red]Error:[/red] Missing R2 environment variables: R2_BUCKET_NAME, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ACCOUNT_ID, R2_CDN")
        raise typer.Exit(code=1)

    return R2StorageService(
        bucket_name=bucket_name,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        account_id=account_id,
        cdn=cdn,
    )


@app.command()
def upload(
    file: Annotated[str, typer.Option("--file", "-f", help="Local path to the file to upload")],
    name: Annotated[Optional[str], typer.Option("--name", "-n", help="Remote name for the file (defaults to local filename)")] = None,
):
    """Upload a file to R2 storage."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"[storage:upload] Uploading {file}...")
    storage = _get_storage_service()
    try:
        with open(file, "rb") as f:
            file_data = f.read()

        file_name = name or (file.split('/')[-1] if '/' in file else file)
        url = storage.upload_data(file_name, file_data)

        print(f"[green][storage:upload][/green] Success! URL: {url}")
        print(json.dumps({"url": url}))
    except Exception as e:
        print(f"[red]Error:[/red] Upload failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def presign(
    path: Annotated[str, typer.Option("--path", "-p", help="Remote file path to generate a presigned URL for")],
    expires_in: Annotated[int, typer.Option("--expiresIn", "-e", help="Expiry in seconds")] = 3600,
):
    """Generate a presigned upload URL for R2 storage."""
    from dotenv import load_dotenv
    load_dotenv()
    
    storage = _get_storage_service()
    try:
        result = storage.create_presigned_upload(path, expires_in=expires_in)
        print(json.dumps(result))
    except Exception as e:
        print(f"[red]Error:[/red] Presign failed: {e}")
        raise typer.Exit(code=1)
