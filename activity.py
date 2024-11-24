import argparse
import os
import json
import sys
import fnmatch
import subprocess
from datetime import datetime, timezone
from github import Github
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

# Determine the script's directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Load environment variables from .env and .env.local in the script's directory
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))
load_dotenv(os.path.join(SCRIPT_DIR, '.env.local'), override=True)

# Set up argument parser
parser = argparse.ArgumentParser(description='Log activity to GitHub.')
parser.add_argument('--repo-path', required=True, help='Path to the Git repository')
args = parser.parse_args()

# Retrieve configuration from environment variables
ACCESS_TOKEN: Optional[str] = os.getenv('GITHUB_ACCESS_TOKEN')
OWNER: Optional[str] = os.getenv('OWNER')
REPO_NAME: Optional[str] = os.getenv('REPO_NAME')
FILE_PATH: Optional[str] = os.getenv('FILE_PATH')
PUSH_ON_GITHUB: Optional[str] = os.getenv('PUSH_ON_GITHUB', 'true').lower()

# Check if all required environment variables are set
missing_vars = [var for var in ['GITHUB_ACCESS_TOKEN', 'OWNER', 'REPO_NAME', 'FILE_PATH'] if os.getenv(var) is None]
if missing_vars:
    print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Since we have checked that none of the variables are None, we can assert they are strings
assert ACCESS_TOKEN is not None
assert OWNER is not None
assert REPO_NAME is not None
assert FILE_PATH is not None

# Convert PUSH_ON_GITHUB to a boolean
PUSH_ON_GITHUB_BOOL = PUSH_ON_GITHUB == 'true'

# Determine if the repository is hosted on GitHub
def is_github_repo(repo_path: str) -> bool:
    try:
        # Change directory to the repository path
        os.chdir(repo_path)
        # Get the remote URL
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], stderr=subprocess.DEVNULL)
        remote_url = remote_url.decode('utf-8').strip()
        return 'github.com' in remote_url
    except Exception as e:
        # If there's an error, assume it's not a GitHub repository
        return False

# Load repository configurations
def load_configs() -> List[Dict[str, Any]]:
    configs = []

    # Paths to configuration files
    main_config_path = os.path.join(SCRIPT_DIR, 'repos_config.json')
    local_config_path = os.path.join(SCRIPT_DIR, 'repos_config.local.json')

    # Load main configuration
    if os.path.exists(main_config_path):
        try:
            with open(main_config_path, 'r') as config_file:
                main_configs: List[Dict[str, Any]] = json.load(config_file)
                configs.extend(main_configs)
        except Exception as e:
            print(f"Error reading 'repos_config.json': {e}")
            sys.exit(1)
    else:
        print("Warning: Configuration file 'repos_config.json' not found.")

    # Load local configuration if it exists
    if os.path.exists(local_config_path):
        try:
            with open(local_config_path, 'r') as local_config_file:
                local_configs: List[Dict[str, Any]] = json.load(local_config_file)
                # Prepend local configurations to give them higher priority
                configs = local_configs + configs
        except Exception as e:
            print(f"Error reading 'repos_config.local.json': {e}")
            sys.exit(1)

    if not configs:
        print("Error: No repository configurations found.")
        sys.exit(1)

    return configs

repo_configs = load_configs()

# Determine if the repository matches any pattern
repo_path: str = args.repo_path

# Expand user tilde (~) to full path
repo_path = os.path.abspath(os.path.expanduser(repo_path))

# Check if the repository is hosted on GitHub
repo_is_on_github = is_github_repo(repo_path)

# If PUSH_ON_GITHUB is false and the repo is on GitHub, skip pushing activity
if not PUSH_ON_GITHUB_BOOL and repo_is_on_github:
    print("Skipping activity logging because PUSH_ON_GITHUB is false and the repository is on GitHub.")
    sys.exit(0)

PROJECT_NAME = 'Secret Project'  # Default project name
USER_MESSAGE = 'Work, work'      # Default message

# Iterate over configurations to find a matching pattern
for config in repo_configs:
    pattern = config.get('pattern')
    if pattern:
        # Expand user tilde (~) in pattern and get absolute path
        pattern = os.path.abspath(os.path.expanduser(pattern))
        if fnmatch.fnmatch(repo_path, pattern):
            PROJECT_NAME = config.get('project_name', PROJECT_NAME)
            USER_MESSAGE = config.get('message', USER_MESSAGE)
            break  # Stop after finding the first matching pattern

# Commit message formatted as [USER_DEFINED_PROJECT_NAME] - [USER_MESSAGE]
COMMIT_MESSAGE: str = f'[{PROJECT_NAME}] - {USER_MESSAGE}'

# Initialize Github object
g = Github(ACCESS_TOKEN)

try:
    # Get the repository
    repo = g.get_repo(f"{OWNER}/{REPO_NAME}")

    try:
        # Get the contents of the file
        contents = repo.get_contents(FILE_PATH)
        # Decode the file content
        file_content = contents.decoded_content.decode('utf-8')
        sha = contents.sha
    except Exception:
        # If file does not exist, initialize content
        file_content = ''
        sha = None

    # Append the current datetime to the file content using timezone-aware datetime
    timestamp = datetime.now(timezone.utc).isoformat()
    new_content = file_content + f"\n[{timestamp}] {COMMIT_MESSAGE}"

    if sha:
        # Update the file
        repo.update_file(FILE_PATH, COMMIT_MESSAGE, new_content, sha)
    else:
        # Create the file if it doesn't exist
        repo.create_file(FILE_PATH, COMMIT_MESSAGE, new_content)

    print('Activity logged successfully on GitHub.')
except Exception as e:
    print(f"An error occurred: {e}")
