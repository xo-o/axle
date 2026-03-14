import boto3
import mimetypes
import json
from botocore.config import Config
from typing import Union

class R2StorageService:
    def __init__(self, bucket_name: str, access_key_id: str, secret_access_key: str, account_id: str, cdn: str):
        self.bucket_name = bucket_name
        self.account_id = account_id
        self.cdn = cdn.rstrip('/')

        # Configure boto3 client for Cloudflare R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )

    def upload_data(self, file_name: str, data: Union[bytes, str], content_type: str = 'application/octet-stream') -> str:
        try:
            guessed_type, _ = mimetypes.guess_type(file_name)
            content_type = guessed_type or content_type

            if isinstance(data, str):
                data = data.encode('utf-8')

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=data,
                ContentType=content_type
            )
            return self.get_url(file_name)
        except Exception as e:
            print(f"[R2] Failed to upload file: {file_name}")
            print(f"[R2] Error: {e}")
            raise RuntimeError('Failed to upload to R2') from e

    def upload_json(self, file_name: str, data: dict) -> str:
        content = json.dumps(data)
        return self.upload_data(file_name, content, 'application/json')

    def create_presigned_upload(self, file_path: str, expires_in: int = 3600, content_type: str = None) -> dict:
        inferred_type = content_type or mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        presigned_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': file_path,
                'ContentType': inferred_type
            },
            ExpiresIn=expires_in
        )

        return {
            "fileName": file_path.split('/')[-1] if '/' in file_path else file_path,
            "filePath": file_path,
            "contentType": inferred_type,
            "presignedUrl": presigned_url,
            "url": self.get_url(file_path)
        }

    def get_url(self, file_name: str) -> str:
        return f"{self.cdn}/{file_name}"
