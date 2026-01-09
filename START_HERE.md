# 🚀 START HERE - After Reboot Guide

## ✅ Everything is Ready!

Your AI CLI Memory System is **fully installed and configured**. Here's what you need to know:

---

## 🎯 How to Launch Claude with Memory

### Just launch Claude normally:
```bash
claude
```

**That's it!** The memory system will automatically:
- ✅ Start tracking this session
- ✅ Retrieve relevant context from previous sessions
- ✅ Log all commands and file changes
- ✅ Check for tool updates in the background
- ✅ Save everything when you exit

### What You'll See:
```bash
🚀 Starting codex session...
📝 Session ID: abc123
💭 Found 2 recent session(s) in this directory
📂 Git: main
```

---

## 📊 View Your Memory Stats

```bash
# Quick stats
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats

# Get context for current directory
python3 ~/ai-cli-memory-system/scripts/memory_manager.py context

# Check what tools are installed
python3 ~/ai-cli-memory-system/scripts/auto_updater.py status
```

---

## 🌐 Launch Web Dashboard

```bash
# Start the dashboard
python3 ~/ai-cli-memory-system/scripts/dashboard.py

# Then open: http://localhost:5555
```

The dashboard shows:
- 📊 Session statistics
- 📈 Activity timeline
- 🗂️ Top projects
- 🧠 Knowledge base
- 📁 Most modified files

---

## ☁️ Cloud Sync (Optional)

### Configure Dropbox Sync (Easiest):
```bash
python3 ~/ai-cli-memory-system/scripts/cloud_sync.py configure dropbox
```

### Push to cloud:
```bash
python3 ~/ai-cli-memory-system/scripts/cloud_sync.py push
```

### Pull from cloud (on another machine):
```bash
python3 ~/ai-cli-memory-system/scripts/cloud_sync.py pull
```

### Check sync status:
```bash
python3 ~/ai-cli-memory-system/scripts/cloud_sync.py status
```

---

## 🔧 Shell Aliases (Recommended)

Add these to your `~/.zshrc`:

```bash
# AI CLI Memory shortcuts
alias ai-stats='python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats'
alias ai-context='python3 ~/ai-cli-memory-system/scripts/memory_manager.py context'
alias ai-update='python3 ~/ai-cli-memory-system/scripts/auto_updater.py update-all'
alias ai-dashboard='python3 ~/ai-cli-memory-system/scripts/dashboard.py'
alias ai-sync='python3 ~/ai-cli-memory-system/scripts/cloud_sync.py sync'
```

Then:
```bash
source ~/.zshrc
```

Now you can use:
```bash
ai-stats
ai-dashboard
ai-sync
```

---

## 📁 Important Locations

### Your Data:
- **Database**: `~/.claude/memory/context.db`
- **Hooks**: `~/.claude/hooks.sh`
- **Settings**: `~/.claude/settings.json`
- **Scripts**: `~/ai-cli-memory-system/scripts/`

### GitHub Repository:
**https://github.com/heyfinal/ai-cli-memory-system**

---

## 🎓 What Gets Tracked Automatically

### Every Session:
- ✅ Start/end time and duration
- ✅ Working directory and git branch
- ✅ Files you create/modify/read/delete
- ✅ Commands you run
- ✅ Programming language context
- ✅ Git commits in the directory

### Knowledge Base:
- ✅ Solutions to problems
- ✅ Coding patterns you use
- ✅ Project-specific preferences
- ✅ Common commands and workflows

### Summaries:
- ✅ Weekly rollups (automatic on Sundays)
- ✅ Project statistics
- ✅ Time spent per project
- ✅ Most active files

---

## 🆘 Troubleshooting

### Memory not working?
```bash
# Test the hooks
/Users/daniel/.claude/hooks.sh pre

# Check database
ls -lh ~/.claude/memory/context.db
```

### Database error?
```bash
# Reinitialize
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats
```

### Want to start fresh?
```bash
# Backup first!
cp ~/.claude/memory/context.db ~/.claude/memory/context.db.backup

# Then delete
rm ~/.claude/memory/context.db
```

---

## 📚 Learn More

- **README**: `~/ai-cli-memory-system/README.md`
- **Quick Start**: `~/ai-cli-memory-system/QUICKSTART.md`
- **Deploy Guide**: `~/ai-cli-memory-system/DEPLOY.md`
- **GitHub**: https://github.com/heyfinal/ai-cli-memory-system

---

## 🎉 You're All Set!

Just open a new terminal and run:
```bash
claude
```

Your AI assistant now has **persistent memory** across all sessions! 🧠✨

---

## 🚀 Advanced Features

### Create Custom Knowledge:
```python
from memory_manager import MemoryManager
m = MemoryManager()
m.add_knowledge(
    category="pattern",
    title="My Custom Pattern",
    description="How I like to structure my code"
)
```

### Query Memory:
```python
context = m.get_relevant_context(cwd="/my/project")
print(context['relevant_knowledge'])
```

### Export for Analysis:
```bash
sqlite3 ~/.claude/memory/context.db ".dump" > memory_export.sql
```

---

**Questions? Issues?**
- GitHub Issues: https://github.com/heyfinal/ai-cli-memory-system/issues
- Your Database: `~/.claude/memory/context.db`

**Happy coding with persistent memory! 🎯**
