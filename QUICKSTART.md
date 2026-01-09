# 🚀 Quick Start Guide

## Installation (30 seconds)

```bash
cd ~/ai-cli-memory-system
./install.sh
```

That's it! The system is now active.

## Verify Installation

```bash
# Check memory stats
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats

# Check CLI tool versions
python3 ~/ai-cli-memory-system/scripts/auto_updater.py status
```

## First Session

```bash
# Just start your AI CLI tool normally
claude

# You'll see:
# 🚀 Starting claude session...
# 📝 Session ID: abc123
# 💭 Found X recent session(s) in this directory
```

## Common Commands

### Memory Management
```bash
# View stats
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats

# Get context for current directory
python3 ~/ai-cli-memory-system/scripts/memory_manager.py context

# Create weekly summary
python3 ~/ai-cli-memory-system/scripts/memory_manager.py weekly 2026 2 claude
```

### Auto-Updates
```bash
# Check for updates
python3 ~/ai-cli-memory-system/scripts/auto_updater.py check

# Update specific tool
python3 ~/ai-cli-memory-system/scripts/auto_updater.py update claude

# Update all tools (with auto-confirm)
python3 ~/ai-cli-memory-system/scripts/auto_updater.py update-all -y

# Show installed versions
python3 ~/ai-cli-memory-system/scripts/auto_updater.py status
```

## Shell Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# AI CLI shortcuts
alias ai-stats='python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats'
alias ai-context='python3 ~/ai-cli-memory-system/scripts/memory_manager.py context'
alias ai-update='python3 ~/ai-cli-memory-system/scripts/auto_updater.py update-all'
alias ai-check='python3 ~/ai-cli-memory-system/scripts/auto_updater.py check'
```

Then:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Now you can use:
```bash
ai-stats
ai-context
ai-update
ai-check
```

## Troubleshooting

### Database not initialized
```bash
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats
```

### Hooks not firing
Check `~/.claude/settings.json`:
```json
{
  "hooks": {
    "pre-session": "/Users/YOURUSER/ai-cli-memory-system/hooks/unified_hooks.sh pre",
    "post-session": "/Users/YOURUSER/ai-cli-memory-system/hooks/unified_hooks.sh post"
  }
}
```

### Scripts not executable
```bash
chmod +x ~/ai-cli-memory-system/scripts/*.py
chmod +x ~/ai-cli-memory-system/hooks/*.sh
```

## What Happens Automatically

### On Session Start
1. ✅ Check for CLI tool updates (background)
2. ✅ Start session tracking
3. ✅ Retrieve relevant context from previous sessions
4. ✅ Display git status if in a repo

### During Session
1. ✅ Log commands executed
2. ✅ Track file modifications
3. ✅ Record decisions and solutions
4. ✅ Update knowledge base

### On Session End
1. ✅ Save session with duration
2. ✅ Update project statistics
3. ✅ Create weekly summary (on Sundays)

## Next Steps

- Read the full [README.md](README.md)
- Customize [config/claude_config.json](config/claude_config.json)
- Explore the [database schema](sql/schema.sql)
- Check out [advanced usage examples](README.md#-advanced-usage)

## Support

Having issues? Check:
1. [GitHub Issues](https://github.com/heyfinal/ai-cli-memory-system/issues)
2. [Full Documentation](README.md)
3. [Discord Community](https://discord.gg/yourserver)

---

**Enjoy your enhanced AI CLI experience! 🎉**
