# Lark Webhook Notify

A Python library for sending rich notifications to Lark (Feishu) webhooks with configurable templates and hierarchical configuration management.

## Features

- **Hierarchical Configuration**: TOML file -> Environment variables -> CLI arguments
- **Multiple Templates**: Legacy, modern, simple message, and alert templates
- **Rich Notifications**: Collapsible panels, status indicators, markdown support
- **Secure**: Proper HMAC-SHA256 signature generation
- **CLI Interface**: Command-line tool for quick notifications
- **Python API**: Comprehensive programmatic interface

## Installation

```bash
# Install from PyPI
pip install lark-webhook-notify
# Or if you are using uv
uv add lark-webhook-notify
```

## Quick Start

### 1. Configuration

Create a configuration file or set environment variables:

```toml
# lark_webhook.toml
lark_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
lark_webhook_secret = "YOUR_WEBHOOK_SECRET"
```

Or use environment variables:

```bash
export LARK_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
export LARK_WEBHOOK_SECRET="YOUR_WEBHOOK_SECRET"
```

### 2. Python API

```python
from lark_webhook_notify import send_task_notification, send_alert, send_simple_message

# Send task notification (cauldron compatible)
send_task_notification(
    task_name="deployment",
    status=0,  # 0=success, 1+=failed, None=running
    desc="Deploy application to production",
    group="artifacts",
    prefix="prod-deploy"
)

# Send alert notification
send_alert(
    alert_title="System Alert",
    alert_message="High memory usage detected on server",
    severity="warning"  # info, warning, error, critical
)

# Send simple message
send_simple_message(
    title="Build Complete",
    content="Application v2.1.0 built successfully ",
    color="green"
)
```

### 3. CLI Usage

```bash
# Task notifications
lark-weebhook-notify task "build-project" --desc "Building application" --status 0

# Alert notifications
lark-weebhook-notify alert "Service Down" "Database connection failed" --severity critical

# Simple messages
lark-weebhook-notify message "Hello" "This is a test message" --color blue

# List available templates
lark-weebhook-notify templates

# Test connection
lark-weebhook-notify test
```

## Configuration

### Configuration Hierarchy

Settings are loaded in order of precedence (highest to lowest):

1. **Command line arguments** / direct parameters
2. **Environment variables** (`LARK_WEBHOOK_URL`, `LARK_WEBHOOK_SECRET`)
3. **TOML file** (`lark_webhook.toml` by default)
4. **Default values**

### Configuration Files

#### TOML Configuration

```toml
# lark_webhook.toml
lark_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
lark_webhook_secret = "YOUR_WEBHOOK_SECRET"
```

#### Environment Variables

```bash
# Required
export LARK_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
export LARK_WEBHOOK_SECRET="YOUR_WEBHOOK_SECRET"
```

#### Custom Configuration

```python
from lark_webhook_notify import create_settings, LarkWebhookNotifier

# Custom TOML file
settings = create_settings(toml_file="/path/to/custom.toml")

# Direct parameters (highest priority)
settings = create_settings(
    webhook_url="https://example.com/webhook",
    webhook_secret="custom-secret"
)
```

## Templates

### Available Templates

| Template  | Description                                                    |
| --------- | -------------------------------------------------------------- |
| `start`   | Task start notifications                                       |
| `task`    | Rich card with collapsible panels to report the result of task |
| `legacy`  | Simple template (old version compatible)                       |
| `message` | Basic text message                                             |
| `alert`   | Severity-based styling                                         |
| `raw`     | Raw card content passthrough                                   |

### Debug Mode

Enable debug logging for detailed information:

```bash
# CLI
lark-webhook-notify --debug test
```

```python
# Python
import logging
logging.getLogger("lark-webhook-notify").setLevel(logging.DEBUG)
```

### Getting Help

- Check the [Issues](https://github.com/BobAnkh/lark-webhook-notify/issues) page
- Review this documentation
- Enable debug mode for detailed error information

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code passes linting (`uvx ruff check`) and format (`uvx ruff format`)
5. Submit a pull request

## License

Apache-2.0 License. See [LICENSE](LICENSE) for details.
