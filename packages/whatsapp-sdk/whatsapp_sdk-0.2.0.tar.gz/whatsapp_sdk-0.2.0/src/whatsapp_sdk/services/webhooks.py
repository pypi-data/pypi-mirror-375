"""Webhooks service for WhatsApp SDK.

Handles webhook verification, signature validation, and event parsing
for incoming WhatsApp webhook events.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from whatsapp_sdk.exceptions import WhatsAppWebhookError
from whatsapp_sdk.models import WebhookEvent, WebhookMessage, WebhookStatus

if TYPE_CHECKING:
    from whatsapp_sdk.config import WhatsAppConfig


class WebhooksService:
    """Service for handling WhatsApp webhooks.

    Handles webhook verification, signature validation, and event parsing.
    """

    def __init__(self, config: WhatsAppConfig):
        """Initialize webhooks service.

        Args:
            config: WhatsApp configuration
        """
        self.config = config

    # ========================================================================
    # WEBHOOK VERIFICATION
    # ========================================================================

    def verify_token(self, token: str) -> bool:
        """Verify webhook token during setup.

        Args:
            token: Token received from webhook verification request

        Returns:
            True if token is valid

        Example:
            # In your webhook endpoint
            if webhooks.verify_token(request.args.get("hub.verify_token")):
                return request.args.get("hub.challenge")
        """
        if not self.config.webhook_verify_token:
            raise WhatsAppWebhookError("Webhook verify token not configured")

        return token == self.config.webhook_verify_token

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        """Verify webhook signature for security.

        Args:
            signature: X-Hub-Signature-256 header value
            payload: Raw request body as bytes

        Returns:
            True if signature is valid

        Example:
            # In your webhook endpoint
            signature = request.headers.get("X-Hub-Signature-256")
            payload = request.get_data()

            if not webhooks.verify_signature(signature, payload):
                return "Invalid signature", 403
        """
        if not self.config.app_secret:
            raise WhatsAppWebhookError("App secret not configured")

        # Extract the hash from the signature (format: sha256=hash)
        if not signature or not signature.startswith("sha256="):
            return False

        signature_hash = signature[7:]  # Remove "sha256=" prefix

        # Calculate expected hash
        expected_hash = hmac.new(
            self.config.app_secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        # Compare hashes (constant time comparison for security)
        return hmac.compare_digest(signature_hash, expected_hash)

    # ========================================================================
    # EVENT PARSING
    # ========================================================================

    def parse_event(self, payload: Dict[str, Any]) -> WebhookEvent:
        """Parse webhook event payload.

        Args:
            payload: Webhook JSON payload

        Returns:
            WebhookEvent object with parsed data

        Example:
            # In your webhook endpoint
            event = webhooks.parse_event(request.json)

            for entry in event.entry:
                for change in entry.changes:
                    if change.value.messages:
                        for message in change.value.messages:
                            process_message(message)
        """
        return WebhookEvent(**payload)

    def process_message(self, message: Dict[str, Any]) -> WebhookMessage:
        """Process a single message from webhook.

        Args:
            message: Message dictionary from webhook

        Returns:
            WebhookMessage object

        Example:
            # Process incoming message
            webhook_message = webhooks.process_message(message_dict)

            if webhook_message.type == "text":
                print(f"Received text: {webhook_message.text.body}")
            elif webhook_message.type == "image":
                print(f"Received image: {webhook_message.image.id}")
        """
        return WebhookMessage(**message)

    def process_status(self, status: Dict[str, Any]) -> WebhookStatus:
        """Process a status update from webhook.

        Args:
            status: Status dictionary from webhook

        Returns:
            WebhookStatus object

        Example:
            # Process status update
            webhook_status = webhooks.process_status(status_dict)

            if webhook_status.status == "delivered":
                print(f"Message {webhook_status.id} was delivered")
            elif webhook_status.status == "read":
                print(f"Message {webhook_status.id} was read")
        """
        return WebhookStatus(**status)

    # ========================================================================
    # WEBHOOK HANDLER HELPERS
    # ========================================================================

    def handle_verification(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Handle webhook verification request.

        Args:
            mode: hub.mode parameter (should be "subscribe")
            token: hub.verify_token parameter
            challenge: hub.challenge parameter to echo back

        Returns:
            Challenge string if verification successful, None otherwise

        Example:
            # FastAPI example
            @app.get("/webhook")
            def verify_webhook(
                hub_mode: str = Query(None, alias="hub.mode"),
                hub_verify_token: str = Query(None, alias="hub.verify_token"),
                hub_challenge: str = Query(None, alias="hub.challenge")
            ):
                result = webhooks.handle_verification(
                    hub_mode,
                    hub_verify_token,
                    hub_challenge
                )
                if result:
                    return result
                return Response(status_code=403)
        """
        if mode == "subscribe" and self.verify_token(token):
            return challenge
        return None

    def handle_event(self, signature: str, payload: bytes) -> WebhookEvent:
        """Handle incoming webhook event with validation.

        Args:
            signature: X-Hub-Signature-256 header value
            payload: Raw request body as bytes

        Returns:
            Parsed WebhookEvent if valid

        Raises:
            WhatsAppWebhookError: If signature is invalid

        Example:
            # FastAPI example
            @app.post("/webhook")
            async def handle_webhook(
                request: Request,
                x_hub_signature_256: str = Header(None)
            ):
                body = await request.body()

                try:
                    event = webhooks.handle_event(x_hub_signature_256, body)
                    # Process event...
                    return {"status": "ok"}
                except WhatsAppWebhookError as e:
                    return Response(status_code=403)
        """
        # Verify signature
        if not self.verify_signature(signature, payload):
            raise WhatsAppWebhookError("Invalid webhook signature")

        # Parse payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise WhatsAppWebhookError("Invalid JSON payload") from None

        return self.parse_event(data)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def extract_messages(self, event: WebhookEvent) -> List[WebhookMessage]:
        """Extract all messages from a webhook event.

        Args:
            event: WebhookEvent object

        Returns:
            List of WebhookMessage objects

        Example:
            event = webhooks.parse_event(payload)
            messages = webhooks.extract_messages(event)

            for message in messages:
                print(f"From: {message.from_}")
                print(f"Type: {message.type}")
        """
        messages = []

        for entry in event.entry:
            for change in entry.changes:
                if change.value.messages:
                    for msg in change.value.messages:
                        messages.append(msg)

        return messages

    def extract_statuses(self, event: WebhookEvent) -> List[WebhookStatus]:
        """Extract all status updates from a webhook event.

        Args:
            event: WebhookEvent object

        Returns:
            List of WebhookStatus objects

        Example:
            event = webhooks.parse_event(payload)
            statuses = webhooks.extract_statuses(event)

            for status in statuses:
                print(f"Message ID: {status.id}")
                print(f"Status: {status.status}")
        """
        statuses = []

        for entry in event.entry:
            for change in entry.changes:
                if change.value.statuses:
                    for status in change.value.statuses:
                        statuses.append(status)

        return statuses
