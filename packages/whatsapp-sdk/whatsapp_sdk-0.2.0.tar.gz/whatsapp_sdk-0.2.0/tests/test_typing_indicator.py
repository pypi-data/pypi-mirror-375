"""Tests for Typing Indicator functionality."""


from __future__ import annotations

import pytest

from whatsapp_sdk.models import MessageResponse
from whatsapp_sdk.services.messages import MessagesService


class TestTypingIndicator:
    """Test typing indicator functionality."""

    @pytest.fixture()
    def messages_service(self, mock_http_client, mock_config):
        """Create messages service with mocked dependencies."""
        return MessagesService(
            http_client=mock_http_client,
            config=mock_config,
            phone_number_id="123456789",
        )

    def test_mark_as_read_without_typing(self, messages_service, mock_http_client):
        """Test marking message as read without typing indicator."""
        mock_response = {
            "messaging_product": "whatsapp",
            "contacts": [],
            "messages": [{"id": "wamid.read123"}],
        }
        mock_http_client.post.return_value = mock_response

        response = messages_service.mark_as_read("wamid.123456")

        call_args = mock_http_client.post.call_args
        payload = call_args.kwargs["json"]

        assert payload["messaging_product"] == "whatsapp"
        assert payload["status"] == "read"
        assert payload["message_id"] == "wamid.123456"
        assert "typing_indicator" not in payload
        assert isinstance(response, MessageResponse)

    def test_mark_as_read_with_typing(self, messages_service, mock_http_client):
        """Test marking message as read with typing indicator."""
        mock_response = {
            "messaging_product": "whatsapp",
            "contacts": [],
            "messages": [{"id": "wamid.typing123"}],
        }
        mock_http_client.post.return_value = mock_response

        response = messages_service.mark_as_read("wamid.123456", typing_indicator=True)

        call_args = mock_http_client.post.call_args
        payload = call_args.kwargs["json"]

        assert payload["messaging_product"] == "whatsapp"
        assert payload["status"] == "read"
        assert payload["message_id"] == "wamid.123456"
        assert "typing_indicator" in payload
        assert payload["typing_indicator"]["type"] == "text"
        assert isinstance(response, MessageResponse)

    def test_send_typing_indicator(self, messages_service, mock_http_client):
        """Test sending typing indicator directly."""
        mock_response = {
            "messaging_product": "whatsapp",
            "contacts": [],
            "messages": [{"id": "wamid.typing456"}],
        }
        mock_http_client.post.return_value = mock_response

        response = messages_service.send_typing_indicator("wamid.789")

        call_args = mock_http_client.post.call_args
        payload = call_args.kwargs["json"]

        assert payload["messaging_product"] == "whatsapp"
        assert payload["status"] == "read"
        assert payload["message_id"] == "wamid.789"
        assert "typing_indicator" in payload
        assert payload["typing_indicator"]["type"] == "text"
        assert isinstance(response, MessageResponse)

    def test_typing_indicator_workflow(self, messages_service, mock_http_client):
        """Test complete workflow with typing indicator."""
        # Setup mock responses
        typing_response = {
            "messaging_product": "whatsapp",
            "contacts": [],
            "messages": [{"id": "wamid.typing"}],
        }
        message_response = {
            "messaging_product": "whatsapp",
            "contacts": [{"input": "+1234567890", "wa_id": "1234567890"}],
            "messages": [{"id": "wamid.sent"}],
        }

        mock_http_client.post.side_effect = [typing_response, message_response]

        # Step 1: Show typing indicator
        typing_result = messages_service.send_typing_indicator("wamid.incoming")
        assert isinstance(typing_result, MessageResponse)

        # Step 2: Send actual message
        send_result = messages_service.send_text("+1234567890", "Processing complete!")
        assert isinstance(send_result, MessageResponse)

        # Verify both calls were made
        assert mock_http_client.post.call_count == 2

        # Verify typing indicator call
        first_call = mock_http_client.post.call_args_list[0]
        typing_payload = first_call.kwargs["json"]
        assert typing_payload["typing_indicator"]["type"] == "text"

        # Verify message send call
        second_call = mock_http_client.post.call_args_list[1]
        message_payload = second_call.kwargs["json"]
        assert message_payload["type"] == "text"
        assert message_payload["text"]["body"] == "Processing complete!"
