# Code Documentation - Jules API CLI

This document provides a technical overview of the Jules API CLI project, its architecture, and its core modules.

## Project Structure

```
jules_api_cli/
├── launch.bat            # Windows interactive launcher
├── launch.sh             # Unix/Mac interactive launcher
├── README.md             # Project overview and installation
├── LICENSE               # GNU GPL v3 License
├── requirements.txt      # Dependency list (for reference)
└── src/
    ├── __init__.py       # Package initialization
    ├── cli.py            # Main entry point and CLI parsing
    ├── jules_client.py   # Core API client for Jules
    ├── sessions.py       # Session management logic
    ├── activities.py     # Activity monitoring logic
    ├── sources.py        # Repository source management
    └── utils.py          # Helper utilities for formatting
```

## Architecture

The application follows a modular architecture where the CLI logic is separated from the API interaction logic.

1.  **Entry Point**: `src/cli.py` uses `argparse` to handle command-line arguments and subcommands.
2.  **API Client**: `src/jules_client.py` contains the `JulesClient` class, which handles authentication via headers and performs HTTP requests to the Jules REST API.
3.  **Resource Modules**: `src/sessions.py`, `src/activities.py`, and `src/sources.py` contain the business logic for interacting with specific API resources.
4.  **Launchers**: `launch.bat` and `launch.sh` provide a user-friendly, interactive numbered menu system using `uv run` to manage the environment and dependencies on the fly.

## Core Modules

| Module | Description | Key Functions |
|:--- |:--- |:--- |
| `cli.py` | Command-line interface definition. | `main()`, `create_parser()` |
| `jules_client.py` | Handles robust API interaction, retries, and logging. | `JulesClient`, `get_client()` |
| `sessions.py` | Manages AI coding sessions. | `create_session()`, `list_sessions()`, `get_session()` |
| `activities.py` | Tracks what the agent is doing. | `list_activities()`, `get_activity()` |
| `sources.py` | Manages connected repositories. | `list_sources()`, `get_source()` |
| `utils.py` | Formatting output (tables, JSON, minimal, raw). | `output()`, `print_error()`, `print_success()` |

### API Client Features

The `JulesClient` implementation in `jules_client.py` provides several robustness features:

- **Authentication**: Injects `x-goog-api-key` and `Content-Type` headers into every request.
- **Retries**: Implements a retry strategy for transient errors (HTTP 429, 500, 502, 503, 504) with exponential backoff.
- **Timeouts**: Enforces a 30-second timeout on all requests to avoid indefinite hanging.
- **Pagination**: Provides a generator-based `paginate()` method for easy traversal of large resource lists.
- **Verbose Logging**: When initialized with `verbose=True`, logs raw HTTP methods, URLs, and response codes to `stderr`.
- **Error Handling**: Custom `JulesAPIError` extracts detailed error messages from the API response and includes the failed request context.

## Execution Flow

1.  The user runs `launch.bat` (or `launch.sh`).
2.  The launcher checks if `uv` is installed and ensures a `.env` file exists.
3.  The interactive menu prompts the user for a choice.
4.  The choice maps to a CLI command (e.g., `python -m src.cli sessions list`).
5.  `cli.py` parses the arguments and calls the corresponding function in a resource module.
6.  The resource module uses `get_client()` to interact with the Jules API.
7.  Results are formatted and displayed to the user.

## Dependencies

- **Requests**: For HTTP communication.
- **Python-dotenv**: For loading the API key from `.env`.
- **Tabulate**: For pretty-printing tables in the terminal.
- **uv**: Managed via the launcher for fast dependency handling and execution.
