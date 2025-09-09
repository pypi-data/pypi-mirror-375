"""Webhook models for WhatsApp SDK.

These models handle incoming webhook events from WhatsApp,
including messages, status updates, and system notifications.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# WEBHOOK MESSAGE TYPES
# ============================================================================


class WebhookTextMessage(BaseModel):
    """Incoming text message."""

    body: str = Field(..., description="Text content of the message")


class WebhookImageMessage(BaseModel):
    """Incoming image message."""

    id: str = Field(..., description="Media ID of the image")
    mime_type: str = Field(..., description="MIME type of the image")
    sha256: str = Field(..., description="SHA256 hash of the image")
    caption: Optional[str] = Field(None, description="Optional caption")


class WebhookVideoMessage(BaseModel):
    """Incoming video message."""

    id: str = Field(..., description="Media ID of the video")
    mime_type: str = Field(..., description="MIME type of the video")
    sha256: str = Field(..., description="SHA256 hash of the video")
    caption: Optional[str] = Field(None, description="Optional caption")


class WebhookAudioMessage(BaseModel):
    """Incoming audio message."""

    id: str = Field(..., description="Media ID of the audio")
    mime_type: str = Field(..., description="MIME type of the audio")
    sha256: str = Field(..., description="SHA256 hash of the audio")
    voice: Optional[bool] = Field(None, description="Whether this is a voice message")


class WebhookDocumentMessage(BaseModel):
    """Incoming document message."""

    id: str = Field(..., description="Media ID of the document")
    mime_type: str = Field(..., description="MIME type of the document")
    sha256: str = Field(..., description="SHA256 hash of the document")
    caption: Optional[str] = Field(None, description="Optional caption")
    filename: Optional[str] = Field(None, description="Document filename")


class WebhookLocationMessage(BaseModel):
    """Incoming location message."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    name: Optional[str] = Field(None, description="Location name")
    address: Optional[str] = Field(None, description="Location address")


class WebhookStickerMessage(BaseModel):
    """Incoming sticker message."""

    id: str = Field(..., description="Media ID of the sticker")
    mime_type: str = Field(..., description="MIME type of the sticker")
    sha256: str = Field(..., description="SHA256 hash of the sticker")
    animated: Optional[bool] = Field(None, description="Whether the sticker is animated")


class WebhookButtonReply(BaseModel):
    """Button reply from interactive message."""

    id: str = Field(..., description="Button ID that was clicked")
    title: str = Field(..., description="Button title that was clicked")


class WebhookListReply(BaseModel):
    """List selection from interactive message."""

    id: str = Field(..., description="Selected row ID")
    title: str = Field(..., description="Selected row title")
    description: Optional[str] = Field(None, description="Selected row description")


class WebhookInteractiveMessage(BaseModel):
    """Incoming interactive message response."""

    type: str = Field(..., description="Interactive type: button_reply or list_reply")
    button_reply: Optional[WebhookButtonReply] = Field(None, description="Button reply data")
    list_reply: Optional[WebhookListReply] = Field(None, description="List selection data")


class WebhookReactionMessage(BaseModel):
    """Incoming reaction message."""

    message_id: str = Field(..., description="ID of the message being reacted to")
    emoji: str = Field(..., description="Emoji used for reaction")


class WebhookContext(BaseModel):
    """Message context (for replies)."""

    from_: str = Field(..., alias="from", description="Sender of the original message")
    id: str = Field(..., description="ID of the message being replied to")


# ============================================================================
# WEBHOOK MESSAGE WRAPPER
# ============================================================================


