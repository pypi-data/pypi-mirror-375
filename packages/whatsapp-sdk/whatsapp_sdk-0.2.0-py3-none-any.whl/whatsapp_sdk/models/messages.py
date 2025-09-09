"""Message models for WhatsApp SDK.

These models represent all message types supported by WhatsApp Business API.
Includes both request models (what users send) and response models (what API returns).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# TEXT MESSAGE MODELS
# ============================================================================


class TextMessage(BaseModel):
    """Text message request model.

    Used to send plain text or text with URL preview.
    """

    body: str = Field(
        ..., max_length=4096, description="The text content of the message (max 4096 chars)"
    )
    preview_url: bool = Field(False, description="Enable URL preview for links in the message")


# ============================================================================
# MEDIA MESSAGE MODELS
# ============================================================================


class ImageMessage(BaseModel):
    """Image message request model.

    Send images via media ID or URL.
    """

    id: Optional[str] = Field(None, description="Media ID from uploaded image")
    link: Optional[str] = Field(None, description="URL of the image (HTTPS only)")
    caption: Optional[str] = Field(
        None, max_length=1024, description="Optional caption for the image (max 1024 chars)"
    )

    @field_validator("id", "link")
    @classmethod
    def validate_media_source(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Ensure either id or link is provided, not both."""
        if info.field_name == "link" and v and info.data.get("id"):
            raise ValueError("Provide either 'id' or 'link', not both")
        return v


