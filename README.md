# Agent-Communication-Tool
With this file, your local CLI agent (claude code, kimi code) will be able to communicate with each other. 


  AgentCommunicationTool

  A multi-AI collaboration framework that enables two AI agents (Claude Code and Kimi Code) to work together on the same
   project asynchronously.

  Core Concept

  Agents communicate via monitored markdown files. A background daemon sends Windows notifications every 5 minutes
  reminding both AIs to check for updates.

  File Structure

  ┌──────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────┐
  │       File       │                                            Purpose                                            │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ communication.md │ Shared hub with sections [Work Log], [Claude], [Kimi] — each AI writes only in their own      │
  │                  │ section                                                                                       │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ questions.md     │ AIs post questions here; user replies directly below each one                                 │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ monitor.py       │ Background Python daemon that polls files and sends native Windows toast notifications        │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ instruction.md   │ Workflow guide for Kimi Code explaining the rules and protocol                                │
  └──────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────┘

  How It Works

  1. User runs pythonw monitor.py once to start the daemon
  2. Every 5 minutes, a Windows notification fires: "AI Collab — Check Files"
  3. If files changed, the notification includes what changed; otherwise it's a routine reminder
  4. Both AIs check the files, log completed tasks to [Work Log], and leave timestamped messages for each other
  5. AIs post questions to questions.md; user replies inline

  Tech Stack

  - Python 3 — monitoring loop, MD5 file change detection, subprocess calls
  - PowerShell + .NET (System.Windows.Forms.NotifyIcon) — native Windows toast notifications
  - Markdown — all communication and documentation

  Key Design Choice

  No server, no database, no API — just text files, timestamps, and periodic polling. Lightweight and easy to inspect.
