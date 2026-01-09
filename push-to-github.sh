#!/bin/bash
# Push to existing GitHub repository
# First create the repo manually at: https://github.com/new

set -e

cd ~/ai-cli-memory-system

# Get username
USERNAME=$(bash -c 'unset GITHUB_TOKEN && gh api user -q .login')
echo "📝 Your GitHub username: $USERNAME"

# Update documentation with username
echo "📝 Updating documentation..."
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" README.md
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" install.sh
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" DEPLOY.md
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" QUICKSTART.md
rm -f *.bak */*.bak

echo "✓ Documentation updated"

# Commit updates
git add .
git commit -m "Update documentation with GitHub username: $USERNAME

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>" || true

# Check if remote exists
if git remote get-url origin &> /dev/null; then
    echo "✓ Remote 'origin' already configured"
else
    echo "🔗 Adding remote..."
    git remote add origin "https://github.com/$USERNAME/ai-cli-memory-system.git"
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
bash -c 'unset GITHUB_TOKEN && git push -u origin main'

echo ""
echo "✅ Success! Repository is live at:"
echo "   https://github.com/$USERNAME/ai-cli-memory-system"
echo ""
echo "📝 Next: Add topics on GitHub:"
echo "   ai, cli, memory, claude, copilot, gemini, developer-tools, productivity, python, sqlite"
echo ""
echo "🧪 Test installation:"
echo "   curl -fsSL https://raw.githubusercontent.com/$USERNAME/ai-cli-memory-system/main/install.sh | bash"
echo ""
