#!/usr/bin/env python3
"""Read-only Slack collection. Private state is separated by conversation.

Settings come from environment variables first, then from a JSON config file
(SLACK_REPLY_DRAFTS_CONFIG, default ~/.config/slack-reply-drafts/config.json):

  team_id        SLACK_TEAM_ID            Workspace id the token must belong to
  user_id        SLACK_USER_ID            The user whose replies are drafted
  data_dir       SLACK_REPLY_DRAFTS_DIR   Private state directory
                                          (default ~/.local/share/slack-reply-drafts)
  workspace_url  SLACK_WORKSPACE_URL      Permalink host; defaults to the URL
                                          reported by auth.test
  token_file     SLACK_TOKEN_FILE         Optional file with a SLACK_USER_TOKEN=...
                                          line, used when the variable is unset

The token itself is read from SLACK_USER_TOKEN by scripts/slack-read.
"""
import argparse
import concurrent.futures
import fcntl
import json
import os
import re
from pathlib import Path
import subprocess
import threading
import time

CONFIG_PATH = Path(os.environ.get('SLACK_REPLY_DRAFTS_CONFIG', '~/.config/slack-reply-drafts/config.json')).expanduser()

def load_config():
    try:
        config = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
    except ValueError as error:
        raise SystemExit(f'Invalid config file {CONFIG_PATH}: {error}')
    if not isinstance(config, dict):
        raise SystemExit(f'Invalid config file {CONFIG_PATH}: expected a JSON object')
    return config

def setting(config, env, key, default=''):
    return os.environ.get(env) or config.get(key) or default

CONFIG = load_config()
ROOT = Path(setting(CONFIG, 'SLACK_REPLY_DRAFTS_DIR', 'data_dir', '~/.local/share/slack-reply-drafts')).expanduser()
HELPER = str(Path(__file__).resolve().with_name('slack-read'))
TEAM = setting(CONFIG, 'SLACK_TEAM_ID', 'team_id')
USER = setting(CONFIG, 'SLACK_USER_ID', 'user_id')
WORKSPACE_URL = setting(CONFIG, 'SLACK_WORKSPACE_URL', 'workspace_url')
TOKEN_FILE = setting(CONFIG, 'SLACK_TOKEN_FILE', 'token_file')
RATE_LOCK = threading.Lock()
NEXT_CALL = {}

def helper_env():
    """Environment for slack-read, with the token loaded from the token file if needed."""
    env = dict(os.environ)
    if not env.get('SLACK_USER_TOKEN') and TOKEN_FILE:
        for line in Path(TOKEN_FILE).expanduser().read_text().splitlines():
            name, _, value = line.strip().removeprefix('export ').partition('=')
            if name.strip() == 'SLACK_USER_TOKEN':
                env['SLACK_USER_TOKEN'] = value.strip().strip('"\'')
    return env

def redact(value):
    if isinstance(value, str):
        value = re.sub(r'\b(?:xox[baprs]-|sk-)[A-Za-z0-9_.-]+', '[REDACTED CREDENTIAL]', value)
        value = re.sub(r'\b(?:sk_|gh[pousr]_|AKIA)[A-Za-z0-9_-]+', '[REDACTED CREDENTIAL]', value)
        value = re.sub(r'(?m)^[ \t]*(?!<|https?://)(?=[^\n]*[a-z])(?=[^\n]*[A-Z])(?=[^\n]*\d)(?=[^\n]*[$%&!*#])[^\s]{10,}[ \t]*$', '[REDACTED CREDENTIAL]', value)
        return re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)?', '[REDACTED TOKEN]', value)
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, dict):
        return {k:redact(v) for k,v in value.items()}
    return value

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(redact(value), ensure_ascii=False, indent=2) + '\n')
    temp.chmod(0o600)
    temp.replace(path)

def read(path, default):
    return json.loads(path.read_text()) if path.exists() else default

def api(method, **params):
    for attempt in range(6):
        with RATE_LOCK:
            now = time.monotonic()
            ready = max(now, NEXT_CALL.get(method, now))
            NEXT_CALL[method] = ready + 1.3
        time.sleep(max(0, ready - time.monotonic()))
        result = subprocess.run([HELPER, method] + [f'{k}={v}' for k,v in params.items()], capture_output=True, text=True, timeout=90, env=helper_env())
        try:
            data = json.loads(result.stdout)
        except ValueError:
            data = {'ok': False, 'error': 'transport_error'}
        if data.get('ok'):
            return data
        if data.get('error') not in ('ratelimited', 'transport_error', 'internal_error'):
            raise RuntimeError(f'{method}: {data.get("error")}')
        time.sleep(min(60, 2 ** attempt * 2))
    raise RuntimeError(f'{method}: retries exhausted')

def pages(method, key, **params):
    cursor = ''
    while True:
        data = api(method, limit=999, **params, **({'cursor': cursor} if cursor else {}))
        yield from data.get(key, [])
        cursor = data.get('response_metadata', {}).get('next_cursor', '')
        if not cursor:
            if data.get('has_more'):
                raise RuntimeError(f'{method}: has_more without cursor')
            break

