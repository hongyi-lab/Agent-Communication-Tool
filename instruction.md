# Collaboration Workflow Instruction

> **Fill in before sharing:** Replace `{AGENT_NAME}` with this agent's actual name (e.g. Claude, Kimi, Gemini).

You are **{AGENT_NAME}**, working alongside other AI agents on the same project.
This document tells you everything you need to know to collaborate correctly.

---

## File Overview

| File | Purpose |
|------|---------|
| `communication.md` | Main channel between all agents |
| `questions.md` | Questions for the human user |
| `monitor.py` | Background script — sends reminders every 5 min |
| `config.json` | Registered agents and check interval |

---

## Your Writing Rules

**You may ONLY write inside the `## [{AGENT_NAME}]` section of `communication.md`.**

- Do not edit any other agent's section.
- You MAY append to `## [Work Log]` when completing a task.
- Always prefix your messages with a timestamp:

