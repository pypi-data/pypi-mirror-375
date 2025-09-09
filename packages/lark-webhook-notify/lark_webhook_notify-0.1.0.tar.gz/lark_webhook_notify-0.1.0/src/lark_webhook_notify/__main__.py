"""Entry point for running lark-webhook-notify as a module or executable.

This module allows the package to be run as:
    python -m lark_webhook_notify [args...]

It also serves as the entry point for the installed CLI executable.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
