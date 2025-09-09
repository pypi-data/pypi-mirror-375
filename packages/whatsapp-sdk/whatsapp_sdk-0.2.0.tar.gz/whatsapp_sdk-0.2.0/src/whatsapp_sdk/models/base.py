"""Base Pydantic models for WhatsApp SDK.

These models represent the core structures used across the SDK,
matching Meta's WhatsApp Cloud API v23.0 exactly.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model for WhatsApp API responses.

    All WhatsApp API responses include these common fields.
    """

    messaging_product: str = Field(
        default="whatsapp", description="The messaging product (always 'whatsapp')"
    )

    class Config:
        extra = "allow"  # Allow additional fields from API


class Contact(BaseModel):
    """Contact information in API responses.

    Represents a WhatsApp contact that was processed.
    """

    input: str = Field(..., description="The phone number input originally provided")
    wa_id: str = Field(..., description="The WhatsApp ID of the contact (formatted phone number)")

    class Config:
        extra = "allow"


class Message(BaseModel):
    """Message information in API responses.

    Represents a sent message confirmation.
    """

    id: str = Field(..., description="The unique message ID from WhatsApp")

    class Config:
        extra = "allow"


class Error(BaseModel):
    """Error model matching Meta's error format.

    WhatsApp API errors follow this structure.
    """

    code: int = Field(..., description="Error code from WhatsApp API")
    title: Optional[str] = Field(None, description="Short error title")
    message: str = Field(..., description="Detailed error message")
    error_data: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    error_subcode: Optional[int] = Field(None, description="More specific error subcode")
    error_user_title: Optional[str] = Field(None, description="User-friendly error title")
    error_user_msg: Optional[str] = Field(None, description="User-friendly error message")
    fbtrace_id: Optional[str] = Field(None, description="Facebook trace ID for debugging")

    class Config:
        extra = "allow"


class ErrorResponse(BaseModel):
    """Complete error response from WhatsApp API."""

    error: Error = Field(..., description="The error details")

    class Config:
        extra = "allow"


class MessageResponse(BaseResponse):
    """Standard response after sending a message.

    This is the response you get when successfully sending any message type.
    """

    contacts: List[Contact] = Field(
        default_factory=list, description="List of contacts that were processed"
    )
    messages: List[Message] = Field(
        default_factory=list, description="List of messages that were sent"
    )

    class Config:
        extra = "allow"


class PaginationCursor(BaseModel):
    """Pagination cursor for list responses."""

    before: Optional[str] = Field(None, description="Cursor for previous page")
    after: Optional[str] = Field(None, description="Cursor for next page")


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""

    cursors: Optional[PaginationCursor] = Field(None, description="Pagination cursors")
    next: Optional[str] = Field(None, description="URL for next page")
    previous: Optional[str] = Field(None, description="URL for previous page")
