"""Utility functions for output formatting."""

import json
import sys
from typing import Any, List, Optional

from tabulate import tabulate


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as pretty-printed JSON."""
    return json.dumps(data, indent=indent, default=str)


def format_table(data: List[dict], columns: Optional[List[str]] = None) -> str:
    """
    Format a list of dictionaries as a table.

    Args:
        data: List of dictionaries to format
        columns: Optional list of columns to include (uses all if not specified)
    """
    if not data:
        return "No results found."

    if columns:
        # Filter to only requested columns
        filtered_data = [{k: v for k, v in item.items() if k in columns} for item in data]
        headers = columns
    else:
        filtered_data = data
        headers = list(data[0].keys()) if data else []

    rows = [[item.get(col, "") for col in headers] for item in filtered_data]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_minimal(data: List[dict], key: str = "id") -> str:
    """Format data as a simple list of values (one per line)."""
    if not data:
        return ""
    return "\n".join(str(item.get(key, item.get("name", ""))) for item in data)


def output(
    data: Any,
    format_type: str = "table",
    columns: Optional[List[str]] = None,
    minimal_key: str = "id",
) -> None:
    """
    Output data in the specified format.

    Args:
        data: Data to output
        format_type: One of 'json', 'table', 'minimal'
        columns: Columns to include in table format
        minimal_key: Key to use for minimal format
    """
    if format_type == "json":
        print(format_json(data))
    elif format_type == "minimal":
        if isinstance(data, list):
            print(format_minimal(data, minimal_key))
        else:
            print(data.get(minimal_key, data.get("name", data.get("id", ""))))
    else:  # table
        if isinstance(data, list):
            print(format_table(data, columns))
        elif isinstance(data, dict):
            # Single item - format as key-value pairs
            rows = [[k, _truncate(str(v), 80)] for k, v in data.items()]
            print(tabulate(rows, headers=["Field", "Value"], tablefmt="simple"))
        else:
            print(data)


def _truncate(text: str, max_len: int = 80) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✓ {message}")


def get_git_remote_url() -> Optional[str]:
    """
    Get the remote origin URL of the current git repository.
    Returns None if not in a git repo or no remote found.
    """
    import subprocess
    
    try:
        # Check if inside git tree
        subprocess.check_call(
            ["git", "rev-parse", "--is-inside-work-tree"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        # Get URL
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return url
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def parse_source_from_url(url: str) -> Optional[str]:
    """
    Extract 'owner/repo' from a GitHub URL.
    Handles SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git).
    """
    if not url:
        return None
    
    # Remove .git suffix
    if url.endswith(".git"):
        url = url[:-4]
        
    # Handle SSH
    if "git@github.com:" in url:
        return url.split("git@github.com:")[-1]
    
    # Handle HTTPS
    if "github.com/" in url:
        return url.split("github.com/")[-1]
        
    return None
