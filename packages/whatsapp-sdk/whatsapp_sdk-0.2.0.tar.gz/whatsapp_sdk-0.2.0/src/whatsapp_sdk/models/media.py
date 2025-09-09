"""Media models for WhatsApp SDK.

These models handle media upload, download, and management
for images, videos, documents, and audio files.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MediaUploadResponse(BaseModel):
    """Response after uploading media.

    Contains the media ID to use in messages.
    """

    id: str = Field(..., description="Media ID to use when sending messages")


class MediaURLResponse(BaseModel):
    """Response when retrieving media URL.

    Contains the URL and metadata for downloading media.
    """

    url: str = Field(..., description="URL to download the media (expires after 5 minutes)")
    mime_type: str = Field(..., description="MIME type of the media file")
    sha256: str = Field(..., description="SHA256 hash of the media file")
    file_size: int = Field(..., description="Size of the media file in bytes")
    id: str = Field(..., description="Media ID")


class MediaDeleteResponse(BaseModel):
    """Response after deleting media.

    Confirms media deletion status.
    """

    success: bool = Field(..., description="Whether the media was successfully deleted")


class MediaUploadRequest(BaseModel):
    """Request to upload media.

    Parameters for uploading media files.
    """

    file_path: Optional[str] = Field(None, description="Local file path to upload")
    file_bytes: Optional[bytes] = Field(None, description="File content as bytes")
    mime_type: str = Field(..., description="MIME type of the file (e.g., image/jpeg, video/mp4)")
    filename: Optional[str] = Field(
        None, description="Filename to use (required when uploading bytes)"
    )


class SupportedMediaTypes(BaseModel):
    """Supported media types and their constraints.

    Reference for valid media types and size limits.
    """

    class ImageTypes(BaseModel):
        """Supported image formats."""

        jpeg: str = Field(default="image/jpeg", description="JPEG images")
        png: str = Field(default="image/png", description="PNG images")
        webp: str = Field(default="image/webp", description="WebP images")
        max_size: int = Field(default=5242880, description="Max size: 5MB")

    class DocumentTypes(BaseModel):
        """Supported document formats."""

        pdf: str = Field(default="application/pdf", description="PDF documents")
        doc: str = Field(default="application/msword", description="Word documents")
        docx: str = Field(
            default="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            description="Word documents",
        )
        ppt: str = Field(default="application/vnd.ms-powerpoint", description="PowerPoint")
        pptx: str = Field(
            default="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            description="PowerPoint",
        )
        xls: str = Field(default="application/vnd.ms-excel", description="Excel")
        xlsx: str = Field(
            default="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            description="Excel",
        )
        txt: str = Field(default="text/plain", description="Plain text")
        max_size: int = Field(default=104857600, description="Max size: 100MB")

    class AudioTypes(BaseModel):
        """Supported audio formats."""

        aac: str = Field(default="audio/aac", description="AAC audio")
        mp4: str = Field(default="audio/mp4", description="MP4 audio")
        mpeg: str = Field(default="audio/mpeg", description="MPEG audio")
        amr: str = Field(default="audio/amr", description="AMR audio")
        ogg: str = Field(default="audio/ogg", description="OGG audio")
        opus: str = Field(default="audio/opus", description="Opus audio")
        max_size: int = Field(default=16777216, description="Max size: 16MB")

    class VideoTypes(BaseModel):
        """Supported video formats."""

        mp4: str = Field(default="video/mp4", description="MP4 video")
        threegp: str = Field(default="video/3gpp", description="3GPP video")
        max_size: int = Field(default=16777216, description="Max size: 16MB")

    class StickerTypes(BaseModel):
        """Supported sticker formats."""

        webp: str = Field(default="image/webp", description="WebP stickers")
        max_size: int = Field(default=524288, description="Max size: 512KB")
        dimensions: str = Field(default="512x512", description="Required dimensions")

    images: ImageTypes = Field(default_factory=ImageTypes)
    documents: DocumentTypes = Field(default_factory=DocumentTypes)
    audio: AudioTypes = Field(default_factory=AudioTypes)
    video: VideoTypes = Field(default_factory=VideoTypes)
    stickers: StickerTypes = Field(default_factory=StickerTypes)


class ResumableUploadSession(BaseModel):
    """Resumable upload session for large files.

    Used for uploading files larger than 5MB.
    """

    id: str = Field(..., description="Upload session ID")
    upload_url: str = Field(..., description="URL for uploading file chunks")
    file_offset: int = Field(0, description="Current upload offset in bytes")
    file_size: int = Field(..., description="Total file size in bytes")
    expires_at: str = Field(..., description="Session expiration timestamp")
