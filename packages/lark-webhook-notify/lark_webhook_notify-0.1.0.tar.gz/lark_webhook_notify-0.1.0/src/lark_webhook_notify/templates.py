"""Template system for Lark webhook notifications.

This module provides six predefined templates for different notification types:
1. LegacyTaskTemplate - A legacy template format
2. StartTaskTemplate - Task start notifications
3. ReportTaskResultTemplate - Task completion/result notifications
4. SimpleMessageTemplate - Basic text messages
5. AlertTemplate - Urgent notifications with severity levels
6. RawContentTemplate - Direct card content passthrough

Each template is a class that can be instantiated with parameters and then
passed to the LarkWebhookNotifier client.
"""

from typing import Optional, Dict, Any, Literal
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path

# Type aliases for better readability
SeverityLevel = Literal["info", "warning", "error", "critical"]
ColorTheme = Literal["blue", "green", "red", "orange", "wathet", "purple", "grey"]
CardContent = Dict[str, Any]
LanguageCode = Literal["zh", "en"]

# Translation dictionaries
TRANSLATIONS: Dict[LanguageCode, Dict[str, str]] = {
    "zh": {
        "task_name": "任务名称",
        "start_time": "开始时间",
        "completion_time": "完成时间",
        "task_description": "任务描述",
        "estimated_duration": "预计用时",
        "execution_duration": "执行时长",
        "execution_status": "执行状态",
        "result_storage": "结果存储",
        "storage_prefix": "存储前缀",
        "result_overview": "结果概览",
        "running": "正在运行",
        "completed": "已成功完成",
        "failed": "失败",
        "success": "已完成",
        "failure": "失败",
        "task_notification": "任务运行情况通知",
        "task_completion_notification": "任务完成情况通知",
        "task_failure_notification": "任务失败情况通知",
        "no_description": "*No description provided*",
        "timestamp": "时间",
        "unknown_task": "未知任务",
        "return_code": "返回值",
        "group": "任务组别",
    },
    "en": {
        "task_name": "Task Name",
        "start_time": "Start Time",
        "completion_time": "Completion Time",
        "task_description": "Task Description",
        "estimated_duration": "Estimated Duration",
        "execution_duration": "Execution Duration",
        "execution_status": "Execution Status",
        "result_storage": "Result Storage",
        "storage_prefix": "Storage Prefix",
        "result_overview": "Result Overview",
        "running": "Running",
        "completed": "Successfully Completed",
        "failed": "Failed",
        "success": "Completed",
        "failure": "Failed",
        "task_notification": "Task Status Notification",
        "task_completion_notification": "Task Completion Notification",
        "task_failure_notification": "Task Failure Notification",
        "no_description": "*No description provided*",
        "timestamp": "Timestamp",
        "unknown_task": "Unknown Task",
        "return_code": "Return Status",
        "group": "Task Group",
    },
}


def get_translation(key: str, language: LanguageCode = "zh") -> str:
    """Get translation for a given key and language.

    Args:
        key: Translation key
        language: Language code (default: "zh")

    Returns:
        Translated string or the key itself if not found
    """
    return TRANSLATIONS.get(language, TRANSLATIONS["zh"]).get(key, key)


def get_task_summary(log_file_path: str) -> str:
    """Extract task summary from log file (compatible with cauldron format).

    Parses the last few lines of a log file to extract task metrics and
    format them as a markdown table. This maintains compatibility with
    the cauldron log file format.

    Args:
        log_file_path: Path to the log file to parse

    Returns:
        Markdown table string containing task metrics, or error message
    """
    log_path = Path(log_file_path)

    try:
        if not log_path.exists():
            return f"Error: Log file not found at {log_path}"

        with log_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 10:
            return "Error: Log file too short to extract summary"

        # Extract relevant lines (last 8 lines, excluding the final 2)
        relevant_lines = lines[-10:-2]

        markdown_table_rows = ["| 指标 | 样本数 | 误差 |", "|:---|:---|:---|"]
        for line in relevant_lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) >= 5:
                metric = parts[0]
                sample_count = parts[2]
                error_info = f"{parts[3]} {parts[4]}"
                markdown_table_rows.append(
                    f"| {metric} | {sample_count} | {error_info} |"
                )

        if len(markdown_table_rows) <= 2:
            return "No valid metric data found in log file"

        markdown_table = "\n".join(markdown_table_rows)

    except PermissionError:
        markdown_table = f"Error: Permission denied reading {log_path}"
    except Exception as e:
        markdown_table = f"An error occurred while processing log file: {e}"

    return markdown_table


