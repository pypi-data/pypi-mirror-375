"""Template models for WhatsApp SDK.

These models handle template management including creation,
listing, and deletion of message templates.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TemplateButton(BaseModel):
    """Template button definition.

    Represents buttons in template definitions.
    """

    type: str = Field(..., description="Button type: QUICK_REPLY, URL, or PHONE_NUMBER")
    text: str = Field(..., description="Button text")
    url: Optional[str] = Field(
        None, description="URL for URL buttons (can include {{1}} placeholder)"
    )
    phone_number: Optional[str] = Field(None, description="Phone number for PHONE_NUMBER buttons")
    example: Optional[List[str]] = Field(None, description="Example values for URL placeholders")


class TemplateHeaderExample(BaseModel):
    """Example values for template header."""

    header_text: Optional[List[str]] = Field(
        None, description="Example text values for header placeholders"
    )
    header_handle: Optional[List[str]] = Field(
        None, description="Example media handles for media headers"
    )


class TemplateBodyExample(BaseModel):
    """Example values for template body."""

    body_text: Optional[List[List[str]]] = Field(
        None, description="Example text values for body placeholders"
    )


class TemplateExample(BaseModel):
    """Combined examples for template."""

    header_text: Optional[List[str]] = Field(None, description="Header text examples")
    body_text: Optional[List[List[str]]] = Field(None, description="Body text examples")
    header_handle: Optional[List[str]] = Field(None, description="Header media handle examples")


class TemplateComponentDefinition(BaseModel):
    """Template component definition for creating templates."""

    type: str = Field(..., description="Component type: HEADER, BODY, FOOTER, or BUTTONS")
    format: Optional[str] = Field(None, description="Header format: TEXT, IMAGE, VIDEO, DOCUMENT")
    text: Optional[str] = Field(None, description="Component text with {{placeholders}}")
    buttons: Optional[List[TemplateButton]] = Field(
        None, description="List of buttons for BUTTONS component"
    )
    example: Optional[TemplateExample] = Field(None, description="Example values for placeholders")


class Template(BaseModel):
    """Complete template definition.

    Represents a message template in the system.
    """

    id: Optional[str] = Field(None, description="Template ID")
    name: str = Field(..., description="Template name (unique identifier)")
    language: str = Field(..., description="Template language code (e.g., en_US)")
    category: str = Field(
        ..., description="Template category: MARKETING, UTILITY, or AUTHENTICATION"
    )
    components: List[TemplateComponentDefinition] = Field(..., description="Template components")
    status: Optional[str] = Field(None, description="Template status: APPROVED, PENDING, REJECTED")
    rejected_reason: Optional[str] = Field(
        None, description="Reason for rejection if status is REJECTED"
    )
    quality_score: Optional[Dict[str, Any]] = Field(
        None, description="Template quality score information"
    )


class TemplateResponse(BaseModel):
    """Response after creating a template."""

    id: str = Field(..., description="Template ID")
    status: str = Field(..., description="Template status")
    category: Optional[str] = Field(None, description="Template category")


class TemplateListResponse(BaseModel):
    """Response when listing templates."""

    data: List[Template] = Field(..., description="List of templates")
    paging: Optional[Dict[str, Any]] = Field(None, description="Pagination information")


class TemplateDeleteResponse(BaseModel):
    """Response after deleting a template."""

    success: bool = Field(..., description="Whether deletion was successful")


class MessageTemplateUpdate(BaseModel):
    """Update existing template components."""

    components: List[TemplateComponentDefinition] = Field(
        ..., description="Updated template components"
    )


class TemplateAnalytics(BaseModel):
    """Template performance analytics."""

    template_id: str = Field(..., description="Template ID")
    template_name: str = Field(..., description="Template name")
    sent: int = Field(0, description="Number of messages sent")
    delivered: int = Field(0, description="Number of messages delivered")
    read: int = Field(0, description="Number of messages read")
    clicked: Optional[int] = Field(
        None, description="Number of button clicks (for templates with buttons)"
    )
    start_time: str = Field(..., description="Analytics period start time")
    end_time: str = Field(..., description="Analytics period end time")
