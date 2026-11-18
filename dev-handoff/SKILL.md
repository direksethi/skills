---
name: dev-handoff
description: Write a git-committed session snapshot into the current repo so a fresh Claude Code or Codex session can resume with zero context bloat.
argument-hint: "[optional note]"
disable-model-invocation: true
---

Create a **handoff snapshot**: a single markdown file, committed (and pushed if possible)
to the current repo, that lets a brand-new session (Claude Code or Codex) pick up this
work without re-reading the prior conversation.

## Guard

Run `git rev-parse --show-toplevel`. If this fails (not a git repo), stop immediately and
tell the user: "dev-handoff needs a git repo to write and commit the snapshot. Run it from
inside your project." Do not create folders, write files, or run other git commands.

## Steps

1. Gather git facts for `<root>` (the repo root from the guard step):
   - Current branch (`git branch --show-current`; treat empty as `(detached HEAD)`)
   - Last commit (`git log -1 --pretty=format:'%h %s'`; treat missing as `(no commits yet)`)
   - Working tree status (`git status --porcelain`)
   - Unstaged and staged diff stats (`git diff --stat HEAD`, `git diff --stat --cached`)
   - Untracked files (`git ls-files --others --exclude-standard`)
   - Unpushed commits vs upstream (`git log @{u}.. --oneline`, or note "no upstream tracking branch")
   - Remote (`git remote -v`)

2. Ensure `<root>/snapshots/` exists (`mkdir -p`).

3. Synthesize the snapshot from this conversation plus the git facts above. Write real,
   specific content, with no `TODO` / `(fill in)` placeholders. If a section is genuinely
   empty, say so honestly (e.g. "No failed attempts this session.").

4. Write `<root>/snapshots/dev-handoff_<YYYY-MM-DD_HHmm>.md` (local time) with exactly
   this structure:

   ```
   > **Snapshot:** <human timestamp>
   > **Branch:** <branch>
   > **Repo:** <root>
   > **Last commit:** <hash> <subject>
   > _<one-line note from the arguments passed to this skill, as a headline; omit if none>_

   # Goal
   <1-4 sentences: what this session is ultimately trying to accomplish.>

   ## Current State
   <What works, what's half-done, what was just decided. Name modules, commands, blockers.>

   ## Files in Flight
   <Files actively being edited, cross-referenced against the git facts, each with a
   one-clause reason it matters. If the tree is clean, say so.>

   ## Changed
   <The git-factual record: staged + unstaged diff stat, untracked files, unpushed
   commits. Keep this grounded in the injected facts, not the conversation.>

   ## Failed Attempts
   <Approaches tried and abandoned, and why, so the next session doesn't repeat them.>

   ## Next Steps
   <An ordered, actionable checklist the next session can execute immediately.>

   ## Suggested Skills
   <Skills the next session should invoke via the Skill tool to continue this work.
   Omit this section entirely if none apply.>
   ```

5. Redact secrets before writing: API keys, tokens, passwords, and personally
   identifiable information must never land in the snapshot, even if they appeared in
   the conversation or a diff.

6. Commit: `git add <file>` then `git commit -m "chore(dev-handoff): snapshot <timestamp>"`.
   Do not set or override the git author: use the repo's existing config as-is.

7. Push, with a safe fallback:
   - If the branch already tracks an upstream, run `git push`.
   - Otherwise run `git push -u origin <branch>`.
   - If there's no remote, or the push fails for any reason, keep the local commit and
     warn the user clearly with the manual push command. A failed push is a warning, not
     an error: the commit must remain.

8. Report back, concisely: the absolute path to the snapshot, whether it was committed
   and pushed or committed locally only, and this resume tip verbatim:
   > In a fresh Claude Code or Codex session, just say "read the latest dev-handoff":
   > open the newest file in `snapshots/` and pick up exactly where this left off.
