#!/usr/bin/env python3
"""
AI CLI Auto-Updater
Automatically checks and updates Claude Code, Codex, Gemini, and other CLI tools
"""

import os
import sys
import json
import subprocess
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List

class CLIUpdater:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.expanduser("~/.claude/memory/context.db")
        self.db_path = db_path

    def get_installed_version(self, tool: str) -> Optional[str]:
        """Get currently installed version of a tool"""
        try:
            if tool == "claude":
                result = subprocess.run(
                    ["claude", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Extract version from output like "Claude Code v2.1.1"
                    version_line = result.stdout.strip().split('\n')[0]
                    version = version_line.split()[-1].lstrip('v')
                    return version

            elif tool == "codex":
                # GitHub Copilot CLI
                result = subprocess.run(
                    ["gh", "copilot", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().split()[-1]

            elif tool == "gemini":
                # Gemini CLI (via gcloud or direct install)
                result = subprocess.run(
                    ["gemini", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().split()[-1]

            elif tool == "cursor":
                # Cursor IDE CLI
                result = subprocess.run(
                    ["cursor", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()

            elif tool == "aider":
                result = subprocess.run(
                    ["aider", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().split()[-1]

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return None

        return None

    def get_install_path(self, tool: str) -> Optional[str]:
        """Get installation path for a tool"""
        try:
            result = subprocess.run(
                ["which", tool],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def check_for_updates(self, tool: str) -> Dict[str, any]:
        """Check if updates are available for a tool"""
        current_version = self.get_installed_version(tool)
        install_path = self.get_install_path(tool)

        result = {
            "tool": tool,
            "installed": current_version is not None,
            "current_version": current_version,
            "install_path": install_path,
            "update_available": False,
            "latest_version": None,
            "update_command": None
        }

        if not current_version:
            return result

        # Check for updates based on tool type
        try:
            if tool == "claude":
                # Check npm for updates
                npm_result = subprocess.run(
                    ["npm", "outdated", "-g", "@anthropic-ai/claude-code", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if npm_result.stdout:
                    outdated = json.loads(npm_result.stdout)
                    if "@anthropic-ai/claude-code" in outdated:
                        result["latest_version"] = outdated["@anthropic-ai/claude-code"]["latest"]
                        result["update_available"] = True
                        result["update_command"] = "npm update -g @anthropic-ai/claude-code"

            elif tool == "codex":
                # Check GitHub CLI extensions
                gh_result = subprocess.run(
                    ["gh", "extension", "list"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "copilot" in gh_result.stdout:
                    # Check for extension updates
                    update_result = subprocess.run(
                        ["gh", "extension", "upgrade", "--dry-run", "copilot"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if "already up to date" not in update_result.stdout.lower():
                        result["update_available"] = True
                        result["update_command"] = "gh extension upgrade copilot"

            elif tool == "gemini":
                # Check pip for updates
                pip_result = subprocess.run(
                    ["pip3", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if pip_result.returncode == 0:
                    outdated = json.loads(pip_result.stdout)
                    for package in outdated:
                        if package["name"] == "google-generativeai":
                            result["latest_version"] = package["latest_version"]
                            result["update_available"] = True
                            result["update_command"] = "pip3 install --upgrade google-generativeai"

            elif tool == "aider":
                pip_result = subprocess.run(
                    ["pip3", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if pip_result.returncode == 0:
                    outdated = json.loads(pip_result.stdout)
                    for package in outdated:
                        if package["name"] == "aider-chat":
                            result["latest_version"] = package["latest_version"]
                            result["update_available"] = True
                            result["update_command"] = "pip3 install --upgrade aider-chat"

        except Exception as e:
            result["error"] = str(e)

        return result

    def update_tool(self, tool: str, auto_confirm: bool = False) -> bool:
        """Update a specific tool"""
        update_info = self.check_for_updates(tool)

        if not update_info["update_available"]:
            print(f"✓ {tool} is already up to date ({update_info['current_version']})")
            return True

        print(f"🔄 Update available for {tool}:")
        print(f"   Current: {update_info['current_version']}")
        print(f"   Latest: {update_info['latest_version']}")
        print(f"   Command: {update_info['update_command']}")

        if not auto_confirm:
            response = input("   Update now? [Y/n]: ").strip().lower()
            if response and response != 'y':
                print("   Skipped")
                return False

        print(f"   Updating {tool}...")

        try:
            result = subprocess.run(
                update_info['update_command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                print(f"✓ {tool} updated successfully!")
                self.record_update(tool, update_info['current_version'], update_info['latest_version'])
                return True
            else:
                print(f"✗ Failed to update {tool}")
                print(f"   Error: {result.stderr}")
                return False

        except Exception as e:
            print(f"✗ Error updating {tool}: {e}")
            return False

    def record_update(self, tool: str, old_version: str, new_version: str):
        """Record update in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cli_versions (tool_name, version, install_path, last_check, update_available, latest_version, updated_at)
            VALUES (?, ?, ?, ?, 0, ?, ?)
            ON CONFLICT(tool_name) DO UPDATE SET
                version = excluded.version,
                last_check = excluded.last_check,
                update_available = 0,
                latest_version = excluded.latest_version,
                updated_at = excluded.updated_at
        """, (
            tool,
            new_version,
            self.get_install_path(tool),
            datetime.now().isoformat(),
            new_version,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def should_check_updates(self, tool: str) -> bool:
        """Check if we should check for updates (don't check too frequently)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT last_check FROM cli_versions
            WHERE tool_name = ?
        """, (tool,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return True

        last_check = datetime.fromisoformat(row[0])
        # Check at most once per day
        return datetime.now() - last_check > timedelta(hours=24)

    def check_all_tools(self, tools: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Check all tools for updates"""
        if tools is None:
            tools = ["claude", "codex", "gemini", "aider", "cursor"]

        results = {}

        for tool in tools:
            if self.should_check_updates(tool):
                print(f"Checking {tool}...")
                results[tool] = self.check_for_updates(tool)
            else:
                print(f"Skipping {tool} (checked recently)")
                results[tool] = {"skipped": True}

        return results

    def update_all_tools(self, tools: Optional[List[str]] = None, auto_confirm: bool = False):
        """Update all tools that have updates available"""
        if tools is None:
            tools = ["claude", "codex", "gemini", "aider"]

        print("🔍 Checking for updates...\n")

        for tool in tools:
            if self.should_check_updates(tool):
                self.update_tool(tool, auto_confirm)
                print()


def main():
    """CLI interface for auto-updater"""
    updater = CLIUpdater()

    if len(sys.argv) < 2:
        print("AI CLI Auto-Updater")
        print("\nUsage: auto_updater.py <command> [options]")
        print("\nCommands:")
        print("  check [tool...]        - Check for updates")
        print("  update [tool...]       - Update specific tool(s)")
        print("  update-all [-y]        - Update all tools (-y for auto-confirm)")
        print("  status                 - Show current versions")
        print("\nSupported tools: claude, codex, gemini, aider, cursor")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        tools = sys.argv[2:] if len(sys.argv) > 2 else None
        results = updater.check_all_tools(tools)

        print("\n📊 Update Status:")
        for tool, info in results.items():
            if info.get("skipped"):
                continue

            status = "✗" if not info["installed"] else "✓"
            print(f"\n{status} {tool}:")

            if info["installed"]:
                print(f"   Version: {info['current_version']}")
                if info["update_available"]:
                    print(f"   ⬆️  Update available: {info['latest_version']}")
                else:
                    print(f"   ✓ Up to date")
            else:
                print(f"   Not installed")

    elif command == "update":
        if len(sys.argv) < 3:
            print("Error: Please specify tool(s) to update")
            sys.exit(1)

        tools = sys.argv[2:]
        for tool in tools:
            updater.update_tool(tool)

    elif command == "update-all":
        auto_confirm = "-y" in sys.argv or "--yes" in sys.argv
        updater.update_all_tools(auto_confirm=auto_confirm)

    elif command == "status":
        tools = ["claude", "codex", "gemini", "aider", "cursor"]
        print("📋 Installed AI CLI Tools:\n")

        for tool in tools:
            version = updater.get_installed_version(tool)
            path = updater.get_install_path(tool)

            if version:
                print(f"✓ {tool:12} v{version}")
                print(f"  {path}")
            else:
                print(f"✗ {tool:12} Not installed")
            print()


if __name__ == "__main__":
    main()