class LarkTemplate(ABC):
    """Base class for Lark notification templates.

    All templates must implement the generate method which returns a dictionary
    representing the Lark card content structure.
    """

    def __init__(self, language: LanguageCode = "zh"):
        """Initialize base template.

        Args:
            language: Display language code (default: "zh")
        """
        self.language = language

    def _t(self, key: str) -> str:
        """Get translation for the current template language.

        Args:
            key: Translation key

        Returns:
            Translated string
        """
        return get_translation(key, self.language)

    @abstractmethod
    def generate(self) -> CardContent:
        """Generate the template card content.

        Returns:
            Dictionary containing the Lark card structure

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        pass


class LegacyTaskTemplate(LarkTemplate):
    """Legacy template format compatible with cauldron (old=True).

    This template uses the original cauldron template structure for backward
    compatibility. It's a simpler format that relies on a predefined template ID.
    """

    def __init__(
        self,
        task_name: Optional[str] = None,
        status: Optional[int] = None,
        group: Optional[str] = None,
        prefix: Optional[str] = None,
        task_summary: Optional[str] = None,
        language: LanguageCode = "zh",
    ):
        """Initialize legacy task template.

        Args:
            task_name: Name of the task being reported
            status: Task status code (None=running, 0=success, other=failed)
            group: Storage group identifier for task results
            prefix: Storage path prefix for task results
            task_summary: Markdown table summary of task results
            language: Display language code (default: "zh")
        """
        super().__init__(language)
        self.task_name = task_name or self._t("unknown_task")
        self.status = status or 0
        self.group = group or ""
        self.prefix = prefix or ""
        self.task_summary = task_summary or ""

    def generate(self) -> CardContent:
        """Generate legacy task notification card."""
        task_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        if self.status is not None and self.status != 0:
            task_status = f"<font color='red'> :CrossMark: {self._t('failed')}: {self._t('return_code')} {self.status}</font>"
        else:
            task_status = (
                f"<font color='green'> :CheckMark: {self._t('completed')}</font>"
            )

        return {
            "type": "template",
            "data": {
                "template_id": "AAqz08XD5HCzP",
                "template_version_name": "1.0.3",
                "template_variable": {
                    "task_name": self.task_name,
                    "task_time": task_time,
                    "attachment_group": self.group,
                    "attachment_prefix": self.prefix,
                    "task_summary": self.task_summary,
                    "task_status": task_status,
                },
            },
        }


class StartTaskTemplate(LarkTemplate):
    """Template for task start notifications.

    This template is used to notify about tasks that are beginning execution.
    It provides a clean, informative card showing the task is in progress.
    """

    def __init__(
        self,
        task_name: str,
        desc: Optional[str] = None,
        group: Optional[str] = None,
        prefix: Optional[str] = None,
        estimated_duration: Optional[str] = None,
        language: LanguageCode = "zh",
    ):
        """Initialize start task template.

        Args:
            task_name: Name of the task being started
            desc: Human-readable task description
            group: Storage group identifier for future results
            prefix: Storage path prefix for future results
            estimated_duration: Expected duration (e.g., "5 minutes")
            language: Display language code (default: "zh")
        """
        super().__init__(language)
        self.task_name = task_name or self._t("unknown_task")
        self.desc = desc or self._t("no_description")
        self.group = group
        self.prefix = prefix
        self.estimated_duration = estimated_duration

    def generate(self) -> CardContent:
        """Generate start task notification card."""
        task_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        elements = []

        # Task metadata element
        task_desc_text = f"\n**{self._t('task_description')}:** {self.desc}"
        duration_text = (
            f"\n**{self._t('estimated_duration')}:** {self.estimated_duration}"
            if self.estimated_duration
            else ""
        )
        task_status = (
            f"<font color='wathet-400'> :StatusInFlight: {self._t('running')}</font>"
        )

        task_metadata = {
            "tag": "markdown",
            "content": f"**{self._t('task_name')}:** {self.task_name}\n**{self._t('start_time')}:** {task_time}{task_desc_text}{duration_text}\n**{self._t('execution_status')}:** {task_status}",
            "text_align": "left",
            "text_size": "normal",
            "margin": "0px 0px 0px 0px",
        }
        elements.append(task_metadata)

        # Storage information if provided
        if self.group or self.prefix:
            task_result_storage = {
                "tag": "column_set",
                "background_style": "grey-100",
                "horizontal_spacing": "12px",
                "horizontal_align": "left",
                "columns": [
                    {
                        "tag": "column",
                        "width": "auto",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": f"**{self._t('result_storage')}**\n{self.group or ''}",
                                "text_align": "center",
                                "text_size": "normal_v2",
                                "margin": "0px 4px 0px 4px",
                            }
                        ],
                        "vertical_spacing": "8px",
                        "horizontal_align": "left",
                        "vertical_align": "top",
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": f"**{self._t('storage_prefix')}**\n{self.prefix or ''}",
                                "text_align": "center",
                                "text_size": "normal_v2",
                            }
                        ],
                        "vertical_spacing": "8px",
                        "horizontal_align": "left",
                        "vertical_align": "top",
                        "weight": 1,
                    },
                ],
                "margin": "0px 0px 0px 0px",
            }
            elements.append(task_result_storage)

        return {
            "schema": "2.0",
            "config": {
                "update_multi": True,
                "style": {
                    "text_size": {
                        "normal_v2": {
                            "default": "normal",
                            "pc": "normal",
                            "mobile": "heading",
                        }
                    }
                },
            },
            "body": {
                "direction": "vertical",
                "elements": elements,
            },
            "header": {
                "title": {"tag": "plain_text", "content": self._t("task_notification")},
                "subtitle": {"tag": "plain_text", "content": ""},
                "text_tag_list": [
                    {
                        "tag": "text_tag",
                        "text": {"tag": "plain_text", "content": self._t("running")},
                        "color": "wathet",
                    }
                ],
                "template": "wathet",
                "padding": "12px 8px 12px 8px",
            },
        }


class ReportTaskResultTemplate(LarkTemplate):
    """Template for task completion/result notifications.

    This template is used to notify about completed tasks with results.
    It includes collapsible panels for detailed results and supports both
    success and failure status indicators.
    """

    def __init__(
        self,
        task_name: str,
        status: int,
        group: Optional[str] = None,
        prefix: Optional[str] = None,
        desc: Optional[str] = None,
        msg: Optional[str] = None,
        duration: Optional[str] = None,
        language: LanguageCode = "zh",
    ):
        """Initialize task result template.

        Args:
            task_name: Name of the completed task
            status: Task status code (0=success, other=failed)
            group: Storage group identifier for task results
            prefix: Storage path prefix for task results
            desc: Human-readable task description
            msg: Custom result message (auto-generated from log if None and file exists)
            duration: Task execution duration
            language: Display language code (default: "zh")
        """
        super().__init__(language)
        self.task_name = task_name
        self.status = status
        self.group = group
        self.prefix = prefix
        self.desc = desc
        self.duration = duration

        # Auto-generate message from log file if not provided
        if msg is None:
            log_file_path = f"log-{task_name}.txt"
            self.msg = get_task_summary(log_file_path)
        else:
            self.msg = msg

    def generate(self) -> CardContent:
        """Generate task result notification card."""
        task_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Determine status colors and text
        if self.status == 0:
            task_status = (
                f"<font color='green'> :CheckMark: {self._t('completed')}</font>"
            )
            color = "green"
            head_tag = self._t("success")
            head_flag = self._t("success")
        else:
            task_status = f"<font color='red'> :CrossMark: {self._t('failed')}: {self.status}</font>"
            color = "red"
            head_tag = self._t("failure")
            head_flag = self._t("failure")

        elements = []

        # Task metadata element
        task_desc_text = (
            f"\n**{self._t('task_description')}：** {self.desc}" if self.desc else ""
        )
        duration_text = (
            f"\n**{self._t('execution_duration')}：** {self.duration}"
            if self.duration
            else ""
        )
        task_metadata = {
            "tag": "markdown",
            "content": f"**{self._t('task_name')}：** {self.task_name}\n**{self._t('completion_time')}：** {task_time}{task_desc_text}{duration_text}\n**{self._t('execution_status')}：** {task_status}",
            "text_align": "left",
            "text_size": "normal",
            "margin": "0px 0px 0px 0px",
        }
        elements.append(task_metadata)

        # Storage information if provided
        if self.group or self.prefix:
            task_result_storage = {
                "tag": "column_set",
                "background_style": "grey-100",
                "horizontal_spacing": "12px",
                "horizontal_align": "left",
                "columns": [
                    {
                        "tag": "column",
                        "width": "auto",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": f"**{self._t('group')}**\n{self.group or ''}",
                                "text_align": "center",
                                "text_size": "normal_v2",
                                "margin": "0px 4px 0px 4px",
                            }
                        ],
                        "vertical_spacing": "8px",
                        "horizontal_align": "left",
                        "vertical_align": "top",
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": f"**{self._t('storage_prefix')}**\n{self.prefix or ''}",
                                "text_align": "center",
                                "text_size": "normal_v2",
                            }
                        ],
                        "vertical_spacing": "8px",
                        "horizontal_align": "left",
                        "vertical_align": "top",
                        "weight": 1,
                    },
                ],
                "margin": "0px 0px 0px 0px",
            }
            elements.append(task_result_storage)

        # Result summary (collapsible panel)
        if self.msg:
            task_result_summary = {
                "tag": "collapsible_panel",
                "expanded": False,
                "header": {
                    "title": {
                        "tag": "markdown",
                        "content": f"**<font color='grey-800'>{self._t('result_overview')}</font>**",
                    },
                    "background_color": "grey-200",
                    "vertical_align": "center",
                    "icon": {
                        "tag": "standard_icon",
                        "token": "down-small-ccm_outlined",
                        "color": "",
                        "size": "16px 16px",
                    },
                    "icon_position": "right",
                    "icon_expanded_angle": -180,
                },
                "border": {"color": "grey", "corner_radius": "5px"},
                "vertical_spacing": "8px",
                "padding": "8px 8px 8px 8px",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"{self.msg}",
                        "text_align": "left",
                        "text_size": "normal_v2",
                        "margin": "0px 0px 0px 0px",
                    }
                ],
            }
            elements.append(task_result_summary)

        return {
            "schema": "2.0",
            "config": {
                "update_multi": True,
                "style": {
                    "text_size": {
                        "normal_v2": {
                            "default": "normal",
                            "pc": "normal",
                            "mobile": "heading",
                        }
                    }
                },
            },
            "body": {
                "direction": "vertical",
                "elements": elements,
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{self._t('task_notification')} - {head_flag}",
                },
                "subtitle": {"tag": "plain_text", "content": ""},
                "text_tag_list": [
                    {
                        "tag": "text_tag",
                        "text": {"tag": "plain_text", "content": head_tag},
                        "color": color,
                    }
                ],
                "template": color,
                "padding": "12px 8px 12px 8px",
            },
        }


class SimpleMessageTemplate(LarkTemplate):
    """Simple text message template for basic notifications.

    This template provides a clean, minimal notification format suitable for
    general purpose messaging without complex UI elements.
    """

    def __init__(
        self,
        title: str,
        content: str,
        color: ColorTheme = "blue",
        language: LanguageCode = "zh",
    ):
        """Initialize simple message template.

        Args:
            title: Message title displayed in the header
            content: Main message content (supports markdown)
            color: Theme color for the card header
            language: Display language code (default: "zh")
        """
        super().__init__(language)
        self.title = title
        self.content = content
        self.color = color

    def generate(self) -> CardContent:
        """Generate simple message card."""
        return {
            "schema": "2.0",
            "body": {
                "direction": "vertical",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": self.content,
                        "text_align": "left",
                        "text_size": "normal",
                    }
                ],
            },
            "header": {
                "title": {"tag": "plain_text", "content": self.title},
                "template": self.color,
            },
        }


class AlertTemplate(LarkTemplate):
    """Alert template for urgent and status notifications.

    This template provides severity-based styling and iconography to clearly
    communicate the importance and type of alert being sent.
    """

    def __init__(
        self,
        alert_title: str,
        alert_message: str,
        severity: SeverityLevel = "warning",
        timestamp: Optional[str] = None,
        language: LanguageCode = "zh",
    ):
        """Initialize alert template.

        Args:
            alert_title: Title of the alert notification
            alert_message: Detailed alert message content
            severity: Alert severity level (info, warning, error, critical)
            timestamp: Custom timestamp string (defaults to current time)
            language: Display language code (default: "zh")

        Raises:
            ValueError: If severity is not one of the supported values
        """
        super().__init__(language)
        self.alert_title = alert_title
        self.alert_message = alert_message
        self.severity = severity
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Validate severity
        valid_severities = {"info", "warning", "error", "critical"}
        if severity not in valid_severities:
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {', '.join(valid_severities)}"
            )

    def generate(self) -> CardContent:
        """Generate alert notification card."""
        # Mapping severity levels to colors and icons
        color_map: Dict[SeverityLevel, ColorTheme] = {
            "info": "blue",
            "warning": "orange",
            "error": "red",
            "critical": "red",
        }

        icon_map: Dict[SeverityLevel, str] = {
            "info": ":InfoCircle:",
            "warning": ":WarningTriangle:",
            "error": ":CrossMark:",
            "critical": ":Fire:",
        }

        color = color_map[self.severity]
        icon = icon_map[self.severity]

        return {
            "schema": "2.0",
            "body": {
                "direction": "vertical",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"{icon} **{self.alert_message}**\n\n**{self._t('timestamp')}：** {self.timestamp}",
                        "text_align": "left",
                        "text_size": "normal",
                    }
                ],
            },
            "header": {
                "title": {"tag": "plain_text", "content": self.alert_title},
                "subtitle": {"tag": "plain_text", "content": self.severity.upper()},
                "template": color,
                "text_tag_list": [
                    {
                        "tag": "text_tag",
                        "text": {"tag": "plain_text", "content": self.severity.upper()},
                        "color": color,
                    }
                ],
            },
        }


class RawContentTemplate(LarkTemplate):
    """Template for passing raw card content directly.

    This template allows you to pass pre-built Lark card content directly
    without any modification. Useful when you have custom card structures
    or when integrating with existing card generation logic.
    """

    def __init__(self, card_content: CardContent, language: LanguageCode = "zh"):
        """Initialize raw content template.

        Args:
            card_content: Pre-built Lark card content dictionary
            language: Display language code (default: "zh")
        """
        super().__init__(language)
        self.card_content = card_content

    def generate(self) -> CardContent:
        """Generate raw card content (passthrough)."""
        return self.card_content
