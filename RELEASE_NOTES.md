# Release Notes - Jules API CLI

## [v0.0.14] - 2026-01-31

⚡ **Supercharged Release!** This major update transforms the CLI into a true power-user tool. We've added seamless repository detection, parallel brainstorming, secure authentication, and a full-blown interactive TUI with diff capabilities.

### 🚀 New Features (Power & Seamlessness)

- **🖥️ Interactive TUI Dashboard (`tui`)**:
    - A glorious terminal UI built with `textual` to browse sessions visually.
    - **Side-by-Side Diff Viewer**: Inspect `git` diffs of generated code directly inside the terminal without switching context.
    - Real-time activity feed and session status monitoring.
- **⚡ "Task" Shortcut**:
    - New `jules-cli task "Do x"` command alias for rapid-fire session creation.
    - **Repository Inference**: No more `--source` flag! If you are in a git repo, we auto-detect it.
- **🧠 Parallel Execution**:
    - Need ideas? Run `jules-cli task "Brainstorm" --parallel 5` to spawn 5 concurrent AI sessions.
    - Perfect for getting diverse perspectives or running multiple experiments at once.
- **🔄 Sync Command**:
    - `jules-cli sessions sync <id>` automatically fetches the remote branch and checks it out locally.
    - Closing the loop from "Plan" to "Local Code" instantly.
- **🔐 Auth Management**:
    - `jules-cli auth login` provides a secure, interactive way to set your API keys without editing files.
- **⌨️ Shell Autocompletion**:
    - Native tab-completion for `bash` and `powershell` so you never have to memorize flags again.

### ⚡ Improvements

- **Performance**: Async diff loading ensures the TUI remains responsive even with large changes.
- **Cleanup**: Refactored CLI routing to support modular subcommands (`auth`, `tui`, `completion`).
- **Dependencies**: Added `rich`, `textual`, and `argcomplete` to the core stack.

### 📚 Documentation

- Updated `README.md` to feature the new workflow and TUI.
- Added `auth` and `tui` modules to `CODE_DOCUMENTATION.md`.
- Expanded `DESIGN_PHILOSOPHY.md` to include "Power without Complexity".

---

## [v0.0.7] - 2026-01-31

🚀 **Initial Release!** The Jules API CLI is born. This initial release provides a complete, robust, and developer-friendly interface for the Jules REST API, allowing you to manage AI coding sessions directly from your terminal.

### 🚀 New Features

- **Full Resource Management**:
    - 📦 **Sources**: Connect and view your GitHub repositories.
    - 🛰️ **Sessions**: Create both repository-based and **Repoless** (serverless) coding sessions.
    - 🕵️ **Activities**: Real-time monitoring of everything the agent is doing.
- **Interactive Workflow**:
    - 🛠️ **Universal Launchers**: `launch.bat` (Windows) and `launch.sh` (Unix/Mac) provide a numbered menu system for common workflows.
    - 📂 **Flexible Prompts**: Load your prompts directly from text input, local `.md`/`.txt` files, or even select them interactively from a directory.
- **Advanced Output Formatting**:
    - Support for `table` (pretty printing), `json` (for automation), `minimal` (just IDs), and `raw` (total API response bypass).

### ⚡ Improvements & Robustness

- **Production-Ready Networking**:
    - 🔄 **Auto-Retries**: Exponential backoff logic for handling transient API errors (429, 500+).
    - ⏱️ **Request Timeouts**: Built-in 30-second safeguards to prevent terminal hangs.
    - AIP-160 Filter Support for listing resources efficiently.
- **Developer Experience**:
    - 📝 **Verbose Logging**: Use `--verbose` or `-v` to see raw API request details.
    - 📦 **Modern Stack**: Built with `uv` for zero-overhead execution and dependency management.
    - 🔍 **Detailed Error Reporting**: Informative messages including HTTP methods and URLs for easy debugging.

### 📚 Documentation

- Comprehensive `README.md` with usage examples and setup guides.
- Detailed `CODE_DOCUMENTATION.md` for developers interested in the architecture.
- Full `DESIGN_PHILOSOPHY.md` and `SECURITY.md` (via open-source prep).

### 🏗️ Infrastructure & Maintenance

- Modular Python design with dedicated resource files.
- Modern `pyproject.toml` configuration.
- Unified `.env` management for security.

---

*Note: This is the initial stable release of the CLI tool.*
