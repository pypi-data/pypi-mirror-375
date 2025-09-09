"""Messages service for WhatsApp SDK.

Handles sending all types of messages including text, media, location,
contacts, and interactive messages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from whatsapp_sdk.models import (
    AudioMessage,
    Contact,
    ContactMessage,
    DocumentMessage,
    ImageMessage,
    InteractiveMessage,
    MessageResponse,
    StickerMessage,
    TextMessage,
    VideoMessage,
)

if TYPE_CHECKING:
    from whatsapp_sdk.config import WhatsAppConfig
    from whatsapp_sdk.http_client import HTTPClient


class MessagesService:
    """Service for sending WhatsApp messages.

    Handles all message types: text, media, location, contacts, interactive.
    """

    def __init__(self, http_client: HTTPClient, config: WhatsAppConfig, phone_number_id: str):
        """Initialize messages service.

        Args:
            http_client: HTTP client for API requests
            config: WhatsApp configuration
            phone_number_id: WhatsApp Business phone number ID
        """
        self.http_client = http_client
        self.config = config
        self.phone_number_id = phone_number_id
        self.base_url = f"{config.base_url}/{phone_number_id}/messages"

    # ========================================================================
    # TEXT MESSAGES
    # ========================================================================

    def send_text(
        self,
        to: str,
        body: Optional[str] = None,
        text: Union[str, TextMessage, Dict[str, Any], None] = None,
        preview_url: bool = False,
    ) -> MessageResponse:
        """Send a text message.

        Args:
            to: Recipient's WhatsApp phone number
            body: Text content (convenience parameter)
            text: Text content or TextMessage object or dict
            preview_url: Enable URL preview for links

        Returns:
            MessageResponse with message ID and status

        Examples:
            # Simple text
            response = messages.send_text("+1234567890", "Hello!")

            # With URL preview
            response = messages.send_text(
                "+1234567890",
                "Check out https://example.com",
                preview_url=True
            )

            # Using TextMessage model
            msg = TextMessage(body="Hello!", preview_url=True)
            response = messages.send_text("+1234567890", text=msg)
        """
        # Handle different input formats
        if body is not None:
            text_data = {"body": body, "preview_url": preview_url}
        elif isinstance(text, str):
            text_data = {"body": text, "preview_url": preview_url}
        elif isinstance(text, TextMessage):
            text_data = text.model_dump()
        elif isinstance(text, dict):
            text_data = text
        else:
            raise ValueError("Must provide either 'body' or 'text' parameter")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "text",
            "text": text_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    # ========================================================================
    # MEDIA MESSAGES
    # ========================================================================

    def send_image(
        self,
        to: str,
        image: Union[str, ImageMessage, Dict[str, Any]],
        caption: Optional[str] = None,
    ) -> MessageResponse:
        """Send an image message.

        Args:
            to: Recipient's WhatsApp phone number
            image: Media ID, URL, ImageMessage object, or dict
            caption: Optional caption for the image

        Returns:
            MessageResponse with message ID and status

        Examples:
            # Using media ID
            response = messages.send_image("+1234567890", "media_id_123")

            # Using URL with caption
            response = messages.send_image(
                "+1234567890",
                "https://example.com/image.jpg",
                caption="Look at this!"
            )

            # Using ImageMessage model
            img = ImageMessage(link="https://example.com/pic.jpg", caption="Nice!")
            response = messages.send_image("+1234567890", img)
        """
        # Handle different input formats
        if isinstance(image, str):
            # Determine if it's a media ID or URL
            image_data = {"link": image} if image.startswith("http") else {"id": image}
            if caption:
                image_data["caption"] = caption
        elif isinstance(image, ImageMessage):
            image_data = image.model_dump(exclude_none=True)
        elif isinstance(image, dict):
            image_data = image
        else:
            raise ValueError("Invalid image parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "image",
            "image": image_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_document(
        self,
        to: str,
        document: Union[str, DocumentMessage, Dict[str, Any]],
        caption: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> MessageResponse:
        """Send a document message.

        Args:
            to: Recipient's WhatsApp phone number
            document: Media ID, URL, DocumentMessage object, or dict
            caption: Optional caption for the document
            filename: Filename to display (required for URLs)

        Returns:
            MessageResponse with message ID and status
        """
        # Handle different input formats
        if isinstance(document, str):
            if document.startswith("http"):
                document_data = {"link": document}
                if filename:
                    document_data["filename"] = filename
            else:
                document_data = {"id": document}
            if caption:
                document_data["caption"] = caption
        elif isinstance(document, DocumentMessage):
            document_data = document.model_dump(exclude_none=True)
        elif isinstance(document, dict):
            document_data = document
        else:
            raise ValueError("Invalid document parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "document",
            "document": document_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_audio(
        self, to: str, audio: Union[str, AudioMessage, Dict[str, Any]]
    ) -> MessageResponse:
        """Send an audio message.

        Args:
            to: Recipient's WhatsApp phone number
            audio: Media ID, URL, AudioMessage object, or dict

        Returns:
            MessageResponse with message ID and status
        """
        # Handle different input formats
        if isinstance(audio, str):
            audio_data = {"link": audio} if audio.startswith("http") else {"id": audio}
        elif isinstance(audio, AudioMessage):
            audio_data = audio.model_dump(exclude_none=True)
        elif isinstance(audio, dict):
            audio_data = audio
        else:
            raise ValueError("Invalid audio parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "audio",
            "audio": audio_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_video(
        self,
        to: str,
        video: Union[str, VideoMessage, Dict[str, Any]],
        caption: Optional[str] = None,
    ) -> MessageResponse:
        """Send a video message.

        Args:
            to: Recipient's WhatsApp phone number
            video: Media ID, URL, VideoMessage object, or dict
            caption: Optional caption for the video

        Returns:
            MessageResponse with message ID and status
        """
        # Handle different input formats
        if isinstance(video, str):
            video_data = {"link": video} if video.startswith("http") else {"id": video}
            if caption:
                video_data["caption"] = caption
        elif isinstance(video, VideoMessage):
            video_data = video.model_dump(exclude_none=True)
        elif isinstance(video, dict):
            video_data = video
        else:
            raise ValueError("Invalid video parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "video",
            "video": video_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_sticker(
        self, to: str, sticker: Union[str, StickerMessage, Dict[str, Any]]
    ) -> MessageResponse:
        """Send a sticker message.

        Args:
            to: Recipient's WhatsApp phone number
            sticker: Media ID, URL, StickerMessage object, or dict

        Returns:
            MessageResponse with message ID and status
        """
        # Handle different input formats
        if isinstance(sticker, str):
            sticker_data = {"link": sticker} if sticker.startswith("http") else {"id": sticker}
        elif isinstance(sticker, StickerMessage):
            sticker_data = sticker.model_dump(exclude_none=True)
        elif isinstance(sticker, dict):
            sticker_data = sticker
        else:
            raise ValueError("Invalid sticker parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "sticker",
            "sticker": sticker_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    # ========================================================================
    # OTHER MESSAGE TYPES
    # ========================================================================

    def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> MessageResponse:
        """Send a location message.

        Args:
            to: Recipient's WhatsApp phone number
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            name: Optional location name
            address: Optional location address

        Returns:
            MessageResponse with message ID and status

        Examples:
            # Basic location
            response = messages.send_location(
                "+1234567890",
                37.4847, -122.1477
            )

            # With name and address
            response = messages.send_location(
                "+1234567890",
                37.4847, -122.1477,
                name="Meta Headquarters",
                address="1 Hacker Way, Menlo Park, CA"
            )
        """
        location_data: Dict[str, Any] = {"latitude": latitude, "longitude": longitude}
        if name:
            location_data["name"] = name
        if address:
            location_data["address"] = address

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "location",
            "location": location_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_contact(
        self, to: str, contacts: Union[List[Contact], ContactMessage, Dict[str, Any]]
    ) -> MessageResponse:
        """Send contact information.

        Args:
            to: Recipient's WhatsApp phone number
            contacts: List of Contact objects, ContactMessage, or dict

        Returns:
            MessageResponse with message ID and status

        Examples:
            # Using Contact model
            from whatsapp_sdk.models import Contact, Name, Phone

            contact = Contact(
                name=Name(
                    formatted_name="John Doe",
                    first_name="John",
                    last_name="Doe"
                ),
                phones=[Phone(phone="+1234567890", type="MOBILE")]
            )
            response = messages.send_contact("+1234567890", [contact])
        """
        # Handle different input formats
        if isinstance(contacts, list):
            contacts_data: Any = [
                c.model_dump(exclude_none=True) if hasattr(c, "model_dump") else c for c in contacts
            ]
        elif isinstance(contacts, ContactMessage):
            contacts_data = [
                c.model_dump(exclude_none=True) if hasattr(c, "model_dump") else c for c in contacts.contacts
            ]
        elif isinstance(contacts, dict):
            contacts_data = contacts.get("contacts", [contacts])
        else:
            raise ValueError("Invalid contacts parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "contacts",
            "contacts": contacts_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_interactive(
        self, to: str, interactive: Union[InteractiveMessage, Dict[str, Any]]
    ) -> MessageResponse:
        """Send an interactive message with buttons or lists.

        Args:
            to: Recipient's WhatsApp phone number
            interactive: InteractiveMessage object or dict

        Returns:
            MessageResponse with message ID and status

        Examples:
            # Button message
            from whatsapp_sdk.models import (
                InteractiveMessage,
                InteractiveBody,
                InteractiveAction,
                Button
            )

            interactive = InteractiveMessage(
                type="button",
                body=InteractiveBody(text="Choose an option:"),
                action=InteractiveAction(
                    buttons=[
                        Button(type="reply", reply={"id": "1", "title": "Yes"}),
                        Button(type="reply", reply={"id": "2", "title": "No"})
                    ]
                )
            )
            response = messages.send_interactive("+1234567890", interactive)
        """
        # Handle different input formats
        if isinstance(interactive, InteractiveMessage):
            interactive_data = interactive.model_dump(exclude_none=True)
        elif isinstance(interactive, dict):
            interactive_data = interactive
        else:
            raise ValueError("Invalid interactive parameter type")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "interactive",
            "interactive": interactive_data,
        }

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    # ========================================================================
    # MESSAGE MANAGEMENT
    # ========================================================================

    def mark_as_read(self, message_id: str, typing_indicator: bool = False) -> MessageResponse:
        """Mark a message as read and optionally show typing indicator.

        Args:
            message_id: WhatsApp message ID to mark as read
            typing_indicator: If True, shows typing indicator for up to 25 seconds

        Returns:
            MessageResponse confirming the action

        Examples:
            # Mark as read only
            response = messages.mark_as_read("wamid.xxx")

            # Mark as read and show typing indicator
            response = messages.mark_as_read("wamid.xxx", typing_indicator=True)
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        # Add typing indicator if requested
        if typing_indicator:
            payload["typing_indicator"] = {"type": "text"}

        response = self.http_client.post(self.base_url, json=payload)
        return MessageResponse(**response)

    def send_typing_indicator(self, message_id: str) -> MessageResponse:
        """Send typing indicator without marking message as read.

        Shows the typing indicator for up to 25 seconds or until a message is sent.
        Note: This also marks the message as read.

        Args:
            message_id: WhatsApp message ID to respond to

        Returns:
            MessageResponse confirming the action

        Example:
            # Show typing indicator while processing
            messages.send_typing_indicator("wamid.xxx")
            # Process message...
            messages.send_text(to, "Response ready!")
        """
        return self.mark_as_read(message_id, typing_indicator=True)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for WhatsApp API.

        Args:
            phone: Phone number in any format

        Returns:
            Formatted phone number (digits only)
        """
        # Remove all non-digit characters
        formatted = "".join(filter(str.isdigit, phone))

        # Validate length (7-15 digits per WhatsApp requirements)
        if len(formatted) < 7 or len(formatted) > 15:
            raise ValueError(f"Invalid phone number length: {formatted}")

        return formatted
