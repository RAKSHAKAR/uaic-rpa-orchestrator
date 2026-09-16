"""Storage Service managing screenshot captures and cloud storage providers."""

import logging
import os
import time
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.schemas.settings import StorageSettings, StorageTestRequest, StorageTestResponse

logger = logging.getLogger("uaic_orchestrator.storage")


class StorageService:
    """Provides abstracted storage operations across Local disk, AWS S3, Azure Blob, and GCS."""

    @staticmethod
    def get_local_dir() -> Path:
        """Ensures and returns local screenshots directory."""
        dir_path = settings.SCREENSHOTS_DIR
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @classmethod
    async def save_screenshot_bytes(
        cls,
        filename: str,
        image_bytes: bytes,
        storage_cfg: StorageSettings | None = None,
        claim_id: str | None = None,
        portal_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Saves screenshot image bytes to the configured storage provider (Local / S3 / Azure / GCS).
        Hierarchically stores under backend/screenshots/{claim_id}/{portal}/ as well as root.
        Falls back seamlessly to local disk if cloud upload is unconfigured or encounters an error.
        """
        provider = (storage_cfg.storage_provider if storage_cfg else "local").lower()
        local_dir = cls.get_local_dir()
        local_path = local_dir / filename

        # Infer claim_id and portal_key if not explicitly passed
        if (not claim_id or not portal_key) and "_" in filename:
            parts = filename.split("_")
            if len(parts) >= 2:
                claim_id = claim_id or parts[0]
                portal_key = portal_key or parts[1]

        # 1. Save hierarchical path if claim_id and portal_key are known
        if claim_id and portal_key:
            portal_dir = local_dir / str(claim_id) / str(portal_key)
            portal_dir.mkdir(parents=True, exist_ok=True)
            hierarchical_path = portal_dir / filename
            with open(hierarchical_path, "wb") as f:
                f.write(image_bytes)

        # 2. Always write to flat root dir as failover & instant lookup
        with open(local_path, "wb") as f:
            f.write(image_bytes)

        stored_provider = "local"
        remote_url = None
        storage_notes = "Saved to local server storage"

        # 2. Upload to S3 if configured
        if provider == "s3" and storage_cfg and storage_cfg.s3_bucket_name:
            try:
                import boto3
                s3_kwargs: dict[str, Any] = {"region_name": storage_cfg.s3_region or "us-east-1"}
                if storage_cfg.s3_access_key and storage_cfg.s3_secret_key:
                    s3_kwargs["aws_access_key_id"] = storage_cfg.s3_access_key
                    s3_kwargs["aws_secret_access_key"] = storage_cfg.s3_secret_key
                s3 = boto3.client("s3", **s3_kwargs)
                s3.put_object(
                    Bucket=storage_cfg.s3_bucket_name,
                    Key=f"screenshots/{filename}",
                    Body=image_bytes,
                    ContentType="image/png",
                )
                stored_provider = "s3"
                remote_url = f"https://{storage_cfg.s3_bucket_name}.s3.{storage_cfg.s3_region}.amazonaws.com/screenshots/{filename}"
                storage_notes = f"Uploaded to S3 bucket '{storage_cfg.s3_bucket_name}'"
                logger.info(f"Screenshot uploaded to S3: {remote_url}")
            except Exception as e:
                logger.warning(f"S3 upload failed for {filename}, retained on local disk: {e}")
                storage_notes = f"S3 upload failed ({e}); saved to local fallback"

        # 3. Upload to Azure Blob if configured
        elif provider == "azure_blob" and storage_cfg and storage_cfg.azure_connection_string:
            try:
                from azure.storage.blob import BlobServiceClient
                blob_service = BlobServiceClient.from_connection_string(storage_cfg.azure_connection_string)
                container_client = blob_service.get_container_client(storage_cfg.azure_container_name or "screenshots")
                if not container_client.exists():
                    container_client.create_container()
                blob_client = container_client.get_blob_client(filename)
                blob_client.upload_blob(image_bytes, overwrite=True)
                stored_provider = "azure_blob"
                remote_url = blob_client.url
                storage_notes = f"Uploaded to Azure Blob container '{storage_cfg.azure_container_name}'"
                logger.info(f"Screenshot uploaded to Azure Blob: {remote_url}")
            except Exception as e:
                logger.warning(f"Azure Blob upload failed for {filename}, retained on local disk: {e}")
                storage_notes = f"Azure Blob upload failed ({e}); saved to local fallback"

        # 4. Upload to GCS if configured
        elif provider == "gcs" and storage_cfg and storage_cfg.gcs_bucket_name:
            try:
                from google.cloud import storage as gcs_storage
                client = gcs_storage.Client(project=storage_cfg.gcs_project_id or None)
                bucket = client.bucket(storage_cfg.gcs_bucket_name)
                blob = bucket.blob(f"screenshots/{filename}")
                blob.upload_from_string(image_bytes, content_type="image/png")
                stored_provider = "gcs"
                remote_url = f"gs://{storage_cfg.gcs_bucket_name}/screenshots/{filename}"
                storage_notes = f"Uploaded to GCS bucket '{storage_cfg.gcs_bucket_name}'"
                logger.info(f"Screenshot uploaded to GCS: {remote_url}")
            except Exception as e:
                logger.warning(f"GCS upload failed for {filename}, retained on local disk: {e}")
                storage_notes = f"GCS upload failed ({e}); saved to local fallback"

        return {
            "filename": filename,
            "local_path": str(local_path),
            "stored_provider": stored_provider,
            "remote_url": remote_url,
            "notes": storage_notes,
            "size_bytes": len(image_bytes),
        }

    @classmethod
    async def test_connection(cls, req: StorageTestRequest) -> StorageTestResponse:
        """Tests connectivity, write permissions, and bucket access for the selected provider."""
        t_start = time.perf_counter()
        provider = (req.storage_provider or "local").lower()

        if provider == "local":
            try:
                local_dir = cls.get_local_dir()
                test_file = local_dir / f".test_{int(time.time())}.tmp"
                test_file.write_text("UAIC Storage Test OK", encoding="utf-8")
                test_file.unlink(missing_ok=True)
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=True,
                    storage_provider="local",
                    message="Local disk storage verified. Write & delete operations succeeded.",
                    duration_ms=dur,
                    details={
                        "directory": str(local_dir),
                        "exists": local_dir.exists(),
                        "writable": os.access(local_dir, os.W_OK),
                    },
                )
            except Exception as e:
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=False,
                    storage_provider="local",
                    message=f"Local storage verification failed: {e}",
                    duration_ms=dur,
                    error_detail=str(e),
                )

        elif provider == "s3":
            if not req.s3_bucket_name:
                return StorageTestResponse(
                    success=False,
                    storage_provider="s3",
                    message="S3 bucket name is required.",
                    error_detail="Missing s3_bucket_name",
                )
            try:
                import boto3
                s3_kwargs: dict[str, Any] = {"region_name": req.s3_region or "us-east-1"}
                if req.s3_access_key and req.s3_secret_key:
                    s3_kwargs["aws_access_key_id"] = req.s3_access_key
                    s3_kwargs["aws_secret_access_key"] = req.s3_secret_key
                s3 = boto3.client("s3", **s3_kwargs)
                s3.head_bucket(Bucket=req.s3_bucket_name)
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=True,
                    storage_provider="s3",
                    message=f"Amazon S3 connected successfully! Bucket '{req.s3_bucket_name}' is accessible.",
                    duration_ms=dur,
                    details={"bucket": req.s3_bucket_name, "region": req.s3_region or "us-east-1"},
                )
            except Exception as e:
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=False,
                    storage_provider="s3",
                    message=f"Amazon S3 connection failed: {e}",
                    duration_ms=dur,
                    error_detail=str(e),
                )

        elif provider == "azure_blob":
            if not req.azure_connection_string:
                return StorageTestResponse(
                    success=False,
                    storage_provider="azure_blob",
                    message="Azure Connection String is required.",
                    error_detail="Missing azure_connection_string",
                )
            try:
                from azure.storage.blob import BlobServiceClient
                blob_service = BlobServiceClient.from_connection_string(req.azure_connection_string)
                container_client = blob_service.get_container_client(req.azure_container_name or "screenshots")
                exists = container_client.exists()
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=True,
                    storage_provider="azure_blob",
                    message=f"Azure Blob Storage connected successfully! Container '{req.azure_container_name or 'screenshots'}' exists={exists}.",
                    duration_ms=dur,
                    details={"container": req.azure_container_name or "screenshots", "exists": exists},
                )
            except Exception as e:
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=False,
                    storage_provider="azure_blob",
                    message=f"Azure Blob Storage connection failed: {e}",
                    duration_ms=dur,
                    error_detail=str(e),
                )

        elif provider == "gcs":
            if not req.gcs_bucket_name:
                return StorageTestResponse(
                    success=False,
                    storage_provider="gcs",
                    message="GCS bucket name is required.",
                    error_detail="Missing gcs_bucket_name",
                )
            try:
                from google.cloud import storage as gcs_storage
                client = gcs_storage.Client(project=req.gcs_project_id or None)
                bucket = client.bucket(req.gcs_bucket_name)
                exists = bucket.exists()
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=True,
                    storage_provider="gcs",
                    message=f"Google Cloud Storage connected successfully! Bucket '{req.gcs_bucket_name}' exists={exists}.",
                    duration_ms=dur,
                    details={"bucket": req.gcs_bucket_name, "exists": exists},
                )
            except Exception as e:
                dur = round((time.perf_counter() - t_start) * 1000, 2)
                return StorageTestResponse(
                    success=False,
                    storage_provider="gcs",
                    message=f"Google Cloud Storage connection failed: {e}",
                    duration_ms=dur,
                    error_detail=str(e),
                )

        return StorageTestResponse(
            success=False,
            storage_provider=provider,
            message=f"Unknown storage provider '{provider}'.",
            error_detail="Invalid provider choice",
        )
