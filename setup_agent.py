"""
setup_agent.py — CLI helper to register, remove, and list AI agents.

Usage:
    python setup_agent.py list
    python setup_agent.py add   <AgentName> [--description "..."]
    python setup_agent.py remove <AgentName>
    python setup_agent.py init   (re-generate communication.md from config)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
COMM_FILE = os.path.join(BASE_DIR, "communication.md")
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.md")
INSTRUCTION_TEMPLATE = os.path.join(BASE_DIR, "instruction.md")


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {"check_interval": 300, "agents": []}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def agent_names(cfg: dict) -> list[str]:
    return [a["name"] for a in cfg.get("agents", [])]


def build_comm_md(cfg: dict) -> str:
    names = agent_names(cfg)
    rules = "\n".join(f"> - **{n}** writes ONLY in `## [{n}]`" for n in names)

    header = f"""# AI Collaboration Communication Log

> **Rules:**
{rules}
> - All agents log completed tasks in `## [Work Log]`
> - Questions for the user go in `questions.md`
> - Format: `[YYYY-MM-DD HH:MM] message`
> - Prefix urgent messages with `[URGENT]`

---

## [Work Log]
> Shared task progress — all agents write here

<!-- WORK LOG START -->

<!-- WORK LOG END -->

---
"""

    sections = []
    for name in names:
        tag = name.upper().replace(" ", "_")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        sections.append(
            f"## [{name}]\n"
            f"> {name} writes here — status updates, blockers, notes to other agents\n\n"
            f"<!-- {tag} START -->\n\n"
            f"[{ts}] Communication channel established. Ready to collaborate.\n\n"
            f"<!-- {tag} END -->\n"
        )

    return header + "\n---\n\n".join(sections)


def init_comm_md(cfg: dict) -> None:
    if not os.path.exists(COMM_FILE):
        content = build_comm_md(cfg)
        with open(COMM_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created {COMM_FILE}")
        return

    with open(COMM_FILE, "r", encoding="utf-8") as f:
        existing = f.read()

    additions = []
    for name in agent_names(cfg):
        if f"## [{name}]" not in existing:
            tag = name.upper().replace(" ", "_")
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            additions.append(
                f"\n---\n\n"
                f"## [{name}]\n"
                f"> {name} writes here — status updates, blockers, notes to other agents\n\n"
                f"<!-- {tag} START -->\n\n"
                f"[{ts}] Communication channel established. Ready to collaborate.\n\n"
                f"<!-- {tag} END -->\n"
            )

    if additions:
        with open(COMM_FILE, "a", encoding="utf-8") as f:
            f.write("".join(additions))
        print(f"Added {len(additions)} new section(s) to {COMM_FILE}")
    else:
        print("communication.md already has sections for all registered agents.")


def remove_comm_section(name: str) -> None:
    if not os.path.exists(COMM_FILE):
        return
    with open(COMM_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"\n---\n\n## \[" + re.escape(name) + r"\].*?<!-- " + re.escape(name.upper().replace(" ", "_")) + r" END -->\n"
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)

    if new_content != content:
        with open(COMM_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Removed [{name}] section from communication.md")


def init_questions_md() -> None:
    if not os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            f.write("# Questions for the User\n\n"
                    "> Agents post questions here. User replies with `[Reply]` below each one.\n"
                    "> Format: `[YYYY-MM-DD HH:MM] [AgentName] question?`\n\n")
        print(f"Created {QUESTIONS_FILE}")


def cmd_list(cfg: dict) -> None:
    agents = cfg.get("agents", [])
    if not agents:
        print("No agents registered.")
        return
    print(f"{'Name':<20} Description")
    print("-" * 60)
    for a in agents:
        print(f"{a['name']:<20} {a.get('description', '')}")


def cmd_add(cfg: dict, name: str, description: str) -> None:
    if any(a["name"].lower() == name.lower() for a in cfg.get("agents", [])):
        print(f"Agent '{name}' already registered.")
        sys.exit(1)
    cfg.setdefault("agents", []).append({"name": name, "description": description})
    save_config(cfg)
    print(f"Registered agent: {name}")
    init_comm_md(cfg)
    _print_instruction_hint(name)


def cmd_remove(cfg: dict, name: str) -> None:
    before = len(cfg.get("agents", []))
    cfg["agents"] = [a for a in cfg.get("agents", []) if a["name"].lower() != name.lower()]
    if len(cfg["agents"]) == before:
        print(f"Agent '{name}' not found.")
        sys.exit(1)
    save_config(cfg)
    remove_comm_section(name)
    print(f"Removed agent: {name}")


def cmd_init(cfg: dict) -> None:
    init_comm_md(cfg)
    init_questions_md()
    print("Initialization complete.")


def _print_instruction_hint(name: str) -> None:
    print(f"\nTip: generate instruction for '{name}' with:")
    print(f"  python setup_agent.py init")
    print(f"Then share instruction.md with {name} at session start.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage AI agents for the communication tool.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List registered agents")

    p_add = sub.add_parser("add", help="Register a new agent")
    p_add.add_argument("name", help="Agent name (e.g. Claude, Gemini)")
    p_add.add_argument("--description", default="", help="Short description")

    p_rm = sub.add_parser("remove", help="Remove an agent")
    p_rm.add_argument("name", help="Agent name to remove")

    sub.add_parser("init", help="Re-generate communication.md and questions.md from config")

    args = parser.parse_args()
    cfg = load_config()

    if args.command == "list":
        cmd_list(cfg)
    elif args.command == "add":
        cmd_add(cfg, args.name, args.description)
    elif args.command == "remove":
        cmd_remove(cfg, args.name)
    elif args.command == "init":
        cmd_init(cfg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
