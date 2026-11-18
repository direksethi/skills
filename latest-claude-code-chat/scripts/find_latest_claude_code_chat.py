#!/usr/bin/env python3
"""Find and summarize the latest local Claude Code JSONL transcript."""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path.home() / ".claude" / "projects"


def iso_from_mtime(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds")


def clip(text: str, limit: int = 900) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def content_to_text(content: Any, limit: int = 900) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return clip(content, limit)
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                parts.append(clip(str(item), limit))
                continue
            kind = item.get("type")
            if kind == "text":
                parts.append(str(item.get("text", "")))
            elif kind == "tool_use":
                name = item.get("name", "tool")
                tool_input = item.get("input", {})
                if isinstance(tool_input, dict):
                    command = tool_input.get("command") or tool_input.get("description") or ""
                    parts.append(f"[tool_use: {name} {clip(command, 180)}]".strip())
                else:
                    parts.append(f"[tool_use: {name}]")
            elif kind == "tool_result":
                result = item.get("content", "")
                parts.append(f"[tool_result: {clip(str(result), 260)}]")
            elif kind == "image":
                parts.append("[image]")
            elif kind == "thinking":
                continue
            else:
                parts.append(f"[{kind or 'content'}]")
        return clip("\n".join(part for part in parts if part), limit)
    return clip(str(content), limit)


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    line_count = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line_count += 1
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"type": "parse-error", "raw": line[:500]})
    return rows, line_count


def find_latest(root: Path) -> Path | None:
    candidates = [Path(p) for p in glob.glob(str(root / "**" / "*.jsonl"), recursive=True)]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def summarize(path: Path, limit: int) -> dict[str, Any]:
    rows, line_count = parse_jsonl(path)
    session_id = None
    cwd = None
    last_timestamp = None
    turns: list[dict[str, str]] = []

    for row in rows:
        session_id = row.get("sessionId") or session_id
        cwd = row.get("cwd") or cwd
        last_timestamp = row.get("timestamp") or last_timestamp

        msg = row.get("message")
        if not isinstance(msg, dict):
            continue
        role = msg.get("role") or row.get("type") or "message"
        text = content_to_text(msg.get("content"))
        if not text:
            continue
        turns.append(
            {
                "timestamp": str(row.get("timestamp") or ""),
                "role": str(role),
                "text": text,
            }
        )

    project = cwd
    resume_command = None
    if session_id and project:
        resume_command = f"cd {project}\nclaude --resume {session_id}"
    elif session_id:
        resume_command = f"claude --resume {session_id}"

    return {
        "transcript_path": str(path),
        "session_id": session_id,
        "project": project,
        "modified_time": iso_from_mtime(path),
        "size_bytes": path.stat().st_size,
        "line_count": line_count,
        "latest_timestamp": last_timestamp,
        "resume_command": resume_command,
        "recent_turns": turns[-limit:],
    }


def print_human(summary: dict[str, Any]) -> None:
    print(f"Transcript: {summary['transcript_path']}")
    print(f"Session ID: {summary.get('session_id') or '(unknown)'}")
    print(f"Project: {summary.get('project') or '(unknown)'}")
    print(f"Modified: {summary['modified_time']}")
    print(f"Lines: {summary['line_count']}")
    print(f"Size: {summary['size_bytes']} bytes")
    print(f"Latest timestamp: {summary.get('latest_timestamp') or '(unknown)'}")
    if summary.get("resume_command"):
        print("\nResume command:")
        print(summary["resume_command"])

    print("\nRecent turns:")
    for turn in summary["recent_turns"]:
        timestamp = turn.get("timestamp") or "no timestamp"
        role = turn.get("role") or "message"
        print(f"\n[{timestamp}] {role}")
        print(turn.get("text") or "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Claude Code projects directory")
    parser.add_argument("--limit", type=int, default=14, help="Number of recent text turns to print")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human-readable text")
    args = parser.parse_args()

    root = Path(os.path.expanduser(args.root))
    latest = find_latest(root)
    if latest is None:
        message = {"error": f"No Claude Code transcripts found under {root}"}
        if args.json:
            print(json.dumps(message, indent=2))
        else:
            print(message["error"])
        return 1

    summary = summarize(latest, max(args.limit, 1))
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_human(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
