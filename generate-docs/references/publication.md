# Publication recipe

The renderer takes a JSON manifest. Paths resolve from `root`, which resolves relative to the manifest. Chapters stay in the given order. Markdown H1 is replaced by the chapter title; lower headings become PDF bookmarks. Same-book Markdown links are remapped into the PDF, including fragments. Other relative links use `source_base_url`, pinned to the verified revision.

## Manifest

```json
{
  "root": "../..",
  "output": "docs/exports",
  "filename": "Product-System-Documentation",
  "title": "Product Name",
  "title_lines": ["Product", "Name"],
  "subtitle": "System documentation",
  "version": "1.0.1",
  "date": "27 October 2026",
  "edition": "Platform reference",
  "brand": "CLIENT / DELIVERY PARTNER",
  "partner": "Delivery Partner",
  "logo": "public/brand/client.svg",
  "partner_logo": "public/brand/partner.svg",
  "font_sans": "docs/assets/sans.woff2",
  "font_mono": "docs/assets/mono.woff2",
  "summary": "One or two sentences explaining the system's purpose.",
  "scope": ["PRODUCT & WORKFLOWS", "ARCHITECTURE & INTEGRATIONS", "TECHNICAL REFERENCE & OPERATIONS"],
  "revision_note": "Source revision abc1234. Deployment settings may differ.",
  "source_base_url": "https://github.com/ORG/REPO/blob/FULL_COMMIT_SHA",
  "contents_intro": "Start with the overview and workflows. Technical chapters explain how the system is built and operated.",
  "scope_note": "Main chapters describe verified implementation. Appendices preserve historical material.",
  "chapters": [
    {"file": "README.md", "title": "System overview", "description": "Purpose and end-to-end flow", "category": "Overview"},
    {"file": "docs/architecture.md", "title": "Architecture", "description": "Runtime and component boundaries", "category": "Technical design"},
    {"file": "docs/plans/original-plan.md", "title": "Original proposal", "description": "Historical design record", "category": "Appendix", "notice": "Historical proposal. Refer to current reference chapters for implemented behavior."}
  ]
}
```

Use actual chapter paths, brand metadata and source revisions. `logo`, `partner`, `partner_logo`, `title_lines`, scope text and historical notices are optional. Font paths are required, ensuring repeatable typography without Next.js or a network font dependency. Use available licensed fonts, for example Geist and Geist Mono already distributed with the project, or local open-license alternatives. SVG/PNG/JPEG images and WOFF2/TTF fonts are embedded in the HTML and PDF. Remote images must be copied into the project before rendering. Brand asset use must remain within the current client's boundary.

## Build and inspect

Run with the skill's absolute path, from the project:

```sh
uv run --with 'weasyprint>=70,<71' --with markdown --with beautifulsoup4 python /path/to/generate-docs/scripts/build_docs.py docs/exports/document.json
uv run --with pymupdf --with pillow python /path/to/generate-docs/scripts/check_pdf.py docs/exports/Product-System-Documentation-v1.0.1.pdf --qa-dir /tmp/docs-qa
```

WeasyPrint also needs native Pango/font libraries. If unavailable, report the dependency, use the environment's supported installer if authorized, or use an available PDF renderer and recheck pagination and links. Never claim a PDF is complete when only HTML exists.

The checker returns page/bookmark/link counts and failures for invalid internal page targets, missing bookmarks, empty pages or text outside page bounds. It writes 4-by-4 contact sheets plus cover and contents renders. Use a PDF viewer or render additional individual pages for detailed inspection. Images and graphics can overflow without text geometry detecting them, so visual inspection remains necessary.

## Design decisions to preserve

- A4, 18 mm side margins and 22/20 mm top/bottom margins leave room for running matter.
- The cover uses a 48 pt title, 22 pt subtitle and a restrained brand lockup. Split long product names with `title_lines` to avoid collisions.
- Body text is 9.5 pt with 1.47 line spacing. Chapter headings are 28 pt; H2/H3 are 15/11 pt.
- Contents rows have 1.5 mm vertical padding. This fit the original 14-chapter manual on one page; recheck after changing titles or chapter count.
- Every chapter begins on a new page. Headings stay with following content; paragraphs preserve widows/orphans.
- Tables have repeated dark headers, light zebra rows and wrapped identifiers. Wide tables may need fewer columns, a separate reference appendix or a landscape adaptation. Do not force tiny type.
- Code wraps inside a light panel. A code block taller than a page may need splitting at a meaningful boundary.
- Keep version separate from source revision. A documentation version does not create an application release or Git tag.

Edit the CSS deliberately for another brand or page format, and rerun visual QA. Prefer keeping a project-local copy of the renderer and stylesheet for publications that must rebuild independently of installed skill updates.
