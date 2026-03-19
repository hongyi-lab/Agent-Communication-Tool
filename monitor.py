"""
monitor.py — Periodically reminds all registered AI agents to check shared
communication files. Supports macOS, Linux, and Windows.

Run once in the background:
    macOS/Linux:  python monitor.py &
    Windows:      pythonw monitor.py          (silent, no console window)
                  python monitor.py           (foreground with log output)

Stop: Ctrl+C or kill the process.
"""

import json
import os
import platform
import subprocess
import sys
import hashlib
import time
from datetime import datetime


CHECK_INTERVAL = 300  # seconds (5 minutes)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
COMM_FILE = os.path.join(BASE_DIR, "communication.md")
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.md")

SYSTEM = platform.system()  # 'Darwin', 'Linux', 'Windows'


def send_notification(title: str, message: str) -> None:
    if SYSTEM == "Darwin":
        _notify_macos(title, message)
    elif SYSTEM == "Linux":
        _notify_linux(title, message)
    elif SYSTEM == "Windows":
        _notify_windows(title, message)
    else:
        log(f"[NOTIFY] {title}: {message}")


def _notify_macos(title: str, message: str) -> None:
    script = (
        f'display notification "{_esc(message)}" '
        f'with title "{_esc(title)}"'
    )
    try:
        subprocess.Popen(
            ["osascript", "-e", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        log(f"[NOTIFY] osascript not found. {title}: {message}")


def _notify_linux(title: str, message: str) -> None:
    try:
        subprocess.Popen(
            ["notify-send", "--urgency=normal", "--expire-time=8000", title, message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        log(f"[NOTIFY] notify-send not found. {title}: {message}")


def _notify_windows(title: str, message: str) -> None:
    ps = f"""
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$balloon.BalloonTipTitle = '{_esc(title)}'
$balloon.BalloonTipText = '{_esc(message)}'
$balloon.Visible = $true
$balloon.ShowBalloonTip(8000)
Start-Sleep -Seconds 9
$balloon.Dispose()
"""
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
            creationflags=flags,
        )
    except FileNotFoundError:
        log(f"[NOTIFY] powershell not found. {title}: {message}")


def _esc(s: str) -> str:
    return s.replace("'", "\\'")


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {"agents": [], "check_interval": CHECK_INTERVAL}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def file_hash(path: str) -> str | None:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> None:
    config = load_config()
    interval = config.get("check_interval", CHECK_INTERVAL)
    agents = config.get("agents", [])
    agent_names = [a["name"] for a in agents] if agents else ["All agents"]

    log(f"Monitor started on {SYSTEM}. Checking every {interval}s.")
    log(f"Registered agents: {', '.join(agent_names)}")
    log(f"Watching: {COMM_FILE}")
    log(f"Watching: {QUESTIONS_FILE}")

    prev_hashes = {
        COMM_FILE: file_hash(COMM_FILE),
        QUESTIONS_FILE: file_hash(QUESTIONS_FILE),
    }

    while True:
        config = load_config()
        interval = config.get("check_interval", CHECK_INTERVAL)

        time.sleep(interval)

        changed_files = []
        for path, label in [(COMM_FILE, "communication.md"), (QUESTIONS_FILE, "questions.md")]:
            curr = file_hash(path)
            if curr != prev_hashes[path]:
                changed_files.append(f"{label} updated")
                prev_hashes[path] = curr

        if changed_files:
            detail = " | ".join(changed_files)
            msg = f"Changes detected: {detail}\nOpen the files to review."
            log(f"CHANGED — {detail}")
        else:
            msg = "No changes — routine check-in reminder.\nOpen communication.md or questions.md"
            log("No changes — sending routine reminder")

        send_notification(title="AI Collab — Check Files", message=msg)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Monitor stopped.")
        sys.exit(0)
