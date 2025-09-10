import os
import logging
import re
from typing import List, Dict, Any, Optional, Union
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import html2text

class SlackNotifier:
    """
    An advanced custom wrapper for the Slack SDK to simplify sending rich messages and files.
    """

    def __init__(self, token: str, timeout: int = 30, log: bool = True):
        """
        Initializes the SlackNotifier with a Slack Bot Token.

        Args:
            token (str): Your Slack Bot User OAuth Token. This is required.
            timeout (int): The timeout in seconds for API requests. Defaults to 30.
            log (bool): If True, informational logs are printed to the console.
                        Set to False for production environments to maintain security. Defaults to True.
        """
        if not token:
            raise ValueError("Slack token cannot be empty.")

        self.logger = logging.getLogger(f"cherry.{id(self)}")
        self.logger.propagate = False

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        if log:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.addHandler(logging.NullHandler())

        self.client = WebClient(token=token, timeout=timeout)
        self.user_cache = {}
        self.channel_cache = {}
        
        try:
            auth_test = self.client.auth_test()
            self.bot_user_id = auth_test["user_id"]
            self.logger.info(f"Successfully authenticated as user {auth_test['user']} ({self.bot_user_id}) in workspace {auth_test['team']}.")
            self.logger.info(f"Slack client initialized with a {timeout}-second timeout.")
        except SlackApiError as e:
            self.logger.error(f"Authentication failed. Please check your token and permissions. Error: {e.response['error']}")
            raise ConnectionError(f"Could not connect to Slack: {e.response['error']}")

    def _resolve_user_id(self, user_identifier: str) -> str | None:
        """Resolves a user's email, name, or ID to their Slack User ID."""
        if user_identifier.startswith('U'):
            return user_identifier

        if user_identifier in self.user_cache:
            return self.user_cache[user_identifier]

        try:
            if '@' in user_identifier:
                response = self.client.users_lookupByEmail(email=user_identifier)
                user_id = response["user"]["id"]
                self.user_cache[user_identifier] = user_id
                return user_id

            for page in self.client.users_list():
                for user in page["members"]:
                    if user.get("real_name") == user_identifier or user.get("name") == user_identifier:
                        user_id = user["id"]
                        self.user_cache[user_identifier] = user_id
                        return user_id
        
        except SlackApiError as e:
            if e.response['error'] == 'users_not_found':
                self.logger.warning(f"Could not find a user with identifier: {user_identifier}")
            else:
                self.logger.error(f"Error resolving user '{user_identifier}': {e.response['error']}")
        
        return None

    def _resolve_channel_id(self, channel_name: str) -> str | None:
        """Resolves a channel name (e.g., '#general') to its ID."""
        clean_name = channel_name.lstrip('#')
        
        if clean_name in self.channel_cache:
            return self.channel_cache[clean_name]

        try:
            for page in self.client.conversations_list(types="public_channel,private_channel"):
                for channel in page["channels"]:
                    if channel["name"] == clean_name:
                        channel_id = channel["id"]
                        self.channel_cache[clean_name] = channel_id
                        return channel_id
        except SlackApiError as e:
            self.logger.error(f"Error listing channels: {e.response['error']}")

        self.logger.warning(f"Could not find a channel with name: #{clean_name}")
        return None

    def _get_conversation_id(self, target: str) -> str | None:
        """
        Resolves any target to a usable conversation ID.
        This is now more robust and can handle user-supplied DM Channel IDs.
        """
        if target.startswith(('C', 'G')):  # Public/Private channels
            return target
        if target.startswith('#'):
            return self._resolve_channel_id(target)

        # All other targets (U..., D..., email, name) should resolve to a user ID.
        user_id = None
        if target.startswith('U'):
            user_id = target
        elif target.startswith('D'):
            self.logger.info(f"Target is a DM channel ID ('{target}'). Resolving to a User ID for robustness.")
            try:
                # Requires 'im:read' scope to look up DM channel info
                info = self.client.conversations_info(channel=target)
                user_id = info["channel"]["user"]
            except SlackApiError as e:
                self.logger.error(f"Could not get user from DM channel '{target}': {e.response['error']}. Please use a User ID ('U...') or email instead, or add the 'im:read' scope to the bot.")
                return None  # Fail early as we can't resolve the user
        else:  # It's an email or name
            user_id = self._resolve_user_id(target)

        # If we have a user ID, open a DM channel with them. This is the canonical way.
        if user_id:
            try:
                response = self.client.conversations_open(users=user_id)
                return response["channel"]["id"]
            except SlackApiError as e:
                self.logger.error(f"Failed to open DM with user {user_id}: {e.response['error']}")
        
        self.logger.error(f"Could not resolve target '{target}' to any valid conversation ID.")
        return None
        
    def send(self, 
             targets: Union[str, List[str]], 
             message: str, 
             file_paths: Optional[List[str]] = None) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Sends a message and/or files to one or more targets.
        Auto-detects if the message string contains HTML and converts it.

        Args:
            targets (Union[str, List[str]]): A single destination (e.g., '#channel', 'user@example.com', 'U12345')
                                             or a list of destinations.
            message (str): The text message to send. Can be plain text or HTML.
            file_paths (Optional[List[str]]): A list of local paths to files to upload. Defaults to None.
        
        Returns:
            Dict[str, Optional[Dict[str, Any]]]: A dictionary mapping each target to its Slack API response
                                                 for detailed success/failure checking.
        """
        if isinstance(targets, str):
            targets = [targets]

        responses: Dict[str, Optional[Dict[str, Any]]] = {}
        processed_message = self._process_message(message)

        for target in targets:
            conversation_id = self._get_conversation_id(target)
            if not conversation_id:
                self.logger.error(f"Aborting send for target '{target}': could not find destination.")
                responses[target] = {"ok": False, "error": "target_resolution_failed"}
                continue

            try:
                if file_paths:
                    self.logger.info(f"Uploading {len(file_paths)} file(s) to {target}...")
                    response = self.client.files_upload_v2(
                        channel=conversation_id,
                        file_uploads=[{"file": path} for path in file_paths],
                        initial_comment=processed_message
                    )
                    self.logger.info(f"File(s) sent successfully to {target}.")
                else:
                    self.logger.info(f"Sending message to {target}...")
                    response = self.client.chat_postMessage(
                        channel=conversation_id,
                        text=processed_message
                    )
                    self.logger.info(f"Message sent successfully to {target}.")
                
                responses[target] = response.data if response else None

            except SlackApiError as e:
                self.logger.error(f"Failed to send to '{target}': {e.response['error']}")
                responses[target] = e.response
        
        return responses

    def send_blocks(self, 
                    targets: Union[str, List[str]], 
                    blocks: List[Dict[str, Any]],
                    fallback_text: str = "A rich message that cannot be displayed.") -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Sends a message using Slack's Block Kit to one or more targets.

        Args:
            targets (Union[str, List[str]]): A single destination string or a list of destination strings.
            blocks (List[Dict[str, Any]]): A list of block objects constructed according to Slack's Block Kit framework.
            fallback_text (str): Text to display in notifications where blocks cannot be rendered.
        
        Returns:
            Dict[str, Optional[Dict[str, Any]]]: A dictionary mapping each target to its Slack API response.
        """
        if isinstance(targets, str):
            targets = [targets]
            
        responses: Dict[str, Optional[Dict[str, Any]]] = {}

        for target in targets:
            conversation_id = self._get_conversation_id(target)
            if not conversation_id:
                self.logger.error(f"Aborting send_blocks for '{target}': could not find destination.")
                responses[target] = {"ok": False, "error": "target_resolution_failed"}
                continue
            
            try:
                self.logger.info(f"Sending block message to {target}...")
                response = self.client.chat_postMessage(
                    channel=conversation_id,
                    blocks=blocks,
                    text=fallback_text
                )
                self.logger.info(f"Block message sent successfully to {target}.")
                responses[target] = response.data if response else None
            except SlackApiError as e:
                self.logger.error(f"Failed to send block message to '{target}': {e.response['error']}")
                responses[target] = e.response
        
        return responses
        
    def _process_message(self, message: str) -> str:
        """Processes the message string, auto-detecting and converting HTML to mrkdwn."""
        html_pattern = re.compile(r"<([a-z][a-z0-9]*)\b[^>]*>", re.IGNORECASE)
        
        if not html_pattern.search(message):
            return message

        try:
            self.logger.info("HTML detected. Converting message from HTML to mrkdwn.")
            
            processed_message = message.replace('<b>', '*').replace('</b>', '*')
            processed_message = processed_message.replace('<strong>', '*').replace('</strong>', '*')
            processed_message = processed_message.replace('<i>', '_').replace('</i>', '_')
            processed_message = processed_message.replace('<em>', '_').replace('</em>', '_')

            h = html2text.HTML2Text()
            h.body_width = 0
            
            return h.handle(processed_message)
        except Exception as e:
            self.logger.error(f"Failed to convert HTML to mrkdwn: {e}")
            return message

    @staticmethod
    def create_header_block(title: str) -> Dict[str, Any]:
        """Creates a simple Slack header block."""
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title,
                "emoji": True
            }
        }

    @staticmethod
    def create_fields_section(fields: Dict[str, str]) -> Dict[str, Any]:
        """Creates a Slack section block with two-column key-value fields."""
        mrkdwn_fields = [f"* {key}:*\n{value}" for key, value in fields.items()]
        return {
            "type": "section",
            "fields": [{"type": "mrkdwn", "text": field} for field in mrkdwn_fields]
        }

