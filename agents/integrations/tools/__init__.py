"""Wrappers de domínio sobre o provider Composio (Calendar, Gmail, Slack)."""

from .calendar import schedule_meeting
from .email import send_email
from .notify import notify_handoff

__all__ = ["schedule_meeting", "send_email", "notify_handoff"]
