#!/bin/bash

# ============================================
# Jules API CLI - Interactive Menu
# ============================================

cd "$(dirname "$0")"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo ""
    echo "  ERROR: uv is not installed!"
    echo ""
    echo "  Install with: pip install uv"
    echo "  Or: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    read -p "  Press Enter to exit..."
    exit 1
fi

# Create .env from example if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo ""
    echo "  ============================================"
    echo "   SETUP REQUIRED"
    echo "  ============================================"
    echo "   Please edit .env and add your JULES_API_KEY"
    echo "   Get your key: https://jules.google.com/settings"
    echo "  ============================================"
    echo ""
    read -p "  Press Enter to continue..."
fi

# Run CLI command
run_cli() {
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli "$@"
}

# Pause and wait for user
pause_menu() {
    echo ""
    echo "  ============================================"
    read -p "  Press Enter to return to menu..."
}

# Main menu loop
while true; do
    clear
    echo ""
    echo "  ============================================"
    echo "        JULES API CLI"
    echo "  ============================================"
    echo ""
    echo "   SOURCES (Repositories)"
    echo "   [1] List all sources"
    echo "   [2] Get source details"
    echo ""
    echo "   SESSIONS"
    echo "   [3] List all sessions"
    echo "   [4] Get session details"
    echo "   [5] Create new session"
    echo "   [6] Send message to session"
    echo "   [7] Approve plan"
    echo "   [8] Delete session"
    echo ""
    echo "   ACTIVITIES"
    echo "   [9] List activities for session"
    echo "   [10] Get activity details"
    echo ""
    echo "   OTHER"
    echo "   [11] Show help"
    echo "   [0] Exit"
    echo ""
    echo "  ============================================"
    read -p "  Enter your choice: " CHOICE

    case $CHOICE in
        0)
            echo ""
            echo "  Goodbye!"
            echo ""
            exit 0
            ;;
        1)
            echo ""
            echo "  Fetching sources..."
            echo ""
            run_cli sources list
            pause_menu
            ;;
        2)
            echo ""
            read -p "  Enter source ID (e.g., github-owner-repo): " SOURCE_ID
            echo ""
            run_cli sources get "$SOURCE_ID"
            pause_menu
            ;;
        3)
            echo ""
            echo "  Fetching sessions..."
            echo ""
            run_cli sessions list
            pause_menu
            ;;
        4)
            echo ""
            read -p "  Enter session ID: " SESSION_ID
            echo ""
            run_cli sessions get "$SESSION_ID"
            pause_menu
            ;;
        5)
            echo ""
            echo "  Create New Session"
            echo "  ------------------"
            read -p "  Task description: " PROMPT
            read -p "  Source ID (e.g., github-owner-repo): " SOURCE
            read -p "  Branch (press Enter for 'main'): " BRANCH
            BRANCH=${BRANCH:-main}
            read -p "  Session title (optional, press Enter to skip): " TITLE
            read -p "  Auto-create PR? (y/n): " AUTO_PR

            EXTRA_ARGS=""
            if [[ "$AUTO_PR" =~ ^[Yy]$ ]]; then
                EXTRA_ARGS="--auto-pr"
            fi

            if [ -z "$TITLE" ]; then
                run_cli sessions create -p "$PROMPT" -s "$SOURCE" -b "$BRANCH" $EXTRA_ARGS
            else
                run_cli sessions create -p "$PROMPT" -s "$SOURCE" -b "$BRANCH" -t "$TITLE" $EXTRA_ARGS
            fi
            pause_menu
            ;;
        6)
            echo ""
            read -p "  Enter session ID: " SESSION_ID
            read -p "  Message to send: " MESSAGE
            echo ""
            run_cli sessions send "$SESSION_ID" "$MESSAGE"
            pause_menu
            ;;
        7)
            echo ""
            read -p "  Enter session ID to approve plan: " SESSION_ID
            echo ""
            run_cli sessions approve "$SESSION_ID"
            pause_menu
            ;;
        8)
            echo ""
            read -p "  Enter session ID to delete: " SESSION_ID
            read -p "  Are you sure? (y/n): " CONFIRM
            if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
                echo ""
                run_cli sessions delete "$SESSION_ID"
            fi
            pause_menu
            ;;
        9)
            echo ""
            read -p "  Enter session ID: " SESSION_ID
            echo ""
            run_cli activities list "$SESSION_ID"
            pause_menu
            ;;
        10)
            echo ""
            read -p "  Enter session ID: " SESSION_ID
            read -p "  Enter activity ID: " ACTIVITY_ID
            echo ""
            run_cli activities get "$SESSION_ID" "$ACTIVITY_ID"
            pause_menu
            ;;
        11)
            echo ""
            run_cli --help
            pause_menu
            ;;
        *)
            echo "  Invalid choice. Press Enter to try again..."
            read
            ;;
    esac
done
