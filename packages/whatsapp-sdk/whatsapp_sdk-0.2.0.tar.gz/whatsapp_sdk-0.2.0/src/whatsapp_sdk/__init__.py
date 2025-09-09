"""WhatsApp Business SDK for Python.

A comprehensive, synchronous SDK for the WhatsApp Business API.
"""

from __future__ import annotations

__version__ = "0.2.0"

from .client import WhatsAppClient
from .config import WhatsAppConfig
from .exceptions import (
    WhatsAppAPIError,
    WhatsAppAuthenticationError,
    WhatsAppConfigError,
    WhatsAppError,
    WhatsAppMediaError,
    WhatsAppRateLimitError,
    WhatsAppTimeoutError,
    WhatsAppValidationError,
    WhatsAppWebhookError,
)

# Import all models for convenience
from .models import (  # Base models; Webhook models
    AudioMessage,
    ContactMessage,
    DocumentMessage,
    ImageMessage,
    InteractiveMessage,
    LocationMessage,
    MessageResponse,
    TemplateMessage,
    TextMessage,
    VideoMessage,
    WebhookEvent,
    WebhookMessage,
)

__all__ = [
    "AudioMessage",
    "ContactMessage",
    "DocumentMessage",
    "ImageMessage",
    "InteractiveMessage",
    "LocationMessage",
    "MessageResponse",
    "TemplateMessage",
    "TextMessage",
    "VideoMessage",
    "WebhookEvent",
    "WebhookMessage",
    "WhatsAppAPIError",
    "WhatsAppAuthenticationError",
    "WhatsAppClient",
    "WhatsAppConfig",
    "WhatsAppConfigError",
    "WhatsAppError",
    "WhatsAppMediaError",
    "WhatsAppRateLimitError",
    "WhatsAppTimeoutError",
    "WhatsAppValidationError",
    "WhatsAppWebhookError",
]
