"""Templates service for WhatsApp SDK.

Handles template management including sending template messages,
creating, listing, updating, and deleting templates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from whatsapp_sdk.models import (
    MessageResponse,
    Template,
    TemplateComponent,
    TemplateListResponse,
    TemplateResponse,
)

if TYPE_CHECKING:
    from whatsapp_sdk.config import WhatsAppConfig
    from whatsapp_sdk.http_client import HTTPClient


class TemplatesService:
    """Service for managing WhatsApp message templates.

    Handles template operations: send, create, list, get, delete, update.
    """

    def __init__(self, http_client: HTTPClient, config: WhatsAppConfig, phone_number_id: str):
        """Initialize templates service.

        Args:
            http_client: HTTP client for API requests
            config: WhatsApp configuration
            phone_number_id: WhatsApp Business phone number ID
        """
        self.http_client = http_client
        self.config = config
        self.phone_number_id = phone_number_id
        self.base_url = f"{config.base_url}/{phone_number_id}"

    # ========================================================================
    # SEND TEMPLATE MESSAGE
    # ========================================================================

    def send(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: Union[List[TemplateComponent], List[Dict[str, Any]], None] = None,
    ) -> MessageResponse:
        """Send a template message.

        Args:
            to: Recipient's WhatsApp phone number
            template_name: Name of the approved template
            language_code: Language code (e.g., en_US, es_ES)
            components: Template components with parameters

        Returns:
            MessageResponse with message ID and status

        Examples:
            # Simple template without parameters
            response = templates.send(
                to="+1234567890",
                template_name="hello_world",
                language_code="en_US"
            )

            # Template with parameters
            from whatsapp_sdk.models import TemplateComponent, TemplateParameter

            components = [
                TemplateComponent(
                    type="body",
                    parameters=[
                        TemplateParameter(type="text", text="John"),
                        TemplateParameter(type="text", text="ABC123")
                    ]
                )
            ]

            response = templates.send(
                to="+1234567890",
                template_name="order_confirmation",
                language_code="en_US",
                components=components
            )

            # Template with header image
            components = [
                TemplateComponent(
                    type="header",
                    parameters=[
                        TemplateParameter(
                            type="image",
                            image={"link": "https://example.com/image.jpg"}
                        )
                    ]
                ),
                TemplateComponent(
                    type="body",
                    parameters=[
                        TemplateParameter(type="text", text="John")
                    ]
                )
            ]
        """
        # Format components
        if components:
            formatted_components = []
            for comp in components:
                if isinstance(comp, TemplateComponent):
                    formatted_components.append(comp.model_dump(exclude_none=True))
                elif isinstance(comp, dict):
                    formatted_components.append(comp)
                else:
                    raise ValueError("Invalid component type")
        else:
            formatted_components = None

        # Build payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone_number(to),
            "type": "template",
            "template": {"name": template_name, "language": {"code": language_code}},
        }

        if formatted_components:
            template_dict = payload["template"]
            if isinstance(template_dict, dict):
                template_dict["components"] = formatted_components

        response = self.http_client.post(f"{self.base_url}/messages", json=payload)
        return MessageResponse(**response)

    # ========================================================================
    # TEMPLATE MANAGEMENT
    # ========================================================================

    def create(
        self,
        name: str,
        category: str,
        language: str,
        components: List[Dict[str, Any]],
        allow_category_change: bool = True,
    ) -> TemplateResponse:
        """Create a new message template.

        Args:
            name: Template name (must be unique)
            category: Template category (MARKETING, UTILITY, or AUTHENTICATION)
            language: Language code (e.g., en_US)
            components: Template components (header, body, footer, buttons)
            allow_category_change: Allow automatic category change if needed

        Returns:
            TemplateResponse with template ID and status

        Examples:
            # Create a simple template
            response = templates.create(
                name="welcome_message",
                category="MARKETING",
                language="en_US",
                components=[
                    {
                        "type": "HEADER",
                        "format": "TEXT",
                        "text": "Welcome to {{1}}!"
                    },
                    {
                        "type": "BODY",
                        "text": "Hi {{1}}, thanks for joining {{2}}. We're excited to have you!"
                    },
                    {
                        "type": "FOOTER",
                        "text": "Reply STOP to unsubscribe"
                    }
                ]
            )

            # Create template with buttons
            response = templates.create(
                name="appointment_reminder",
                category="UTILITY",
                language="en_US",
                components=[
                    {
                        "type": "BODY",
                        "text": "Your appointment is on {{1}} at {{2}}"
                    },
                    {
                        "type": "BUTTONS",
                        "buttons": [
                            {
                                "type": "QUICK_REPLY",
                                "text": "Confirm"
                            },
                            {
                                "type": "QUICK_REPLY",
                                "text": "Reschedule"
                            }
                        ]
                    }
                ]
            )
        """
        # Get WhatsApp Business Account ID (WABA ID)
        # This is typically different from phone_number_id
        # For now, we'll need to fetch it or have it configured
        waba_id = self._get_waba_id()

        payload = {
            "name": name,
            "category": category,
            "language": language,
            "components": components,
            "allow_category_change": allow_category_change,
        }

        response = self.http_client.post(
            f"{self.config.base_url}/{waba_id}/message_templates", json=payload
        )
        return TemplateResponse(**response)

    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> TemplateListResponse:
        """List all message templates.

        Args:
            limit: Maximum number of templates to return
            after: Cursor for pagination
            fields: Specific fields to include in response

        Returns:
            TemplateListResponse with list of templates

        Example:
            # List all templates
            templates_list = templates.list()

            # List with pagination
            templates_list = templates.list(limit=10)

            # Get next page
            next_page = templates.list(after=templates_list.paging["cursors"]["after"])
        """
        waba_id = self._get_waba_id()

        params: Dict[str, Any] = {}
        if limit:
            params["limit"] = str(limit)
        if after:
            params["after"] = after
        if fields:
            params["fields"] = ",".join(fields)

        response = self.http_client.get(
            f"{self.config.base_url}/{waba_id}/message_templates", params=params
        )
        return TemplateListResponse(**response)

    def get(self, template_id: str) -> Template:
        """Get details of a specific template.

        Args:
            template_id: Template ID

        Returns:
            Template with full details

        Example:
            template = templates.get("12345678")
        """
        response = self.http_client.get(f"{self.config.base_url}/{template_id}")
        return Template(**response)

    def delete(self, template_name: str) -> bool:
        """Delete a message template.

        Args:
            template_name: Name of the template to delete

        Returns:
            True if deletion was successful

        Example:
            success = templates.delete("old_template")
        """
        waba_id = self._get_waba_id()

        response = self.http_client.delete(
            f"{self.config.base_url}/{waba_id}/message_templates", params={"name": template_name}
        )

        return bool(response.get("success", False))

    def update(self, template_id: str, components: List[Dict[str, Any]]) -> TemplateResponse:
        """Update template components.

        Note: Only certain template elements can be updated after creation.

        Args:
            template_id: Template ID to update
            components: Updated components

        Returns:
            TemplateResponse with update status

        Example:
            response = templates.update(
                template_id="12345678",
                components=[
                    {
                        "type": "BODY",
                        "text": "Updated message text with {{1}} parameter"
                    }
                ]
            )
        """
        payload = {"components": components}

        response = self.http_client.post(f"{self.config.base_url}/{template_id}", json=payload)
        return TemplateResponse(**response)

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

    def _get_waba_id(self) -> str:
        """Get WhatsApp Business Account ID.

        This needs to be fetched from the API or configured.
        For now, we'll try to fetch it from the phone number.

        Returns:
            WABA ID string
        """
        # In a real implementation, this would fetch the WABA ID
        # from the phone number details or be configured separately
        # For now, we'll use a placeholder approach

        # Try to get from phone number details
        try:
            response = self.http_client.get(
                f"{self.config.base_url}/{self.phone_number_id}",
                params={"fields": "whatsapp_business_account"},
            )
            return str(
                response.get("whatsapp_business_account", {}).get("id", self.phone_number_id)
            )
        except Exception:
            # Fallback to using phone_number_id
            # In production, this should be properly configured
            return self.phone_number_id
