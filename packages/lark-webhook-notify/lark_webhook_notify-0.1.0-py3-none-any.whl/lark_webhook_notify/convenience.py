"""Convenience functions for backward compatibility and easy usage.

This module provides high-level convenience functions that create template instances
and send them using the LarkWebhookNotifier. These functions maintain backward
compatibility with the original cauldron interface while using the new template system.
"""

from typing import Optional, Dict, Any

from .client import LarkWebhookNotifier
from .templates import (
    LegacyTaskTemplate,
    StartTaskTemplate,
    ReportTaskResultTemplate,
    SimpleMessageTemplate,
    AlertTemplate,
    SeverityLevel,
    ColorTheme,
    LanguageCode,
)


def send_task_notification(
    task_name: str,
    status: Optional[int] = None,
    group: Optional[str] = None,
    prefix: Optional[str] = None,
    desc: Optional[str] = None,
    msg: Optional[str] = None,
    legacy_format: bool = False,
    duration: Optional[str] = None,
    language: LanguageCode = "zh",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a task notification (backward compatible with cauldron interface).

    This convenience function automatically selects the appropriate template based
    on the task status and parameters provided.

    Args:
        task_name: Name of the task being reported
        status: Task status code (None=running, 0=success, other=failed)
        group: Storage group identifier for task results
        prefix: Storage path prefix for task results
        desc: Human-readable task description
        msg: Custom message content (auto-generated from log if None for completed tasks)
        legacy_format: Use legacy template format for compatibility
        duration: Task execution duration
        language: Display language code (default: "zh")
        webhook_url: Override configured webhook URL
        webhook_secret: Override configured webhook secret

    Returns:
        Response dictionary from the webhook API

    Example:
        >>> # Send running task notification
        >>> send_task_notification("build-project", desc="Building application")
        >>>
        >>> # Send completed task notification
        >>> send_task_notification("build-project", status=0, group="artifacts")
        >>>
        >>> # Send failed task notification with custom message
        >>> send_task_notification(
        ...     "build-project",
        ...     status=1,
        ...     msg="Build failed: compilation error"
        ... )
    """
    if legacy_format:
        # Use legacy template for backward compatibility
        template = LegacyTaskTemplate(
            task_name=task_name,
            status=status,
            group=group,
            prefix=prefix,
            task_summary=msg,
            language=language,
        )
    elif status is None:
        # Task is starting/running
        template = StartTaskTemplate(
            task_name=task_name,
            desc=desc,
            group=group,
            prefix=prefix,
            estimated_duration=duration,
            language=language,
        )
    else:
        # Task has completed (success or failure)
        template = ReportTaskResultTemplate(
            task_name=task_name,
            status=status,
            group=group,
            prefix=prefix,
            desc=desc,
            msg=msg,
            duration=duration,
            language=language,
        )

    with LarkWebhookNotifier(
        webhook_url=webhook_url, webhook_secret=webhook_secret
    ) as notifier:
        return notifier.send_template(template)


def send_alert(
    alert_title: str,
    alert_message: str,
    severity: SeverityLevel = "warning",
    timestamp: Optional[str] = None,
    language: LanguageCode = "zh",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an alert notification with severity-based styling.

    Args:
        alert_title: Title of the alert notification
        alert_message: Detailed alert message content
        severity: Alert severity level (info, warning, error, critical)
        timestamp: Custom timestamp string (defaults to current time)
        language: Display language code (default: "zh")
        webhook_url: Override configured webhook URL
        webhook_secret: Override configured webhook secret

    Returns:
        Response dictionary from the webhook API

    Example:
        >>> # Send warning alert
        >>> send_alert("System Warning", "High memory usage detected")
        >>>
        >>> # Send critical alert
        >>> send_alert(
        ...     "Service Down",
        ...     "Database connection failed",
        ...     severity="critical"
        ... )
    """
    template = AlertTemplate(
        alert_title=alert_title,
        alert_message=alert_message,
        severity=severity,
        timestamp=timestamp,
        language=language,
    )

    with LarkWebhookNotifier(
        webhook_url=webhook_url, webhook_secret=webhook_secret
    ) as notifier:
        return notifier.send_template(template)


def send_simple_message(
    title: str,
    content: str,
    color: ColorTheme = "blue",
    language: LanguageCode = "zh",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a simple text message notification.

    Args:
        title: Message title displayed in the header
        content: Main message content (supports markdown formatting)
        color: Theme color for the card header
        language: Display language code (default: "zh")
        webhook_url: Override configured webhook URL
        webhook_secret: Override configured webhook secret

    Returns:
        Response dictionary from the webhook API

    Example:
        >>> # Send simple info message
        >>> send_simple_message(
        ...     "Deployment Complete",
        ...     "Application v2.1.0 deployed successfully"
        ... )
        >>>
        >>> # Send styled message with markdown
        >>> send_simple_message(
        ...     "Build Report",
        ...     "**Status:** Success\\n**Duration:** 5m 32s\\n**Tests:** All passed",
        ...     color="green"
        ... )
    """
    template = SimpleMessageTemplate(
        title=title, content=content, color=color, language=language
    )

    with LarkWebhookNotifier(
        webhook_url=webhook_url, webhook_secret=webhook_secret
    ) as notifier:
        return notifier.send_template(template)


def send_task_start(
    task_name: str,
    desc: Optional[str] = None,
    group: Optional[str] = None,
    prefix: Optional[str] = None,
    estimated_duration: Optional[str] = None,
    language: LanguageCode = "zh",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a task start notification.

    Args:
        task_name: Name of the task being started
        desc: Human-readable task description
        group: Storage group identifier for future results
        prefix: Storage path prefix for future results
        estimated_duration: Expected duration (e.g., "5 minutes")
        language: Display language code (default: "zh")
        webhook_url: Override configured webhook URL
        webhook_secret: Override configured webhook secret

    Returns:
        Response dictionary from the webhook API

    Example:
        >>> send_task_start(
        ...     "data-processing",
        ...     desc="Processing daily analytics",
        ...     estimated_duration="30 minutes"
        ... )
    """
    template = StartTaskTemplate(
        task_name=task_name,
        desc=desc,
        group=group,
        prefix=prefix,
        estimated_duration=estimated_duration,
        language=language,
    )

    with LarkWebhookNotifier(
        webhook_url=webhook_url, webhook_secret=webhook_secret
    ) as notifier:
        return notifier.send_template(template)


def send_task_result(
    task_name: str,
    status: int,
    group: Optional[str] = None,
    prefix: Optional[str] = None,
    desc: Optional[str] = None,
    msg: Optional[str] = None,
    duration: Optional[str] = None,
    language: LanguageCode = "zh",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a task result notification.

    Args:
        task_name: Name of the completed task
        status: Task status code (0=success, other=failed)
        group: Storage group identifier for task results
        prefix: Storage path prefix for task results
        desc: Human-readable task description
        msg: Custom result message (auto-generated from log if None)
        duration: Task execution duration
        language: Display language code (default: "zh")
        webhook_url: Override configured webhook URL
        webhook_secret: Override configured webhook secret

    Returns:
        Response dictionary from the webhook API

    Example:
        >>> send_task_result(
        ...     "data-processing",
        ...     status=0,
        ...     desc="Daily analytics processing",
        ...     duration="25 minutes",
        ...     msg="Processed 1.2M records successfully"
        ... )
    """
    template = ReportTaskResultTemplate(
        task_name=task_name,
        status=status,
        group=group,
        prefix=prefix,
        desc=desc,
        msg=msg,
        duration=duration,
        language=language,
    )

    with LarkWebhookNotifier(
        webhook_url=webhook_url, webhook_secret=webhook_secret
    ) as notifier:
        return notifier.send_template(template)
