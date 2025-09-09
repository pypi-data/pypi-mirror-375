"""Exception classes for WhatsApp SDK.

Custom exceptions for different error scenarios in the SDK.
"""

from __future__ import annotations


class WhatsAppError(Exception):
    """Base exception for all WhatsApp SDK errors."""


class WhatsAppAPIError(WhatsAppError):
    """General API error from WhatsApp."""


class WhatsAppAuthenticationError(WhatsAppError):
    """Authentication/authorization error."""


class WhatsAppRateLimitError(WhatsAppError):
    """Rate limit exceeded error."""


class WhatsAppValidationError(WhatsAppError):
    """Request validation error."""


class WhatsAppWebhookError(WhatsAppError):
    """Webhook processing error."""


class WhatsAppMediaError(WhatsAppError):
    """Media upload/download error."""


class WhatsAppTimeoutError(WhatsAppError):
    """Request timeout error."""


class WhatsAppConfigError(WhatsAppError):
    """Configuration error."""
