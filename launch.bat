@echo off
setlocal EnableDelayedExpansion

REM ============================================
REM Jules API CLI - Interactive Menu
REM ============================================

cd /d "%~dp0"

REM Check for uv
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo  ERROR: uv is not installed!
    echo.
    echo  Install with: pip install uv
    echo  Or: winget install astral-sh.uv
    echo.
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

:MENU
cls
echo.
echo  ============================================
echo        JULES API CLI
echo  ============================================
echo.
echo   SOURCES (Repositories)
echo   [1] List all sources
echo   [2] Get source details
echo.
echo   SESSIONS
echo   [3] List all sessions
echo   [4] Get session details
echo   [5] Create new session
echo   [6] Send message to session
echo   [7] Approve plan
echo   [8] Delete session
echo.
echo   ACTIVITIES
echo   [9] List activities for session
echo   [10] Get activity details
echo.
echo   OTHER
echo   [11] Show help
echo   [0] Exit
echo.
echo  ============================================
set /p CHOICE="  Enter your choice: "

if "%CHOICE%"=="0" goto EXIT
if "%CHOICE%"=="1" goto SOURCES_LIST
if "%CHOICE%"=="2" goto SOURCES_GET
if "%CHOICE%"=="3" goto SESSIONS_LIST
if "%CHOICE%"=="4" goto SESSIONS_GET
if "%CHOICE%"=="5" goto SESSIONS_CREATE
if "%CHOICE%"=="6" goto SESSIONS_SEND
if "%CHOICE%"=="7" goto SESSIONS_APPROVE
if "%CHOICE%"=="8" goto SESSIONS_DELETE
if "%CHOICE%"=="9" goto ACTIVITIES_LIST
if "%CHOICE%"=="10" goto ACTIVITIES_GET
if "%CHOICE%"=="11" goto SHOW_HELP

echo  Invalid choice. Press any key to try again...
pause >nul
goto MENU

:SOURCES_LIST
echo.
echo  Fetching sources...
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sources list
goto PAUSE_AND_MENU

:SOURCES_GET
echo.
set /p SOURCE_ID="  Enter source ID (e.g., github-owner-repo): "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sources get "%SOURCE_ID%"
goto PAUSE_AND_MENU

:SESSIONS_LIST
echo.
echo  Fetching sessions...
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions list
goto PAUSE_AND_MENU

:SESSIONS_GET
echo.
set /p SESSION_ID="  Enter session ID: "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions get "%SESSION_ID%"
goto PAUSE_AND_MENU

:SESSIONS_CREATE
echo.
echo  Create New Session
echo  ------------------
set /p PROMPT="  Task description: "
set /p SOURCE="  Source ID (e.g., github-owner-repo): "
set /p BRANCH="  Branch (press Enter for 'main'): "
if "%BRANCH%"=="" set BRANCH=main
set /p TITLE="  Session title (optional, press Enter to skip): "
set /p AUTO_PR="  Auto-create PR? (y/n): "

set EXTRA_ARGS=
if /i "%AUTO_PR%"=="y" set EXTRA_ARGS=--auto-pr

if "%TITLE%"=="" (
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions create -p "%PROMPT%" -s "%SOURCE%" -b "%BRANCH%" %EXTRA_ARGS%
) else (
    uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions create -p "%PROMPT%" -s "%SOURCE%" -b "%BRANCH%" -t "%TITLE%" %EXTRA_ARGS%
)
goto PAUSE_AND_MENU

:SESSIONS_SEND
echo.
set /p SESSION_ID="  Enter session ID: "
set /p MESSAGE="  Message to send: "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions send "%SESSION_ID%" "%MESSAGE%"
goto PAUSE_AND_MENU

:SESSIONS_APPROVE
echo.
set /p SESSION_ID="  Enter session ID to approve plan: "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions approve "%SESSION_ID%"
goto PAUSE_AND_MENU

:SESSIONS_DELETE
echo.
set /p SESSION_ID="  Enter session ID to delete: "
set /p CONFIRM="  Are you sure? (y/n): "
if /i not "%CONFIRM%"=="y" goto MENU
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli sessions delete "%SESSION_ID%"
goto PAUSE_AND_MENU

:ACTIVITIES_LIST
echo.
set /p SESSION_ID="  Enter session ID: "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli activities list "%SESSION_ID%"
goto PAUSE_AND_MENU

:ACTIVITIES_GET
echo.
set /p SESSION_ID="  Enter session ID: "
set /p ACTIVITY_ID="  Enter activity ID: "
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli activities get "%SESSION_ID%" "%ACTIVITY_ID%"
goto PAUSE_AND_MENU

:SHOW_HELP
echo.
uv run --with requests --with python-dotenv --with tabulate python -m src.cli --help
goto PAUSE_AND_MENU

:PAUSE_AND_MENU
echo.
echo  ============================================
echo  Press any key to return to menu...
pause >nul
goto MENU

:EXIT
echo.
echo  Goodbye!
echo.
endlocal
exit /b 0
