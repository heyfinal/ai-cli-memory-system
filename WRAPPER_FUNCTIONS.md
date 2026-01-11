# Memory-Aware AI CLI Wrapper Functions
**Updated**: 2026-01-11
**Method**: Shell functions in ~/.zshrc (more resilient than scripts)

## What Was Done

Instead of creating wrapper scripts (which get overwritten by updates), we added **shell functions** to `~/.zshrc` that wrap the `claude` and `codex` commands.

### Advantages Over Script Wrappers:
- ✅ Won't be overwritten by binary updates
- ✅ Always loaded in every new shell
- ✅ Can be easily edited in one place
- ✅ Uses `command` builtin to call original binaries

## How It Works

### Claude Wrapper Function
When you type `claude`:
1. Captures current directory and git branch
2. Builds memory-loading prompt
3. Starts session tracking (AI CLI Memory System)
4. Shows "🧠 Loading memory context..."
5. Sends prompt to real `claude` binary via `command claude`
6. Captures learnings on exit

### Codex Wrapper Function
Same process for `codex` command, with additional automation:
- ✅ Always runs with `--ask-for-approval never` (no prompts)
- ✅ Always runs with `--sandbox danger-full-access` (full file access)
- ✅ Enables fully autonomous operation

## The Prompt Injected

```
Read your memory graph to load context about:
- Daniel Gillaspy (person, projects, preferences, work history)  
- Active projects in current directory: /path/to/current/dir
- Current git branch: branch-name

IMPORTANT PREFERENCES:
- Use 'codex' CLI as subagent for routine tasks
- Reserve Claude Code for complex reasoning
- This reduces Claude API usage significantly

Check memory for recent work and be ready to continue.
```

## Usage

### Interactive Mode (Memory Auto-Loads)
```bash
claude    # Memory loads automatically
codex     # Memory loads automatically
```

### Non-Interactive Mode (Arguments Passed Through)
```bash
claude --help
codex version
```

## Verification

Check that functions are loaded:
```bash
type claude
type codex
```

Should show:
```
claude is a shell function from /Users/daniel/.zshrc
codex is a shell function from /Users/daniel/.zshrc
```

## Testing

```bash
# Test claude wrapper
claude
> "What do you know about me from memory?"

# Test codex wrapper  
codex
> "What preferences do I have?"
```

## Editing the Wrappers

```bash
vim ~/.zshrc
# Search for "# Claude Code Memory-Aware Wrapper"
# Edit the MEMORY_PROMPT or logic
source ~/.zshrc  # Reload
```

## Integration with AI CLI Memory System

The wrappers integrate with your memory system:
- **Session tracking**: `memory_manager.py start/end`
- **Learning capture**: `capture_learnings.sh analyze`
- **Memory storage**: `~/.claude/memory/context.db`
- **Learning logs**: `~/.claude/memory/learnings.jsonl`

## Preferences Remembered

The wrapper now tells me on EVERY launch to:
- ✅ Use codex for routine tasks (code reviews, refactoring, testing)
- ✅ Reserve Claude Code for complex reasoning and critical decisions
- ✅ This reduces Claude API usage significantly

This preference is also stored in the memory graph permanently.

## Technical Details

### Claude Wrapper
```bash
# The wrapper uses 'command' builtin to avoid recursion
command claude "$@"    # Calls real binary, not function

# If no args, inject memory prompt via stdin
echo "$MEMORY_PROMPT" | command claude

# If args provided, pass them directly
command claude "$@"
```

### Codex Wrapper (with automation flags)
```bash
# Codex always runs with full automation flags
# If no args, inject memory prompt
echo "$MEMORY_PROMPT" | command codex --ask-for-approval never --sandbox danger-full-access

# If args provided, add flags before arguments
command codex --ask-for-approval never --sandbox danger-full-access "$@"
```

## Comparison to Previous Approach

| Aspect | Script Wrapper | Shell Function |
|--------|---------------|----------------|
| Location | ~/.local/bin/ | ~/.zshrc |
| Overwritten by updates | Yes ❌ | No ✅ |
| Requires chmod +x | Yes | No |
| PATH manipulation needed | Yes | No |
| Easy to edit | No (separate file) | Yes (one file) |
| Loaded automatically | Only if in PATH | Always ✅ |

---

**Status**: ✅ Active and Working
**Last Updated**: 2026-01-11
**Method**: Shell functions in ~/.zshrc
**Codex Automation**: Full (--ask-for-approval never --sandbox danger-full-access)
