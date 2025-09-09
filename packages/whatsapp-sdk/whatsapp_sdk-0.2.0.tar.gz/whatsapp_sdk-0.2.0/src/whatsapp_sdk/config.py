"""Configuration module for WhatsApp SDK.

Handles all configuration settings and validation.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class WhatsAppConfig(BaseModel):
    """Configuration for WhatsApp SDK.

    Contains all settings needed to interact with the WhatsApp Business API.
    """

    phone_number_id: str = Field(..., description="WhatsApp Business phone number ID")
    access_token: str = Field(..., description="Meta access token for API authentication")
    app_secret: Optional[str] = Field(
        None, description="App secret for webhook signature validation"
    )
    webhook_verify_token: Optional[str] = Field(None, description="Token for webhook verification")
    base_url: str = Field("https://graph.facebook.com", description="Meta Graph API base URL")
    api_version: str = Field("v23.0", description="WhatsApp API version")
    timeout: int = Field(30, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, description="Maximum number of retries for failed requests")
    rate_limit: int = Field(80, gt=0, description="Maximum requests per second")

    class Config:
        """Pydantic config."""

        validate_assignment = True
