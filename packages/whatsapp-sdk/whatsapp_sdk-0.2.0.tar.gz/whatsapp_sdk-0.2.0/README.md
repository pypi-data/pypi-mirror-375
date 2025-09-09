# WhatsApp SDK Python

[![PyPI version](https://badge.fury.io/py/whatsapp-sdk.svg)](https://badge.fury.io/py/whatsapp-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/whatsapp-sdk.svg)](https://pypi.org/project/whatsapp-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/alejandrovelez243/whatsapp-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/alejandrovelez243/whatsapp-sdk/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/alejandrovelez243/whatsapp-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/alejandrovelez243/whatsapp-sdk)
[![Documentation Status](https://readthedocs.org/projects/whatsapp-sdk/badge/?version=latest)](https://whatsapp-sdk.readthedocs.io/en/latest)

A comprehensive **synchronous** Python SDK for WhatsApp Business Cloud API, following Meta's official documentation.

## 🌟 Features

- ✅ **100% Synchronous** - Simple, straightforward API without async complexity
- 📘 **Fully Type-Hinted** - Complete type safety with Pydantic models
- 🔄 **Auto-Retry Logic** - Built-in retry mechanism for robust API calls
- 🔐 **Webhook Verification** - Secure webhook signature validation
- 📦 **Media Management** - Upload, download, and manage media files
- 💬 **Template Messages** - Full template message support
- 🔔 **Interactive Messages** - Buttons, lists, and quick replies
- 📍 **Location Messages** - Send and receive location data
- 👥 **Contact Messages** - Share contact cards
- ⌨️ **Typing Indicators** - Show typing status for better user experience
- ✨ **Modern Python** - Supports Python 3.8+
- 🛡️ **Secure**: Webhook signature validation and secure token handling
- 📝 **Well-Documented**: Extensive documentation and examples

## Installation

```bash
pip install whatsapp-sdk
```

## Quick Start

```python
from whatsapp_sdk import WhatsAppClient

# Initialize client
client = WhatsAppClient(
    phone_number_id="YOUR_PHONE_NUMBER_ID",
    access_token="YOUR_ACCESS_TOKEN"
)

# Send a text message
response = client.messages.send_text(
    to="+1234567890",
    body="Hello from WhatsApp SDK!"
)
print(f"Message sent! ID: {response.messages[0].id}")
```

## Configuration

### Using Environment Variables

```bash
export WHATSAPP_PHONE_NUMBER_ID="your_phone_id"
export WHATSAPP_ACCESS_TOKEN="your_access_token"
```

```python
from whatsapp_sdk import WhatsAppClient

# Create client from environment
client = WhatsAppClient.from_env()
```

### Direct Configuration

```python
client = WhatsAppClient(
    phone_number_id="YOUR_PHONE_NUMBER_ID",
    access_token="YOUR_ACCESS_TOKEN",
    app_secret="YOUR_APP_SECRET",  # Optional: for webhook validation
    webhook_verify_token="YOUR_VERIFY_TOKEN",  # Optional: for webhook setup
    api_version="v23.0",  # Optional: API version
    timeout=30,  # Optional: Request timeout
    max_retries=3,  # Optional: Max retry attempts
    rate_limit=80  # Optional: Requests per second
)
```

## Usage Examples

### Sending Messages

#### Text Messages

```python
# Simple text
response = client.messages.send_text(
    to="+1234567890",
    body="Hello World!"
)

# Text with URL preview
response = client.messages.send_text(
    to="+1234567890",
    body="Check out https://example.com",
    preview_url=True
)

# Using Pydantic model
from whatsapp_sdk import TextMessage

message = TextMessage(
    body="Hello with Pydantic!",
    preview_url=True
)
response = client.messages.send_text(
    to="+1234567890",
    text=message
)
```

#### Media Messages

```python
# Send image
response = client.messages.send_image(
    to="+1234567890",
    image="https://example.com/image.jpg",
    caption="Look at this!"
)

# Send document
response = client.messages.send_document(
    to="+1234567890",
    document="https://example.com/file.pdf",
    caption="Important document",
    filename="contract.pdf"
)

# Send video
response = client.messages.send_video(
    to="+1234567890",
    video="https://example.com/video.mp4",
    caption="Check this out!"
)

# Send audio
response = client.messages.send_audio(
    to="+1234567890",
    audio="https://example.com/audio.mp3"
)
```

#### Location Messages

```python
response = client.messages.send_location(
    to="+1234567890",
    latitude=37.4847,
    longitude=-122.1477,
    name="Meta Headquarters",
    address="1 Hacker Way, Menlo Park, CA"
)
```

#### Contact Messages

```python
from whatsapp_sdk import Contact, Name, Phone, Email

contact = Contact(
    name=Name(
        formatted_name="John Doe",
        first_name="John",
        last_name="Doe"
    ),
    phones=[
        Phone(phone="+1234567890", type="MOBILE")
    ],
    emails=[
        Email(email="john@example.com", type="WORK")
    ]
)

response = client.messages.send_contact(
    to="+9876543210",
    contacts=[contact]
)
```

#### Interactive Messages

```python
from whatsapp_sdk import (
    InteractiveMessage,
    InteractiveBody,
    InteractiveAction,
    Button
)

# Button message
interactive = InteractiveMessage(
    type="button",
    body=InteractiveBody(text="Choose an option:"),
    action=InteractiveAction(
        buttons=[
            Button(type="reply", reply={"id": "yes", "title": "Yes"}),
            Button(type="reply", reply={"id": "no", "title": "No"})
        ]
    )
)

response = client.messages.send_interactive(
    to="+1234567890",
    interactive=interactive
)
```

### Message Status

```python
# Mark message as read
response = client.messages.mark_as_read("wamid.xxx")

# Mark as read with typing indicator
response = client.messages.mark_as_read("wamid.xxx", typing_indicator=True)

# Show typing indicator while processing
response = client.messages.send_typing_indicator("wamid.xxx")
```

### Template Messages

```python
# Send template message
response = client.templates.send(
    to="+1234567890",
    template_name="hello_world",
    language_code="en_US"
)

# Send template with parameters
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

response = client.templates.send(
    to="+1234567890",
    template_name="order_confirmation",
    language_code="en_US",
    components=components
)
```

### Media Operations

```python
# Upload media from file
response = client.media.upload("/path/to/image.jpg")
media_id = response.id
print(f"Uploaded: {media_id}")

# Upload from bytes
with open("document.pdf", "rb") as f:
    response = client.media.upload_from_bytes(
        file_bytes=f.read(),
        mime_type="application/pdf",
        filename="document.pdf"
    )

# Get media URL and info
url_response = client.media.get_url("media_id_123")
print(f"URL: {url_response.url}")
print(f"Size: {url_response.file_size} bytes")

# Download media to memory
content = client.media.download("media_id_123")
with open("downloaded.jpg", "wb") as f:
    f.write(content)

# Download directly to file (memory efficient)
saved_path = client.media.download_to_file(
    "media_id_123",
    "/path/to/save/file.jpg"
)

# Delete media
success = client.media.delete("media_id_123")
```

### Webhook Handling

```python
# FastAPI webhook example
from fastapi import FastAPI, Request, Header, Query

app = FastAPI()

@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    result = client.webhooks.handle_verification(
        hub_mode, hub_verify_token, hub_challenge
    )
    if result:
        return result
    return {"error": "Invalid token"}, 403

@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    body = await request.body()
    event = client.webhooks.handle_event(x_hub_signature_256, body)

    # Process messages
    messages = client.webhooks.extract_messages(event)
    for message in messages:
        if message.type == "text":
            print(f"Received: {message.text.body}")

    return {"status": "ok"}
```

## Development Status

### ✅ Completed Phases

- **Phase 1**: Foundation & Setup
  - Project structure
  - Configuration management
  - HTTP client setup
  - Exception hierarchy

- **Phase 2**: Core Models (Pydantic)
  - Base models (BaseResponse, Error, Contact)
  - Message models (Text, Image, Video, Audio, Document, Location, etc.)
  - Contact models (Name, Phone, Email, Address, Organization)
  - Template models (Template, Component, Parameter)
  - Media models (Upload, URL, Delete responses)
  - Webhook models (Event, Entry, Message, Status)

- **Phase 3**: Services Implementation ✅
  - **Messages Service**: All message types with full functionality
  - **Templates Service**: Send, create, list, delete, update templates
  - **Media Service**: Upload, download, delete media files
  - **Webhooks Service**: Verification, signature validation, event parsing

- **Phase 4**: Client Integration ✅
  - All services wired and functional
  - Environment configuration support
  - Clean service-oriented architecture

### 📋 Upcoming Phases

- **Phase 5**: Testing
  - Unit tests for all services
  - Integration tests
  - Mock responses

- **Phase 6**: Examples & Documentation
  - Basic usage examples
  - Advanced examples
  - API documentation

- **Phase 7**: Quality & Release
  - Code quality checks
  - CI/CD setup
  - PyPI release

## API Design Principles

- **Synchronous First**: No async/await complexity
- **Pydantic Models**: Type-safe data structures
- **Flexible Input**: Accept Pydantic models, dicts, or simple parameters
- **Always Returns Pydantic**: Consistent, type-safe responses
- **Service-Oriented**: Clean separation of concerns

## Requirements

- Python 3.8+
- httpx
- pydantic >= 2.0

## Contributing

This SDK is under active development. Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/whatsapp-sdk.git
cd whatsapp-sdk

# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src/ tests/

# Run type checking
uv run mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Full documentation](https://whatsapp-sdk.readthedocs.io) (coming soon)
- **Issues**: [GitHub Issues](https://github.com/yourusername/whatsapp-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/whatsapp-sdk/discussions)

## Disclaimer

This SDK is not officially affiliated with Meta or WhatsApp. It's an independent implementation following the official WhatsApp Business API documentation.
