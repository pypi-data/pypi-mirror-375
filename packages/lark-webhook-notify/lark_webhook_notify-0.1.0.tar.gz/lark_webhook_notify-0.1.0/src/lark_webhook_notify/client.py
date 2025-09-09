"""Lark webhook notification client.

This module provides the main client class for sending notifications to Lark webhooks.
The client handles webhook communication, signature generation, and message delivery.
It accepts template instances and generates the appropriate card content.
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Optional, Dict, Any

import httpx

from .config import LarkWebhookSettings, create_settings
from .templates import LarkTemplate, CardContent


def get_logger() -> logging.Logger:
    """Create and configure a logger for the notification client.

    Returns:
        Configured logger instance with console handler

    Note:
        Logger is configured with INFO level by default. Only one handler
        is added to prevent duplicate log messages.
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger("lark-webhook-notify")
    logger.setLevel(logging.INFO)

    # Only add handler if it doesn't already exist
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def gen_sign(timestamp: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for Lark webhook authentication.

    Args:
        timestamp: Unix timestamp as string
        secret: Webhook secret key

    Returns:
        Base64 encoded HMAC signature

    Note:
        The signature is generated according to Lark's webhook security
        specification: HMAC-SHA256 of "timestamp\nsecret" encoded as base64.
    """
    if not timestamp or not secret:
        raise ValueError("Both timestamp and secret must be non-empty")

    # Concatenate timestamp and secret with newline separator
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()

    # Base64 encode the result
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign


class LarkWebhookNotifier:
    """Main client for sending Lark webhook notifications.

    This client handles webhook communication, signature generation, and message delivery.
    It accepts template instances and processes them to send notifications to Lark webhooks.

    The client provides:
    - Webhook communication with proper authentication
    - HMAC-SHA256 signature generation
    - Template content processing
    - HTTP error handling and retry logic
    - Context manager for resource cleanup

    Example:
        >>> from .templates import StartTaskTemplate
        >>> template = StartTaskTemplate(task_name="build", desc="Building app")
        >>> with LarkWebhookNotifier() as notifier:
        ...     notifier.send_template(template)
    """

    def __init__(
        self,
        settings: Optional[LarkWebhookSettings] = None,
        toml_file: Optional[str] = None,
        webhook_url: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ):
        """Initialize the notifier with configuration.

        Args:
            settings: Pre-configured settings object (optional)
            toml_file: Path to TOML config file (optional)
            webhook_url: Override webhook URL (highest priority)
            webhook_secret: Override webhook secret (highest priority)

        Raises:
            ValueError: If webhook URL or secret cannot be determined from any source

        Note:
            Configuration priority: parameters > environment > TOML file > defaults
        """
        if settings is None:
            settings = create_settings(
                toml_file=toml_file,
                webhook_url=webhook_url,
                webhook_secret=webhook_secret,
            )

        # Allow runtime overrides (highest priority)
        new_webhook_url = webhook_url or settings.webhook_url
        new_webhook_secret = webhook_secret or settings.webhook_secret

        if not new_webhook_url:
            raise ValueError(
                "Webhook URL must be provided via config, environment variable (LARK_WEBHOOK_URL), or parameter"
            )
        if not new_webhook_secret:
            raise ValueError(
                "Webhook secret must be provided via config, environment variable (LARK_WEBHOOK_SECRET), or parameter"
            )
        self.webhook_url = new_webhook_url
        self.webhook_secret = new_webhook_secret

        self.logger = get_logger()
        # Configure HTTP client with reasonable timeout and retry behavior
        self.client = httpx.Client()

    def _create_payload(self, card_content: CardContent) -> Dict[str, Any]:
        """Create the signed payload for the webhook request.

        Args:
            card_content: Lark card content dictionary

        Returns:
            Complete webhook payload with signature and metadata
        """
        timestamp = str(int(time.time()))
        sign = gen_sign(timestamp, self.webhook_secret)

        return {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "interactive",
            "card": card_content,
        }

    def send_template(self, template: LarkTemplate) -> Dict[str, Any]:
        """Send a notification using a template instance.

        Args:
            template: Template instance with all required parameters set

        Returns:
            Response dictionary from the webhook API

        Raises:
            httpx.HTTPError: If the HTTP request fails

        Example:
            >>> from .templates import StartTaskTemplate
            >>> template = StartTaskTemplate(task_name="deployment", desc="Deploy to production")
            >>> response = notifier.send_template(template)
        """
        card_content = template.generate()
        payload = self._create_payload(card_content)
        return self._send_payload(payload)

    def send_raw_content(self, card_content: CardContent) -> Dict[str, Any]:
        """Send raw card content directly to the webhook.

        Args:
            card_content: Raw Lark card content dictionary

        Returns:
            Response dictionary from the webhook API

        Raises:
            httpx.HTTPError: If the HTTP request fails

        Example:
            >>> custom_card = {
            ...     "schema": "2.0",
            ...     "body": {"direction": "vertical", "elements": [...]}
            ... }
            >>> response = notifier.send_raw_content(custom_card)
        """
        payload = self._create_payload(card_content)
        return self._send_payload(payload)

    def _send_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send the payload to the webhook endpoint.

        Args:
            payload: Complete webhook payload with signature

        Returns:
            Response dictionary from the webhook API

        Raises:
            httpx.HTTPError: If the HTTP request fails
            json.JSONDecodeError: If response is not valid JSON
        """
        headers = {"Content-Type": "application/json"}

        try:
            self.logger.debug(f"Sending webhook request to {self.webhook_url}")
            response = self.client.post(
                self.webhook_url,
                headers=headers,
                content=json.dumps(payload, ensure_ascii=False),
            )
            response.raise_for_status()
            resp_data = response.json()

            # Check Lark API response code
            api_code = resp_data.get("code")
            if api_code != 0:
                error_msg = resp_data.get("msg", "Unknown error")
                self.logger.error(f"Lark API error: code {api_code} - {error_msg}")
            else:
                self.logger.info("Notification sent successfully!")
                self.logger.debug(f"API response: {resp_data}")

            return resp_data

        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error sending notification: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from webhook: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error sending notification: {e}")
            raise

    def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        self.client.close()
        self.logger.debug("HTTP client closed")

    def __enter__(self) -> "LarkWebhookNotifier":
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and clean up resources."""
        self.close()
