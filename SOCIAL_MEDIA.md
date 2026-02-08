# Social Media Announcements - Jules API CLI v0.0.14

## 🚀 LinkedIn

⚡ **Jules API CLI v0.0.14: The Power User Update**

We've massively upgraded the Jules CLI with features designed for speed and productivity. It's no longer just an API wrapper—it's a full-fledged productivity suite.

**What's New in v0.0.14?**
*   🖥️ **Interactive TUI**: A beautiful terminal dashboard (built with Textual) to manage sessions and inspect `git` diffs side-by-side.
*   🧠 **Brainstorm Mode**: Spawn parallel AI sessions (`--parallel 5`) to explore multiple solutions at once.
*   ⚡ **Zero-Config**: Automatic repository detection—just type `jules-cli task "Fix this"`.
*   🔄 **Sync**: One command to fetch the AI's code and checkout the branch locally.

This release bridges the gap between AI planning and your local dev environment.

🔗 Get it here: https://github.com/krishnakanthb13/jules_api_cli

#OpenSource #AI #DevTools #Python #Terminal #Productivity

---

## 🤖 Reddit (r/python / r/commandline)

**Title: [Update] Jules CLI v0.0.14 - Now with TUI, Diff Viewer, and Parallel Brainstorming**

I've just released a major update to the **Jules API CLI**, adding the "Power User" features requested by the community.

**The Big Additions:**
1.  **Terminal UI (`tui`)**: A Textual-based dashboard to browse sessions. The killer feature? A **Side-by-Side Diff Viewer** that fetches the remote PR branch and renders changes directly in your terminal.
2.  **Parallel Execution**: You ran `jules-cli task "Optimize SQL"` and want 3 different approaches? Now you can run with `--parallel 3` to spawn 3 independent sessions concurrently.
3.  **Repo Inference**: The CLI now reads your `.git/config` to detect the active repo. No more copy-pasting `--source github-owner-repo` manually.
4.  **Sync**: `jules-cli session sync <id>` automates `git fetch origin <branch> && git checkout <branch>`.

**Tech Stack Update:**
- Added `rich` and `textual` for the UI bits.
- Used `concurrent.futures` for the parallel spawner.
- Interactive `auth` command using `getpass`.

Repo: https://github.com/krishnakanthb13/jules_api_cli

Feedback on the TUI implementation is welcome!

---

## 🐦 X (Twitter)

⚡ **Jules CLI v0.0.14 is here!**

This is the "Power User" update. 🔋

🖥️ **Full TUI** with Side-by-Side Diff Viewer
🧠 **Parallel Mode** for mass brainstorming
🔄 **Sync command** to auto-fetch AI branches
⚡ **Auto-detects** your git repo

The terminal is the new IDE.

🔗 https://github.com/krishnakanthb13/jules_api_cli

#AI #OpenSource #DevTools #Python #Textual

---

## 🚀 LinkedIn

🚀 Initial Release: Jules API CLI (v0.0.7)

Excited to announce the launch of the Jules API CLI!

Jules is a powerful AI coding agent from Google DeepMind.
This CLI brings its full potential directly to your terminal.

Key Highlights:

✅ Unified Interface
   Manage Sources, Sessions, and Activities easily.

✅ Interactive Launchers
   Cross-platform scripts for Windows and Unix/Mac.

✅ Robust Networking
   Built-in retries, timeouts, and verbose logging.

✅ Developer First
   Output in tables, JSON, or raw formats.

Special thanks to Google DeepMind for the Jules API!

Check it out on GitHub: https://github.com/krishnakanthb13/jules_api_cli

#OpenSource #AI #Python #DeveloperTools #GoogleDeepMind #JulesAPI #CLI

---

## 🤖 Reddit (r/programming / r/commandline)

**Title: [Show HN/Showcase] Jules API CLI - Manage your AI coding sessions from the terminal**

Hey everyone,

I've just open-sourced the initial version (**v0.0.7**) of a CLI tool for the **Jules REST API** (Google DeepMind's AI coding agent).

I built this with a focus on **robustness** and **dev-ex**, using Python and `uv` for zero-config execution.

**Core capabilities:**
1. **Resource Lifecycle**: Full CRUD for Sources, Sessions, and Activities.
2. **Hybrid Workflow**: Seamless support for both repo-based context and serverless "Repoless" environments.
3. **AIP-160 Compliance**: Integrated filtering for efficient resource listing.
4. **Monitoring**: Real-time activity streams and plan approval flows.

**Technical highlights:**
- **Resilience**: Exponential backoff for transient errors (429, 5xx) and 30s request timeouts.
- **Multi-interface**: Native shell launchers (.sh/.bat) for interactive workflows alongside CLI flags.
- **Formatting**: Pluggable output handlers for `table`, `json`, and `raw` API response bypass.

It's open source (**GPL v3**) and I'd love to get some peer feedback on the client abstraction and session state handling!

**GitHub**: https://github.com/krishnakanthb13/jules_api_cli

---

## 🐦 X (Twitter)

🚀 Announcing Jules API CLI v0.0.7! 🛰️

Bring the power of Google DeepMind's Jules AI coding agent to your terminal.

✅ Repo-based & Serverless sessions
📈 Real-time activity tracking
🛠️ Interactive launchers for Win/Mac/Linux
⚙️ Robust: Retries & Timeouts built-in

Check it out: https://github.com/krishnakanthb13/jules_api_cli

#AI #OpenSource #DevTools #JulesAPI #Python #DeepMind
