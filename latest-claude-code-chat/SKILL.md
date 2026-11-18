---
name: latest-claude-code-chat
description: Find and summarize the latest local Claude Code conversation transcript. Use when the user asks for their latest Claude Code chat, Claude Code thread, Claude Code transcript, Claude session, where Claude Code stopped, what to resume after hitting limits, or asks Codex to continue work from a Claude Code conversation.
---

# Latest Claude Code Chat

## Workflow

Use the bundled script first. Paths below are relative to this skill's folder (the directory that holds this SKILL.md), so run them from there or prefix them with that folder's path:

```bash
python3 scripts/find_latest_claude_code_chat.py --limit 14
```

The script searches `~/.claude/projects/**/*.jsonl`, picks the most recently modified transcript, and prints:

- transcript path
- session ID
- project/cwd
- modified time
- line count
- latest known timestamp
- `claude --resume ...` command when enough data exists
- recent user/assistant turns with large images, thinking blocks, and tool blobs summarized

If the user asks for more context, rerun with a larger limit:

```bash
python3 scripts/find_latest_claude_code_chat.py --limit 30
```

If the user asks for machine-readable output:

```bash
python3 scripts/find_latest_claude_code_chat.py --limit 20 --json
```

## Response Pattern

Report the latest thread plainly:

- link the transcript path
- state project/cwd, session ID, modified time, line count, and last visible message
- include the resume command:

```bash
cd <project>
claude --resume <session-id>
```

Then summarize the handoff point: what Claude Code was doing, what edits or commands had just completed, and what remained unfinished.

If the user wants Codex to continue the work, inspect the project files and git state before editing. Treat the transcript as context, not as the source of truth for current files.

## Safety

Claude transcripts can contain private text, pasted content, images, command output, and secrets. Read the minimum needed. Do not dump entire transcripts into chat unless the user explicitly asks. Prefer summaries and exact file/session references.

Never edit or delete Claude Code transcript files. They are evidence/history.
