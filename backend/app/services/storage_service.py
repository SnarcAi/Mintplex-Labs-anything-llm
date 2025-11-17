"""
File storage service for handling uploads (S3 or local).
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

from app.core.config import settings


class StorageService:
    """Service for managing file uploads to S3 or local storage."""

    def __init__(self):
        self.use_s3 = bool(settings.AWS_ACCESS_KEY_ID and S3_AVAILABLE)

        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.S3_ENDPOINT_URL or None,
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        else:
            # Use local storage
            self.upload_dir = Path("uploads")
            self.upload_dir.mkdir(exist_ok=True)

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        folder: str = "uploads",
    ) -> str:
        """
        Upload a file to storage.

        Args:
            file_data: File content as bytes
            filename: Original filename
            content_type: MIME type
            folder: Storage folder/prefix

        Returns:
            Public URL of the uploaded file
        """
        # Generate unique filename
        ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{ext}"
        key = f"{folder}/{unique_filename}"

        if self.use_s3:
            return await self._upload_to_s3(file_data, key, content_type)
        else:
            return await self._upload_local(file_data, key)

    async def _upload_to_s3(self, file_data: bytes, key: str, content_type: str) -> str:
        """Upload file to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type,
                ACL='public-read',
            )

            # Generate public URL
            if settings.S3_ENDPOINT_URL:
                url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{key}"
            else:
                url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

            return url
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")

    async def _upload_local(self, file_data: bytes, key: str) -> str:
        """Upload file to local storage."""
        file_path = self.upload_dir / key

        # Create subdirectories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        # Return relative URL (in production, use proper domain)
        return f"/uploads/{key}"


# Singleton instance
storage_service = StorageService()
