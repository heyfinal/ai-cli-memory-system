# 🧠 AI CLI Memory System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20WSL-lightgrey.svg)

**Give your AI CLI tools a persistent memory across all sessions**

*Never lose context again. Every conversation, decision, and pattern is remembered.*

[Features](#-features) •
[Quick Start](#-quick-start) •
[Installation](#-installation) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

<img src="https://user-images.githubusercontent.com/placeholder/demo.gif" alt="Demo" width="800"/>

</div>

---

## 🎯 What is this?

AI CLI Memory System is a **unified contextual memory layer** for AI-powered CLI tools like Claude Code, GitHub Copilot CLI (Codex), Gemini, and Aider. It tracks every session, learns your patterns, and automatically provides relevant context when you return to work.

### The Problem
- 🔴 Starting fresh every session - no context from yesterday
- 🔴 Repeating the same explanations to AI assistants
- 🔴 Losing track of decisions made in previous sessions
- 🔴 No memory of what worked and what didn't
- 🔴 Managing multiple AI CLI tools with separate contexts

### The Solution
- 🟢 **Persistent memory** across all sessions and tools
- 🟢 **Automatic context capture** - no manual note-taking
- 🟢 **Intelligent retrieval** - relevant memories when you need them
- 🟢 **Pattern learning** - remembers your coding style and preferences
- 🟢 **Unified system** - works with Claude, Codex, Gemini, Aider, and more

---

## ✨ Features

### 🎪 Core Features

#### 🧠 Contextual Persistent Memory
```bash
# Your AI assistant remembers:
- What you worked on yesterday
- Decisions you made last week
- Solutions to similar problems
- Your project-specific preferences
- File patterns and common operations
```

#### 🔄 Auto-Update System
```bash
# All your AI CLI tools stay up-to-date automatically
✓ Claude Code
✓ GitHub Copilot CLI (Codex)
✓ Gemini CLI
✓ Aider
✓ Cursor

# Just launch any tool - updates check in the background
```

#### 📊 Intelligent Context Retrieval
```python
# When you start working:
- Retrieves last 10 sessions in current directory
- Finds project-specific patterns
- Surfaces relevant solutions from knowledge base
- Identifies similar past work
```

#### 📈 Session Tracking
- Automatic session start/end
- Git branch and commit tracking
- Files modified with language detection
- Commands executed with outcomes
- Duration and productivity metrics

#### 🗂️ Knowledge Base
- Pattern recognition across projects
- Solution library with search
- Gotchas and warnings
- Personal preferences and coding style

#### 📅 Weekly Summaries
- Automatic rollup every Sunday
- Key decisions made
- Problems solved
- New patterns learned
- Time spent by project

---

## 🚀 Quick Start

### One-Line Install
```bash
curl -fsSL https://raw.githubusercontent.com/heyfinal/ai-cli-memory-system/main/install.sh | bash
```

### Start Using Immediately
```bash
# Just launch your AI CLI tool as usual
claude

# Memory system automatically:
# ✓ Tracks this session
# ✓ Retrieves relevant context
# ✓ Logs decisions and solutions
# ✓ Updates knowledge base
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git
- Any AI CLI tool (Claude Code, Codex, Gemini, Aider)

### Automatic Installation

#### macOS / Linux / WSL
```bash
# Clone the repository
git clone https://github.com/heyfinal/ai-cli-memory-system.git
cd ai-cli-memory-system

# Run installer
./install.sh
```

The installer will:
1. ✅ Check dependencies
2. ✅ Install all scripts and hooks
3. ✅ Initialize the database
4. ✅ Configure Claude Code
5. ✅ Set up shell integration
6. ✅ Run validation tests

### Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

```bash
# 1. Create directories
mkdir -p ~/ai-cli-memory-system/{scripts,hooks,config,sql}
mkdir -p ~/.claude/memory

# 2. Copy files
cp -r scripts/* ~/ai-cli-memory-system/scripts/
cp -r hooks/* ~/ai-cli-memory-system/hooks/
cp -r sql/* ~/ai-cli-memory-system/sql/

# 3. Make executable
chmod +x ~/ai-cli-memory-system/scripts/*.py
chmod +x ~/ai-cli-memory-system/hooks/*.sh

# 4. Initialize database
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats

# 5. Configure Claude Code
# Add to ~/.claude/settings.json:
{
  "hooks": {
    "pre-session": "~/ai-cli-memory-system/hooks/unified_hooks.sh pre",
    "post-session": "~/ai-cli-memory-system/hooks/unified_hooks.sh post"
  }
}

# 6. Add to shell config (~/.zshrc or ~/.bashrc)
export AI_CLI_MEMORY="$HOME/.claude/memory/context.db"
export AI_HOOKS_DIR="$HOME/ai-cli-memory-system/hooks"
```
</details>

---

## 📖 Documentation

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AI CLI Tools Layer                     │
│     Claude Code │ Codex │ Gemini │ Aider │ Cursor      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Unified Hooks System                    │
│   • Pre-session: Context retrieval & auto-update        │
│   • Post-session: Session save & summarization          │
└────────────────────────┬────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Memory   │  │  Auto    │  │ Context  │
    │ Manager  │  │ Updater  │  │ Retrieval│
    └────┬─────┘  └──────────┘  └────┬─────┘
         │                            │
         ▼                            ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database (context.db)                │
│  • Sessions        • Knowledge Base    • Projects       │
│  • Commands        • Patterns          • Entities       │
│  • Files           • Relations         • Summaries      │
└─────────────────────────────────────────────────────────┘
```

### Database Schema

The system uses a sophisticated SQLite schema with:

- **Sessions**: Every AI CLI session with metadata
- **Context**: Decisions, solutions, and observations
- **Files**: All file modifications with diff stats
- **Commands**: Executed commands with outcomes
- **Knowledge Base**: Reusable patterns and solutions
- **Projects**: Project-specific preferences
- **Entities & Relations**: Graph structure for complex queries
- **Weekly Summaries**: Compressed historical data

### Usage Examples

#### Check Memory Stats
```bash
python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats
```

Output:
```json
{
  "by_tool": {
    "claude": {"sessions": 127, "total_time": 45832},
    "codex": {"sessions": 43, "total_time": 12456}
  },
  "recent_activity": [
    {"date": "2026-01-09", "sessions": 5},
    {"date": "2026-01-08", "sessions": 8}
  ],
  "top_projects": [
    {"path": "/Users/daniel/myproject", "sessions": 45, "time": 18723}
  ]
}
```

#### Get Context for Current Directory
```bash
python3 ~/ai-cli-memory-system/scripts/memory_manager.py context
```

#### Check for Updates
```bash
python3 ~/ai-cli-memory-system/scripts/auto_updater.py check
```

Output:
```
🔍 Checking for updates...

✓ claude:
   Version: 2.1.1
   ✓ Up to date

✓ codex:
   Version: 1.0.4
   ⬆️  Update available: 1.0.5
```

#### Update All Tools
```bash
python3 ~/ai-cli-memory-system/scripts/auto_updater.py update-all -y
```

#### Create Weekly Summary
```bash
python3 ~/ai-cli-memory-system/scripts/memory_manager.py weekly 2026 2 claude
```

---

## 🎨 How It Works

### 1. Session Start (Pre-Hook)
```bash
🚀 Starting claude session...
✓ Checking for updates...
📝 Session ID: a3f7d9e2b1c4
💭 Found 3 recent session(s) in this directory
📂 Git: feature/new-api
```

### 2. During Session
- Commands are logged automatically
- File changes tracked with language detection
- Decisions and solutions added to knowledge base
- Context continuously updated

### 3. Session End (Post-Hook)
```bash
👋 Ending claude session...
✓ Session saved
✓ Knowledge base updated
📊 Creating weekly summary...
✓ Session completed successfully
```

### 4. Next Session
When you return to the same project:
- Previous decisions are retrieved
- Similar problems are surfaced
- Project patterns are applied
- Relevant knowledge is loaded

---

## 🔧 Configuration

### Claude Code Integration

Edit `~/.claude/settings.json`:

```json
{
  "hooks": {
    "pre-session": "~/ai-cli-memory-system/hooks/unified_hooks.sh pre",
    "post-session": "~/ai-cli-memory-system/hooks/unified_hooks.sh post"
  }
}
```

### Memory Configuration

Edit `~/ai-cli-memory-system/config/claude_config.json`:

```json
{
  "memory": {
    "enabled": true,
    "database": "~/.claude/memory/context.db",
    "auto_summarize": true,
    "summarize_interval": "weekly"
  },
  "auto_update": {
    "enabled": true,
    "check_interval": "daily",
    "auto_install": false
  },
  "context_retrieval": {
    "enabled": true,
    "max_recent_sessions": 10,
    "include_project_patterns": true,
    "include_knowledge_base": true
  }
}
```

---

## 🔌 Supported CLI Tools

| Tool | Status | Auto-Update | Memory Integration |
|------|--------|-------------|-------------------|
| Claude Code | ✅ Full | ✅ Yes | ✅ Yes |
| GitHub Copilot CLI | ✅ Full | ✅ Yes | ✅ Yes |
| Gemini CLI | ✅ Full | ✅ Yes | ✅ Yes |
| Aider | ✅ Full | ✅ Yes | ✅ Yes |
| Cursor | 🟡 Partial | ✅ Yes | 🟡 Partial |

---

## 🛠️ Advanced Usage

### Custom Memory Queries

```python
from memory_manager import MemoryManager

manager = MemoryManager()

# Get context for specific directory
context = manager.get_relevant_context(
    cwd="/Users/daniel/myproject",
    file_patterns=["*.py"],
    limit=20
)

# Add custom knowledge
manager.add_knowledge(
    category="pattern",
    title="API Error Handling Pattern",
    description="Use retry with exponential backoff for API calls",
    context={"language": "python", "framework": "requests"}
)

# Export for MCP integration
mcp_data = manager.export_context_for_mcp()
```

### Shell Integration

Add to your `.zshrc` or `.bashrc`:

```bash
# AI CLI Memory shortcuts
alias ai-stats='python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats'
alias ai-update='python3 ~/ai-cli-memory-system/scripts/auto_updater.py update-all'
alias ai-context='python3 ~/ai-cli-memory-system/scripts/memory_manager.py context'

# Auto-check updates on shell start (async)
python3 ~/ai-cli-memory-system/scripts/auto_updater.py check &> /dev/null &
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🐛 **Report bugs** - Open an issue with details
2. 💡 **Suggest features** - Share your ideas
3. 🔧 **Submit PRs** - Fix bugs or add features
4. 📖 **Improve docs** - Help others understand

### Development Setup

```bash
git clone https://github.com/heyfinal/ai-cli-memory-system.git
cd ai-cli-memory-system

# Install in development mode
./install.sh

# Run tests
python3 -m pytest tests/

# Lint code
pylint scripts/*.py
```

---

## 📊 Roadmap

- [x] Core memory system
- [x] Auto-update for major CLI tools
- [x] SQLite backend with efficient queries
- [x] Weekly summaries
- [x] Cross-platform support (macOS, Linux, WSL)
- [ ] Web dashboard for visualizing memory
- [ ] AI-powered context suggestion
- [ ] Multi-machine sync (optional cloud backup)
- [ ] Integration with more AI tools (Copilot Workspace, Continue, etc.)
- [ ] Export to Obsidian/Notion/Roam
- [ ] Team sharing capabilities

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- Claude Code team at Anthropic
- GitHub Copilot team
- Google Gemini team
- All AI CLI tool developers

---

<div align="center">

[⬆ Back to top](#-ai-cli-memory-system)

</div>
