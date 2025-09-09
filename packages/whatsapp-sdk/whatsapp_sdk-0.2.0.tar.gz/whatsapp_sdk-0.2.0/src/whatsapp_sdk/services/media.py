"""Media service for WhatsApp SDK.

Handles media operations including upload, download, and deletion
of images, videos, documents, and audio files.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from whatsapp_sdk.exceptions import WhatsAppMediaError
from whatsapp_sdk.models import MediaDeleteResponse, MediaUploadResponse, MediaURLResponse

if TYPE_CHECKING:
    from whatsapp_sdk.config import WhatsAppConfig
    from whatsapp_sdk.http_client import HTTPClient


class MediaService:
    """Service for managing WhatsApp media.

    Handles media operations: upload, download, get URL, delete.
    """

    def __init__(self, http_client: HTTPClient, config: WhatsAppConfig, phone_number_id: str):
        """Initialize media service.

        Args:
            http_client: HTTP client for API requests
            config: WhatsApp configuration
            phone_number_id: WhatsApp Business phone number ID
        """
        self.http_client = http_client
        self.config = config
        self.phone_number_id = phone_number_id
        # Use HTTPClient's properly constructed base_url that includes v23.0
        self.base_url = f"{http_client.base_url}/{phone_number_id}/media"

    # ========================================================================
    # UPLOAD MEDIA
    # ========================================================================

    def upload(self, file_path: str, mime_type: Optional[str] = None) -> MediaUploadResponse:
        """Upload a media file from local path.

        Args:
            file_path: Path to the file to upload
            mime_type: MIME type of the file (auto-detected if not provided)

        Returns:
            MediaUploadResponse with media ID

        Raises:
            WhatsAppMediaError: If file doesn't exist or upload fails

        Examples:
            # Upload an image
            response = media.upload("/path/to/image.jpg")
            media_id = response.id

            # Upload with explicit MIME type
            response = media.upload(
                "/path/to/document.pdf",
                mime_type="application/pdf"
            )
        """
        file_path_obj = Path(file_path)

        # Check if file exists
        if not file_path_obj.exists():
            raise WhatsAppMediaError(f"File not found: {file_path}")

        # Auto-detect MIME type if not provided
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(str(file_path_obj))
            if not mime_type:
                raise WhatsAppMediaError(f"Could not determine MIME type for: {file_path}")

        # Validate file size based on media type
        file_size = file_path_obj.stat().st_size
        self._validate_file_size(mime_type, file_size)

        # Prepare file for upload
        with open(file_path_obj, "rb") as file:
            files = {"file": (file_path_obj.name, file, mime_type)}
            data = {"messaging_product": "whatsapp", "type": mime_type}

            # Use HTTPClient's multipart upload method with proper error handling and retries
            result = self.http_client.upload_multipart(
                f"{self.phone_number_id}/media",
                files=files,
                data=data
            )

        return MediaUploadResponse(**result)

    def upload_from_bytes(
        self, file_bytes: bytes, mime_type: str, filename: str
    ) -> MediaUploadResponse:
        """Upload media from bytes in memory.

        Args:
            file_bytes: File content as bytes
            mime_type: MIME type of the file
            filename: Filename to use for the upload

        Returns:
            MediaUploadResponse with media ID

        Examples:
            # Upload from bytes
            with open("image.jpg", "rb") as f:
                file_bytes = f.read()

            response = media.upload_from_bytes(
                file_bytes=file_bytes,
                mime_type="image/jpeg",
                filename="photo.jpg"
            )

            # Upload generated content
            import io
            from PIL import Image

            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')

            response = media.upload_from_bytes(
                file_bytes=img_bytes.getvalue(),
                mime_type="image/jpeg",
                filename="generated.jpg"
            )
        """
        # Validate file size
        self._validate_file_size(mime_type, len(file_bytes))

        # Prepare file for upload
        files = {"file": (filename, file_bytes, mime_type)}
        data = {"messaging_product": "whatsapp", "type": mime_type}

        # Use HTTPClient's multipart upload method with proper error handling and retries
        result = self.http_client.upload_multipart(
            f"{self.phone_number_id}/media",
            files=files,
            data=data
        )

        return MediaUploadResponse(**result)

    # ========================================================================
    # DOWNLOAD MEDIA
    # ========================================================================

    def get_url(self, media_id: str) -> str:
        """Get download URL for a media file.

        Args:
            media_id: WhatsApp media ID

        Returns:
            Download URL (expires after 5 minutes)

        Examples:
            # Get URL for downloading
            url = media.get_url("media_id_123")

            # Use the URL to download
            import requests
            response = requests.get(url, headers={
                "Authorization": f"Bearer {access_token}"
            })
            content = response.content
        """
        response = self.http_client.get(f"{media_id}")
        media_info = MediaURLResponse(**response)
        return media_info.url

    def download(self, media_id: str) -> bytes:
        """Download media file content.

        Args:
            media_id: WhatsApp media ID

        Returns:
            File content as bytes

        Examples:
            # Download media
            content = media.download("media_id_123")

            # Save to file
            with open("downloaded_file.jpg", "wb") as f:
                f.write(content)
        """
        # First get the URL
        url = self.get_url(media_id)

        # Download the file using HTTPClient's binary download method
        # Note: The media URL requires authentication which HTTPClient handles
        try:
            content = self.http_client.download_binary(url)
            return content
        except Exception as e:
            raise WhatsAppMediaError(f"Download failed: {e}") from e

    def download_to_file(self, media_id: str, file_path: str) -> str:
        """Download media directly to a file.

        Args:
            media_id: WhatsApp media ID
            file_path: Path where to save the file

        Returns:
            Path to the saved file

        Examples:
            # Download to specific path
            saved_path = media.download_to_file(
                "media_id_123",
                "/path/to/save/image.jpg"
            )
        """
        content = self.download(media_id)

        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path_obj, "wb") as f:
            f.write(content)

        return str(file_path_obj)

    # ========================================================================
    # DELETE MEDIA
    # ========================================================================

    def delete(self, media_id: str) -> bool:
        """Delete a media file.

        Args:
            media_id: WhatsApp media ID to delete

        Returns:
            True if deletion was successful

        Examples:
            # Delete media
            success = media.delete("media_id_123")
            if success:
                print("Media deleted successfully")
        """
        response = self.http_client.delete(f"{media_id}")
        result = MediaDeleteResponse(**response)
        return result.success

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _validate_file_size(self, mime_type: str, file_size: int) -> None:
        """Validate file size based on media type.

        Args:
            mime_type: MIME type of the file
            file_size: Size of the file in bytes

        Raises:
            WhatsAppMediaError: If file size exceeds limits
        """
        # Define size limits (in bytes)
        size_limits = {
            "image": 5 * 1024 * 1024,  # 5MB
            "video": 16 * 1024 * 1024,  # 16MB
            "audio": 16 * 1024 * 1024,  # 16MB
            "document": 100 * 1024 * 1024,  # 100MB
            "sticker": 512 * 1024,  # 512KB
        }

        # Determine media type from MIME type
        if mime_type.startswith("image/"):
            if mime_type == "image/webp":
                # Could be a sticker
                max_size = size_limits["sticker"]
                media_type = "sticker"
            else:
                max_size = size_limits["image"]
                media_type = "image"
        elif mime_type.startswith("video/"):
            max_size = size_limits["video"]
            media_type = "video"
        elif mime_type.startswith("audio/"):
            max_size = size_limits["audio"]
            media_type = "audio"
        else:
            # Treat as document
            max_size = size_limits["document"]
            media_type = "document"

        if file_size > max_size:
            raise WhatsAppMediaError(
                f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds "
                f"limit for {media_type} ({max_size / 1024 / 1024:.2f}MB)"
            )
