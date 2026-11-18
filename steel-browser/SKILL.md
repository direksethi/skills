---
name: steel-browser
description: Use a real Chromium browser from a headless machine through a self-hosted Steel Browser and the agent-browser CLI. Use whenever a task needs a page rendered with JavaScript, a screenshot of a site, clicking through a web flow, filling forms, or checking a deployed app, instead of plain HTTP fetching. Covers when to hand off to a human for logins, 2FA and captchas.
---

# Steel Browser

A headless server has no screen. Steel Browser is a headless Chromium that runs
in Docker, stays on, and idles near 0% CPU. This skill drives it with the
agent-browser CLI over the Chrome DevTools Protocol (CDP).

## Setup

- A running Steel Browser instance (https://github.com/steel-dev/steel-browser),
  usually `docker compose up -d` with `restart: unless-stopped`. Keep it on a
  private network: the CDP endpoint gives full control of the browser.
- The agent-browser CLI (https://github.com/vercel-labs/agent-browser) on PATH,
  or its path in `AGENT_BROWSER_BIN`.
- `STEEL_CDP` set to the instance's CDP endpoint, for example
  `export STEEL_CDP=ws://steel.internal:3000`. There is no default: the wrapper
  refuses to run without it.
- `scripts/steel` from this skill on PATH, for example
  `ln -s "$PWD/scripts/steel" ~/.local/bin/steel`.

## Driving it

Use the `steel` command (`scripts/steel`): agent-browser connected to Steel,
with its own pinned tab so parallel agents do not collide.

```bash
steel open https://example.com      # navigate
steel snapshot                      # compact accessibility tree with @e refs
steel click @e3                     # act on a ref from the snapshot
steel fill @e2 "text"
steel get text body                 # page text
steel screenshot /tmp/page.png      # then read the PNG to look at it
steel --help                        # everything else
steel close                         # when finished: closes your tab, Steel stays up
```

Always `steel close` at the end of a task. An open tab with a busy page
(animations, video, live dashboards) keeps the browser using CPU. Never open
Steel's own session viewer UI inside Steel: it records itself in a loop.

Prefer `snapshot` over screenshots for reading and acting; it costs far fewer
tokens. Take a screenshot when layout or visuals matter.

Playwright, Puppeteer, Stagehand and browser-use can connect to the same
endpoint (`chromium.connectOverCDP(process.env.STEEL_CDP)`). Steel's REST API
(`/v1/sessions`, `/v1/scrape`, `/v1/screenshot`) is served from the same host
and port over HTTP.

## Rules

- Steel keeps no logins between sessions and has no accounts signed in. Do not
  sign in to any account in it unless the task calls for it, and never reuse one
  session across accounts that belong to different owners.
- Hand off to a human for logins, 2FA and captchas. When a page needs the user
  (a login, a 2FA code, a captcha, a payment, anything in their own signed-in
  browser), do not keep fighting it in Steel. Stop, give the user the exact URL
  and what to do there, and wait for them to confirm before continuing. If the
  environment provides a way to open a URL on the user's own machine, use that
  instead of asking them to copy it. Ask before any account-changing action.
- Local dev servers: Steel runs in a container and cannot reach the host's
  127.0.0.1. Bind the dev server to an address the container can reach and open
  it by that URL.

## Maintenance

Run these in the directory that holds your Steel `docker-compose.yml`:

    docker compose ps
    docker compose logs --tail 50 api
    docker compose pull && docker compose up -d     # update
    docker compose restart api                      # reset a wedged browser
