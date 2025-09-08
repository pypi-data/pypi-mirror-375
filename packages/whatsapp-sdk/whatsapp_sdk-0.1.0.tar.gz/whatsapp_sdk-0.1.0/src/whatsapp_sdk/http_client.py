"""HTTP client for WhatsApp SDK.

Handles all HTTP communication with the WhatsApp Business API,
including retries, rate limiting, and error handling.
"""

import time
from typing import Any, Dict, Optional

import httpx

from .config import WhatsAppConfig
from .exceptions import (
    WhatsAppAPIError,
    WhatsAppAuthenticationError,
    WhatsAppError,
    WhatsAppRateLimitError,
    WhatsAppValidationError,
)


class HTTPClient:
    """Synchronous HTTP client for WhatsApp API requests.

    Handles:
    - Request/response processing
    - Error handling and retries
    - Rate limiting
    - Authentication
    """

    def __init__(self, config: WhatsAppConfig):
        """Initialize HTTP client.

        Args:
            config: WhatsApp configuration
        """
        self.config = config
        self.base_url = f"{config.base_url}/{config.api_version}"

        # Create httpx client with default headers
        self.client = httpx.Client(
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Content-Type": "application/json",
                "User-Agent": "WhatsApp-sdk/0.1.0",
            },
        )

        # Rate limiting
        self._last_request_time: float = 0
        self._request_interval = 1.0 / config.rate_limit  # Seconds between requests

    def post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make POST request to WhatsApp API.

        Args:
            endpoint: API endpoint (can be relative or absolute)
            json: JSON payload
            **kwargs: Additional httpx request parameters

        Returns:
            Response data as dictionary

        Raises:
            WhatsAppAPIError: For API errors
            WhatsAppRateLimitError: For rate limit errors
            WhatsAppAuthenticationError: For auth errors
        """
        # Handle rate limiting
        self._apply_rate_limit()

        # Build full URL if endpoint is relative
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith("http") else endpoint

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.post(url, json=json, **kwargs)
                return self._handle_response(response)
            except WhatsAppRateLimitError:
                # For rate limit errors, wait longer
                if attempt < self.config.max_retries:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                raise
            except WhatsAppError as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(0.5 * (attempt + 1))  # Linear backoff
                    continue
                raise
            except httpx.HTTPError as e:
                last_error = WhatsAppAPIError(f"HTTP error: {e!s}")
                if attempt < self.config.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise last_error from None

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise WhatsAppAPIError("Unknown error occurred")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make GET request to WhatsApp API.

        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional httpx request parameters

        Returns:
            Response data as dictionary
        """
        # Handle rate limiting
        self._apply_rate_limit()

        # Build full URL if endpoint is relative
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith("http") else endpoint

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.get(url, params=params, **kwargs)
                return self._handle_response(response)
            except WhatsAppError as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise
            except httpx.HTTPError as e:
                last_error = WhatsAppAPIError(f"HTTP error: {e!s}")
                if attempt < self.config.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise last_error from None

        if last_error:
            raise last_error
        raise WhatsAppAPIError("Unknown error occurred")

    def delete(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make DELETE request to WhatsApp API.

        Args:
            endpoint: API endpoint
            **kwargs: Additional httpx request parameters

        Returns:
            Response data as dictionary
        """
        # Handle rate limiting
        self._apply_rate_limit()

        # Build full URL if endpoint is relative
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith("http") else endpoint

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.delete(url, **kwargs)
                return self._handle_response(response)
            except WhatsAppError as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise
            except httpx.HTTPError as e:
                last_error = WhatsAppAPIError(f"HTTP error: {e!s}")
                if attempt < self.config.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise last_error from None

        if last_error:
            raise last_error
        raise WhatsAppAPIError("Unknown error occurred")

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors.

        Args:
            response: HTTP response

        Returns:
            Response data as dictionary

        Raises:
            Various WhatsAppError subclasses based on error type
        """
        # Check status code
        if response.status_code == 429:
            raise WhatsAppRateLimitError("Rate limit exceeded")

        if response.status_code == 401:
            raise WhatsAppAuthenticationError("Invalid access token")

        if response.status_code == 400:
            # Parse error details
            try:
                error_data = response.json()
                error = error_data.get("error", {})
                message = error.get("message", "Validation error")
                raise WhatsAppValidationError(message)
            except (ValueError, KeyError):
                raise WhatsAppValidationError("Bad request") from None

        if response.status_code >= 400:
            # General API error
            try:
                error_data = response.json()
                error = error_data.get("error", {})
                message = error.get("message", f"HTTP {response.status_code}")
                code = error.get("code", response.status_code)
                raise WhatsAppAPIError(f"Error {code}: {message}")
            except (ValueError, KeyError):
                raise WhatsAppAPIError(f"HTTP {response.status_code}") from None

        # Parse successful response
        try:
            data: Dict[str, Any] = response.json()
            return data
        except ValueError:
            # Some endpoints return empty responses
            if response.status_code == 204:
                return {"success": True}
            raise WhatsAppAPIError("Invalid JSON response") from None

    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self._request_interval:
            time.sleep(self._request_interval - time_since_last)

        self._last_request_time = time.time()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> "HTTPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
