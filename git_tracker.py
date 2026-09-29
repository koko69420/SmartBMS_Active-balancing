#!/usr/bin/env python3
"""
KiCad-Aware Automated Git Save Tracker
--------------------------------------
Monitors the repository for explicit user saves to schematic, PCB, and project files.
Strictly ignores KiCad autosaves, lock files, and backup archives.
Debounces multi-sheet saves and automatically commits and pushes to GitHub.
"""

import os
import sys
import time
import datetime
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Debounce delay in seconds (waits for all files in a multi-sheet save to finish writing)
DEBOUNCE_DELAY = 2.5

# File extensions and patterns to strictly ignore
IGNORE_PATTERNS = [
    ".git",
    "_autosave",
    ".autosave",
    ".lck",
    ".bak",
    "-bak",
    "-backups",
    "fp-info-cache",
    ".kicad_prl",
    "tracker.log",
    "tracker.pid",
    "__pycache__",
    ".~lock.",
    "#auto_saved_files#",
    ".tmp",
]

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted, flush=True)
    try:
        with open("tracker.log", "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def is_ignored(path_str):
    p = str(path_str).lower()
    for pat in IGNORE_PATTERNS:
        if pat.lower() in p:
            return True
    filename = os.path.basename(path_str)
    if filename.startswith("~") or filename.startswith("#") or filename.startswith("._"):
        return True
    return False


class GitCommitWorker:
    def __init__(self, repo_dir):
        self.repo_dir = Path(repo_dir).resolve()
        self.timer = None
        self.lock = threading.Lock()
        self.pending_files = set()

    def schedule_commit(self, changed_path):
        rel_path = os.path.relpath(changed_path, self.repo_dir)
        with self.lock:
            self.pending_files.add(rel_path)
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(DEBOUNCE_DELAY, self._execute_git_sync)
            self.timer.daemon = True
            self.timer.start()

    def _execute_git_sync(self):
        with self.lock:
            files_to_sync = list(self.pending_files)
            self.pending_files.clear()
            self.timer = None

        try:
            # 1. Check git status
            status_res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=15,
            )
            changes = status_res.stdout.strip()
            if not changes:
                # No actual git changes (e.g. file touched with same content)
                return

            changed_lines = changes.splitlines()
            short_names = []
            for line in changed_lines:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    short_names.append(os.path.basename(parts[1]))

            # 2. Stage changes (respects .gitignore)
            subprocess.run(["git", "add", "-A"], cwd=self.repo_dir, check=True, timeout=30)

            # 3. Create descriptive commit message
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if len(short_names) == 1:
                commit_msg = f"Save: update {short_names[0]} ({now_str})"
            elif 1 < len(short_names) <= 3:
                commit_msg = f"Save: update {', '.join(short_names)} ({now_str})"
            else:
                commit_msg = f"Save: update {len(short_names)} project files ({now_str})"

            commit_res = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=20,
            )

            if commit_res.returncode == 0:
                log(f"Committed: {commit_msg}")
            else:
                if "nothing to commit" in commit_res.stdout:
                    return
                log(f"Commit note: {commit_res.stdout.strip() or commit_res.stderr.strip()}")

            # 4. Push to remote
            push_res = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=45,
            )
            if push_res.returncode == 0:
                log("Pushed successfully to remote origin/main.")
            else:
                err = push_res.stderr.strip() or push_res.stdout.strip()
                log(f"Warning: git push returned code {push_res.returncode}: {err}")

        except Exception as e:
            log(f"Error during git sync: {e}")


class KiCadChangeHandler(FileSystemEventHandler):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker

    def on_modified(self, event):
        if event.is_directory or is_ignored(event.src_path):
            return
        log(f"Detected save on: {os.path.basename(event.src_path)}")
        self.worker.schedule_commit(event.src_path)

    def on_created(self, event):
        if event.is_directory or is_ignored(event.src_path):
            return
        log(f"Detected new file: {os.path.basename(event.src_path)}")
        self.worker.schedule_commit(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or is_ignored(event.src_path):
            return
        log(f"Detected file deletion: {os.path.basename(event.src_path)}")
        self.worker.schedule_commit(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        if not is_ignored(event.dest_path):
            log(f"Detected file move to: {os.path.basename(event.dest_path)}")
            self.worker.schedule_commit(event.dest_path)


def main():
    repo_path = Path(__file__).resolve().parent
    log(f"Starting SmartBMS Git Save Tracker in: {repo_path}")
    log("Ignoring autosaves, lock files, and backups.")
    log("Watching for manual saves...")

    worker = GitCommitWorker(repo_path)
    handler = KiCadChangeHandler(worker)
    observer = Observer()
    observer.schedule(handler, str(repo_path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Stopping Git Save Tracker...")
        observer.stop()
    observer.join()
    log("Tracker stopped.")


if __name__ == "__main__":
    main()
