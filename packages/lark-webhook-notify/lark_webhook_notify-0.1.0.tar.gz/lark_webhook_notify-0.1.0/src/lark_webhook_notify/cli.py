"""Command-line interface for Lark webhook notifications.

This module provides a comprehensive CLI for sending different types of notifications
using the new template system. It supports all six template types and maintains
backward compatibility with the original interface.
"""

import argparse
import json
import logging
import sys

from .client import LarkWebhookNotifier
from .templates import (
    LegacyTaskTemplate,
    RawContentTemplate,
)
from .convenience import (
    send_task_notification,
    send_alert,
    send_simple_message,
    send_task_start,
    send_task_result,
)


def get_logger() -> logging.Logger:
    """Get the configured logger."""
    return logging.getLogger("lark-webhook-notify")


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Send notifications to Lark webhook using predefined templates. "
        "Configuration is read from TOML file, environment variables, and CLI arguments (in order of precedence)."
    )

    # Global options
    parser.add_argument(
        "--config", help="Path to TOML configuration file (default: lark_webhook.toml)"
    )
    parser.add_argument(
        "--webhook-url",
        help="Lark webhook URL (overrides config/env: LARK_WEBHOOK_URL)",
    )
    parser.add_argument(
        "--webhook-secret",
        help="Lark webhook secret (overrides config/env: LARK_WEBHOOK_SECRET)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--language",
        choices=["zh", "en"],
        default="zh",
        help="Display language for templates (default: zh)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Task notification command (backward compatible)
    task_parser = subparsers.add_parser(
        "task", help="Send task notification (auto-detects template based on status)"
    )
    task_parser.add_argument("task_name", help="Name of the task")
    task_parser.add_argument(
        "--status",
        type=int,
        help="Task status code (omit for start notification, 0 for success, other for failed)",
    )
    task_parser.add_argument("--group", help="Storage group for results")
    task_parser.add_argument("--prefix", help="Storage prefix for results")
    task_parser.add_argument("--desc", help="Task description")
    task_parser.add_argument("--msg", help="Custom message for task summary")
    task_parser.add_argument("--duration", help="Task duration (e.g., '5 minutes')")
    task_parser.add_argument(
        "--legacy", action="store_true", help="Use legacy template format"
    )

    # Task start command
    start_parser = subparsers.add_parser("start", help="Send task start notification")
    start_parser.add_argument("task_name", help="Name of the task")
    start_parser.add_argument("--desc", help="Task description")
    start_parser.add_argument("--group", help="Storage group for future results")
    start_parser.add_argument("--prefix", help="Storage prefix for future results")
    start_parser.add_argument(
        "--duration", help="Estimated duration (e.g., '10 minutes')"
    )

    # Task result command
    result_parser = subparsers.add_parser(
        "result", help="Send task result notification"
    )
    result_parser.add_argument("task_name", help="Name of the completed task")
    result_parser.add_argument(
        "status", type=int, help="Task status code (0=success, other=failed)"
    )
    result_parser.add_argument("--group", help="Storage group for results")
    result_parser.add_argument("--prefix", help="Storage prefix for results")
    result_parser.add_argument("--desc", help="Task description")
    result_parser.add_argument("--msg", help="Custom result message")
    result_parser.add_argument("--duration", help="Task execution duration")

    # Legacy task command
    legacy_parser = subparsers.add_parser(
        "legacy", help="Send legacy task notification"
    )
    legacy_parser.add_argument("task_name", help="Name of the task")
    legacy_parser.add_argument("--status", type=int, help="Task status code")
    legacy_parser.add_argument("--group", help="Storage group for results")
    legacy_parser.add_argument("--prefix", help="Storage prefix for results")
    legacy_parser.add_argument("--summary", help="Task summary content")

    # Alert command
    alert_parser = subparsers.add_parser("alert", help="Send alert notification")
    alert_parser.add_argument("title", help="Alert title")
    alert_parser.add_argument("message", help="Alert message")
    alert_parser.add_argument(
        "--severity",
        choices=["info", "warning", "error", "critical"],
        default="warning",
        help="Alert severity level",
    )
    alert_parser.add_argument("--timestamp", help="Custom timestamp")

    # Simple message command
    message_parser = subparsers.add_parser("message", help="Send simple message")
    message_parser.add_argument("title", help="Message title")
    message_parser.add_argument("content", help="Message content")
    message_parser.add_argument("--color", default="blue", help="Message color theme")

    # Raw content command
    raw_parser = subparsers.add_parser("raw", help="Send raw card content")
    raw_parser.add_argument("content", help="JSON string of card content")

    # List templates command
    subparsers.add_parser("templates", help="List available template types")

    # Test connection command
    subparsers.add_parser("test", help="Test webhook connection")

    return parser


def cmd_task(args) -> int:
    """Handle backward-compatible task notification command."""
    try:
        send_task_notification(
            task_name=args.task_name,
            status=args.status,
            group=args.group,
            prefix=args.prefix,
            desc=args.desc,
            msg=args.msg,
            duration=args.duration,
            legacy_format=args.legacy,
            language=args.language,
            webhook_url=args.webhook_url,
            webhook_secret=args.webhook_secret,
        )
        return 0
    except Exception as e:
        get_logger().error(f"Failed to send task notification: {e}")
        return 1


def cmd_start(args) -> int:
    """Handle task start notification command."""
    try:
        send_task_start(
            task_name=args.task_name,
            desc=args.desc,
            group=args.group,
            prefix=args.prefix,
            estimated_duration=args.duration,
            language=args.language,
            webhook_url=args.webhook_url,
            webhook_secret=args.webhook_secret,
        )
        return 0
    except Exception as e:
        get_logger().error(f"Failed to send task start notification: {e}")
        return 1


def cmd_result(args) -> int:
    """Handle task result notification command."""
    try:
        send_task_result(
            task_name=args.task_name,
            status=args.status,
            group=args.group,
            prefix=args.prefix,
            desc=args.desc,
            msg=args.msg,
            duration=args.duration,
            language=args.language,
            webhook_url=args.webhook_url,
            webhook_secret=args.webhook_secret,
        )
        return 0
    except Exception as e:
        get_logger().error(f"Failed to send task result notification: {e}")
        return 1


def cmd_legacy(args) -> int:
    """Handle legacy task notification command."""
    try:
        template = LegacyTaskTemplate(
            task_name=args.task_name,
            status=args.status,
            group=args.group,
            prefix=args.prefix,
            task_summary=args.summary,
            language=args.language,
        )
        with LarkWebhookNotifier(
            webhook_url=args.webhook_url, webhook_secret=args.webhook_secret
        ) as notifier:
            notifier.send_template(template)
        return 0
    except Exception as e:
        get_logger().error(f"Failed to send legacy notification: {e}")
        return 1


def cmd_alert(args) -> int:
    """Handle alert notification command."""
    try:
        send_alert(
            alert_title=args.title,
            alert_message=args.message,
            severity=args.severity,
            timestamp=args.timestamp,
            language=args.language,
            webhook_url=args.webhook_url,
            webhook_secret=args.webhook_secret,
        )
        return 0
    except Exception as e:
        get_logger().error(f"Failed to send alert: {e}")
        return 1


def cmd_message(args) -> int:
    """Handle simple message command."""
    try:
        send_simple_message(
            title=args.title,
            content=args.content,
            color=args.color,
            language=args.language,
            webhook_url=args.webhook_url,
            webhook_secret=args.webhook_secret,
        )
        return 0
    except Exception as e:
        get_logger().error(f"Failed to send message: {e}")
        return 1


def cmd_raw(args) -> int:
    """Handle raw content command."""
    try:
        card_content = json.loads(args.content)
        template = RawContentTemplate(card_content=card_content, language=args.language)

        with LarkWebhookNotifier(
            webhook_url=args.webhook_url, webhook_secret=args.webhook_secret
        ) as notifier:
            notifier.send_template(template)
        return 0
    except json.JSONDecodeError as e:
        get_logger().error(f"Invalid JSON in content: {e}")
        return 1
    except Exception as e:
        get_logger().error(f"Failed to send raw content: {e}")
        return 1


def cmd_templates(args) -> int:
    """Handle list templates command."""
    print("Available template types:")
    print(
        "  - task          : Auto-detect template based on status (backward compatible)"
    )
    print("  - start         : Task start notifications")
    print("  - result        : Task completion/result notifications")
    print("  - legacy        : Legacy cauldron-compatible format")
    print("  - alert         : Severity-based alert notifications")
    print("  - message       : Simple text messages")
    print("  - raw           : Raw card content passthrough")
    print()
    print("Template usage patterns:")
    print(
        "  Start task    -> lark-webhook-notify start 'task-name' --desc 'Description'"
    )
    print(
        "  Task success  -> lark-webhook-notify result 'task-name' 0 --duration '5 min'"
    )
    print(
        "  Task failure  -> lark-webhook-notify result 'task-name' 1 --msg 'Error details'"
    )
    print(
        "  Alert         -> lark-webhook-notify alert 'Title' 'Message' --severity error"
    )
    print(
        "  Simple msg    -> lark-webhook-notify message 'Title' 'Content' --color green"
    )
    return 0


def cmd_test(args) -> int:
    """Handle test connection command."""
    try:
        send_simple_message(
            title="Test Notification",
            content="This is a test message from lark-webhook-notify",
            language=args.language,
            webhook_url=args.webhook_url,
            webhook_secret=args.webhook_secret,
        )
        print("Test notification sent successfully!")
        return 0
    except Exception as e:
        get_logger().error(f"Test failed: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    if args.debug:
        get_logger().setLevel(logging.DEBUG)

    # Handle commands
    if args.command == "task":
        return cmd_task(args)
    elif args.command == "start":
        return cmd_start(args)
    elif args.command == "result":
        return cmd_result(args)
    elif args.command == "legacy":
        return cmd_legacy(args)
    elif args.command == "alert":
        return cmd_alert(args)
    elif args.command == "message":
        return cmd_message(args)
    elif args.command == "raw":
        return cmd_raw(args)
    elif args.command == "templates":
        return cmd_templates(args)
    elif args.command == "test":
        return cmd_test(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
