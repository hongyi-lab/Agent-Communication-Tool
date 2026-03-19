"""
monitor.py — Every 5 minutes, sends a Windows notification reminding
Claude Code and Kimi Code to check communication.md and questions.md.

Run once in the background:
    pythonw monitor.py        # silent background (no console window)
    python monitor.py         # foreground with log output

Stop: close the console window, or kill the process.
"""

import time
import subprocess
import os
import hashlib
from datetime import datetime

CHECK_INTERVAL = 300  # seconds (5 minutes)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMM_FILE = os.path.join(BASE_DIR, "communication.md")
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.md")


def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def send_windows_notification(title, message):
    """Send a Windows toast notification via PowerShell."""
    ps = f"""
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$balloon.BalloonTipTitle = '{title}'
$balloon.BalloonTipText = '{message}'
$balloon.Visible = $true
$balloon.ShowBalloonTip(8000)
Start-Sleep -Seconds 9
$balloon.Dispose()
"""
    subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    log("Monitor started. Checking every 5 minutes.")
    log(f"Watching: {COMM_FILE}")
    log(f"Watching: {QUESTIONS_FILE}")

    prev_comm_hash = file_hash(COMM_FILE)
    prev_q_hash = file_hash(QUESTIONS_FILE)

    while True:
        time.sleep(CHECK_INTERVAL)

        curr_comm_hash = file_hash(COMM_FILE)
        curr_q_hash = file_hash(QUESTIONS_FILE)

        changed_files = []
        if curr_comm_hash != prev_comm_hash:
            changed_files.append("communication.md updated")
            prev_comm_hash = curr_comm_hash
        if curr_q_hash != prev_q_hash:
            changed_files.append("questions.md updated")
            prev_q_hash = curr_q_hash

        if changed_files:
            detail = " | ".join(changed_files)
            msg = f"Changes detected: {detail}"
            log(f"CHANGED — {msg}")
        else:
            msg = "No changes — routine check-in reminder"
            log("No changes — sending routine reminder")

        send_windows_notification(
            title="AI Collab — Check Files",
            message=f"{msg}\nOpen communication.md or questions.md"
        )


if __name__ == "__main__":
    main()
