"""Sessions resource management - coding task sessions."""

from typing import Optional

from .jules_client import get_client, JulesAPIError
from .utils import output, print_error, print_success


def list_sessions(
    page_size: int = 30,
    format_type: str = "table",
    all_pages: bool = False,
) -> None:
    """
    List all sessions.

    Args:
        page_size: Number of sessions per page (1-100)
        format_type: Output format (json/table/minimal)
        all_pages: Fetch all pages instead of just the first
    """
    client = get_client()

    try:
        if all_pages:
            sessions = list(client.paginate("sessions", page_size=page_size))
        else:
            data = client.get("sessions", {"pageSize": page_size})
            sessions = data.get("sessions", [])

        if format_type == "raw":
            output(sessions, "json")
            return

        # Simplify for display
        display_data = []
        for session in sessions:
            display_data.append({
                "id": session.get("id", ""),
                "title": session.get("title", "")[:40],
                "state": session.get("state", ""),
                "created": session.get("createTime", "")[:10],
            })

        columns = ["id", "title", "state", "created"]
        output(display_data, format_type, columns=columns, minimal_key="id")

    except JulesAPIError as e:
        print_error(str(e))


def get_session(session_id: str, format_type: str = "table") -> None:
    """
    Get details for a specific session.

    Args:
        session_id: The session ID
        format_type: Output format (json/table/minimal)
    """
    client = get_client()

    try:
        data = client.get(f"sessions/{session_id}")

        if format_type == "json":
            output(data, format_type)
        else:
            # Format outputs if present
            outputs = data.get("outputs", [])
            pr_urls = []
            for out in outputs:
                pr = out.get("pullRequest", {})
                if pr.get("url"):
                    pr_urls.append(pr["url"])

            display = {
                "id": data.get("id", ""),
                "name": data.get("name", ""),
                "title": data.get("title", ""),
                "state": data.get("state", ""),
                "prompt": data.get("prompt", "")[:100] + ("..." if len(data.get("prompt", "")) > 100 else ""),
                "url": data.get("url", ""),
                "created": data.get("createTime", ""),
                "updated": data.get("updateTime", ""),
                "pull_requests": ", ".join(pr_urls) if pr_urls else "None",
            }
            output(display, format_type)

    except JulesAPIError as e:
        print_error(str(e))


def create_session(
    prompt: str,
    source: Optional[str] = None,
    branch: str = "main",
    title: Optional[str] = None,
    require_approval: bool = False,
    auto_pr: bool = False,
    repoless: bool = False,
    format_type: str = "table",
) -> None:
    """
    Create a new session.

    Args:
        prompt: Task description for Jules
        source: Source name (e.g., 'sources/github-owner-repo'), optional for repoless
        branch: Starting branch name
        title: Optional session title
        require_approval: Require explicit plan approval
        auto_pr: Automatically create PR when ready
        repoless: Create a repoless session (no repository needed)
        format_type: Output format (json/table/minimal)
    """
    client = get_client()

    body = {
        "prompt": prompt,
    }

    # Only add sourceContext if not repoless and source is provided
    if not repoless and source:
        # Ensure source has proper prefix
        if not source.startswith("sources/"):
            source = f"sources/{source}"

        body["sourceContext"] = {
            "source": source,
            "githubRepoContext": {
                "startingBranch": branch,
            },
        }

    if title:
        body["title"] = title

    if require_approval:
        body["requirePlanApproval"] = True

    if auto_pr and not repoless:
        body["automationMode"] = "AUTO_CREATE_PR"

    try:
        data = client.post("sessions", body)
        session_type = "Repoless session" if repoless else "Session"
        print_success(f"{session_type} created: {data.get('id', 'unknown')}")

        if format_type == "json":
            output(data, format_type)
        else:
            display = {
                "id": data.get("id", ""),
                "name": data.get("name", ""),
                "title": data.get("title", ""),
                "state": data.get("state", ""),
                "url": data.get("url", ""),
                "type": "Repoless" if repoless else "Repository-based",
            }
            output(display, format_type)

    except JulesAPIError as e:
        print_error(str(e))


def delete_session(session_id: str) -> None:
    """
    Delete a session.

    Args:
        session_id: The session ID to delete
    """
    client = get_client()

    try:
        client.delete(f"sessions/{session_id}")
        print_success(f"Session {session_id} deleted.")
    except JulesAPIError as e:
        print_error(str(e))


def send_message(session_id: str, message: str, format_type: str = "table") -> None:
    """
    Send a message to an active session.

    Args:
        session_id: The session ID
        message: The message to send
        format_type: Output format
    """
    client = get_client()

    try:
        client.post(f"sessions/{session_id}:sendMessage", {"prompt": message})
        print_success("Message sent. Use 'activities list' to see the response.")
    except JulesAPIError as e:
        print_error(str(e))


def approve_plan(session_id: str) -> None:
    """
    Approve a pending plan in a session.

    Args:
        session_id: The session ID
    """
    client = get_client()

    try:
        client.post(f"sessions/{session_id}:approvePlan", {})
        print_success(f"Plan approved for session {session_id}.")
    except JulesAPIError as e:
        print_error(str(e))
