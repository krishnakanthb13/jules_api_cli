@echo off
setlocal EnableDelayedExpansion

REM ============================================
REM Jules API CLI - Workflow-Based Interface
REM ============================================

cd /d "%~dp0"

REM Check for uv
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo  ERROR: uv is not installed!
    echo  Install with: pip install uv
    echo  Or: winget install astral-sh.uv
    pause
    exit /b 1
)

REM Create .env from example if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo.
        echo  ============================================
        echo   SETUP REQUIRED
        echo  ============================================
        echo   Please edit .env and add your JULES_API_KEY
        echo   Get your key: https://jules.google.com/settings
        echo  ============================================
        echo.
        pause
    )
)

REM Store current session for workflow
set CURRENT_SESSION=
set CURRENT_SOURCE=

:MAIN_MENU
cls
echo.
echo  ============================================
echo        JULES API CLI - Workflow
echo  ============================================
echo.
if defined CURRENT_SOURCE echo   Current Source:  %CURRENT_SOURCE%
if defined CURRENT_SESSION echo   Current Session: %CURRENT_SESSION%
if defined CURRENT_SOURCE echo.
if defined CURRENT_SOURCE echo  --------------------------------------------
echo.
echo   STEP 1: Select a Repository (optional)
echo   [1] List sources ^& select one
echo.
echo   STEP 2: Create a Session
echo   [2] Create session with repository
echo   [3] Create REPOLESS session (no repo needed)
echo.
echo   STEP 3: Monitor ^& Interact
echo   [4] Check session status
echo   [5] View activities
echo   [6] Send a message
echo   [7] Approve plan
echo.
echo   STEP 4: View Results
echo   [8] View session outputs (PRs/files)
echo.
echo  --------------------------------------------
echo   OTHER
echo   [9] List all my sessions
echo   [10] Switch to different session
echo   [0] Exit
echo.
echo  ============================================
set /p CHOICE="  Enter your choice: "

if "%CHOICE%"=="0" goto EXIT
if "%CHOICE%"=="1" goto STEP1_SOURCES
if "%CHOICE%"=="2" goto STEP2_CREATE
if "%CHOICE%"=="3" goto STEP2_REPOLESS
if "%CHOICE%"=="4" goto STEP3_STATUS
if "%CHOICE%"=="5" goto STEP3_ACTIVITIES
if "%CHOICE%"=="6" goto STEP3_MESSAGE
if "%CHOICE%"=="7" goto STEP3_APPROVE
if "%CHOICE%"=="8" goto STEP4_RESULTS
if "%CHOICE%"=="9" goto LIST_SESSIONS
if "%CHOICE%"=="10" goto SWITCH_SESSION

echo  Invalid choice.
timeout /t 1 >nul
goto MAIN_MENU

REM ============================================
REM STEP 1: Select a Repository
REM ============================================
:STEP1_SOURCES
cls
echo.
echo  ============================================
echo   STEP 1: Select a Repository
echo  ============================================
echo.
echo  Fetching your connected repositories...
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sources list
echo.
echo  --------------------------------------------
set /p SOURCE_INPUT="  Enter source ID to select (or press Enter to go back): "
if "%SOURCE_INPUT%"=="" goto MAIN_MENU
set CURRENT_SOURCE=%SOURCE_INPUT%
echo.
echo  Source selected: %CURRENT_SOURCE%
echo.
echo  Ready for Step 2: Create a session!
echo.
pause
goto MAIN_MENU

REM ============================================
REM STEP 2: Create a Session (with repo)
REM ============================================
:STEP2_CREATE
cls
echo.
echo  ============================================
echo   STEP 2: Create Session (with Repository)
echo  ============================================
echo.
if not defined CURRENT_SOURCE (
    echo  No source selected! Please complete Step 1 first.
    echo  Or use option [3] for a repoless session.
    echo.
    pause
    goto MAIN_MENU
)
echo  Using source: %CURRENT_SOURCE%
echo.
set /p PROMPT="  What would you like Jules to do? "
echo.
set /p BRANCH="  Branch (press Enter for 'main'): "
if "%BRANCH%"=="" set BRANCH=main
set /p TITLE="  Session title (optional): "
set /p AUTO_PR="  Auto-create PR when done? (y/n): "

set EXTRA_ARGS=
if /i "%AUTO_PR%"=="y" set EXTRA_ARGS=--auto-pr

echo.
echo  Creating session...
echo.

if "%TITLE%"=="" (
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions create -p "%PROMPT%" -s "%CURRENT_SOURCE%" -b "%BRANCH%" %EXTRA_ARGS%
) else (
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions create -p "%PROMPT%" -s "%CURRENT_SOURCE%" -b "%BRANCH%" -t "%TITLE%" %EXTRA_ARGS%
)

