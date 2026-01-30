#!/bin/bash

# ============================================
# Jules API CLI - Workflow-Based Interface
# ============================================

cd "$(dirname "$0")"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo ""
    echo "  ERROR: uv is not installed!"
    echo "  Install with: pip install uv"
    echo "  Or: curl -LsSf https://astral.sh/uv/install.sh | sh"
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
    read -p "  Press Enter to continue..."
fi

# Run CLI command
run_cli() {
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli "$@"
}

# Store current session/source for workflow
CURRENT_SESSION=""
CURRENT_SOURCE=""

# Main menu loop
while true; do
    clear
    echo ""
    echo "  ============================================"
    echo "        JULES API CLI - Workflow"
    echo "  ============================================"
    echo ""
    if [ -n "$CURRENT_SOURCE" ]; then
        echo "   Current Source:  $CURRENT_SOURCE"
    fi
    if [ -n "$CURRENT_SESSION" ]; then
        echo "   Current Session: $CURRENT_SESSION"
    fi
    if [ -n "$CURRENT_SOURCE" ] || [ -n "$CURRENT_SESSION" ]; then
        echo ""
        echo "  --------------------------------------------"
    fi
    echo ""
    echo "   STEP 1: Select a Repository"
    echo "   [1] List sources & select one"
    echo ""
    echo "   STEP 2: Create a Session"
    echo "   [2] Create new session"
    echo ""
    echo "   STEP 3: Monitor & Interact"
    echo "   [3] Check session status"
    echo "   [4] View activities"
    echo "   [5] Send a message"
    echo "   [6] Approve plan"
    echo ""
    echo "   STEP 4: View Results"
    echo "   [7] View session outputs (PRs)"
    echo ""
    echo "  --------------------------------------------"
    echo "   OTHER"
    echo "   [8] List all my sessions"
    echo "   [9] Switch to different session"
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

        # ============================================
        # STEP 1: Select a Repository
        # ============================================
        1)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 1: Select a Repository"
            echo "  ============================================"
            echo ""
            echo "  Fetching your connected repositories..."
            echo ""
            run_cli sources list
            echo ""
            echo "  --------------------------------------------"
            read -p "  Enter source ID to select (or press Enter to go back): " SOURCE_INPUT
            if [ -n "$SOURCE_INPUT" ]; then
                CURRENT_SOURCE="$SOURCE_INPUT"
                echo ""
                echo "  ✓ Source selected: $CURRENT_SOURCE"
                echo ""
                echo "  Ready for Step 2: Create a session!"
            fi
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # STEP 2: Create a Session
        # ============================================
        2)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 2: Create a Session"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SOURCE" ]; then
                echo "  ⚠ No source selected! Please complete Step 1 first."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Using source: $CURRENT_SOURCE"
            echo ""
            read -p "  What would you like Jules to do? " PROMPT
            echo ""
            read -p "  Branch (press Enter for 'main'): " BRANCH
            BRANCH=${BRANCH:-main}
            read -p "  Session title (optional): " TITLE
            read -p "  Auto-create PR when done? (y/n): " AUTO_PR

            EXTRA_ARGS=""
            if [[ "$AUTO_PR" =~ ^[Yy]$ ]]; then
                EXTRA_ARGS="--auto-pr"
            fi

            echo ""
            echo "  Creating session..."
            echo ""

            if [ -z "$TITLE" ]; then
                run_cli sessions create -p "$PROMPT" -s "$CURRENT_SOURCE" -b "$BRANCH" $EXTRA_ARGS
            else
                run_cli sessions create -p "$PROMPT" -s "$CURRENT_SOURCE" -b "$BRANCH" -t "$TITLE" $EXTRA_ARGS
            fi

            # Get the latest session ID
            LATEST_ID=$(run_cli sessions list --format minimal 2>/dev/null | head -n 1)
            if [ -n "$LATEST_ID" ]; then
                CURRENT_SESSION="$LATEST_ID"
                echo ""
                echo "  ✓ Session created! ID: $CURRENT_SESSION"
                echo ""
                echo "  Jules is now working on your task."
                echo "  Go to Step 3 to monitor progress!"
            fi
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # STEP 3: Monitor & Interact
        # ============================================
        3)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: Check Session Status"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option 9."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            run_cli sessions get "$CURRENT_SESSION"
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        4)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: View Session Activities"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option 9."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            run_cli activities list "$CURRENT_SESSION"
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        5)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: Send Message to Jules"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option 9."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            read -p "  Your message: " MESSAGE
            echo ""
            run_cli sessions send "$CURRENT_SESSION" "$MESSAGE"
            echo ""
            echo "  ✓ Message sent! Check activities to see Jules' response."
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        6)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: Approve Plan"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option 9."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            echo "  Approving the plan..."
            echo ""
            run_cli sessions approve "$CURRENT_SESSION"
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # STEP 4: View Results
        # ============================================
        7)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 4: View Session Results"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option 9."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            echo "  Fetching session details (including PR links)..."
            echo ""
            run_cli sessions get "$CURRENT_SESSION" --format json
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # OTHER OPTIONS
        # ============================================
        8)
            clear
            echo ""
            echo "  ============================================"
            echo "   All My Sessions"
            echo "  ============================================"
            echo ""
            run_cli sessions list
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        9)
            clear
            echo ""
            echo "  ============================================"
            echo "   Switch to Different Session"
            echo "  ============================================"
            echo ""
            echo "  Current sessions:"
            echo ""
            run_cli sessions list
            echo ""
            read -p "  Enter session ID to switch to: " NEW_SESSION
            if [ -n "$NEW_SESSION" ]; then
                CURRENT_SESSION="$NEW_SESSION"
                echo ""
                echo "  ✓ Switched to session: $CURRENT_SESSION"
            fi
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        *)
            echo "  Invalid choice."
            sleep 1
            ;;
    esac
done
