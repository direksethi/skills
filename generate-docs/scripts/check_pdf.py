#!/usr/bin/env python3
"""Check PDF navigation and geometry, and render contact sheets for visual QA."""
import argparse
import json
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw


def check(path, qa_dir=None):
    pdf = pymupdf.open(path)
    errors = []
    links = 0
    for i, page in enumerate(pdf):
        words = page.get_text('words')
        if not words:
            errors.append(f'Page {i+1}: no extractable text; inspect for an empty page')
        for x0, y0, x1, y1, word, *_ in words:
            if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                errors.append(f'Page {i+1}: text outside page: {word}')
        for link in page.get_links():
            links += 1
            if link['kind'] == pymupdf.LINK_GOTO and not 0 <= link.get('page', -1) < len(pdf):
                errors.append(f'Page {i+1}: invalid internal target')
    if not pdf.get_toc():
        errors.append('No bookmarks')
    if qa_dir:
        out = Path(qa_dir)
        out.mkdir(parents=True, exist_ok=True)
        for i in range(min(2, len(pdf))):
            pdf[i].get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4)).save(out/f'page-{i+1:02}.png')
        for start in range(0, len(pdf), 16):
            sheet = Image.new('RGB', (908, 1328), '#ddd')
            draw = ImageDraw.Draw(sheet)
            for i in range(start, min(start+16, len(pdf))):
                pix = pdf[i].get_pixmap(matrix=pymupdf.Matrix(.36, .36), alpha=False)
                thumb = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                thumb.thumbnail((221, 314))
                x, y = (i-start) % 4*227, (i-start)//4*332
                sheet.paste(thumb, (x, y+15))
                draw.text((x+5, y+1), str(i+1), fill='black')
            sheet.save(out/f'contact-{start//16+1}.png')
    print(json.dumps({'pages': len(pdf), 'bookmarks': len(pdf.get_toc()), 'links': links, 'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf')
    p.add_argument('--qa-dir')
    args = p.parse_args()
    raise SystemExit(check(args.pdf, args.qa_dir))
