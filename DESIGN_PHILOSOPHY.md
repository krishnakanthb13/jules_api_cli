# Design Philosophy - Jules API CLI

## Problem Definition
Automating code changes using AI agents often requires navigating complex web interfaces or writing custom scripts from scratch. Developers need a way to interact with the Jules REST API that is both powerful enough for shell scripting and simple enough for quick manual tasks.

## Why this Solution?
The Jules API CLI was designed to bridge the gap between a raw REST API and a full-featured web app. It provides:
1.  **Speed**: Using `uv`, the CLI is nearly instantaneous and manages its own dependencies.
2.  **Workflow Focus**: The interactive launchers guide users through the logical steps of an AI coding task.
3.  **Flexibility**: Support for multiple output formats (Table, JSON, Minimal) makes it useful for both humans and "piped" shell commands.

## Design Principles

### 1. Simplicity over Complexity
The CLI intentionally abstracts away the complex JSON structures of the Jules API, presenting the most relevant information (Status, PR URLs, Activity Summaries) in clean tables.

### 2. Interactive First, Scriptable Always
While we provide a rich interactive menu for beginners, every action can be run directly from the CLI with flags, making it perfectly suitable for CI/CD pipelines or local automation scripts.

3.  **Repoless Mode Support**
We've integrated "Repoless" sessions as a first-class citizen, allowing users to spawn ephemeral dev environments without the overhead of connecting a specific GitHub repository.

### 4. Power without Complexity
Advanced features like **Parallel Execution** (brainstorming), **Auth Management**, and the **TUI Dashboard** are layered on top. The base experience remains simple, but the "Pro" features are instantly accessible via flags or subcommands.

## Use Cases
- **Quick Bug Fixes**: Prompting Jules to fix a bug in a specific branch from the comfort of the terminal using Auto-Inference.
- **Brainstorming**: Using `jules-cli task "Idea" --parallel 5` to get 5 unique perspectives in seconds.
- **Code Review**: Using the **TUI** to inspect the diffs of generated code side-by-side without leaving the terminal.
- **CI/CD Integration**: Automatically creating a Jules session as part of a pipeline to generate unit tests or documentation.

## Constraints & Trade-offs
- **API Key**: Requires a manual one-time setup of an API key in the `.env` file.
- **GitHub Connection**: For repository-based sessions, the target repository must already be connected to Jules via the web dashboard.
