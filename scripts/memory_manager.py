#!/usr/bin/env python3
"""
AI CLI Contextual Memory Manager
Handles session tracking, context capture, and intelligent retrieval
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

class MemoryManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.expanduser("~/.claude/memory/context.db")

        self.db_path = db_path
        self.ensure_db_exists()

    def ensure_db_exists(self):
        """Initialize database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        schema_path = os.path.expanduser("~/ai-cli-memory-system/sql/schema.sql")

        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())

        conn.commit()
        conn.close()

    def generate_session_id(self, cli_tool: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{cli_tool}_{timestamp}_{os.getpid()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

    def start_session(self, cli_tool: str) -> str:
        """Start a new session and return session_id"""
        session_id = self.generate_session_id(cli_tool)
        cwd = os.getcwd()

        # Get git info if in a git repo
        git_repo = None
        git_branch = None
        git_commit = None

        try:
            git_repo = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()

            git_branch = subprocess.check_output(
                ["git", "branch", "--show-current"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()

            git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except:
            pass

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (session_id, cli_tool, start_time, working_dir, git_repo, git_branch, git_commit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, cli_tool, datetime.now().isoformat(), cwd, git_repo, git_branch, git_commit))

        # Update or create project entry
        if git_repo:
            cursor.execute("""
                INSERT INTO projects (project_path, project_name, last_session_id, session_count, updated_at)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(project_path) DO UPDATE SET
                    last_session_id = excluded.last_session_id,
                    session_count = session_count + 1,
                    updated_at = excluded.updated_at
            """, (git_repo, os.path.basename(git_repo), session_id, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return session_id

    def end_session(self, session_id: str, exit_code: int = 0):
        """End a session and calculate duration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sessions
            SET end_time = ?,
                exit_code = ?,
                duration_seconds = (
                    SELECT (julianday(?) - julianday(start_time)) * 86400
                    FROM sessions WHERE session_id = ?
                )
            WHERE session_id = ?
        """, (datetime.now().isoformat(), exit_code, datetime.now().isoformat(), session_id, session_id))

        # Update project total time
        cursor.execute("""
            UPDATE projects
            SET total_time_seconds = total_time_seconds + (
                SELECT duration_seconds FROM sessions WHERE session_id = ?
            )
            WHERE project_path = (
                SELECT git_repo FROM sessions WHERE session_id = ?
            )
        """, (session_id, session_id))

        conn.commit()
        conn.close()

    def log_context(self, session_id: str, context_type: str, context_data: Dict[str, Any]):
        """Log contextual information during a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO session_context (session_id, context_type, context_data, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, context_type, json.dumps(context_data), datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def log_file_action(self, session_id: str, file_path: str, action: str,
                       language: Optional[str] = None, lines_added: int = 0, lines_removed: int = 0):
        """Log file modifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO session_files (session_id, file_path, action, language, lines_added, lines_removed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, file_path, action, language, lines_added, lines_removed, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def log_command(self, session_id: str, command: str, exit_code: int, output_summary: Optional[str] = None):
        """Log executed commands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO session_commands (session_id, command, exit_code, output_summary, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, command, exit_code, output_summary, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def add_knowledge(self, category: str, title: str, description: str,
                     context: Optional[Dict] = None, source_session: Optional[str] = None):
        """Add to knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        source_sessions = json.dumps([source_session]) if source_session else None

        cursor.execute("""
            INSERT INTO knowledge_base (category, title, description, context, source_sessions, last_used)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                frequency = frequency + 1,
                last_used = excluded.last_used,
                updated_at = CURRENT_TIMESTAMP
        """, (category, title, description, json.dumps(context) if context else None,
              source_sessions, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_relevant_context(self, cwd: Optional[str] = None,
                           git_branch: Optional[str] = None,
                           file_patterns: Optional[List[str]] = None,
                           limit: int = 10) -> Dict[str, Any]:
        """Retrieve relevant context for current work"""
        if cwd is None:
            cwd = os.getcwd()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        context = {
            "recent_sessions": [],
            "project_patterns": [],
            "relevant_knowledge": [],
            "similar_files": []
        }

        # Get recent sessions in this directory
        cursor.execute("""
            SELECT * FROM recent_sessions
            WHERE working_dir = ?
            LIMIT ?
        """, (cwd, limit))
        context["recent_sessions"] = [dict(row) for row in cursor.fetchall()]

        # Get project-specific patterns
        cursor.execute("""
            SELECT pp.* FROM project_patterns pp
            JOIN projects p ON pp.project_id = p.id
            WHERE p.project_path = (
                SELECT git_repo FROM sessions
                WHERE working_dir = ?
                ORDER BY start_time DESC LIMIT 1
            )
            ORDER BY pp.confidence DESC
        """, (cwd,))
        context["project_patterns"] = [dict(row) for row in cursor.fetchall()]

        # Get relevant knowledge
        cursor.execute("""
            SELECT * FROM knowledge_base
            ORDER BY frequency DESC, last_used DESC
            LIMIT ?
        """, (limit,))
        context["relevant_knowledge"] = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return context

    def create_weekly_summary(self, year: int, week: int, cli_tool: str):
        """Create compressed weekly summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all sessions for this week
        cursor.execute("""
            SELECT
                working_dir,
                COUNT(*) as session_count,
                SUM(duration_seconds) as total_time,
                GROUP_CONCAT(DISTINCT git_branch) as branches,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM sessions
            WHERE cli_tool = ?
                AND strftime('%Y', start_time) = ?
                AND strftime('%W', start_time) = ?
            GROUP BY working_dir
        """, (cli_tool, str(year), f"{week:02d}"))

        for row in cursor.fetchall():
            working_dir, session_count, total_time, branches, unique_sessions = row

            # Get detailed context for summary
            summary_data = {
                "branches_worked_on": branches.split(',') if branches else [],
                "unique_sessions": unique_sessions,
                "average_session_time": total_time / session_count if session_count > 0 else 0
            }

            cursor.execute("""
                INSERT INTO weekly_summaries (year, week_number, cli_tool, project_path, summary_data, session_count, total_time_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(year, week_number, cli_tool, project_path) DO UPDATE SET
                    summary_data = excluded.summary_data,
                    session_count = excluded.session_count,
                    total_time_seconds = excluded.total_time_seconds,
                    created_at = CURRENT_TIMESTAMP
            """, (year, week, cli_tool, working_dir, json.dumps(summary_data), session_count, total_time))

        conn.commit()
        conn.close()

    def export_context_for_mcp(self) -> Dict[str, Any]:
        """Export context in MCP memory-compatible format"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get entities
        cursor.execute("SELECT * FROM entities")
        entities = [dict(row) for row in cursor.fetchall()]

        # Get relations
        cursor.execute("""
            SELECT
                e1.entity_name as from_name,
                er.relation_type,
                e2.entity_name as to_name,
                er.strength
            FROM entity_relations er
            JOIN entities e1 ON er.from_entity_id = e1.id
            JOIN entities e2 ON er.to_entity_id = e2.id
        """)
        relations = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "entities": entities,
            "relations": relations
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total sessions by tool
        cursor.execute("""
            SELECT cli_tool, COUNT(*) as count, SUM(duration_seconds) as total_time
            FROM sessions
            GROUP BY cli_tool
        """)
        stats["by_tool"] = {row[0]: {"sessions": row[1], "total_time": row[2]} for row in cursor.fetchall()}

        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT DATE(start_time) as date, COUNT(*) as sessions
            FROM sessions
            WHERE start_time >= datetime('now', '-7 days')
            GROUP BY DATE(start_time)
            ORDER BY date
        """)
        stats["recent_activity"] = [{"date": row[0], "sessions": row[1]} for row in cursor.fetchall()]

        # Most active projects
        cursor.execute("""
            SELECT project_path, project_name, session_count, total_time_seconds
            FROM projects
            ORDER BY session_count DESC
            LIMIT 10
        """)
        stats["top_projects"] = [
            {
                "path": row[0],
                "name": row[1],
                "sessions": row[2],
                "time": row[3]
            }
            for row in cursor.fetchall()
        ]

        conn.close()

        return stats


def main():
    """CLI interface for memory manager"""
    if len(sys.argv) < 2:
        print("Usage: memory_manager.py <command> [args...]")
        print("Commands:")
        print("  start <tool>           - Start a new session")
        print("  end <session_id>       - End a session")
        print("  context [dir]          - Get relevant context")
        print("  stats                  - Show statistics")
        print("  weekly <year> <week>   - Create weekly summary")
        sys.exit(1)

    manager = MemoryManager()
    command = sys.argv[1]

    if command == "start":
        tool = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        session_id = manager.start_session(tool)
        print(session_id)

    elif command == "end":
        session_id = sys.argv[2]
        exit_code = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        manager.end_session(session_id, exit_code)
        print(f"Session {session_id} ended")

    elif command == "context":
        cwd = sys.argv[2] if len(sys.argv) > 2 else None
        context = manager.get_relevant_context(cwd)
        print(json.dumps(context, indent=2))

    elif command == "stats":
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2))

    elif command == "weekly":
        year = int(sys.argv[2])
        week = int(sys.argv[3])
        tool = sys.argv[4] if len(sys.argv) > 4 else "claude"
        manager.create_weekly_summary(year, week, tool)
        print(f"Weekly summary created for {year}-W{week}")


if __name__ == "__main__":
    main()
