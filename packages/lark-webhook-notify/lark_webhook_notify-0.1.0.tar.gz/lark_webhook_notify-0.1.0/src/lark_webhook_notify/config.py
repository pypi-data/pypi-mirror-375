"""Configuration management for Lark webhook notifications.

This module provides a hierarchical configuration system that reads settings
from multiple sources in order of precedence:
1. Command line arguments / direct parameters (highest)
2. Environment variables (LARK_WEBHOOK_URL, LARK_WEBHOOK_SECRET)
3. TOML configuration file (lark_webhook.toml by default)
4. Default values (lowest)
"""

from typing import Optional
from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class LarkWebhookSettings(BaseSettings):
    """Lark webhook configuration settings.

    This class manages configuration loading from multiple sources with
    proper precedence ordering. Environment variables should be prefixed
    with 'LARK_' (e.g., LARK_WEBHOOK_URL).

    Attributes:
        webhook_url: The Lark webhook URL endpoint
        webhook_secret: The webhook secret for signature generation
    """

    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

    model_config = SettingsConfigDict(
        env_prefix="LARK_",
        env_file=".env",
        toml_file="lark_webhook.toml",
        extra="ignore",
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Define the order of configuration sources.

        Returns sources in order of precedence (highest to lowest):
        1. Direct initialization parameters (CLI args, function params)
        2. Environment variables (LARK_WEBHOOK_URL, LARK_WEBHOOK_SECRET)
        3. TOML configuration file

        Args:
            settings_cls: The settings class being configured
            init_settings: Direct initialization parameters
            env_settings: Environment variable source
            dotenv_settings: .env file source (unused)
            file_secret_settings: Secret file source (unused)

        Returns:
            Tuple of settings sources in precedence order
        """
        # Order: CLI args (init_settings), env vars, TOML file
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def create_settings(
    toml_file: Optional[str] = None,
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> LarkWebhookSettings:
    """Create settings with optional custom configuration sources.

    This function creates a settings instance that respects the configuration
    hierarchy while allowing for custom TOML file paths and direct parameter
    overrides.

    Args:
        toml_file: Custom path to TOML configuration file (optional)
        webhook_url: Direct webhook URL override (highest priority)
        webhook_secret: Direct webhook secret override (highest priority)

    Returns:
        Configured LarkWebhookSettings instance

    Example:
        >>> # Use default configuration sources
        >>> settings = create_settings()
        >>>
        >>> # Use custom TOML file
        >>> settings = create_settings(toml_file="/path/to/config.toml")
        >>>
        >>> # Override with direct parameters
        >>> settings = create_settings(
        ...     webhook_url="https://example.com/webhook",
        ...     webhook_secret="secret123"
        ... )
    """
    # Prepare initialization parameters (highest priority)
    init_kwargs = {}
    if webhook_url:
        init_kwargs["webhook_url"] = webhook_url
    if webhook_secret:
        init_kwargs["webhook_secret"] = webhook_secret

    if toml_file and Path(toml_file).exists():
        # Create a custom settings class with specified TOML file
        class CustomSettings(LarkWebhookSettings):
            model_config = SettingsConfigDict(
                env_prefix="LARK_",
                env_file=".env",
                toml_file=toml_file,
                extra="ignore",
                case_sensitive=False,
            )

        return CustomSettings(**init_kwargs)
    else:
        # Use default TOML file path
        if toml_file and not Path(toml_file).exists():
            # Log a warning about missing custom TOML file, but continue
            import logging

            logger = logging.getLogger("lark-webhook-notify")
            logger.warning(
                f"Custom TOML file not found: {toml_file}. Using default configuration."
            )

        return LarkWebhookSettings(**init_kwargs)


if __name__ == "__main__":
    """Simple configuration test when run as a script."""
    config = create_settings()
    print("Configuration loaded:")
    print(f"  Webhook URL: {config.webhook_url or 'Not configured'}")
    print(f"  Webhook Secret: {'Set' if config.webhook_secret else 'Not configured'}")

    if not config.webhook_url or not config.webhook_secret:
        print("\nConfiguration incomplete. Please set:")
        if not config.webhook_url:
            print("  - LARK_WEBHOOK_URL environment variable, or")
            print("  - webhook_url in lark_webhook.toml")
        if not config.webhook_secret:
            print("  - LARK_WEBHOOK_SECRET environment variable, or")
            print("  - webhook_secret in lark_webhook.toml")
