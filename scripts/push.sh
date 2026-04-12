#!/bin/bash

# ============ CONFIG ============
GITHUB_TOKEN="${GITHUB_TOKEN}"
USERNAME="MrBaconHat"
REPO_NAME="discord-leveling-bot"
DEFAULT_BRANCH="main"  # fallback if no branch exists
# ================================

# Auto-detect current branch or use default
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "$DEFAULT_BRANCH")

# Add remote if missing
if ! git remote | grep -q origin; then
    echo "Adding remote origin..."
    git remote add origin "https://${GITHUB_TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git"
fi

# Stage all changes
git add .

# Commit if there are staged changes
if git diff --cached --quiet; then
    echo "No changes detected. Nothing to commit."
else
    # Ask user to enter update message
    read -p "Enter commit message: " commit_message

    # commit the changes
    echo "Committing changes..."
    git commit -m "Replit-commit $(date '+%Y-%m-%d %H:%M:%S') Commit Message: ${commit_message}"
fi

# Handle first push if branch doesn't exist on remote
if ! git ls-remote --exit-code --heads origin "$CURRENT_BRANCH" >/dev/null 2>&1; then
    echo "First push for branch '$CURRENT_BRANCH'..."
    git push -u origin "$CURRENT_BRANCH"
else
    echo "📤 Pushing changes to GitHub..."
    git push origin "$CURRENT_BRANCH" --force
fi

echo "✅ Push complete."