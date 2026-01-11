# AI CLI Memory System - Installation Guide

## One-Line Installation

Copy and paste this command into your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/heyfinal/ai-cli-memory-system/main/install.sh | bash
```

## What This Installs

1. **Directory Structure**
   - `~/ai-cli-memory-system/` - Main installation directory
   - `~/.claude/memory/` - Memory database and logs

2. **Shell Wrappers** (automatically added to ~/.zshrc or ~/.bashrc)
   - `claude` - Memory-aware Claude Code wrapper
   - `codex` - Memory-aware Codex wrapper with full automation flags

3. **Scripts**
   - `memory_manager.py` - Session tracking and memory management
   - `profile_learner.py` - Continuous learning system
   - `capture_learnings.sh` - Automatic learning capture
   - `auto_updater.py` - Automatic update checker

4. **Hooks**
   - Pre-session hook - Loads memory context
   - Post-session hook - Captures learnings

## For Claude Code Fresh Install

If you're setting up Claude Code on a new machine, paste this into Claude Code:

```
Install the AI CLI Memory System from https://github.com/heyfinal/ai-cli-memory-system by running the installer at https://raw.githubusercontent.com/heyfinal/ai-cli-memory-system/main/install.sh
```

Claude Code will automatically download and run the installer.

## Manual Installation

If you prefer to review the installer first:

```bash
# Download the installer
curl -fsSL https://raw.githubusercontent.com/heyfinal/ai-cli-memory-system/main/install.sh > /tmp/install_memory.sh

# Review it
cat /tmp/install_memory.sh

# Run it
bash /tmp/install_memory.sh
```

## Requirements

- **Python 3.8+** (required)
- **Git** (required)
- **Claude Code CLI** (optional but recommended)
- **Codex CLI** (optional)

The installer will check for these and guide you if anything is missing.

## Post-Installation

After installation completes:

1. **Reload your shell:**
   ```bash
   source ~/.zshrc  # or source ~/.bashrc
   ```

2. **Verify the installation:**
   ```bash
   type claude  # Should show "claude is a shell function"
   type codex   # Should show "codex is a shell function"
   ```

3. **Test the memory system:**
   ```bash
   claude  # Should show "🧠 Loading memory context..."
   ```

## Features

✅ **Automatic Memory Loading** - Every CLI session starts with context
✅ **Continuous Learning** - Builds comprehensive profile over time
✅ **Session Tracking** - Tracks usage patterns and preferences
✅ **Codex Automation** - Runs with full automation flags (no prompts)
✅ **Git Integration** - Context-aware of current branch and project
✅ **Auto-Updates** - Checks for CLI tool updates on shell start

## Uninstallation

To uninstall:

```bash
# Remove installation directory
rm -rf ~/ai-cli-memory-system

# Remove memory data (optional - you may want to keep this)
rm -rf ~/.claude/memory

# Remove wrapper functions from shell config
# Edit ~/.zshrc or ~/.bashrc and remove the "# AI CLI Memory System" section
vim ~/.zshrc
```

## Support

- **Issues:** https://github.com/heyfinal/ai-cli-memory-system/issues
- **Documentation:** https://github.com/heyfinal/ai-cli-memory-system
- **Reinstall:** Just run the installer again - it's idempotent

## What Makes This Different

Traditional CLI tools start fresh every time. This system:
- Remembers your preferences
- Knows your project structure
- Recalls recent conversations
- Builds a comprehensive profile over time
- Works across all AI CLI tools (Claude Code, Codex, etc.)

Think of it as giving your AI tools a persistent memory.

---

**Version:** 1.1.0
**Last Updated:** 2026-01-11
**License:** MIT
