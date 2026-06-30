# HostelWise AI - Google Cloud Storage Helper Module
import os
from google.cloud import storage
from .config import cloud_settings

class GCSStorageManager:
    def __init__(self):
        self.project_id = cloud_settings.GCP_PROJECT
        self.bucket_name = cloud_settings.GCS_BUCKET_NAME
        self.local_upload_dir = cloud_settings.UPLOAD_DIR
        self.client = None
        self.is_active = False
        
        if self.project_id:
            try:
                self.client = storage.Client(project=self.project_id)
                self.is_active = True
                self._ensure_bucket_exists()
            except Exception as e:
                print(f"GCS Client initialization failed: {e}. Defaulting to local storage.")
        else:
            print("GCP_PROJECT not configured. Running GCS Storage Manager in Local Disk mode.")

    def _ensure_bucket_exists(self):
        """Verify the GCS bucket exists, or attempt to create it."""
        if not self.is_active or not self.client:
            return
        try:
            bucket = self.client.lookup_bucket(self.bucket_name)
            if not bucket:
                self.client.create_bucket(self.bucket_name)
                print(f"GCS Bucket '{self.bucket_name}' created successfully.")
        except Exception as e:
            print(f"Warning: GCS Bucket check failed ({e}). Operations will fall back to local disk if needed.")
            self.is_active = False

    def upload_file(self, file_content: bytes, destination_blob_name: str, content_type: str = "text/csv") -> str:
        """
        Uploads file content to GCS bucket if active, or saves locally.
        Returns the destination GCS URI or local absolute file path.
        """
        if self.is_active and self.client:
            try:
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_string(file_content, content_type=content_type)
                gcs_uri = f"gs://{self.bucket_name}/{destination_blob_name}"
                print(f"File successfully uploaded to GCS: {gcs_uri}")
                return gcs_uri
            except Exception as e:
                print(f"GCS upload failed: {e}. Falling back to local disk storage.")
                
        # Local fallback
        local_filename = os.path.basename(destination_blob_name)
        local_path = os.path.join(self.local_upload_dir, local_filename)
        with open(local_path, "wb") as f:
            f.write(file_content)
        print(f"File saved locally: {local_path}")
        return local_path

    def download_file(self, source_blob_name: str) -> bytes:
        """Downloads a blob from GCS as bytes, or reads from local disk."""
        if self.is_active and self.client:
            try:
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(source_blob_name)
                return blob.download_as_bytes()
            except Exception as e:
                print(f"GCS download failed: {e}. Trying local disk.")
                
        # Local fallback
        local_filename = os.path.basename(source_blob_name)
        local_path = os.path.join(self.local_upload_dir, local_filename)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        raise FileNotFoundError(f"File not found in GCS or local path: {source_blob_name}")

# Global storage manager instance
gcs_manager = GCSStorageManager()
