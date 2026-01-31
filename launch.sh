#!/bin/bash
printf "\033]0;Jules API CLI\007"

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
    if [ -n "$CURRENT_SOURCE" ]; then
        echo ""
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
    echo "   STEP 1: Select a Repository (optional)"
    echo "   [1] List sources & select one"
    echo ""
    echo "   STEP 2: Create a Session"
    echo "   [2] Create session with repository"
    echo "   [3] Create REPOLESS session (no repo needed)"
    echo ""
    echo "   STEP 3: Monitor & Interact"
    echo "   [4] Check session status"
    echo "   [5] View activities"
    echo "   [6] Send a message"
    echo "   [7] Approve plan"
    echo ""
    echo "   STEP 4: View Results"
    echo "   [8] View session outputs (PRs/files)"
    echo "   [9] Sync Code (Fetch & Checkout)"
    echo ""
    echo "  --------------------------------------------"
    echo "   OTHER"
    echo "   [10] List all my sessions"
    echo "   [11] Switch to different session"
    echo "   [12] Launch TUI Dashboard"
    echo "   [13] Authenticate (Login)"
    echo "   [0] Exit"
    echo "  ============================================"
    echo ""
    read -p "Enter your choice: " CHOICE

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
        # STEP 2: Create Session (with repo)
        # ============================================
        2)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 2: Create Session (with Repository)"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SOURCE" ]; then
                echo "  ⚠ No source selected! Please complete Step 1 first."
                echo "  Or use option [3] for a repoless session."
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

            echo ""
            echo "  ✓ Session created!"
            echo "  Use option [9] to list sessions and switch."
            echo "  Then go to Step 3 to monitor progress."
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # STEP 2: Create Repoless Session
        # ============================================
        3)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 2: Create REPOLESS Session"
            echo "  ============================================"
            echo ""
            echo "  Repoless sessions run in a serverless cloud"
            echo "  environment with Python, Node, Rust, Bun, etc."
            echo "  No repository needed!"
            echo ""
            echo "   [1] Enter prompt as text"
            echo "   [2] Load prompt from file (.md/.txt)"
            echo "   [3] Load prompt from directory"
            echo ""
            read -p "  Select input type: " P_TYPE

            if [ "$P_TYPE" == "2" ]; then
                read -p "  Enter path to file: " P_FILE
            elif [ "$P_TYPE" == "3" ]; then
                read -p "  Enter directory path: " P_DIR
                # Normalize path (remove trailing slash)
                P_DIR="${P_DIR%/}"
                
                if [ ! -d "$P_DIR" ]; then
                    echo "  ⚠ Directory not found: $P_DIR"
                    read -p "  Press Enter to continue..."
                    continue
                fi

                echo ""
                echo "  Files in $P_DIR:"
                i=0
                files=()
                # List MD and TXT files. Using find to handle spaces and hidden files better.
                while IFS= read -r f; do
                    ((i++))
                    files[$i]="$f"
                    echo "  [$i] $f"
                done < <(find "$P_DIR" -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" \) -printf "%f\n" 2>/dev/null | sort)

                if [ $i -eq 0 ]; then
                    echo "  ⚠ No .md or .txt files found in $P_DIR"
                    read -p "  Press Enter to continue..."
                    continue
                fi

                echo ""
                read -p "  Select file number: " P_NUM
                SELECTED_FILE="${files[$P_NUM]}"
                
                if [ -z "$SELECTED_FILE" ]; then
                    echo "  ⚠ Invalid selection."
                    read -p "  Press Enter to continue..."
                    continue
                fi
                P_FILE="$P_DIR/$SELECTED_FILE"
            else
                read -p "  What would you like Jules to do? " P_TEXT
            fi

            echo ""
            read -p "  Session title (optional): " TITLE

            echo ""
            echo "  Creating repoless session..."
            echo ""

            # Build command arguments using arrays to avoid injection issues
            cli_args=("sessions" "create" "--repoless")
            if [ "$P_TYPE" == "2" ] || [ "$P_TYPE" == "3" ]; then
                cli_args+=("-F" "$P_FILE")
            else
                cli_args+=("-p" "$P_TEXT")
            fi
            if [ -n "$TITLE" ]; then
                cli_args+=("-t" "$TITLE")
            fi

            run_cli "${cli_args[@]}"

            echo ""
            echo "  ✓ Repoless session created!"
            echo "  Use option [9] to list sessions and switch."
            echo "  Then go to Step 3 to monitor progress."
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # STEP 3: Monitor & Interact
        # ============================================
        4)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: Check Session Status"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option [10]."
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

        5)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: View Session Activities"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option [10]."
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

        6)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: Send Message to Jules"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option [10]."
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

        7)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 3: Approve Plan"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option [10]."
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
        8)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 4: View Session Results"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option [10]."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            echo "  Fetching session details (including PR links/files)..."
            echo ""
            run_cli sessions get "$CURRENT_SESSION" --format json
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # STEP 4: Sync Code
        # ============================================
        9)
            clear
            echo ""
            echo "  ============================================"
            echo "   STEP 4: Sync Code (Fetch & Checkout)"
            echo "  ============================================"
            echo ""
            if [ -z "$CURRENT_SESSION" ]; then
                echo "  ⚠ No session selected! Create one in Step 2 or use option [10]."
                echo ""
                read -p "  Press Enter to continue..."
                continue
            fi
            echo "  Session: $CURRENT_SESSION"
            echo ""
            echo "  Syncing code..."
            echo ""
            run_cli sessions sync "$CURRENT_SESSION"
            echo ""
            read -p "  Press Enter to continue..."
            ;;

        # ============================================
        # OTHER OPTIONS
        # ============================================
        10)
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

        11)
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

        12)
            clear
            uv run --with requests --with python-dotenv --with tabulate --with textual --with rich python -m src.cli tui
            ;;

        13)
            clear
            uv run --with requests --with python-dotenv --with tabulate --with textual --with rich python -m src.cli auth login
            read -p "  Press Enter to continue..."
            ;;

        *)
            echo "  Invalid choice."
            sleep 1
            ;;
    esac
done
