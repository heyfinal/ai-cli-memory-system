#!/usr/bin/env python3
"""
AI CLI Memory Cloud Sync
Sync your memory across machines using AWS S3, Google Drive, or Dropbox
"""

import os
import sys
import json
import sqlite3
import hashlib
import boto3
from datetime import datetime
from pathlib import Path
import subprocess

class CloudSync:
    def __init__(self, db_path=None, sync_method='s3'):
        if db_path is None:
            db_path = os.path.expanduser("~/.claude/memory/context.db")

        self.db_path = db_path
        self.sync_method = sync_method
        self.config_path = os.path.expanduser("~/.claude/memory/sync_config.json")
        self.load_config()

    def load_config(self):
        """Load sync configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "sync_enabled": False,
                "sync_method": "s3",
                "s3_bucket": None,
                "s3_key": "ai-cli-memory/context.db",
                "machine_id": self.get_machine_id(),
                "last_sync": None
            }
            self.save_config()

    def save_config(self):
        """Save sync configuration"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_machine_id(self):
        """Get unique machine identifier"""
        import socket
        hostname = socket.gethostname()
        machine_id = hashlib.md5(hostname.encode()).hexdigest()[:8]
        return f"{hostname}_{machine_id}"

    def get_db_checksum(self):
        """Calculate database checksum"""
        if not os.path.exists(self.db_path):
            return None

        hasher = hashlib.sha256()
        with open(self.db_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def backup_db(self):
        """Create local backup before sync"""
        backup_dir = os.path.expanduser("~/.claude/memory/backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"context_{timestamp}.db")

        import shutil
        shutil.copy2(self.db_path, backup_path)

        print(f"✓ Backup created: {backup_path}")
        return backup_path

    # ===== S3 Sync Methods =====

    def upload_to_s3(self):
        """Upload database to S3"""
        if not self.config.get('s3_bucket'):
            print("Error: S3 bucket not configured")
            return False

        try:
            s3 = boto3.client('s3')

            # Create metadata
            metadata = {
                'machine_id': self.config['machine_id'],
                'sync_time': datetime.now().isoformat(),
                'checksum': self.get_db_checksum()
            }

            # Upload with metadata
            s3.upload_file(
                self.db_path,
                self.config['s3_bucket'],
                self.config['s3_key'],
                ExtraArgs={'Metadata': metadata}
            )

            self.config['last_sync'] = datetime.now().isoformat()
            self.save_config()

            print(f"✓ Uploaded to s3://{self.config['s3_bucket']}/{self.config['s3_key']}")
            return True

        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False

    def download_from_s3(self):
        """Download database from S3"""
        if not self.config.get('s3_bucket'):
            print("Error: S3 bucket not configured")
            return False

        try:
            s3 = boto3.client('s3')

            # Check if file exists
            try:
                s3.head_object(Bucket=self.config['s3_bucket'], Key=self.config['s3_key'])
            except:
                print("No backup found in S3")
                return False

            # Backup local DB first
            if os.path.exists(self.db_path):
                self.backup_db()

            # Download
            temp_path = self.db_path + ".download"
            s3.download_file(
                self.config['s3_bucket'],
                self.config['s3_key'],
                temp_path
            )

            # Replace local DB
            import shutil
            shutil.move(temp_path, self.db_path)

            self.config['last_sync'] = datetime.now().isoformat()
            self.save_config()

            print(f"✓ Downloaded from s3://{self.config['s3_bucket']}/{self.config['s3_key']}")
            return True

        except Exception as e:
            print(f"Error downloading from S3: {e}")
            return False

    # ===== Dropbox Sync Methods =====

    def upload_to_dropbox(self):
        """Upload database to Dropbox"""
        dropbox_path = os.path.expanduser("~/Dropbox/AI-CLI-Memory/context.db")
        os.makedirs(os.path.dirname(dropbox_path), exist_ok=True)

        import shutil
        shutil.copy2(self.db_path, dropbox_path)

        self.config['last_sync'] = datetime.now().isoformat()
        self.save_config()

        print(f"✓ Uploaded to Dropbox: {dropbox_path}")
        return True

    def download_from_dropbox(self):
        """Download database from Dropbox"""
        dropbox_path = os.path.expanduser("~/Dropbox/AI-CLI-Memory/context.db")

        if not os.path.exists(dropbox_path):
            print("No backup found in Dropbox")
            return False

        # Backup local DB first
        if os.path.exists(self.db_path):
            self.backup_db()

        import shutil
        shutil.copy2(dropbox_path, self.db_path)

        self.config['last_sync'] = datetime.now().isoformat()
        self.save_config()

        print(f"✓ Downloaded from Dropbox: {dropbox_path}")
        return True

    # ===== Git Sync Methods =====

    def init_git_sync(self):
        """Initialize git repository for syncing"""
        sync_dir = os.path.expanduser("~/.claude/memory/sync")
        os.makedirs(sync_dir, exist_ok=True)

        if not os.path.exists(os.path.join(sync_dir, '.git')):
            subprocess.run(['git', 'init'], cwd=sync_dir)
            print(f"✓ Initialized git repository at {sync_dir}")

        return sync_dir

    def upload_to_git(self):
        """Commit and push to git"""
        sync_dir = self.init_git_sync()

        # Copy database to sync directory
        import shutil
        shutil.copy2(self.db_path, os.path.join(sync_dir, 'context.db'))

        # Commit
        subprocess.run(['git', 'add', 'context.db'], cwd=sync_dir)
        commit_msg = f"Sync from {self.config['machine_id']} at {datetime.now().isoformat()}"
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=sync_dir)

        # Push (requires remote to be configured)
        result = subprocess.run(['git', 'push'], cwd=sync_dir, capture_output=True)

        if result.returncode == 0:
            self.config['last_sync'] = datetime.now().isoformat()
            self.save_config()
            print("✓ Pushed to git remote")
            return True
        else:
            print("Error pushing to git:", result.stderr.decode())
            return False

    # ===== Main Sync Methods =====

    def push(self):
        """Push local database to cloud"""
        print(f"📤 Pushing to {self.sync_method}...")

        if self.sync_method == 's3':
            return self.upload_to_s3()
        elif self.sync_method == 'dropbox':
            return self.upload_to_dropbox()
        elif self.sync_method == 'git':
            return self.upload_to_git()
        else:
            print(f"Unknown sync method: {self.sync_method}")
            return False

    def pull(self):
        """Pull database from cloud"""
        print(f"📥 Pulling from {self.sync_method}...")

        if self.sync_method == 's3':
            return self.download_from_s3()
        elif self.sync_method == 'dropbox':
            return self.download_from_dropbox()
        else:
            print(f"Unknown sync method: {self.sync_method}")
            return False

    def sync(self):
        """Smart sync: merge local and remote"""
        print("🔄 Syncing...")

        # For now, just do pull then push
        # TODO: Implement proper merge strategy
        self.pull()
        self.push()

    def status(self):
        """Show sync status"""
        print("📊 Sync Status:")
        print(f"  Enabled: {self.config.get('sync_enabled', False)}")
        print(f"  Method: {self.config.get('sync_method', 'none')}")
        print(f"  Machine ID: {self.config.get('machine_id')}")
        print(f"  Last Sync: {self.config.get('last_sync', 'Never')}")
        print(f"  Local DB: {self.db_path}")
        print(f"  Checksum: {self.get_db_checksum()}")

    def configure(self, method, **kwargs):
        """Configure sync settings"""
        self.config['sync_method'] = method

        if method == 's3':
            self.config['s3_bucket'] = kwargs.get('bucket')
            self.config['s3_key'] = kwargs.get('key', 'ai-cli-memory/context.db')

        self.config['sync_enabled'] = True
        self.save_config()

        print(f"✓ Configured {method} sync")


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("AI CLI Memory Cloud Sync")
        print("\nUsage: cloud_sync.py <command> [options]")
        print("\nCommands:")
        print("  status              - Show sync status")
        print("  push                - Push local DB to cloud")
        print("  pull                - Pull DB from cloud")
        print("  sync                - Smart sync (pull + push)")
        print("  configure <method>  - Configure sync method")
        print("                        Methods: s3, dropbox, git")
        print("\nExamples:")
        print("  # Configure S3 sync")
        print("  cloud_sync.py configure s3 --bucket my-bucket")
        print("")
        print("  # Push to cloud")
        print("  cloud_sync.py push")
        print("")
        print("  # Pull from cloud")
        print("  cloud_sync.py pull")
        sys.exit(1)

    syncer = CloudSync()
    command = sys.argv[1]

    if command == 'status':
        syncer.status()

    elif command == 'push':
        syncer.push()

    elif command == 'pull':
        syncer.pull()

    elif command == 'sync':
        syncer.sync()

    elif command == 'configure':
        if len(sys.argv) < 3:
            print("Error: Please specify sync method (s3, dropbox, git)")
            sys.exit(1)

        method = sys.argv[2]

        if method == 's3':
            # Parse --bucket argument
            bucket = None
            for i, arg in enumerate(sys.argv):
                if arg == '--bucket' and i + 1 < len(sys.argv):
                    bucket = sys.argv[i + 1]

            if not bucket:
                print("Error: Please specify S3 bucket with --bucket")
                sys.exit(1)

            syncer.configure('s3', bucket=bucket)

        elif method == 'dropbox':
            syncer.configure('dropbox')

        elif method == 'git':
            syncer.configure('git')

        else:
            print(f"Unknown method: {method}")
            sys.exit(1)

    elif command == 'backup':
        syncer.backup_db()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
