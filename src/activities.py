"""Activities resource management - session activity monitoring."""

from typing import Optional

from .jules_client import get_client, JulesAPIError
from .utils import output, print_error


def _get_activity_type(activity: dict) -> str:
    """Determine the type of activity based on which event field is present."""
    event_types = [
        "planGenerated",
        "planApproved",
        "userMessaged",
        "agentMessaged",
        "progressUpdated",
        "sessionCompleted",
        "sessionFailed",
    ]
    for event_type in event_types:
        if event_type in activity:
            return event_type
    return "unknown"


def _get_activity_summary(activity: dict) -> str:
    """Get a brief summary of the activity content."""
    activity_type = _get_activity_type(activity)

    if activity_type == "planGenerated":
        plan = activity.get("planGenerated", {}).get("plan", {})
        steps = plan.get("steps", [])
        return f"{len(steps)} steps"

    elif activity_type == "planApproved":
        plan_id = activity.get("planApproved", {}).get("planId", "")
        return f"Plan {plan_id}"

    elif activity_type == "userMessaged":
        msg = activity.get("userMessaged", {}).get("userMessage", "")
        return msg[:50] + ("..." if len(msg) > 50 else "")

    elif activity_type == "agentMessaged":
        msg = activity.get("agentMessaged", {}).get("agentMessage", "")
        return msg[:50] + ("..." if len(msg) > 50 else "")

    elif activity_type == "progressUpdated":
        progress = activity.get("progressUpdated", {})
        return progress.get("title", "")

    elif activity_type == "sessionCompleted":
        return "Success"

    elif activity_type == "sessionFailed":
        reason = activity.get("sessionFailed", {}).get("reason", "Unknown")
        return reason[:50]

    return activity.get("description", "")[:50]


def list_activities(
    session_id: str,
    page_size: int = 50,
    since: Optional[str] = None,
    format_type: str = "table",
    all_pages: bool = False,
) -> bool:
    """
    List activities for a session.

    Args:
        session_id: The session ID
        page_size: Number of activities per page (1-100)
        since: Filter activities after this timestamp (ISO 8601)
        format_type: Output format (json/table/minimal)
        all_pages: Fetch all pages
    """
    if not 1 <= page_size <= 100:
        print_error("page_size must be between 1 and 100")
        return False
    
    if since:
        import re
        # Basic ISO 8601 check: 2026-01-31T00:00:00Z format
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", since):
            print_error("since must be in ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ)")
            return False

    client = get_client()
    endpoint = f"sessions/{session_id}/activities"

    try:
        params = {"pageSize": page_size}
        if since:
            params["createTime"] = since

        if all_pages:
            activities = list(client.paginate(endpoint, params=params, page_size=page_size))
        else:
            data = client.get(endpoint, params)
            activities = data.get("activities", [])

        if format_type == "raw":
            output(activities, "json")
            return

        if format_type == "json":
            output(activities, format_type)
        else:
            # Simplify for display
            display_data = []
            for activity in activities:
                display_data.append({
                    "id": activity.get("id", ""),
                    "type": _get_activity_type(activity),
                    "originator": activity.get("originator", ""),
                    "summary": _get_activity_summary(activity),
                    "time": activity.get("createTime", "")[:19].replace("T", " "),
                })

            columns = ["id", "type", "originator", "summary", "time"]
            output(display_data, format_type, columns=columns, minimal_key="id")
        return True

    except JulesAPIError as e:
        print_error(str(e))
        return False


def get_activity(
    session_id: str,
    activity_id: str,
    format_type: str = "table",
) -> bool:
    """
    Get details for a specific activity.

    Args:
        session_id: The session ID
        activity_id: The activity ID
        format_type: Output format (json/table/minimal)
    """
    client = get_client()

    try:
        data = client.get(f"sessions/{session_id}/activities/{activity_id}")

        if format_type == "json":
            output(data, format_type)
        else:
            activity_type = _get_activity_type(data)

            display = {
                "id": data.get("id", ""),
                "name": data.get("name", ""),
                "type": activity_type,
                "originator": data.get("originator", ""),
                "description": data.get("description", ""),
                "created": data.get("createTime", ""),
            }

            # Add type-specific details
            if activity_type == "planGenerated":
                plan = data.get("planGenerated", {}).get("plan", {})
                steps = plan.get("steps", [])
                display["plan_steps"] = len(steps)
                for i, step in enumerate(steps[:5]):  # Show first 5 steps
                    display[f"step_{i + 1}"] = step.get("title", "")

            elif activity_type == "userMessaged":
                display["message"] = data.get("userMessaged", {}).get("userMessage", "")

            elif activity_type == "agentMessaged":
                display["message"] = data.get("agentMessaged", {}).get("agentMessage", "")

            elif activity_type == "progressUpdated":
                progress = data.get("progressUpdated", {})
                display["progress_title"] = progress.get("title", "")
                display["progress_detail"] = progress.get("description", "")

            elif activity_type == "sessionFailed":
                display["reason"] = data.get("sessionFailed", {}).get("reason", "")

            # Handle artifacts
            artifacts = data.get("artifacts", [])
            if artifacts:
                display["artifacts"] = len(artifacts)
                for i, artifact in enumerate(artifacts[:3]):
                    if "changeSet" in artifact:
                        patch = artifact["changeSet"].get("gitPatch", {})
                        display[f"artifact_{i + 1}"] = f"ChangeSet: {patch.get('suggestedCommitMessage', '')[:40]}"
                    elif "bashOutput" in artifact:
                        bash = artifact["bashOutput"]
                        display[f"artifact_{i + 1}"] = f"Bash: {bash.get('command', '')[:40]}"
                    elif "media" in artifact:
                        media = artifact["media"]
                        display[f"artifact_{i + 1}"] = f"Media: {media.get('mimeType', '')}"

            output(display, format_type)
        return True

    except JulesAPIError as e:
        print_error(str(e))
        return False
