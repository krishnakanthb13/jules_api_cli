# Jules API CLI

A command-line interface for the [Jules REST API](https://jules.google/docs/api/reference/) that provides simple, intuitive access to Jules's AI coding assistant capabilities.

## Features

- **Sources** - List and inspect connected GitHub repositories
- **Sessions** - Create, manage, and interact with coding sessions
- **Activities** - Monitor session progress, plans, and responses
- **Multiple output formats** - JSON, table, or minimal

## Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/yourusername/jules_api_cli.git
cd jules_api_cli

# Requires uv (fast Python package manager)
# Install uv: pip install uv  OR  winget install astral-sh.uv

# Use the launcher (uses global packages, installs missing ones)
# Windows:
launch.bat

# Unix/Mac:
chmod +x launch.sh
./launch.sh

# Or run directly with uv:
uv run --with requests --with python-dotenv --with tabulate python -m src.cli --help
```

### 2. Configure

Get your API key from [jules.google.com/settings](https://jules.google.com/settings) and add it to `.env`:

```env
JULES_API_KEY=your-api-key-here
```

### 3. Use

```bash
# List your connected repositories
launch.bat sources list

# Create a session
launch.bat sessions create -p "Add unit tests for auth module" -s github-owner-repo

# Check session status
launch.bat sessions get <session_id>

# View activities (see what Jules is doing)
launch.bat activities list <session_id>

# Send a follow-up message
launch.bat sessions send <session_id> "Also add integration tests"
```

## Commands

### Sources

```bash
# List all connected repositories
jules-cli sources list
jules-cli sources list --format json
jules-cli sources list --page-size 10

# Get details for a specific source
jules-cli sources get github-owner-repo
```

### Sessions

```bash
# List all sessions
jules-cli sessions list

# Create a new session
jules-cli sessions create \
  --prompt "Fix the login bug" \
  --source github-owner-repo \
  --branch main \
  --title "Login Bug Fix" \
  --auto-pr

# Get session details
jules-cli sessions get <session_id>

# Send a message to an active session
jules-cli sessions send <session_id> "Add error handling too"

# Approve a pending plan (if --require-approval was used)
jules-cli sessions approve <session_id>

# Delete a session
jules-cli sessions delete <session_id>
```

### Activities

```bash
# List activities for a session
jules-cli activities list <session_id>
jules-cli activities list <session_id> --page-size 20

# Get specific activity details
jules-cli activities get <session_id> <activity_id>
```

### Global Options

```bash
--format, -f    Output format: json, table, minimal (default: table)
--version, -V   Show version
--help, -h      Show help
```

## Session States

Sessions progress through these states:

| State | Description |
|-------|-------------|
| `QUEUED` | Session is waiting to start |
| `PLANNING` | Jules is creating a plan |
| `AWAITING_PLAN_APPROVAL` | Plan needs approval (if `--require-approval` was set) |
| `AWAITING_USER_FEEDBACK` | Jules is waiting for input |
| `IN_PROGRESS` | Jules is executing the plan |
| `PAUSED` | Session is paused |
| `COMPLETED` | Session finished successfully |
| `FAILED` | Session encountered an error |

## Activity Types

| Type | Description |
|------|-------------|
| `planGenerated` | Jules created a plan |
| `planApproved` | Plan was approved |
| `userMessaged` | You sent a message |
| `agentMessaged` | Jules responded |
| `progressUpdated` | Status update during execution |
| `sessionCompleted` | Session finished |
| `sessionFailed` | Session failed |

## Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Jules API key ([get one here](https://jules.google.com/settings))
- At least one GitHub repository connected via the [Jules web app](https://jules.google.com)

## License

MIT

## Links

- [Jules Website](https://jules.google)
- [API Documentation](https://jules.google/docs/api/reference/)
- [Get API Key](https://jules.google.com/settings)
