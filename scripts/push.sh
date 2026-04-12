#!/bin/bash

# ============ CONFIG ============
# Replace the placeholders below with your actual details.
# Make sure this file is listed in .gitignore (NEVER commit your token!)
GITHUB_TOKEN="$GITHUB_TOKEN"
USERNAME="MrBaconHat"
REPO_NAME="discord-leveling-bot"
BRANCH_NAME="main"
# ================================

# Full tokenized push URL
PUSH_URL="https://${GITHUB_TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git"

# Check if there are any changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes detected. Nothing to push."
    exit 0
fi

# Ask user to provide a reason for pushing
read -p "Please enter reason for pushing: " PUSH_REASON

# Stage and commit all changes
git add .
git commit -m PUSH_REASON

# Push to GitHub (force optional)
echo "📤 Pushing changes to GitHub..."
git push "$PUSH_URL" "$BRANCH_NAME" --force
echo "✅ Push complete."