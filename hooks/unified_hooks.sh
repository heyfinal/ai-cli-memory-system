#!/bin/bash
# Unified AI CLI Hooks System
# Works with Claude Code, Codex, Gemini, and other AI CLI tools

set -e

HOOKS_DIR="$HOME/.claude/hooks"
SCRIPTS_DIR="$HOME/ai-cli-memory-system/scripts"
MEMORY_DB="$HOME/.claude/memory/context.db"

# Detect which CLI tool is running
detect_cli_tool() {
    if [[ -n "$CLAUDE_SESSION" ]] || [[ "$0" == *"claude"* ]]; then
        echo "claude"
    elif [[ -n "$CODEX_SESSION" ]] || command -v gh copilot &> /dev/null; then
        echo "codex"
    elif [[ -n "$GEMINI_SESSION" ]]; then
        echo "gemini"
    elif [[ -n "$AIDER_SESSION" ]]; then
        echo "aider"
    else
        echo "unknown"
    fi
}

# Pre-session hook
pre_session() {
    CLI_TOOL=$(detect_cli_tool)

    echo "🚀 Starting $CLI_TOOL session..."

    # Check for updates (async, don't block)
    if [[ -f "$SCRIPTS_DIR/auto_updater.py" ]]; then
        python3 "$SCRIPTS_DIR/auto_updater.py" check "$CLI_TOOL" &> /dev/null &
    fi

    # Start session tracking
    if [[ -f "$SCRIPTS_DIR/memory_manager.py" ]]; then
        SESSION_ID=$(python3 "$SCRIPTS_DIR/memory_manager.py" start "$CLI_TOOL")
        export AI_SESSION_ID="$SESSION_ID"

        # Save session ID to temp file for post-session hook
        echo "$SESSION_ID" > "$HOME/.claude/current_session.tmp"

        echo "📝 Session ID: $SESSION_ID"
    fi

    # Display relevant context
    if [[ -f "$SCRIPTS_DIR/memory_manager.py" ]]; then
        CONTEXT=$(python3 "$SCRIPTS_DIR/memory_manager.py" context "$(pwd)" 2>/dev/null || echo "{}")

        # Parse and display context
        RECENT_SESSIONS=$(echo "$CONTEXT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('recent_sessions', [])))" 2>/dev/null || echo "0")

        if [[ "$RECENT_SESSIONS" -gt 0 ]]; then
            echo "💭 Found $RECENT_SESSIONS recent session(s) in this directory"
        fi
    fi

    # Check git status
    if git rev-parse --git-dir > /dev/null 2>&1; then
        BRANCH=$(git branch --show-current)
        UNCOMMITTED=$(git status --porcelain | wc -l | tr -d ' ')

        echo "📂 Git: $BRANCH"
        if [[ "$UNCOMMITTED" -gt 0 ]]; then
            echo "⚠️  $UNCOMMITTED uncommitted change(s)"
        fi
    fi

    echo ""
}

# Post-session hook
post_session() {
    CLI_TOOL=$(detect_cli_tool)
    EXIT_CODE=${1:-0}

    echo ""
    echo "👋 Ending $CLI_TOOL session..."

    # Get session ID
    SESSION_ID="$AI_SESSION_ID"
    if [[ -z "$SESSION_ID" ]] && [[ -f "$HOME/.claude/current_session.tmp" ]]; then
        SESSION_ID=$(cat "$HOME/.claude/current_session.tmp")
    fi

    # End session tracking
    if [[ -n "$SESSION_ID" ]] && [[ -f "$SCRIPTS_DIR/memory_manager.py" ]]; then
        python3 "$SCRIPTS_DIR/memory_manager.py" end "$SESSION_ID" "$EXIT_CODE"
        echo "✓ Session saved"

        # Clean up temp file
        rm -f "$HOME/.claude/current_session.tmp"
    fi

    # Check if weekly summary is needed (run on Sundays)
    if [[ $(date +%u) -eq 7 ]]; then
        YEAR=$(date +%Y)
        WEEK=$(date +%V)

        if [[ -f "$SCRIPTS_DIR/memory_manager.py" ]]; then
            python3 "$SCRIPTS_DIR/memory_manager.py" weekly "$YEAR" "$WEEK" "$CLI_TOOL" &> /dev/null &
            echo "📊 Creating weekly summary..."
        fi
    fi

    # Show session stats
    if [[ "$EXIT_CODE" -eq 0 ]]; then
        echo "✓ Session completed successfully"
    else
        echo "✗ Session ended with errors (exit code: $EXIT_CODE)"
    fi
}

# Command tracking hook (for real-time logging)
on_command() {
    COMMAND="$1"
    EXIT_CODE="${2:-0}"

    # Skip tracking for common read-only commands
    case "$COMMAND" in
        ls|pwd|echo|cat|head|tail|grep)
            return
            ;;
    esac

    # Log command if session is active
    if [[ -n "$AI_SESSION_ID" ]] && [[ -f "$SCRIPTS_DIR/memory_manager.py" ]]; then
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPTS_DIR')
from memory_manager import MemoryManager
m = MemoryManager('$MEMORY_DB')
m.log_command('$AI_SESSION_ID', '''$COMMAND''', $EXIT_CODE)
" &> /dev/null &
    fi
}

# File change tracking hook
on_file_change() {
    FILE_PATH="$1"
    ACTION="${2:-modified}"  # created, modified, deleted, read

    if [[ -n "$AI_SESSION_ID" ]] && [[ -f "$SCRIPTS_DIR/memory_manager.py" ]]; then
        # Detect language from extension
        EXTENSION="${FILE_PATH##*.}"
        LANGUAGE=""

        case "$EXTENSION" in
            py) LANGUAGE="python" ;;
            js|jsx) LANGUAGE="javascript" ;;
            ts|tsx) LANGUAGE="typescript" ;;
            swift) LANGUAGE="swift" ;;
            go) LANGUAGE="go" ;;
            rs) LANGUAGE="rust" ;;
            java) LANGUAGE="java" ;;
            rb) LANGUAGE="ruby" ;;
            *) LANGUAGE="$EXTENSION" ;;
        esac

        python3 -c "
import sys
sys.path.insert(0, '$SCRIPTS_DIR')
from memory_manager import MemoryManager
m = MemoryManager('$MEMORY_DB')
m.log_file_action('$AI_SESSION_ID', '$FILE_PATH', '$ACTION', '$LANGUAGE')
" &> /dev/null &
    fi
}

# Main hook dispatcher
main() {
    HOOK_TYPE="${1:-pre}"

    # Ensure directories exist
    mkdir -p "$HOME/.claude/memory"
    mkdir -p "$HOOKS_DIR"

    # Initialize database if needed
    if [[ -f "$SCRIPTS_DIR/memory_manager.py" ]] && [[ ! -f "$MEMORY_DB" ]]; then
        python3 "$SCRIPTS_DIR/memory_manager.py" stats &> /dev/null || true
    fi

    case "$HOOK_TYPE" in
        pre|pre-session)
            pre_session
            ;;
        post|post-session)
            post_session "${2:-0}"
            ;;
        command)
            on_command "$2" "${3:-0}"
            ;;
        file)
            on_file_change "$2" "$3"
            ;;
        *)
            echo "Unknown hook type: $HOOK_TYPE"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
