# Collaboration Workflow Instruction

You are Kimi Code, working alongside Claude Code on the same project.
This document tells you everything you need to know to collaborate correctly.

---

## File Overview

| File | Purpose |
|------|---------|
| `communication.md` | Main channel between you and Claude |
| `questions.md` | Questions for the human user |
| `monitor.py` | Background script — sends reminders every 5 min |

---

## Your Writing Rules

**You (Kimi) may ONLY write inside the `## [Kimi]` section of `communication.md`.**
Do not edit Claude's section. Do not edit the Work Log section directly unless logging a completed task.

When you write, always prefix with a timestamp:
```
[YYYY-MM-DD HH:MM] your message here
```

---

## Check-in Protocol

1. **At the start of every session** — read `communication.md` and `questions.md` in full.
2. **Every 5 minutes** — a Windows notification will appear reminding you to check. When it does, re-read both files before continuing work.
3. **After completing any task** — append a line to `## [Work Log]` in `communication.md`.
4. **If you have a question for the user** — append it to `questions.md`. Do not ask the user directly before checking if the question is already answered there.

---

## How to Communicate with Claude

- Write your message in `## [Kimi]` section of `communication.md`
- Claude will see it on the next check-in (within 5 minutes)
- If it's urgent, prefix your message with `[URGENT]`

---

## How to Ask the User a Question

Append to `questions.md`:
```
[YYYY-MM-DD HH:MM] [Kimi] Your question here?
```
Then wait. The user will reply below your question with `[Reply]`.

---

## Work Log Format

When you finish a task, append to `## [Work Log]`:
```
[YYYY-MM-DD HH:MM] [Kimi] Brief description of what was done
```

---

## Starting the Monitor (if not already running)

```bash
pythonw monitor.py
```

Run this once. It will send Windows notifications every 5 minutes.

---

## Summary

- Read `communication.md` → write in `## [Kimi]` only
- Read `questions.md` → append questions, check for replies
- Log finished work in `## [Work Log]`
- Check both files every 5 minutes when notified
