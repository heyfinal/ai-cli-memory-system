#!/usr/bin/env python3
"""
Profile Learner - Continuously builds user profile from AI interactions
Analyzes sessions to extract preferences, patterns, and persona details
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

# MCP Memory Integration
MEMORY_DB = Path.home() / ".claude" / "memory" / "context.db"
SESSION_DB = Path.home() / ".claude" / "memory" / "context.db"


class ProfileLearner:
    """Continuously learns about user from session interactions."""

    def __init__(self):
        self.user_entity = "Daniel Gillaspy"

    def extract_learnings_from_session(self, session_data):
        """Extract learnings from a completed session."""
        learnings = []

        # Analyze working directory patterns
        work_dir = session_data.get('working_dir', '')
        if work_dir:
            learnings.append(self._analyze_work_location(work_dir))

        # Analyze git usage
        git_branch = session_data.get('git_branch', '')
        if git_branch:
            learnings.append(self._analyze_git_pattern(git_branch))

        # Analyze tool preferences
        cli_tool = session_data.get('cli_tool', '')
        learnings.append(self._analyze_tool_preference(cli_tool))

        # Analyze session duration
        duration = session_data.get('duration', 0)
        learnings.append(self._analyze_work_pattern(duration))

        return [l for l in learnings if l]  # Filter out None

    def _analyze_work_location(self, work_dir):
        """Learn from working directory."""
        if 'workapps' in work_dir:
            return f"Works in ~/workapps/ directory for active projects"
        elif 'Downloads' in work_dir:
            return f"Sometimes works from ~/Downloads/ for quick tasks"
        elif '.claude' in work_dir:
            return f"Configures and maintains AI CLI tools and settings"
        return None

    def _analyze_git_pattern(self, git_branch):
        """Learn from git branch naming."""
        if 'main' in git_branch or 'master' in git_branch:
            return f"Works directly on main branch for solo projects"
        elif 'feature' in git_branch:
            return f"Uses feature branches for structured development"
        return f"Uses git branch: {git_branch}"

    def _analyze_tool_preference(self, cli_tool):
        """Learn from CLI tool choice."""
        if cli_tool == 'claude':
            return f"Prefers Claude Code for development tasks"
        elif cli_tool == 'codex':
            return f"Uses Codex CLI for specific workflows"
        return None

    def _analyze_work_pattern(self, duration_seconds):
        """Learn from session duration patterns."""
        if duration_seconds > 3600:  # > 1 hour
            return f"Has extended work sessions (focus-intensive tasks)"
        elif duration_seconds > 600:  # > 10 minutes
            return f"Typical session length: 10-60 minutes"
        elif duration_seconds > 60:  # > 1 minute
            return f"Quick sessions for rapid iteration"
        return None

    def capture_preference(self, preference_type, value):
        """Capture a specific preference discovered during session."""
        timestamp = datetime.now().isoformat()

        observations = {
            'code_style': [
                f"Code style preference: {value} (learned {timestamp})"
            ],
            'communication': [
                f"Communication preference: {value} (learned {timestamp})"
            ],
            'workflow': [
                f"Workflow preference: {value} (learned {timestamp})"
            ],
            'tool': [
                f"Tool preference: {value} (learned {timestamp})"
            ],
            'decision': [
                f"Decision pattern: {value} (learned {timestamp})"
            ],
            'frustration': [
                f"Frustration trigger: {value} - avoid in future (learned {timestamp})"
            ],
            'satisfaction': [
                f"What works well: {value} (learned {timestamp})"
            ]
        }

        return observations.get(preference_type, [f"{preference_type}: {value} (learned {timestamp})"])

    def build_persona_snapshot(self):
        """Build comprehensive persona from all learnings."""
        # This would query the memory graph for all Daniel Gillaspy observations
        # and synthesize them into a persona profile

        persona = {
            "name": "Daniel Gillaspy",
            "professional_background": "20+ years oil & gas, HSE/Safety expert",
            "technical_skills": "Python, JavaScript, AI automation",
            "preferences": {
                "code_quality": "Quality over quantity",
                "communication": "Direct, concise, no fluff",
                "tools": "Claude Code, Playwright, GPT-4",
                "workflow": "Automated, production-ready solutions"
            },
            "patterns": {
                "work_style": "Extended focused sessions",
                "decision_making": "Data-driven, test-oriented",
                "problem_solving": "Root cause analysis, not bandaids"
            },
            "triggers": {
                "frustrations": ["Placeholder code", "0 results", "vague solutions"],
                "satisfaction": ["Working automation", "High match scores", "Production ready"]
            }
        }

        return persona


# Example learning triggers
LEARNING_TRIGGERS = {
    "When user says 'I like'": "satisfaction",
    "When user says 'I prefer'": "preference",
    "When user says 'don't'": "negative_preference",
    "When user frustrated": "frustration",
    "When user approves": "satisfaction",
    "When quality mentioned": "quality_preference",
    "When automation requested": "workflow_preference"
}


def learn_from_interaction(user_message, ai_response, context):
    """Main entry point for learning from interactions."""
    learner = ProfileLearner()
    learnings = []

    # Detect preferences from user messages
    user_lower = user_message.lower()

    if 'i like' in user_lower or 'i prefer' in user_lower:
        # Extract what they like/prefer
        learnings.append(f"Preference detected: {user_message}")

    if 'frustrated' in user_lower or 'worthless' in user_lower or 'not working' in user_lower:
        # Capture frustration triggers
        learnings.append(f"Frustration trigger: {context.get('trigger', 'unknown')}")

    if 'perfect' in user_lower or 'excellent' in user_lower or 'great' in user_lower:
        # Capture what works well
        learnings.append(f"Positive feedback: {context.get('what_worked', 'unknown')}")

    return learnings


def save_learnings_to_memory(learnings):
    """Save learnings to MCP memory graph."""
    # This would use the mcp__memory__add_observations API
    # For now, return structured data

    return {
        "entity": "Daniel Gillaspy",
        "new_observations": learnings,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Example usage
    learner = ProfileLearner()

    # Simulate session data
    session = {
        "working_dir": "/Users/daniel/workapps/job-search-automation",
        "git_branch": "main",
        "cli_tool": "claude",
        "duration": 1200  # 20 minutes
    }

    learnings = learner.extract_learnings_from_session(session)
    print("Learnings extracted:")
    for learning in learnings:
        print(f"  - {learning}")

    # Build persona
    persona = learner.build_persona_snapshot()
    print("\nPersona Snapshot:")
    print(json.dumps(persona, indent=2))
