#!/usr/bin/env python3
"""
Jules API CLI - Command-line interface for the Jules REST API.

Usage:
    python -m src.cli <command> <subcommand> [options]

Examples:
    python -m src.cli sources list
    python -m src.cli sessions create --prompt "Add tests" --source github-owner-repo
    python -m src.cli activities list <session_id>
"""

import argparse
import sys

from . import __version__
from . import sources
from . import sessions
from . import activities


def _add_create_session_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments for creating a session."""
    parser.add_argument(
        "--prompt", "-p",
        help="Task description for Jules",
    )
    parser.add_argument(
        "--prompt-file", "-F",
        help="Path to a .md or .txt file containing the prompt",
    )
    parser.add_argument(
        "--source", "-s",
        default=None,
        help="Source name (e.g., 'github-owner-repo'). Not needed with --repoless. If omitted, tries to infer from git remote.",
    )
    parser.add_argument(
        "--branch", "-b",
        default="main",
        help="Starting branch (default: main)",
    )
    parser.add_argument(
        "--title", "-t",
        help="Session title (optional)",
    )
    parser.add_argument(
        "--repoless", "-r",
        action="store_true",
        help="Create a repoless session (serverless dev environment, no repo needed)",
    )
    parser.add_argument(
        "--require-approval",
        action="store_true",
        help="Require explicit plan approval before execution",
    )
    parser.add_argument(
        "--auto-pr",
        action="store_true",
        help="Automatically create PR when code is ready (not for repoless)",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="jules-cli",
        description="Command-line interface for the Jules REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sources list                     List connected repositories
  %(prog)s sources get github-owner-repo    Get source details
  
  %(prog)s sessions list                    List all sessions
  %(prog)s sessions list                    List all sessions
  %(prog)s task "Fix bug"                   Create a task (shortcut)
  %(prog)s sessions create -p "Fix bug"     Create a session
  %(prog)s sessions get <id>                Get session details
  %(prog)s sessions send <id> "Add tests"   Send message to session
  %(prog)s sessions approve <id>            Approve pending plan
  %(prog)s sessions delete <id>             Delete a session
  
  %(prog)s activities list <session_id>     List session activities
  %(prog)s activities get <session_id> <activity_id>

Documentation: https://jules.google/docs/api/reference/
        """,
    )

    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Global options
    parser.add_argument(
        "--format", "-f",
        choices=["json", "table", "minimal", "raw"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ===== SOURCES =====
    sources_parser = subparsers.add_parser("sources", help="Manage connected repositories")
    sources_sub = sources_parser.add_subparsers(dest="subcommand")

    # sources list
    sources_list = sources_sub.add_parser("list", help="List all connected sources")
    sources_list.add_argument(
        "--page-size", "-n",
        type=int,
        default=30,
        help="Number of results per page (default: 30)",
    )
    sources_list.add_argument(
        "--filter",
        dest="filter_expr",
        help="AIP-160 filter expression (e.g., 'name=sources/github-owner-repo')",
    )
    sources_list.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all_pages",
        help="Fetch all pages of results",
    )

    # sources get
    sources_get = sources_sub.add_parser("get", help="Get source details")
    sources_get.add_argument("source_id", help="Source ID (e.g., 'github-owner-repo')")

    # ===== SESSIONS =====
    sessions_parser = subparsers.add_parser("sessions", help="Manage coding sessions")
    sessions_sub = sessions_parser.add_subparsers(dest="subcommand")

    # sessions list
    sessions_list = sessions_sub.add_parser("list", help="List all sessions")
    sessions_list.add_argument(
        "--page-size", "-n",
        type=int,
        default=30,
        help="Number of results per page (default: 30)",
    )
    sessions_list.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all_pages",
        help="Fetch all pages of results",
    )

    # sessions get
    sessions_get = sessions_sub.add_parser("get", help="Get session details")
    sessions_get.add_argument("session_id", help="Session ID")

    # sessions create
    sessions_create = sessions_sub.add_parser("create", help="Create a new session")
    _add_create_session_args(sessions_create)

    # sessions sync
    sessions_sync = sessions_sub.add_parser("sync", help="Sync/Checkout the branch for a session")
    sessions_sync.add_argument("session_id", help="Session ID")


    # sessions delete
    sessions_delete = sessions_sub.add_parser("delete", help="Delete a session")
    sessions_delete.add_argument("session_id", help="Session ID to delete")

    # sessions send
    sessions_send = sessions_sub.add_parser("send", help="Send a message to a session")
    sessions_send.add_argument("session_id", help="Session ID")
    sessions_send.add_argument("message", help="Message to send")

    # sessions approve
    sessions_approve = sessions_sub.add_parser("approve", help="Approve a pending plan")
    sessions_approve.add_argument("session_id", help="Session ID")

    # ===== ACTIVITIES =====
    activities_parser = subparsers.add_parser("activities", help="View session activities")
    activities_sub = activities_parser.add_subparsers(dest="subcommand")

    # activities list
    activities_list = activities_sub.add_parser("list", help="List activities for a session")
    activities_list.add_argument("session_id", help="Session ID")
    activities_list.add_argument(
        "--page-size", "-n",
        type=int,
        default=50,
        help="Number of results per page (default: 50)",
    )
    activities_list.add_argument(
        "--since",
        help="Filter activities after this timestamp (ISO 8601)",
    )
    activities_list.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all_pages",
        help="Fetch all pages of results",
    )

    # activities get
    activities_get = activities_sub.add_parser("get", help="Get activity details")
    activities_get.add_argument("session_id", help="Session ID")
    activities_get.add_argument("activity_id", help="Activity ID")

    # ===== TASK (Alias) =====
    task_parser = subparsers.add_parser("task", help="Create a new task (alias for sessions create)")
    _add_create_session_args(task_parser)

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Get global options
    format_type = getattr(args, "format", "table")
    verbose = getattr(args, "verbose", False)

    # Initialize client if needed
    from .jules_client import get_client
    get_client(verbose=verbose)

    if args.command is None:
        parser.print_help()
        return 0

    # ===== SOURCES =====
    if args.command == "sources":
        if args.subcommand == "list":
            sources.list_sources(
                page_size=args.page_size,
                filter_expr=args.filter_expr,
                format_type=format_type,
                all_pages=args.all_pages,
            )
        elif args.subcommand == "get":
            sources.get_source(args.source_id, format_type=format_type)
        else:
            parser.parse_args(["sources", "--help"])
            return 1

    # ===== SESSIONS =====
    elif args.command == "sessions":
        if args.subcommand == "list":
            sessions.list_sessions(
                page_size=args.page_size,
                format_type=format_type,
                all_pages=args.all_pages,
            )
        elif args.subcommand == "get":
            sessions.get_session(args.session_id, format_type=format_type)
        elif args.subcommand == "create":
            # Handle prompt from file
            prompt = args.prompt
            if args.prompt_file:
                try:
                    import os
                    if not os.path.exists(args.prompt_file):
                        print(f"Error: Prompt file not found: {args.prompt_file}")
                        return 1
                    with open(args.prompt_file, "r", encoding="utf-8") as f:
                        prompt = f.read()
                except Exception as e:
                    print(f"Error reading prompt file: {e}")
                    return 1

            if not prompt:
                print("Error: Either --prompt or --prompt-file is required.")
                return 1

            # Validate: either repoless or source must be provided
            if not args.repoless and not args.source:
                print("Error: Either --source or --repoless is required.")
                print("  Use --source for repository-based sessions")
                print("  Use --repoless for serverless sessions without a repo")
                return 1
            
            sessions.create_session(
                prompt=prompt,
                source=args.source,
                branch=args.branch,
                title=args.title,
                require_approval=args.require_approval,
                auto_pr=args.auto_pr,
                repoless=args.repoless,
                format_type=format_type,
            )
        elif args.subcommand == "sync":
            sessions.sync_session(args.session_id)
        elif args.subcommand == "delete":
            sessions.delete_session(args.session_id)
        elif args.subcommand == "send":
            sessions.send_message(args.session_id, args.message, format_type=format_type)
        elif args.subcommand == "approve":
            sessions.approve_plan(args.session_id)
        else:
            parser.parse_args(["sessions", "--help"])
            return 1

    # ===== ACTIVITIES =====
    elif args.command == "activities":
        if args.subcommand == "list":
            activities.list_activities(
                session_id=args.session_id,
                page_size=args.page_size,
                since=args.since,
                format_type=format_type,
                all_pages=args.all_pages,
            )
        elif args.subcommand == "get":
            activities.get_activity(
                session_id=args.session_id,
                activity_id=args.activity_id,
                format_type=format_type,
            )
        else:
            parser.parse_args(["activities", "--help"])
            return 1

    # ===== TASK =====
    elif args.command == "task":
        # Handle prompt from file
        prompt = args.prompt
        if args.prompt_file:
            try:
                import os
                if not os.path.exists(args.prompt_file):
                    print(f"Error: Prompt file not found: {args.prompt_file}")
                    return 1
                with open(args.prompt_file, "r", encoding="utf-8") as f:
                    prompt = f.read()
            except Exception as e:
                print(f"Error reading prompt file: {e}")
                return 1

        if not prompt:
            print("Error: Either --prompt or --prompt-file is required.")
            return 1

        # Logic for source inference handles the rest
        sessions.create_session(
            prompt=prompt,
            source=args.source,
            branch=args.branch,
            title=args.title,
            require_approval=args.require_approval,
            auto_pr=args.auto_pr,
            repoless=args.repoless,
            format_type=format_type,
        )

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
