from uuid import uuid4

import boto3
from botocore.client import Config

from app.core.config import settings


class S3Service:
    def __init__(self) -> None:
        client_kwargs: dict = {
            "region_name": settings.aws_region,
            "config": Config(signature_version="s3v4"),
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.client = boto3.client("s3", **client_kwargs)
        self.bucket = settings.s3_bucket_name
        self.expire_seconds = settings.s3_presigned_url_expire_seconds

    def build_object_key(self, org_id: str, document_type: str, file_name: str) -> str:
        safe_name = file_name.replace(" ", "_")
        return f"org/{org_id}/{document_type}/{uuid4()}_{safe_name}"

    def generate_presigned_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
    ) -> dict[str, str]:
        url = self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=self.expire_seconds,
        )
        return {"upload_url": url, "object_key": object_key, "bucket": self.bucket}

    def generate_presigned_download_url(self, *, object_key: str) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": object_key},
            ExpiresIn=self.expire_seconds,
        )


def get_s3_service() -> S3Service:
    return S3Service()
