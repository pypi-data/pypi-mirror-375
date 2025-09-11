from typing import List, Dict, Tuple
import llm
import os
import pathlib
import subprocess
import tempfile
import shutil


def parse_fragment_string(fragment_string: str) -> Tuple[str, Dict[str, str]]:
    """
    Parse a fragment string into URL and arguments
    
    Format: url:arg1:arg2=value:arg3
    Returns: (url, {arg1: True, arg2: "value", arg3: True})
    """
    # Define known repomix flags to detect where arguments start
    known_flags = {
        "compress", "remove-comments", "remove-empty-lines", 
        "output-show-line-numbers", "no-file-summary", 
        "no-directory-structure", "no-files", 
        "include-empty-directories", "no-git-sort-by-changes",
        "include-diffs", "no-gitignore", "no-default-patterns",
        "no-security-check", "verbose", "quiet", "style"
    }
    
    # Split on colons to get all parts
    parts = fragment_string.split(":")
    if len(parts) < 1:
        raise ValueError("Invalid fragment string format")
    
    # Handle different URL formats
    if fragment_string.startswith("https://"):
        # Find where arguments start
        # parts = ['https', '//github.com/user/repo', 'compress']
        arg_start_idx = None
        for i, part in enumerate(parts):
            if i <= 1:  # Skip protocol parts (https, //domain/path)
                continue
            if "=" in part or part in known_flags:
                arg_start_idx = i
                break
        
        if arg_start_idx is None:
            url = fragment_string
            arg_parts = []
        else:
            # Reconstruct URL by joining the parts before arguments
            url_parts = parts[:arg_start_idx]
            url = ":".join(url_parts)
            arg_parts = parts[arg_start_idx:]
            
    elif fragment_string.startswith("ssh://"):
        # Similar logic for SSH URLs
        # parts = ['ssh', '//git@github.com', 'user/repo.git', 'compress']
        arg_start_idx = None
        for i, part in enumerate(parts):
            if i <= 1:  # Skip protocol parts (ssh, //domain)
                continue
            if "=" in part or part in known_flags:
                arg_start_idx = i
                break
        
        if arg_start_idx is None:
            url = fragment_string
            arg_parts = []
        else:
            url_parts = parts[:arg_start_idx]
            url = ":".join(url_parts)
            arg_parts = parts[arg_start_idx:]
            
    elif fragment_string.startswith("git@"):
        # git@host:path format - need to be careful about colons
        # Look for arguments after the repo path
        arg_start_idx = None
        
        # Skip the first colon (after hostname) when looking for arguments
        for i, part in enumerate(parts):
            if i <= 1:  # Skip git@host and first path part
                continue
            if "=" in part or part in known_flags:
                arg_start_idx = i
                break
        
        if arg_start_idx is None:
            url = fragment_string
            arg_parts = []
        else:
            url_parts = parts[:arg_start_idx]
            url = ":".join(url_parts)
            arg_parts = parts[arg_start_idx:]
    else:
        # No protocol prefix, assume simple format
        url = parts[0]
        arg_parts = parts[1:]
    
    # Parse arguments
    args = {}
    for arg in arg_parts:
        if arg and "=" in arg:
            key, value = arg.split("=", 1)
            args[key] = value
        elif arg:
            args[arg] = True
    
    return url, args


def build_repomix_command(repo_path: str, args: Dict[str, str]) -> List[str]:
    """
    Build repomix command with arguments
    
    Args:
        repo_path: Path to the repository
        args: Dictionary of arguments
        
    Returns:
        List of command parts
    """
    cmd = ["repomix", "--stdout"]
    
    # Map of supported arguments to their command-line flags
    supported_args = {
        "compress": "--compress",
        "style": "--style",
        "include": "--include",
        "ignore": "--ignore",
        "remove-comments": "--remove-comments",
        "remove-empty-lines": "--remove-empty-lines",
        "output-show-line-numbers": "--output-show-line-numbers",
        "no-file-summary": "--no-file-summary",
        "no-directory-structure": "--no-directory-structure",
        "no-files": "--no-files",
        "header-text": "--header-text",
        "instruction-file-path": "--instruction-file-path",
        "include-empty-directories": "--include-empty-directories",
        "no-git-sort-by-changes": "--no-git-sort-by-changes",
        "include-diffs": "--include-diffs",
        "no-gitignore": "--no-gitignore",
        "no-default-patterns": "--no-default-patterns",
        "no-security-check": "--no-security-check",
        "token-count-encoding": "--token-count-encoding",
        "top-files-len": "--top-files-len",
        "verbose": "--verbose",
        "quiet": "--quiet",
    }
    
    # Add arguments to command
    for arg, value in args.items():
        if arg in supported_args:
            flag = supported_args[arg]
            if value is True:
                # Boolean flag
                cmd.append(flag)
            elif value and value != "":
                # Value argument
                cmd.extend([flag, value])
            # Skip empty string values
    
    # Add repository path
    cmd.append(repo_path)
    
    return cmd


@llm.hookimpl
def register_fragment_loaders(register):
    register("repomix", repomix_loader)


def repomix_loader(argument: str) -> List[llm.Fragment]:
    """
    Load repository contents as fragments using Repomix
    
    Argument can be:
    - A git repository URL: https://git.sr.ht/~amolith/willow
    - URL with arguments: https://git.sr.ht/~amolith/willow:compress:include=*.py
    
    Examples:
        repomix:https://git.sr.ht/~amolith/willow
        repomix:ssh://git.sr.ht:~amolith/willow:compress
        repomix:git@github.com:user/repo.git:include=*.ts,*.js:ignore=*.md
    """
    # Parse the fragment string to extract URL and arguments
    url, args = parse_fragment_string(argument)
    
    if not url.startswith(("https://", "ssh://", "git@")):
        raise ValueError(
            f"Repository URL must start with https://, ssh://, or git@ - got: {url}"
        )
    
    # Check if repomix is available
    if not shutil.which("repomix"):
        raise ValueError(
            "repomix command not found. Please install repomix first: "
            "https://github.com/yamadashy/repomix"
        )
    
    # Create a temporary directory for the cloned repository
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = pathlib.Path(temp_dir) / "repo"
        
        try:
            # Clone the repository
            subprocess.run(
                ["git", "clone", "--depth=1", url, str(repo_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            
            # Build repomix command with arguments
            repomix_cmd = build_repomix_command(str(repo_path), args)
            
            # Run repomix on the cloned repository
            result = subprocess.run(
                repomix_cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            
            # Create a single fragment with the repomix output
            fragments = [
                llm.Fragment(
                    content=result.stdout,
                    source=f"repomix:{argument}"
                )
            ]
            
            return fragments
            
        except subprocess.CalledProcessError as e:
            # Handle Git or repomix errors
            if "git" in str(e.cmd):
                raise ValueError(
                    f"Failed to clone repository {url}: {e.stderr}"
                )
            elif "repomix" in str(e.cmd):
                raise ValueError(
                    f"Failed to run repomix on {url}: {e.stderr}"
                )
            else:
                raise ValueError(
                    f"Command failed: {e.stderr}"
                )
        except Exception as e:
            # Handle other errors
            raise ValueError(
                f"Error processing repository {argument}: {str(e)}"
            )