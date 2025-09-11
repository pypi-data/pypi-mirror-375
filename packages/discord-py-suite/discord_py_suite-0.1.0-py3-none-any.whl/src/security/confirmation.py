"""Confirmation handler for destructive operations."""

import json
from typing import Any, Dict, List
from mcp.types import TextContent


class ConfirmationHandler:
    """Handles confirmation flows for destructive Discord operations."""

    def __init__(self, policy: Any) -> None:
        self.policy = policy

    def format_confirmation_preview(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> str:
        """Generate a preview of what the operation will do."""
        preview_data = self._generate_preview_data(tool_name, parameters)

        preview_text = f"🚨 **CONFIRMATION REQUIRED** 🚨\n\n"
        preview_text += f"**Tool:** `{tool_name}`\n"
        preview_text += f"**Action:** {preview_data['action']}\n\n"

        if preview_data.get("target"):
            preview_text += f"**Target:** {preview_data['target']}\n"

        if preview_data.get("details"):
            preview_text += f"**Details:** {preview_data['details']}\n"

        if preview_data.get("warning"):
            preview_text += f"\n⚠️ **WARNING:** {preview_data['warning']}\n"

        if self.policy.requires_high_privilege_confirmation(tool_name):
            preview_text += "\n🔥 **HIGH PRIVILEGE OPERATION** 🔥\n"
            preview_text += (
                "This operation has significant impact and cannot be undone easily.\n"
            )

        preview_text += (
            f"\n**Parameters:**\n```json\n{json.dumps(parameters, indent=2)}\n```\n"
        )
        preview_text += "\n**To proceed, call this tool again with `confirm=false`**"

        return preview_text

    def _generate_preview_data(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate preview data based on tool type."""
        preview_data = {"action": "Unknown action"}

        # Channel operations
        if tool_name == "discord_delete_channel":
            preview_data.update(
                {
                    "action": "Delete Discord channel",
                    "target": f"Channel ID: {parameters.get('channel_id', 'Unknown')}",
                    "warning": "This will permanently delete the channel and all its messages!",
                }
            )

        # Member management
        elif tool_name in ["discord_ban_member", "discord_ban_user"]:
            preview_data.update(
                {
                    "action": "Ban user from server",
                    "target": f"User ID: {parameters.get('user_id', 'Unknown')}",
                    "details": f"Delete message days: {parameters.get('delete_message_days', 0)}",
                    "warning": "This will remove the user from the server and optionally delete their recent messages!",
                }
            )

        elif tool_name == "discord_kick_member":
            preview_data.update(
                {
                    "action": "Kick member from server",
                    "target": f"User ID: {parameters.get('user_id', 'Unknown')}",
                    "warning": "This will remove the user from the server (they can rejoin)!",
                }
            )

        elif tool_name == "discord_timeout_member":
            preview_data.update(
                {
                    "action": "Timeout member",
                    "target": f"User ID: {parameters.get('user_id', 'Unknown')}",
                    "details": f"Duration: {parameters.get('duration', 'Unknown')}",
                    "warning": "This will prevent the member from participating in the server!",
                }
            )

        # Role operations
        elif tool_name == "discord_delete_role":
            preview_data.update(
                {
                    "action": "Delete server role",
                    "target": f"Role ID: {parameters.get('role_id', 'Unknown')}",
                    "warning": "This will permanently delete the role and remove it from all members!",
                }
            )

        # Message operations
        elif tool_name == "discord_bulk_delete_messages":
            preview_data.update(
                {
                    "action": "Bulk delete messages",
                    "target": f"Channel ID: {parameters.get('channel_id', 'Unknown')}",
                    "details": f"Message count: {len(parameters.get('message_ids', []))}",
                    "warning": "This will permanently delete multiple messages at once!",
                }
            )

        # Server operations
        elif tool_name == "discord_delete_guild":
            preview_data.update(
                {
                    "action": "Delete entire Discord server",
                    "target": f"Guild ID: {parameters.get('guild_id', 'Unknown')}",
                    "warning": "🔥 THIS WILL PERMANENTLY DELETE THE ENTIRE SERVER! 🔥",
                }
            )

        elif tool_name == "discord_begin_prune":
            preview_data.update(
                {
                    "action": "Remove inactive members",
                    "target": f"Guild ID: {parameters.get('guild_id', 'Unknown')}",
                    "details": f"Inactive days: {parameters.get('days', 'Unknown')}",
                    "warning": "This will permanently remove members who haven't been active!",
                }
            )

        # Forum operations
        elif tool_name == "discord_delete_forum_post":
            preview_data.update(
                {
                    "action": "Delete forum post/thread",
                    "target": f"Thread ID: {parameters.get('thread_id', 'Unknown')}",
                    "warning": "This will permanently delete the forum post and all its messages!",
                }
            )

        # Webhook operations
        elif tool_name == "discord_delete_webhook":
            preview_data.update(
                {
                    "action": "Delete webhook",
                    "target": f"Webhook ID: {parameters.get('webhook_id', 'Unknown')}",
                    "warning": "This will permanently delete the webhook and break any integrations using it!",
                }
            )

        # Generic destructive operation
        else:
            preview_data.update(
                {
                    "action": f"Execute destructive operation: {tool_name}",
                    "warning": "This operation may have permanent effects!",
                }
            )

        return preview_data

    def create_confirmation_response(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> List[TextContent]:
        """Create MCP response for confirmation flow."""
        preview_text = self.format_confirmation_preview(tool_name, parameters)

        return [TextContent(type="text", text=preview_text)]

    def should_show_confirmation(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> bool:
        """Check if confirmation should be shown for this tool call."""
        # Check if tool requires confirmation
        if not self.policy.requires_confirmation(tool_name):
            return False

        # Check if confirm parameter is explicitly set to false
        confirm_param = parameters.get("confirm", True)
        if confirm_param is False:
            return False  # User has confirmed, proceed with execution

        return True  # Show confirmation
