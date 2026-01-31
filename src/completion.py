"""Shell completion generator."""
import sys
from pathlib import Path

# Robust PowerShell completer that parses the current line to suggest subcommands
POWERSHELL_SCRIPT = r"""
Register-ArgumentCompleter -Native -CommandName python -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $commandString = $commandAst.ToString()
    
    # Check if we are running our CLI
    if ($commandString -notlike "*src.cli*") {
        return
    }

    # Define the structure
    $schema = @{
        "sources" = @("list", "get")
        "sessions" = @("list", "create", "get", "send", "approve", "delete", "sync")
        "task" = @()
        "auth" = @("login")
        "activities" = @("list", "get")
        "completion" = @()
    }
    
    $args = $commandString -split " "
    # args[0] is 'python', args[1] is '-m', args[2] is 'src.cli'
    # So the command is at index 3
    
    if ($args.Count -lt 4) {
        return $schema.Keys | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
    
    $cmd = $args[3]
    
    # If we are completing the main command
    if ($args.Count -eq 4 -and $commandString -notlike "* $cmd *" ) {
         return $schema.Keys | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }

    # If we are inside a command, suggest subcommand
    if ($schema.ContainsKey($cmd)) {
        return $schema[$cmd] | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}
"""

def install_completion(shell: str) -> bool:
    """Generate completion script for the specified shell."""
    if shell == "bash":
        print("# Add this to your ~/.bashrc or ~/.zshrc:")
        print("eval \"$(register-python-argcomplete src.cli)\"")
        print("# Note: Requires 'pip install argcomplete'")
        return True
    elif shell == "powershell":
        print("# Add this to your PowerShell Profile ($PROFILE):")
        print(POWERSHELL_SCRIPT)
        return True
    else:
        print(f"Shell {shell} not supported yet.")
        return False
