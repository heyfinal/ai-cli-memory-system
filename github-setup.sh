#!/bin/bash
# GitHub Repository Setup Script
# Run this AFTER completing 'gh auth login'

set -e

cd ~/ai-cli-memory-system

echo "🚀 Creating GitHub repository..."

# Create repository
gh repo create ai-cli-memory-system \
  --public \
  --source=. \
  --remote=origin \
  --description "🧠 Contextual persistent memory system for AI CLI tools (Claude, Codex, Gemini, Aider)" \
  --push

echo "✓ Repository created and code pushed!"

# Add topics
echo "📌 Adding repository topics..."
gh repo edit --add-topic ai,cli,memory,claude,copilot,gemini,developer-tools,productivity,python,sqlite,automation

echo "✓ Topics added!"

# Get the repository URL
REPO_URL=$(gh repo view --json url -q .url)
echo ""
echo "🎉 Success! Your repository is live at:"
echo "   $REPO_URL"
echo ""

# Update README with actual username
USERNAME=$(gh api user -q .login)
echo "📝 Updating README with your username..."

sed -i.bak "s|YOURUSERNAME|$USERNAME|g" README.md
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" install.sh
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" DEPLOY.md
sed -i.bak "s|YOURUSERNAME|$USERNAME|g" QUICKSTART.md

# Clean up backup files
rm -f README.md.bak install.sh.bak DEPLOY.md.bak QUICKSTART.md.bak

echo "✓ README updated with your username: $USERNAME"

# Commit and push updates
git add README.md install.sh DEPLOY.md QUICKSTART.md
git commit -m "Update documentation with actual GitHub username

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push

echo ""
echo "✅ All done! Next steps:"
echo ""
echo "1. View your repository:"
echo "   $REPO_URL"
echo ""
echo "2. Test installation on another machine:"
echo "   curl -fsSL https://raw.githubusercontent.com/$USERNAME/ai-cli-memory-system/main/install.sh | bash"
echo ""
echo "3. Share with the community:"
echo "   - Twitter: 'Just released an AI CLI memory system for Claude, Codex, Gemini! $REPO_URL #AI #CLI'"
echo "   - Reddit: r/programming, r/commandline"
echo "   - Hacker News: Show HN"
echo ""
