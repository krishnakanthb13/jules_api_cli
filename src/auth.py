"""Authentication module for managing API keys."""
import os
import getpass
from pathlib import Path

def login() -> bool:
    """
    Interactively prompt for API key and save to .env file.
    """
    print("\n  === Jules API Authentication ===")
    print("  Get your API key from: https://jules.google.com/settings\n")
    
    key = getpass.getpass("  Paste your API Key: ").strip()
    
    if not key:
        print("Error: Empty key provided.")
        return False
        
    env_path = Path(".env")
    
    # Read existing lines to preserve other vars
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    # Update or append JULES_API_KEY
    key_line = f"JULES_API_KEY={key}\n"
    found = False
    
    for i, line in enumerate(lines):
        if line.startswith("JULES_API_KEY="):
            lines[i] = key_line
            found = True
            break
            
    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(key_line)
        
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"\n  ✓ API Key saved to {env_path.absolute()}")
        return True
    except Exception as e:
        print(f"Error saving .env file: {e}")
        return False
