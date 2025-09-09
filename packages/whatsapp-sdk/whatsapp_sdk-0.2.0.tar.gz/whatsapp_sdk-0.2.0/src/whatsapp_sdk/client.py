"""WhatsApp Business SDK Client.

Main client for interacting with the WhatsApp Business API.
This client wires all services together and provides a clean entry point.
"""

from __future__ import annotations

import os
from typing import Optional

from .config import WhatsAppConfig
from .http_client import HTTPClient
from .services import MediaService, MessagesService, TemplatesService, WebhooksService


class WhatsAppClient:
    """Main WhatsApp Business API client.

    This client provides access to all WhatsApp Business API services
    through a simple, synchronous interface.

    Examples:
        # Initialize with direct parameters
        client = WhatsAppClient(
            phone_number_id="123456789",
            access_token="your_token"
        )

        # Initialize from environment
        client = WhatsAppClient.from_env()

        # Send a message
        response = client.messages.send_text(
            to="+1234567890",
            body="Hello from WhatsApp SDK!"
        )
    """

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        app_secret: Optional[str] = None,
        webhook_verify_token: Optional[str] = None,
        base_url: str = "https://graph.facebook.com",
        api_version: str = "v23.0",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit: int = 80,
    ):
        """Initialize WhatsApp client.

        Args:
            phone_number_id: WhatsApp Business phone number ID
            access_token: Meta access token
            app_secret: App secret for webhook signature validation
            webhook_verify_token: Token for webhook verification
            base_url: API base URL (defaults to Meta's URL)
            api_version: API version (defaults to v23.0)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit: Requests per second limit
        """
        # Create configuration
        self.config = WhatsAppConfig(
            phone_number_id=phone_number_id,
            access_token=access_token,
            app_secret=app_secret,
            webhook_verify_token=webhook_verify_token,
            base_url=base_url,
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit=rate_limit,
        )

        # Store phone number ID for services
        self.phone_number_id = phone_number_id

        # Initialize HTTP client
        self.http_client = HTTPClient(self.config)

        # Initialize services
        self._init_services()

    def _init_services(self) -> None:
        """Initialize all service modules."""
        # Messages service
        self.messages = MessagesService(
            http_client=self.http_client, config=self.config, phone_number_id=self.phone_number_id
        )

        # Templates service
        self.templates = TemplatesService(
            http_client=self.http_client, config=self.config, phone_number_id=self.phone_number_id
        )

        # Media service
        self.media = MediaService(
            http_client=self.http_client, config=self.config, phone_number_id=self.phone_number_id
        )

        # Webhooks service (doesn't need phone_number_id)
        self.webhooks = WebhooksService(config=self.config)

    @classmethod
    def from_env(cls) -> WhatsAppClient:
        """Create client from environment variables.

        Required environment variables:
            - WHATSAPP_PHONE_NUMBER_ID
            - WHATSAPP_ACCESS_TOKEN

        Optional environment variables:
            - WHATSAPP_APP_SECRET
            - WHATSAPP_WEBHOOK_VERIFY_TOKEN
            - WHATSAPP_API_VERSION
            - WHATSAPP_BASE_URL
            - WHATSAPP_TIMEOUT
            - WHATSAPP_MAX_RETRIES
            - WHATSAPP_RATE_LIMIT

        Returns:
            WhatsAppClient instance configured from environment

        Raises:
            ValueError: If required environment variables are missing

        Example:
            # Set environment variables
            export WHATSAPP_PHONE_NUMBER_ID="123456789"
            export WHATSAPP_ACCESS_TOKEN="your_token"

            # Create client
            client = WhatsAppClient.from_env()
        """
        phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
        access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")

        if not phone_number_id:
            raise ValueError("WHATSAPP_PHONE_NUMBER_ID environment variable is required")
        if not access_token:
            raise ValueError("WHATSAPP_ACCESS_TOKEN environment variable is required")

        return cls(
            phone_number_id=phone_number_id,
            access_token=access_token,
            app_secret=os.environ.get("WHATSAPP_APP_SECRET"),
            webhook_verify_token=os.environ.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN"),
            base_url=os.environ.get("WHATSAPP_BASE_URL") or "https://graph.facebook.com",
            api_version=os.environ.get("WHATSAPP_API_VERSION") or "v18.0",
            timeout=int(os.environ.get("WHATSAPP_TIMEOUT", "30")),
            max_retries=int(os.environ.get("WHATSAPP_MAX_RETRIES", "3")),
            rate_limit=int(os.environ.get("WHATSAPP_RATE_LIMIT", "80")),
        )

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"WhatsAppClient(phone_number_id={self.phone_number_id})"