echo.
echo  Session created! Use option [9] to list sessions and switch.
echo  Then go to Step 3 to monitor progress.
echo.
pause
goto MAIN_MENU

REM ============================================
REM STEP 2: Create Repoless Session
REM ============================================
:STEP2_REPOLESS
cls
echo.
echo  ============================================
echo   STEP 2: Create REPOLESS Session
echo  ============================================
echo.
echo  Repoless sessions run in a serverless cloud
echo  environment with Python, Node, Rust, Bun, etc.
echo  No repository needed!
echo.
set /p PROMPT="  What would you like Jules to do? "
echo.
set /p TITLE="  Session title (optional): "

echo.
echo  Creating repoless session...
echo.

if "%TITLE%"=="" (
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions create -p "%PROMPT%" --repoless
) else (
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions create -p "%PROMPT%" -t "%TITLE%" --repoless
)

echo.
echo  Repoless session created!
echo  Use option [9] to list sessions and switch.
echo  Then go to Step 3 to monitor progress.
echo.
pause
goto MAIN_MENU

REM ============================================
REM STEP 3: Monitor & Interact
REM ============================================
:STEP3_STATUS
cls
echo.
echo  ============================================
echo   STEP 3: Check Session Status
echo  ============================================
echo.
if not defined CURRENT_SESSION (
    echo  No session selected! Create one in Step 2 or use option 9.
    echo.
    pause
    goto MAIN_MENU
)
echo  Session: %CURRENT_SESSION%
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions get "%CURRENT_SESSION%"
echo.
pause
goto MAIN_MENU

:STEP3_ACTIVITIES
cls
echo.
echo  ============================================
echo   STEP 3: View Session Activities
echo  ============================================
echo.
if not defined CURRENT_SESSION (
    echo  No session selected! Create one in Step 2 or use option 9.
    echo.
    pause
    goto MAIN_MENU
)
echo  Session: %CURRENT_SESSION%
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli activities list "%CURRENT_SESSION%"
echo.
pause
goto MAIN_MENU

:STEP3_MESSAGE
cls
echo.
echo  ============================================
echo   STEP 3: Send Message to Jules
echo  ============================================
echo.
if not defined CURRENT_SESSION (
    echo  No session selected! Create one in Step 2 or use option 9.
    echo.
    pause
    goto MAIN_MENU
)
echo  Session: %CURRENT_SESSION%
echo.
set /p MESSAGE="  Your message: "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions send "%CURRENT_SESSION%" "%MESSAGE%"
echo.
echo  Message sent! Check activities to see Jules' response.
echo.
pause
goto MAIN_MENU

:STEP3_APPROVE
cls
echo.
echo  ============================================
echo   STEP 3: Approve Plan
echo  ============================================
echo.
if not defined CURRENT_SESSION (
    echo  No session selected! Create one in Step 2 or use option 9.
    echo.
    pause
    goto MAIN_MENU
)
echo  Session: %CURRENT_SESSION%
echo.
echo  Approving the plan...
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions approve "%CURRENT_SESSION%"
echo.
pause
goto MAIN_MENU

REM ============================================
REM STEP 4: View Results
REM ============================================
:STEP4_RESULTS
cls
echo.
echo  ============================================
echo   STEP 4: View Session Results
echo  ============================================
echo.
if not defined CURRENT_SESSION (
    echo  No session selected! Create one in Step 2 or use option 9.
    echo.
    pause
    goto MAIN_MENU
)
echo  Session: %CURRENT_SESSION%
echo.
echo  Fetching session details (including PR links)...
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions get "%CURRENT_SESSION%" --format json
echo.
pause
goto MAIN_MENU

REM ============================================
REM OTHER OPTIONS
REM ============================================
:LIST_SESSIONS
cls
echo.
echo  ============================================
echo   All My Sessions
echo  ============================================
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions list
echo.
pause
goto MAIN_MENU

:SWITCH_SESSION
cls
echo.
echo  ============================================
echo   Switch to Different Session
echo  ============================================
echo.
echo  Current sessions:
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions list
echo.
set /p NEW_SESSION="  Enter session ID to switch to: "
if not "%NEW_SESSION%"=="" set CURRENT_SESSION=%NEW_SESSION%
echo.
echo  Switched to session: %CURRENT_SESSION%
echo.
pause
goto MAIN_MENU

:EXIT
echo.
echo  Goodbye!
echo.
endlocal
exit /b 0