def collect(channel, cutoff, end, bootstrap):
    cid = channel['id']
    folder = ROOT / 'conversations' / cid
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    old = read(folder / 'state.json', {})
    messages = {m['ts']:m for m in read(folder / 'messages.json', [])}
    signatures = old.get('threads', {})
    updated = dict(signatures)
    roots = 0
    # Scan all visible roots: recent replies can belong to arbitrarily old roots.
    for message in pages('conversations.history', 'messages', channel=cid, latest=end):
        roots += 1
        ts = message['ts']
        if float(ts) >= cutoff:
            messages[ts] = message
        if message.get('reply_count') and float(message.get('latest_reply', ts)) >= cutoff:
            signature = [message.get('latest_reply'), message.get('reply_count')]
            if signatures.get(ts) != signature:
                # Fetch complete relevant thread, including an old parent for context.
                for reply in pages('conversations.replies', 'messages', channel=cid, ts=ts, oldest=cutoff, latest=end, inclusive='true'):
                    if float(reply['ts']) >= cutoff or reply['ts'] == ts:
                        messages[reply['ts']] = reply
                messages[ts] = message
                if float(message.get('latest_reply', ts)) <= end:
                    updated[ts] = signature
    items = sorted(messages.values(), key=lambda m:float(m['ts']))
    save(folder / 'channel.json', channel)
    save(folder / 'messages.json', items)
    sent = [m for m in items if m.get('user') == USER and float(m['ts']) >= cutoff and m.get('text') and m.get('subtype') not in ('channel_join','channel_leave')]
    save(folder / 'sent.json', sent)
    if bootstrap:
        seen = [m['ts'] for m in items]
    else:
        seen = old.get('seen', [])
    save(folder / 'state.json', {'threads':updated, 'seen':seen, 'collected_at':end, 'roots_scanned':roots})
    incoming = [m for m in items if float(m['ts']) >= cutoff and m['ts'] not in seen and m.get('user') != USER]
    save(folder / 'pending.json', incoming)
    return {'id':cid, 'name':channel.get('name', channel.get('user',cid)), 'sent':len(sent), 'messages':len(items), 'roots_scanned':roots, 'pending':len(incoming)}

def main():
    parser = argparse.ArgumentParser(description='Read-only Slack collection for the slack-reply-drafts skill.', epilog='Settings: SLACK_USER_TOKEN, SLACK_TEAM_ID, SLACK_USER_ID, SLACK_REPLY_DRAFTS_DIR, SLACK_WORKSPACE_URL, or the JSON config file named by SLACK_REPLY_DRAFTS_CONFIG.')
    parser.add_argument('--bootstrap', action='store_true', help='Initial learning run: mark existing history as seen. Never use during routine monitoring')
    parser.add_argument('--channel', help='Retry one conversation, preserving the other coverage results')
    args = parser.parse_args()
    if not TEAM or not USER:
        raise SystemExit(f'Set SLACK_TEAM_ID and SLACK_USER_ID, or team_id and user_id in {CONFIG_PATH}')
    if not helper_env().get('SLACK_USER_TOKEN'):
        raise SystemExit('Set SLACK_USER_TOKEN, or token_file in the config')
    os.umask(0o077)
    ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = (ROOT / 'collect.lock').open('w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('Another collection is running')
    auth = api('auth.test')
    if (auth.get('team_id'),auth.get('user_id')) != (TEAM,USER):
        raise SystemExit('Slack account mismatch')
    workspace_url = (WORKSPACE_URL or auth.get('url') or '').rstrip('/')
    end = time.time()
    baseline = read(ROOT / 'baseline.json', {})
    cutoff = baseline.get('cutoff', end - 30*86400)
    if not baseline:
        save(ROOT / 'baseline.json', {'cutoff':cutoff,'started_at':end,'team_id':TEAM,'user_id':USER})
    channels = [c for c in pages('conversations.list','channels',types='public_channel,private_channel,im,mpim',exclude_archived='false') if c.get('is_im') or c.get('is_mpim') or c.get('is_member')]
    save(ROOT / 'channels.json', channels)
    if args.channel:
        channels = [c for c in channels if c['id'] == args.channel]
        if not channels:
            raise SystemExit('Requested conversation is not in the accessible membership list')
    results, errors, unavailable = [], [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(collect,c,cutoff,end,args.bootstrap):c for c in channels}
        for future in concurrent.futures.as_completed(futures):
            c = futures[future]
            try:
                row = future.result()
                results.append(row)
                print(json.dumps(row), flush=True)
            except Exception as error:
                row = {'id':c['id'],'error':str(error)}
                if c.get('user') == 'USLACKBOT' and 'channel_not_found' in str(error):
                    unavailable.append(row)
                else:
                    errors.append(row)
                print(json.dumps(row), flush=True)
    users = read(ROOT / 'users.json', {})
    needed = {c.get('user') for c in channels if c.get('user')}
    for c in channels:
        for m in read(ROOT/'conversations'/c['id']/'sent.json',[]):
            needed.update(re.findall(r'<@(U[A-Z0-9]+)',m.get('text','')))
    for uid in needed - users.keys():
        try:
            u = api('users.info',user=uid)['user']
            users[uid] = {'name':u.get('real_name',u.get('name')), 'handle':u.get('name')}
        except RuntimeError:
            users[uid] = {'name':uid}
    save(ROOT / 'users.json', users)
    if args.channel:
        previous = read(ROOT / 'coverage.json', {})
        results = [r for r in previous.get('channels', []) if r['id'] != args.channel] + results
        errors = [r for r in previous.get('errors', []) if r['id'] != args.channel] + errors
        unavailable = [r for r in previous.get('unavailable', []) if r['id'] != args.channel] + unavailable
    report = {'started_at':end,'finished_at':time.time(),'cutoff':cutoff,'bootstrap':args.bootstrap,'workspace_url':workspace_url,'channels':results,'errors':errors,'unavailable':unavailable,'total_sent':sum(r['sent'] for r in results),'total_messages':sum(r['messages'] for r in results)}
    save(ROOT / 'coverage.json',report)
    print(json.dumps({'total_sent':report['total_sent'],'total_messages':report['total_messages'],'errors':errors}),flush=True)
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
