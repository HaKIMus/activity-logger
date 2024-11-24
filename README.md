# Disclaimer

This is my first python-based script. If you can improve the script, go ahead, I'll be more than happy to merge your proposal.

# Example

You can check a working example here: [HaKIMus/activity-collection](https://github.com/HaKIMus/activity-collection/tree/main)

# Activity Logger Script

A Python script that logs your Git commit activity to a specified GitHub repository. This script is useful for tracking your coding activity across different repositories, including those hosted on platforms like Bitbucket or GitLab.

## **Features**

- **Automatic Activity Logging**: Triggers on every Git commit and logs activity to GitHub.
- **Customizable Messages**: Configure project names and messages based on repository patterns.
- **Supports Multiple Repositories**: Use wildcard patterns to apply configurations to multiple repositories.
- **Environment Variable Support**: Securely manage sensitive information using `.env` files.
- **Local Configuration Overrides**: Use local configuration files to override settings without affecting the main configuration.

## **How It Works**

1. **Global Git Hook**: A global `post-commit` Git hook triggers the script after every commit.
2. **Repository Detection**: The script detects the repository path and matches it against configured patterns.
3. **Configuration Matching**: Based on the matched pattern, it sets the project name and message.
4. **Activity Logging**: The script updates a file in your specified GitHub repository, creating a new commit that logs the activity.

## **Setup Instructions**

### **Prerequisites**

- **Python 3.6 or higher**
- **Git installed** on your machine
- A **GitHub account**

### **1. Clone the Repository**

Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/activity-logger.git
cd activity-logger
```

### **2. Install Dependencies**

Install the required Python packages:

```bash
pip install -r requirements.txt
```
### **3. Configure Environment Variables**

Create a .env.local file in the script directory by copying the example:

```bash
cp .env.example .env
```

**Generate a GitHub Personal Access Token**
* Navigate to: GitHub Settings > Developer settings > Personal access tokens.
* Click on "Generate new token".
* Select scopes: Choose repo (or more limited scopes as needed).
* Generate and copy the token.
* Paste the token into the GITHUB_ACCESS_TOKEN field in your .env file.

**Important**: Do not share your personal access token or commit it to version control.

### **4. Set Up Configuration Files**

Create a repos_config.local.json file in the script directory to define patterns for your repositories:

```bash
cp repos_config.json repos_config.local.json
```

### **5. Configure Git Hooks**

**Global Git Hook**
Set up a global Git post-commit hook to trigger the script after every commit.

Create a global hooks directory:
```bash
mkdir -p ~/.git-templates/hooks
```

Configure Git to use the global hooks directory:
```bash
mkdir -p ~/.git-templates/hooks
```

Create the `post-commit` hook:
```bash
nano ~/.git-templates/hooks/post-commit
```
Add the following content:
```bash
#!/bin/bash

# Path to your activity logging script
SCRIPT_PATH="/path/to/activity.py"

# Get the absolute path of the repository
REPO_PATH=$(git rev-parse --show-toplevel)

# Execute the activity logging script
python3 "$SCRIPT_PATH" --repo-path "$REPO_PATH"

# Check if a local post-commit hook exists and is executable
LOCAL_HOOK="$REPO_PATH/.git/hooks/post-commit"
if [ -x "$LOCAL_HOOK" ]; then
  "$LOCAL_HOOK"
fi
```
Replace `/path/to/activity.py` with the actual path to your script.

Make the hook executable:
```bash
chmod +x ~/.git-templates/hooks/post-commit
```

### **7. Optional Configuration**

**Skip Logging When Committing to GitHub Repositories**
You can add an option to skip logging activity when committing to a GitHub repository.

Set PUSH_ON_GITHUB in your .env file:
```bash
PUSH_ON_GITHUB=false
```

### **8. Usage**
After completing the setup, the script will automatically log your activity to GitHub whenever you make a Git commit in repositories that match your configured patterns.

### **9. Security Considerations**

* Protect Your Access Token: Never share your GitHub personal access token or commit it to a repository.
* Use Environment Variables: Store sensitive information in .env files and exclude them from version control.
* Exclude Sensitive Files: Ensure .env, .env.local, and repos_config.local.json are listed in .gitignore.

# License
This project is licensed under the MIT License.