class DocumentMessage(BaseModel):
    """Document message request model.

    Send documents/files via media ID or URL.
    """

    id: Optional[str] = Field(None, description="Media ID from uploaded document")
    link: Optional[str] = Field(None, description="URL of the document (HTTPS only)")
    caption: Optional[str] = Field(
        None, max_length=1024, description="Optional caption for the document (max 1024 chars)"
    )
    filename: Optional[str] = Field(
        None, description="Filename to display (required when using link)"
    )

    @field_validator("id", "link")
    @classmethod
    def validate_media_source(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Ensure either id or link is provided, not both."""
        if info.field_name == "link" and v and info.data.get("id"):
            raise ValueError("Provide either 'id' or 'link', not both")
        return v


class AudioMessage(BaseModel):
    """Audio message request model.

    Send audio files via media ID or URL.
    """

    id: Optional[str] = Field(None, description="Media ID from uploaded audio")
    link: Optional[str] = Field(None, description="URL of the audio file (HTTPS only)")

    @field_validator("id", "link")
    @classmethod
    def validate_media_source(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Ensure either id or link is provided, not both."""
        if info.field_name == "link" and v and info.data.get("id"):
            raise ValueError("Provide either 'id' or 'link', not both")
        return v


class VideoMessage(BaseModel):
    """Video message request model.

    Send videos via media ID or URL.
    """

    id: Optional[str] = Field(None, description="Media ID from uploaded video")
    link: Optional[str] = Field(None, description="URL of the video file (HTTPS only)")
    caption: Optional[str] = Field(
        None, max_length=1024, description="Optional caption for the video (max 1024 chars)"
    )

    @field_validator("id", "link")
    @classmethod
    def validate_media_source(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Ensure either id or link is provided, not both."""
        if info.field_name == "link" and v and info.data.get("id"):
            raise ValueError("Provide either 'id' or 'link', not both")
        return v


class StickerMessage(BaseModel):
    """Sticker message request model.

    Send stickers via media ID or URL.
    """

    id: Optional[str] = Field(None, description="Media ID from uploaded sticker")
    link: Optional[str] = Field(
        None, description="URL of the sticker file (HTTPS only, WebP format)"
    )

    @field_validator("id", "link")
    @classmethod
    def validate_media_source(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Ensure either id or link is provided, not both."""
        if info.field_name == "link" and v and info.data.get("id"):
            raise ValueError("Provide either 'id' or 'link', not both")
        return v


# ============================================================================
# LOCATION MESSAGE MODEL
# ============================================================================


class LocationMessage(BaseModel):
    """Location message request model.

    Send geographic location with optional details.
    """

    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the location")
    name: Optional[str] = Field(None, description="Name of the location")
    address: Optional[str] = Field(None, description="Address of the location")


# ============================================================================
# INTERACTIVE MESSAGE MODELS
# ============================================================================


class InteractiveHeader(BaseModel):
    """Header for interactive messages."""

    type: str = Field(..., description="Header type: text, image, video, or document")
    text: Optional[str] = Field(None, description="Text for text headers")
    image: Union[ImageMessage, Dict[str, str], None] = Field(
        None, description="Image for image headers"
    )
    video: Union[VideoMessage, Dict[str, str], None] = Field(
        None, description="Video for video headers"
    )
    document: Union[DocumentMessage, Dict[str, str], None] = Field(
        None, description="Document for document headers"
    )


class InteractiveBody(BaseModel):
    """Body for interactive messages."""

    text: str = Field(..., max_length=1024, description="Body text (max 1024 chars)")


class InteractiveFooter(BaseModel):
    """Footer for interactive messages."""

    text: str = Field(..., max_length=60, description="Footer text (max 60 chars)")


class Button(BaseModel):
    """Button for interactive messages."""

    type: str = Field("reply", description="Button type (reply)")
    reply: Dict[str, str] = Field(..., description="Reply button with 'id' and 'title'")


class Section(BaseModel):
    """Section for list messages."""

    title: Optional[str] = Field(None, max_length=24, description="Section title (max 24 chars)")
    rows: List[Dict[str, str]] = Field(
        ..., description="List of rows with 'id', 'title', and optional 'description'"
    )


class InteractiveAction(BaseModel):
    """Action for interactive messages."""

    buttons: Optional[List[Button]] = Field(
        None, max_length=3, description="List of buttons (max 3)"
    )
    button: Optional[str] = Field(None, description="Button text for list messages")
    sections: Optional[List[Section]] = Field(
        None, max_length=10, description="List sections (max 10)"
    )
    name: Optional[str] = Field(None, description="Action name for CTA URL buttons")
    parameters: Optional[Dict[str, str]] = Field(None, description="Parameters for CTA URL buttons")


class InteractiveMessage(BaseModel):
    """Interactive message request model.

    Send messages with buttons, lists, or CTA URLs.
    """

    type: str = Field(..., description="Interactive type: button, list, or cta_url")
    header: Optional[InteractiveHeader] = Field(None, description="Optional header")
    body: InteractiveBody = Field(..., description="Message body (required)")
    footer: Optional[InteractiveFooter] = Field(None, description="Optional footer")
    action: InteractiveAction = Field(..., description="Interactive action (required)")


# ============================================================================
# TEMPLATE MESSAGE MODELS
# ============================================================================


class TemplateParameter(BaseModel):
    """Parameter for template components."""

    type: str = Field(
        ..., description="Parameter type: text, currency, date_time, image, document, video"
    )
    text: Optional[str] = Field(None, description="Text value for text parameters")
    image: Union[ImageMessage, Dict[str, str], None] = Field(
        None, description="Image for image parameters"
    )
    video: Union[VideoMessage, Dict[str, str], None] = Field(
        None, description="Video for video parameters"
    )
    document: Union[DocumentMessage, Dict[str, str], None] = Field(
        None, description="Document for document parameters"
    )
    currency: Optional[Dict[str, Any]] = Field(
        None, description="Currency object with fallback_value, code, amount_1000"
    )
    date_time: Optional[Dict[str, Any]] = Field(
        None, description="Date time object with fallback_value"
    )


class TemplateComponent(BaseModel):
    """Component for template messages."""

    type: str = Field(..., description="Component type: header, body, button")
    sub_type: Optional[str] = Field(None, description="Button sub-type: quick_reply, url")
    index: Optional[int] = Field(None, description="Button index (0-based)")
    parameters: List[TemplateParameter] = Field(
        default_factory=list, description="Component parameters"
    )


class TemplateLanguage(BaseModel):
    """Language settings for template messages."""

    code: str = Field(..., description="Language code (e.g., en_US, es_ES)")
    policy: str = Field("deterministic", description="Language policy: deterministic or fallback")


class TemplateMessage(BaseModel):
    """Template message request model.

    Send pre-approved template messages with parameters.
    """

    name: str = Field(..., description="Template name (must be approved)")
    language: TemplateLanguage = Field(..., description="Template language settings")
    components: Optional[List[TemplateComponent]] = Field(
        None, description="Template components with parameters"
    )


# ============================================================================
# REACTION MESSAGE MODEL
# ============================================================================


class ReactionMessage(BaseModel):
    """Reaction message request model.

    Send emoji reactions to messages.
    """

    message_id: str = Field(..., description="ID of the message to react to")
    emoji: str = Field(..., description="Emoji to react with (or empty string to remove)")


# ============================================================================
# MESSAGE STATUS MODEL
# ============================================================================


class MessageStatus(BaseModel):
    """Message status update model.

    Represents status updates for sent messages.
    """

    id: str = Field(..., description="Message ID")
    status: str = Field(..., description="Status: sent, delivered, read, failed")
    timestamp: str = Field(..., description="Unix timestamp of status update")
    recipient_id: str = Field(..., description="Recipient's WhatsApp ID")
    conversation: Optional[Dict[str, Any]] = Field(None, description="Conversation details")
    pricing: Optional[Dict[str, Any]] = Field(None, description="Pricing information")
    errors: Optional[List[Dict[str, Any]]] = Field(
        None, description="Error details if status is failed"
    )
