#!/bin/bash
# Automatic Learning Capture - Runs after AI CLI sessions
# Extracts preferences, patterns, and persona details

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_FILE="$HOME/.claude/current_session.tmp"
LEARNINGS_LOG="$HOME/.claude/memory/learnings.jsonl"

# Create learnings log if it doesn't exist
mkdir -p "$(dirname "$LEARNINGS_LOG")"
touch "$LEARNINGS_LOG"

# Function to capture learning from context
capture_learning() {
    local learning_type="$1"
    local learning_value="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Create JSON learning entry
    cat <<EOF >> "$LEARNINGS_LOG"
{"timestamp": "$timestamp", "type": "$learning_type", "value": "$learning_value", "entity": "Daniel Gillaspy"}
EOF
}

# Analyze last command/session for learnings
analyze_session() {
    # Get session data if available
    if [ -f "$SESSION_FILE" ]; then
        SESSION_ID=$(cat "$SESSION_FILE" 2>/dev/null)

        # Extract learnings using Python script
        python3 "$SCRIPT_DIR/profile_learner.py" "$SESSION_ID" 2>/dev/null

        # Log session completion
        capture_learning "session_completed" "Session $SESSION_ID analyzed"
    fi
}

# Capture specific preference types
capture_code_preference() {
    capture_learning "code_preference" "$1"
}

capture_tool_preference() {
    capture_learning "tool_preference" "$1"
}

capture_workflow_preference() {
    capture_learning "workflow_preference" "$1"
}

capture_frustration() {
    capture_learning "frustration_trigger" "$1"
}

capture_satisfaction() {
    capture_learning "satisfaction_factor" "$1"
}

# Main execution
if [ "$1" = "analyze" ]; then
    analyze_session
elif [ "$1" = "code" ]; then
    capture_code_preference "$2"
elif [ "$1" = "tool" ]; then
    capture_tool_preference "$2"
elif [ "$1" = "workflow" ]; then
    capture_workflow_preference "$2"
elif [ "$1" = "frustration" ]; then
    capture_frustration "$2"
elif [ "$1" = "satisfaction" ]; then
    capture_satisfaction "$2"
else
    # Default: analyze current session
    analyze_session
fi

# Periodically sync learnings to MCP memory (every 10 sessions)
LEARNING_COUNT=$(wc -l < "$LEARNINGS_LOG" 2>/dev/null || echo 0)
if [ $((LEARNING_COUNT % 10)) -eq 0 ] && [ "$LEARNING_COUNT" -gt 0 ]; then
    # Sync to MCP memory graph
    echo "Syncing $LEARNING_COUNT learnings to memory graph..."
    # This would call MCP memory add_observations
fi
