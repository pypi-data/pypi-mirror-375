# plane-adk

A Python SDK for building intelligent agents that integrate with Plane.so workspace management platform. This package provides tools to create automated workflows, handle webhooks, and respond to workspace events.

## Installation

```bash
pip install plane-adk
```

## Usage

### Basic Setup

First, set up your environment variables for Plane OAuth:

```bash
export PLANE_CLIENT_ID="your_client_id"
export PLANE_CLIENT_SECRET="your_client_secret"
export PLANE_REDIRECT_URI="your_redirect_uri"
export PLANE_BASE_URL="https://api.plane.so"  # Optional, defaults to this
```

### Creating a PlaneAgent

```python
from plane_adk.agent import PlaneAgent, Credentials

# Create credentials
credentials = Credentials(
    client_id="your_client_id",
    client_secret="your_client_secret",
    app_installation_id="your_app_installation_id",
    base_url="https://api.plane.so",  # Optional
    redirect_uri="your_redirect_uri"
)

# Initialize the agent
agent = PlaneAgent(credentials)
```

### Handling Events

The PlaneAgent supports various events that you can listen to:

```python
def assigned_callback(handler, context):
    """Called when an issue is assigned to the bot"""
    handler.progress("I've been assigned to this issue!")

    # Access issue details
    issue_id = context.issue_id
    issue_payload = context.issue_payload

    # Add a comment to the issue
    handler.progress("Starting work on this issue...")

def mentioned_callback(handler, context):
    """Called when the bot is mentioned in an issue comment"""
    handler.progress("Thanks for mentioning me!")

    # You can access the comment data
    comment_data = context.event.data

    # Respond to the mention
    handler.progress("I'm here to help with this issue!")

# Register event handlers
agent.issue.on("assigned", assigned_callback)
agent.issue.on("mentioned", mentioned_callback)

# Process incoming webhooks
agent.process_webhook(webhook_data)
```

### Examples

For more detailed examples, check out the `example/` folder which includes:

- **FastAPI Integration**: Complete webhook server setup with OAuth handling
- **AI Task Breakdown**: Advanced example using AI to automatically break down issues into actionable tasks

## Supported Events

- `assigned`: Triggered when an issue is assigned to the bot
- `mentioned`: Triggered when the bot is mentioned in an issue comment
- `unassigned`: Triggered when the bot is unassigned from an issue

## Context Object

The context object passed to event handlers contains:

- `issue_id`: The ID of the issue
- `workspace_id`: The workspace ID
- `workspace_slug`: The workspace slug
- `project_id`: The project ID (if applicable)
- `issue_payload`: Full issue data from Plane API
- `event`: The original webhook event data
- `entity_name`: Type of entity ("issue" or "comment")
- `entity_id`: ID of the entity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.