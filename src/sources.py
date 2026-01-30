"""Sources resource management - connected GitHub repositories."""

from typing import List, Optional

from .jules_client import get_client, JulesAPIError
from .utils import output, print_error


def list_sources(
    page_size: int = 30,
    filter_expr: Optional[str] = None,
    format_type: str = "table",
    all_pages: bool = False,
) -> None:
    """
    List all connected sources (repositories).

    Args:
        page_size: Number of sources per page (1-100)
        filter_expr: AIP-160 filter expression (e.g., 'name=sources/source1')
        format_type: Output format (json/table/minimal)
        all_pages: Fetch all pages instead of just the first
    """
    client = get_client()

    try:
        if all_pages:
            # Fetch all pages
            sources = list(client.paginate("sources", page_size=page_size))
        else:
            # Single page
            params = {"pageSize": page_size}
            if filter_expr:
                params["filter"] = filter_expr
            data = client.get("sources", params)
            sources = data.get("sources", [])

        if format_type == "raw":
            output(sources, "json")
            return

        # Simplify for display
        display_data = []
        for source in sources:
            github = source.get("githubRepo", {})
            display_data.append({
                "id": source.get("id", ""),
                "owner": github.get("owner", ""),
                "repo": github.get("repo", ""),
                "private": "Yes" if github.get("isPrivate") else "No",
                "default_branch": github.get("defaultBranch", {}).get("displayName", ""),
            })

        columns = ["id", "owner", "repo", "private", "default_branch"]
        output(display_data, format_type, columns=columns, minimal_key="id")

    except JulesAPIError as e:
        print_error(str(e))


def get_source(source_id: str, format_type: str = "table") -> None:
    """
    Get details for a specific source.

    Args:
        source_id: The source ID (e.g., 'github-owner-repo')
        format_type: Output format (json/table/minimal)
    """
    client = get_client()

    try:
        # Handle both 'sources/id' and just 'id' formats
        if not source_id.startswith("sources/"):
            endpoint = f"sources/{source_id}"
        else:
            endpoint = source_id

        data = client.get(endpoint)

        if format_type == "json":
            output(data, format_type)
        else:
            # Format for display
            github = data.get("githubRepo", {})
            branches = github.get("branches", [])
            branch_names = [b.get("displayName", "") for b in branches]

            display = {
                "name": data.get("name", ""),
                "id": data.get("id", ""),
                "owner": github.get("owner", ""),
                "repo": github.get("repo", ""),
                "private": "Yes" if github.get("isPrivate") else "No",
                "default_branch": github.get("defaultBranch", {}).get("displayName", ""),
                "branches": ", ".join(branch_names[:10]) + ("..." if len(branch_names) > 10 else ""),
            }
            output(display, format_type)

    except JulesAPIError as e:
        print_error(str(e))
