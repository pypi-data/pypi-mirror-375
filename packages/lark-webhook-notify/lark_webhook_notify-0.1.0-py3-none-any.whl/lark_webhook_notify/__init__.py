from .client import LarkWebhookNotifier
from .config import LarkWebhookSettings, create_settings
from .templates import (
    LarkTemplate,
    LegacyTaskTemplate,
    StartTaskTemplate,
    ReportTaskResultTemplate,
    SimpleMessageTemplate,
    AlertTemplate,
    RawContentTemplate,
    CardContent,
    SeverityLevel,
    ColorTheme,
)
from .convenience import (
    send_task_notification,
    send_alert,
    send_simple_message,
    send_task_start,
    send_task_result,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "LarkWebhookNotifier",
    # Configuration
    "LarkWebhookSettings",
    "create_settings",
    # Templates
    "LarkTemplate",
    "LegacyTaskTemplate",
    "StartTaskTemplate",
    "ReportTaskResultTemplate",
    "SimpleMessageTemplate",
    "AlertTemplate",
    "RawContentTemplate",
    # Convenience functions
    "send_task_notification",
    "send_alert",
    "send_simple_message",
    "send_task_start",
    "send_task_result",
    # Types
    "CardContent",
    "SeverityLevel",
    "ColorTheme",
]
