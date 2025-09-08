"""Exception classes for WhatsApp SDK.

Custom exceptions for different error scenarios in the SDK.
"""


class WhatsAppError(Exception):
    """Base exception for all WhatsApp SDK errors."""

    pass


class WhatsAppAPIError(WhatsAppError):
    """General API error from WhatsApp."""

    pass


class WhatsAppAuthenticationError(WhatsAppError):
    """Authentication/authorization error."""

    pass


class WhatsAppRateLimitError(WhatsAppError):
    """Rate limit exceeded error."""

    pass


class WhatsAppValidationError(WhatsAppError):
    """Request validation error."""

    pass


class WhatsAppWebhookError(WhatsAppError):
    """Webhook processing error."""

    pass


class WhatsAppMediaError(WhatsAppError):
    """Media upload/download error."""

    pass


class WhatsAppTimeoutError(WhatsAppError):
    """Request timeout error."""

    pass


class WhatsAppConfigError(WhatsAppError):
    """Configuration error."""

    pass
