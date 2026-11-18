# Agent skills

Skills that Direk Sethi uses daily with Claude Code and Codex. Each folder is a self-contained `SKILL.md` package: instructions the agent loads when a task matches, plus any scripts the instructions call.

## Skills

| Skill | What it does |
| :--- | :--- |
| [product-copy](product-copy/SKILL.md) | Writes and reviews interface copy in the plain, short, calm register of Linear, Notion and Apple. |
| [dev-handoff](dev-handoff/SKILL.md) | Writes a session snapshot into the current repo and commits it, so a fresh agent session can resume the work. |
| [latest-claude-code-chat](latest-claude-code-chat/SKILL.md) | Finds the newest local Claude Code transcript and summarises where it stopped. |
| [steel-browser](steel-browser/SKILL.md) | Drives a self-hosted Steel Browser through the agent-browser CLI, with a hand-off to a human for logins, 2FA and captchas. |
| [slack-reply-drafts](slack-reply-drafts/SKILL.md) | Drafts Slack replies in your own writing style, with a separate learned profile per conversation. Read-only: it never sends. |

## Install

Copy the folder of the skill you want into your agent's skills directory:

```bash
git clone https://github.com/direksethi/skills.git
cp -r skills/product-copy ~/.claude/skills/      # Claude Code
cp -r skills/product-copy ~/.agents/skills/      # Codex and other agents that read ~/.agents/skills
```

Or use the [skills CLI](https://github.com/vercel-labs/skills), which accepts a GitHub `owner/repo`:

```bash
npx skills add direksethi/skills
```

Keep each folder intact: the instructions refer to scripts by paths relative to the skill folder.

## Requirements

| Skill | Needs |
| :--- | :--- |
| product-copy | Nothing. |
| dev-handoff | `git`, run from inside a repository. Invoked explicitly, not automatically. |
| latest-claude-code-chat | Python 3.9 or later. Reads transcripts under `~/.claude/projects`. |
| steel-browser | A running [Steel Browser](https://github.com/steel-dev/steel-browser) instance, the [agent-browser](https://github.com/vercel-labs/agent-browser) CLI, `bash`, and `STEEL_CDP` set to the instance's CDP endpoint. |
| slack-reply-drafts | Python 3.9 or later on Linux or macOS, `bash`, `curl`, and a Slack user token in `SLACK_USER_TOKEN` with read scopes only. |

### slack-reply-drafts configuration

Slack user token scopes: `channels:read`, `groups:read`, `im:read`, `mpim:read`, `channels:history`, `groups:history`, `im:history`, `mpim:history`, `users:read`. Add no write scopes.

The workspace id, user id, data directory and permalink host come from `~/.config/slack-reply-drafts/config.json` or from environment variables (`SLACK_TEAM_ID`, `SLACK_USER_ID`, `SLACK_REPLY_DRAFTS_DIR`, `SLACK_WORKSPACE_URL`). See [examples/config.example.json](slack-reply-drafts/examples/config.example.json) and the Setup section of the skill. Collected messages, profiles and drafts are written only to the data directory, never to the skill folder.

## Tests

```bash
python3 slack-reply-drafts/scripts/test_collect.py
```

## License

[MIT](LICENSE). Copyright (c) 2026 Direk Sethi.

`product-copy` credits related skills by other authors under "Related skills". None of their content is included here.