class WebhookMessage(BaseModel):
    """Complete incoming message from webhook."""

    from_: str = Field(..., alias="from", description="Sender's WhatsApp ID")
    id: str = Field(..., description="Message ID")
    timestamp: str = Field(..., description="Unix timestamp when message was sent")
    type: str = Field(
        ...,
        description="Message type: text, image, video, audio, document, location, sticker, interactive, reaction",
    )
    context: Optional[WebhookContext] = Field(None, description="Context if this is a reply")
    text: Optional[WebhookTextMessage] = Field(None, description="Text message data")
    image: Optional[WebhookImageMessage] = Field(None, description="Image message data")
    video: Optional[WebhookVideoMessage] = Field(None, description="Video message data")
    audio: Optional[WebhookAudioMessage] = Field(None, description="Audio message data")
    document: Optional[WebhookDocumentMessage] = Field(None, description="Document message data")
    location: Optional[WebhookLocationMessage] = Field(None, description="Location message data")
    sticker: Optional[WebhookStickerMessage] = Field(None, description="Sticker message data")
    interactive: Optional[WebhookInteractiveMessage] = Field(
        None, description="Interactive message response data"
    )
    reaction: Optional[WebhookReactionMessage] = Field(None, description="Reaction message data")
    contacts: List[Dict[str, Optional[Any]]] = Field(default_factory=list, description="Contact cards shared")
    errors: List[Dict[str, Optional[Any]]] = Field(
        default_factory=list, description="Any errors associated with the message"
    )


# ============================================================================
# WEBHOOK STATUS UPDATE
# ============================================================================


class WebhookStatus(BaseModel):
    """Message status update from webhook."""

    id: str = Field(..., description="Message ID")
    status: str = Field(..., description="Status: sent, delivered, read, failed")
    timestamp: str = Field(..., description="Unix timestamp of status update")
    recipient_id: str = Field(..., description="Recipient's WhatsApp ID")
    conversation: Dict[str, Optional[Any]] = Field(default_factory=dict, description="Conversation details")
    pricing: Dict[str, Optional[Any]] = Field(default_factory=dict, description="Pricing information")
    errors: List[Dict[str, Optional[Any]]] = Field(
        default_factory=list, description="Error details if status is failed"
    )


# ============================================================================
# WEBHOOK METADATA
# ============================================================================


class WebhookMetadata(BaseModel):
    """Metadata about the webhook source."""

    display_phone_number: str = Field(..., description="Display phone number")
    phone_number_id: str = Field(..., description="Phone number ID")


class WebhookContact(BaseModel):
    """Contact information from webhook."""

    profile: Dict[str, Optional[str]] = Field(default_factory=dict, description="Contact profile with name")
    wa_id: str = Field(..., description="WhatsApp ID of the contact")


# ============================================================================
# WEBHOOK VALUE (MAIN PAYLOAD)
# ============================================================================


class WebhookValue(BaseModel):
    """Main webhook value containing messages or statuses."""

    messaging_product: str = Field("whatsapp", description="Always 'whatsapp'")
    metadata: WebhookMetadata = Field(..., description="Webhook metadata")
    contacts: Optional[List[WebhookContact]] = Field(None, description="Contact information")
    messages: Optional[List[WebhookMessage]] = Field(None, description="Incoming messages")
    statuses: Optional[List[WebhookStatus]] = Field(None, description="Status updates")
    errors: List[Dict[str, Optional[Any]]] = Field(default_factory=list, description="Any errors")


class WebhookChange(BaseModel):
    """Webhook change event."""

    value: WebhookValue = Field(..., description="Change value")
    field: str = Field(..., description="Field that changed (usually 'messages')")


class WebhookEntry(BaseModel):
    """Webhook entry containing changes."""

    id: str = Field(..., description="Business account ID")
    changes: List[WebhookChange] = Field(..., description="List of changes")


class WebhookEvent(BaseModel):
    """Complete webhook event from WhatsApp."""

    object: str = Field(..., description="Object type (usually 'whatsapp_business_account')")
    entry: List[WebhookEntry] = Field(..., description="List of entries")


# ============================================================================
# WEBHOOK VERIFICATION
# ============================================================================


class WebhookVerification(BaseModel):
    """Webhook verification request."""

    hub_mode: str = Field(..., alias="hub.mode", description="Should be 'subscribe'")
    hub_challenge: str = Field(..., alias="hub.challenge", description="Challenge to echo back")
    hub_verify_token: str = Field(
        ..., alias="hub.verify_token", description="Verify token to validate"
    )
