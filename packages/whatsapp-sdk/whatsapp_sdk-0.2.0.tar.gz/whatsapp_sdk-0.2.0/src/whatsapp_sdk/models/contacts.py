"""Contact models for WhatsApp SDK.

These models represent contact information (vCard) structures
for sending and receiving contact details via WhatsApp.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Name(BaseModel):
    """Contact name information.

    Represents a person's name with various components.
    """

    formatted_name: str = Field(..., description="Full name as it should be displayed")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    suffix: Optional[str] = Field(None, description="Name suffix (e.g., Jr., Sr., III)")
    prefix: Optional[str] = Field(None, description="Name prefix (e.g., Mr., Ms., Dr.)")


class Phone(BaseModel):
    """Contact phone number.

    Represents a phone number with type classification.
    """

    phone: str = Field(..., description="Phone number (can include formatting)")
    type: Optional[str] = Field(None, description="Phone type: HOME, WORK, MOBILE, etc.")
    wa_id: Optional[str] = Field(None, description="WhatsApp ID if this number is on WhatsApp")


class Email(BaseModel):
    """Contact email address.

    Represents an email address with type classification.
    """

    email: str = Field(..., description="Email address")
    type: Optional[str] = Field(None, description="Email type: HOME, WORK, etc.")


class Address(BaseModel):
    """Contact physical address.

    Represents a complete physical address.
    """

    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province")
    zip: Optional[str] = Field(None, description="ZIP or postal code")
    country: Optional[str] = Field(None, description="Full country name")
    country_code: Optional[str] = Field(
        None, max_length=2, description="Two-letter country code (e.g., US, GB)"
    )
    type: Optional[str] = Field(None, description="Address type: HOME, WORK, etc.")


class Organization(BaseModel):
    """Contact organization information.

    Represents workplace or organization details.
    """

    company: Optional[str] = Field(None, description="Company name")
    department: Optional[str] = Field(None, description="Department within company")
    title: Optional[str] = Field(None, description="Job title or position")


class Url(BaseModel):
    """Contact URL.

    Represents a web URL associated with the contact.
    """

    url: str = Field(..., description="Web URL")
    type: Optional[str] = Field(None, description="URL type: HOME, WORK, etc.")


class Contact(BaseModel):
    """Complete contact information.

    Represents a full contact card (vCard) with all details.
    This is used for sending contact information via WhatsApp.
    """

    name: Name = Field(..., description="Contact name (required)")
    phones: Optional[List[Phone]] = Field(None, description="List of phone numbers")
    emails: Optional[List[Email]] = Field(None, description="List of email addresses")
    addresses: Optional[List[Address]] = Field(None, description="List of physical addresses")
    org: Optional[Organization] = Field(None, description="Organization/workplace information")
    birthday: Optional[str] = Field(None, description="Birthday in YYYY-MM-DD format")
    urls: Optional[List[Url]] = Field(None, description="List of URLs")


class ContactMessage(BaseModel):
    """Contact message for sending.

    Wrapper for sending one or more contacts in a message.
    """

    contacts: List[Contact] = Field(
        ..., min_length=1, description="List of contacts to send (at least 1)"
    )


class ReceivedContact(BaseModel):
    """Contact information received in webhooks.

    Simplified contact format received when users share contacts.
    """

    profile: Optional[Name] = Field(None, description="Contact profile name")
    wa_id: Optional[str] = Field(None, description="WhatsApp ID of the contact")
    name: Optional[Name] = Field(None, description="Contact name details")
    phones: Optional[List[Phone]] = Field(None, description="Contact phone numbers")
    emails: Optional[List[Email]] = Field(None, description="Contact email addresses")
    addresses: Optional[List[Address]] = Field(None, description="Contact physical addresses")
    org: Optional[Organization] = Field(None, description="Contact organization")
    birthday: Optional[str] = Field(None, description="Contact birthday")
    urls: Optional[List[Url]] = Field(None, description="Contact URLs")
