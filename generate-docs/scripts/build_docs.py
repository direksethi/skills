#!/usr/bin/env python3
"""Render a configured Markdown book as branded HTML and PDF."""
import argparse
import base64
import html
import json
from pathlib import Path
from string import Template
from urllib.parse import unquote, urlsplit, quote

import markdown
from bs4 import BeautifulSoup
from weasyprint import HTML


def esc(value):
    return html.escape(str(value), quote=True)


def build(config_path):
    config_path = Path(config_path).resolve()
    cfg = json.loads(config_path.read_text())
    root = (config_path.parent / cfg.get('root', '.')).resolve()
    out = (root / cfg.get('output', 'docs/exports')).resolve()
    out.mkdir(parents=True, exist_ok=True)
    version = cfg['version']
    stem = cfg.get('filename', 'System-Documentation') + '-v' + version
    if Path(stem).name != stem:
        raise ValueError('filename and version must not contain path separators')

    def asset(path):
        p = (root / path).resolve()
        mime = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', '.woff2': 'font/woff2', '.ttf': 'font/ttf'}.get(p.suffix.lower())
        if not mime:
            raise ValueError(f'Unsupported asset: {p}')
        return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()

    def logo(key, fallback):
        return f'<img src="{asset(cfg[key])}" alt="{esc(fallback)}">' if cfg.get(key) else esc(fallback)

    chapters = []
    maps = {}
    for i, ch in enumerate(cfg['chapters'], 1):
        path = (root / ch['file']).resolve()
        soup = BeautifulSoup(markdown.markdown(path.read_text(), extensions=['tables', 'fenced_code', 'toc']), 'html.parser')
        first = soup.find('h1')
        removed_id = first.get('id') if first else None
        if first:
            first.decompose()
        ids = {}
        if removed_id:
            ids[removed_id] = f'chapter-{i}'
        for node in soup.find_all(id=True):
            old = node['id']
            node['id'] = f'chapter-{i}-{old}'
            ids[old] = node['id']
        maps[path] = (f'chapter-{i}', ids)
        chapters.append((i, ch, path, soup))

    warnings = []
    for i, ch, path, soup in chapters:
        for a in soup.find_all('a', href=True):
            href = a['href']
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if target in maps:
                chapter, ids = maps[target]
                frag = unquote(parts.fragment)
                if frag and frag not in ids:
                    raise ValueError(f'Missing heading: {path}: {href}')
                a['href'] = '#' + (ids[frag] if frag else chapter)
            elif cfg.get('source_base_url') and target.is_relative_to(root):
                a['href'] = cfg['source_base_url'].rstrip('/') + '/' + quote(target.relative_to(root).as_posix())
                if parts.fragment:
                    a['href'] += '#' + parts.fragment
            else:
                warnings.append(f'Unresolved relative link in {path.name}: {href}')
                del a['href']
        for img in soup.find_all('img', src=True):
            parts = urlsplit(img['src'])
            if not parts.scheme and not parts.netloc:
                p = (path.parent / unquote(parts.path)).resolve()
                img['src'] = asset(str(p))
            elif parts.scheme != 'data':
                raise ValueError('Copy remote images into the project before rendering')

    def css_string(value):
        return json.dumps(str(value), ensure_ascii=False)[1:-1]

    style = Template((Path(__file__).resolve().parents[1] / 'assets/document.css').read_text()).substitute(
        sans=asset(cfg['font_sans']), mono=asset(cfg['font_mono']),
        brand=css_string(cfg['brand']), running_title=css_string(f"{cfg.get('subtitle', 'System documentation')} · v{version}"),
        footer=css_string(f"{cfg['title']} · {cfg['date']}"))
    toc = []
    body = []
    for i, ch, path, soup in chapters:
        title, desc = esc(ch['title']), esc(ch.get('description', ''))
        toc.append(f'<li><a href="#chapter-{i}"><span class="toc-num">{i:02}</span>{title}</a><p>{desc}</p></li>')
        notice = f'<aside class="notice">{esc(ch["notice"])}</aside>' if ch.get('notice') else ''
        body.append(f'<section class="chapter" id="chapter-{i}"><div class="chapter-kicker">{esc(ch.get("category", "Reference"))} / {i:02}</div><h1>{title}</h1><p class="chapter-description">{desc}</p>{notice}<div class="prose">{soup}</div></section>')
    title = esc(cfg['title'])
    subtitle = esc(cfg.get('subtitle', 'System documentation'))
    scope = '<br>'.join(esc(s) for s in cfg.get('scope', []))
    title_lines = '<br>'.join(esc(s) for s in cfg.get('title_lines', [cfg['title']]))
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{title} | {subtitle} v{esc(version)}</title><meta name="author" content="{esc(cfg['brand'])}"><style>{style}</style></head><body>
<section class="cover"><div class="cover-brand">{logo('logo', cfg['brand'])}</div>
<div class="cover-edition">{esc(cfg.get('edition', 'Platform reference'))} / v{esc(version)}</div>
<h1>{title_lines}</h1><div class="cover-subtitle">{subtitle}</div><p class="cover-intro">{esc(cfg.get('summary', ''))}</p>
<div class="cover-rule"></div><p class="cover-scope">{scope}</p>
<div class="cover-bottom"><div class="co-brand">{logo('partner_logo', '')}<span>{esc(cfg.get('partner', ''))}</span></div>
<p class="cover-meta">{esc(cfg['date'])}<br>Document version {esc(version)}<br>{esc(cfg.get('revision_note', ''))}</p></div></section>
<section class="contents" id="contents"><div class="chapter-kicker">Reference guide</div><h1>Contents</h1>
<p class="contents-intro">{esc(cfg.get('contents_intro', 'Select a chapter or use the PDF bookmarks to navigate.'))}</p>
<ol class="toc">{''.join(toc)}</ol><p class="scope-note">{esc(cfg.get('scope_note', ''))}</p></section>
{''.join(body)}</body></html>'''
    # No ambient network requests while rendering local documentation.
    from weasyprint import URLFetcher
    fetch = URLFetcher(allowed_protocols={'data'}, fail_on_errors=True)
    (out / (stem + '.html')).write_text(page)
    pdf = out / (stem + '.pdf')
    HTML(string=page, url_fetcher=fetch).write_pdf(pdf)
    print(json.dumps({'pdf': str(pdf), 'html': str(out / (stem + '.html')), 'warnings': warnings}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', help='JSON document manifest')
    build(parser.parse_args().config)
