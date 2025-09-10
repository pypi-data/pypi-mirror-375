🍒 easy_cherry: The Smart Slack Notifier
easy_cherry is an intelligent, developer-friendly Python library that makes sending Slack notifications incredibly simple. Built as a smart wrapper around the official Slack SDK, easy_cherry handles the boring stuff for you—like resolving user IDs, formatting messages, and managing API responses—so you can focus on what's important.

Whether you're sending a quick debug message, a complex report with attachments, or a high-priority alert to multiple teams, easy_cherry makes it feel effortless.

Key Features
Effortless Targeting: Send messages to users by their email, real name, or ID (U.../D...), and to channels by name (#channel) or ID (C...). easy_cherry figures it out.

Smart Text Formatting: Automatically detects and converts HTML strings into Slack's mrkdwn format. No more is_html=True flags!

Multi-Recipient Support: Send the same message or files to a list of recipients in a single, clean command.

Rich Block Kit Helpers: Includes easy-to-use static methods (create_header_block, create_fields_section) to build beautiful, structured messages.

Bulk File Uploads: Attach multiple files to a single message with ease.

Silent Mode: Easily disable all console logging for production environments to keep your logs clean and secure.

Robust & Resilient: Built-in caching for user/channel lookups, configurable timeouts, and detailed API responses for robust error handling.

Installation
easy_cherry is available on PyPI. You can install it using pip:

pip install easy_cherry-slack-notifier

Quick Start: Your First Notification
Here's how easy it is to send your first message.

import os
from easy_cherry import SlackNotifier

# 1. Get your token from an environment variable for security
slack_token = os.getenv("SLACK_BOT_TOKEN")

# 2. Initialize the notifier
# In production, you might set log=False
notifier = SlackNotifier(token=slack_token, log=True)

# 3. Send a message!
notifier.send("#general", "Hello from easy_cherry! 🍒")

Advanced Usage
Sending to Multiple Recipients
Simply provide a list of targets. easy_cherry handles the rest and gives you a detailed report of the results.

recipients = ["#bi_test_channel", "jane.doe@example.com", "U0123456789"]

html_report = """
<h1>Weekly Report</h1>
<p>Just a quick update: <b>everything is looking great!</b></p>
"""

results = notifier.send(recipients, html_report)

print("--- Send Report ---")
for target, response in results.items():
    if response and response.get("ok"):
        print(f"✅ Successfully sent to {target}")
    else:
        print(f"❌ Failed to send to {target}")

Sending Rich Messages with Blocks
Use the helper methods to build professional-looking reports and alerts.

# 1. Build your blocks
report_blocks = [
    notifier.create_header_block("🚀 System Performance Report"),
    {"type": "divider"},
    notifier.create_fields_section({
        "CPU Load": "12%",
        "Memory Usage": "58%",
        "Status": "✅ All Systems Operational"
    })
]

# 2. Send the blocks
notifier.send_blocks(
    "#devops-alerts",
    report_blocks,
    fallback_text="System Performance Report is ready."
)

Attaching Multiple Files
Provide a list of local file paths to the file_paths argument.

log_files = ["./logs/app.log", "./logs/db_backup.log"]

notifier.send(
    "#data-team",
    "Here are the logs from last night's data pipeline run.",
    file_paths=log_files
)

This library was built to take the friction out of Slack notifications. Enjoy!