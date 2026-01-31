"""Sessions resource management - coding task sessions."""

from typing import Optional

from .jules_client import get_client, JulesAPIError
from .jules_client import get_client, JulesAPIError
from .utils import output, print_error, print_success, get_git_remote_url, parse_source_from_url


def list_sessions(
    page_size: int = 30,
    format_type: str = "table",
    all_pages: bool = False,
) -> bool:
    """
    List all sessions.

    Args:
        page_size: Number of sessions per page (1-100)
        format_type: Output format (json/table/minimal)
        all_pages: Fetch all pages instead of just the first
    """
    if not 1 <= page_size <= 100:
        print_error("page_size must be between 1 and 100")
        return False

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
        return True

    except JulesAPIError as e:
        print_error(str(e))
        return False


def get_session(session_id: str, format_type: str = "table") -> bool:
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
        return True

    except JulesAPIError as e:
        print_error(str(e))
        return False


def create_session(
    prompt: str,
    source: Optional[str] = None,
    branch: str = "main",
    title: Optional[str] = None,
    require_approval: bool = False,
    auto_pr: bool = False,
    repoless: bool = False,
    format_type: str = "table",
    parallel: int = 1,
) -> bool:
    """
    Create a new session (or multiple sessions in parallel).

    Args:
        prompt: Task description for Jules
        source: Source name (e.g., 'sources/github-owner-repo'), optional for repoless
        branch: Starting branch name
        title: Optional session title
        require_approval: Require explicit plan approval
        auto_pr: Automatically create PR when ready
        repoless: Create a repoless session (no repository needed)
        format_type: Output format (json/table/minimal)
        parallel: Number of parallel sessions to create (default 1)
    """
    # ... logic for single vs parallel ...
    if parallel > 1:
        import concurrent.futures
        print(f"Starting {parallel} parallel sessions...")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
            # We call this function recursively with parallel=1
            futures = [
                executor.submit(
                    create_session, 
                    prompt, source, branch, 
                    f"{title} ({i+1})" if title else None, 
                    require_approval, auto_pr, repoless, "minimal", 1
                ) for i in range(parallel)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    print_error(f"Thread failed: {e}")
                    results.append(False)
        
        success_count = sum(1 for r in results if r)
        print(f"\nCreated {success_count}/{parallel} sessions successfully.")
        return success_count > 0

    client = get_client()

    body = {
        "prompt": prompt,
    }

    # Only add sourceContext if not repoless
    if not repoless:
        # Try to infer source if not provided
        if not source:
            url = get_git_remote_url()
            inferred = parse_source_from_url(url)
            if inferred:
                print(f"Inferred source from git: {inferred}")
                source = inferred
            else:
                print_error("Could not infer repository from current directory.")
                print_error("Please specify --source or use --repoless")
                return False

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
        return True

    except JulesAPIError as e:
        print_error(str(e))
        return False


def delete_session(session_id: str) -> bool:
    """
    Delete a session.

    Args:
        session_id: The session ID to delete
    """
    client = get_client()

    try:
        client.delete(f"sessions/{session_id}")
        print_success(f"Session {session_id} deleted.")
        return True
    except JulesAPIError as e:
        print_error(str(e))
        return False


def send_message(session_id: str, message: str, format_type: str = "table") -> bool:
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
        return True
    except JulesAPIError as e:
        print_error(str(e))
        return False


def approve_plan(session_id: str) -> bool:
    """
    Approve a pending plan in a session.

    Args:
        session_id: The session ID
    """
    client = get_client()

    try:
        client.post(f"sessions/{session_id}:approvePlan", {})
        print_success(f"Plan approved for session {session_id}.")
        return True
    except JulesAPIError as e:
        print_error(str(e))
        return False


def sync_session(session_id: str) -> bool:
    """
    Sync (checkout) the branch associated with a session.
    
    Args:
        session_id: The session ID
    """
    client = get_client()
    try:
        # Get session details
        data = client.get(f"sessions/{session_id}")
        outputs = data.get("outputs", [])
        
        branch_name = None
        for out in outputs:
            pr = out.get("pullRequest", {})
            if pr.get("branchName"):
                branch_name = pr.get("branchName")
                break
        
        if not branch_name:
            print_error(f"No branch found for session {session_id}. Has it created a PR yet?")
            return False
            
        import subprocess
        print(f"Syncing branch: {branch_name}...")
        
        # Fetch and checkout
        subprocess.check_call(["git", "fetch", "origin", branch_name])
        subprocess.check_call(["git", "checkout", branch_name])
        
        print_success(f"Checked out branch: {branch_name}")
        return True
        
    except JulesAPIError as e:
        print_error(str(e))
        return False
    except Exception as e:
        print_error(f"Git operation failed: {e}")
        return False
