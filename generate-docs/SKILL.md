---
name: generate-docs
description: Create or refresh code-verified system documentation in structured Markdown and a polished branded PDF with linked contents, bookmarks, and technical reference chapters. Use for documentation packages and branded system manuals.
---

# Generate Docs

Turn a repository into a maintainable documentation set and a presentation-quality PDF. Accept `/generate-docs` as the user's invocation. Scale the chapter list to the system and requested scope.

## Establish the reference

Read the repository's instructions, existing documentation, source, schema/migrations, configuration examples, and relevant recent commits. Record the source revision and document version separately. Verify claims against implementation; distinguish code-verified behavior from deployment-verified behavior. Do not imply that production integrations work merely because code exists.

If the user requests formatting only, preserve the supplied content and report gaps without expanding into an application change. Documentation generation does not authorize deployment, live user changes, or publishing to external repositories. Preserve existing authorization when publishing is explicitly requested.

## Write the Markdown source

Use a documentation index and focused chapters. A useful sequence is:

1. System overview: audience, purpose, boundaries, environments, end-to-end flow.
2. Product guide: roles, access, user workflows, states, and exceptions.
3. Architecture: runtimes, components, request boundaries, repository map.
4. Processing or AI pipeline: stages, triggers, contracts, retries, review, limitations.
5. Integrations: direction of data flow, identity mapping, authentication mechanism, triggers, payloads, failures, reconciliation, onboarding and offboarding propagation.
6. Data model: ownership, relationships, lifecycle, retention, migrations and storage.
7. Configuration: variable names, required/optional status, defaults, saved settings.
8. API and actions: methods, routes, permissions, request/response shape, side effects.
9. Operations: setup, verification, deploy process, monitoring, recovery, troubleshooting.
10. Change history and known limits, with historical evidence/proposals in labeled appendices.

Include only chapters supported by the system. Explain both why the system exists and how it works at implementation level. Describe integration latency, cache/grace windows and revocation semantics when relevant. Exclude credentials, real client records and private machine configuration. Separate proposed behavior from shipped behavior. Use professional language, no emojis or em dashes in newly authored prose. Keep existing quoted material accurate.

## Apply the publication design

Read [references/publication.md](references/publication.md) for the manifest, rendering command, and visual design. Use official assets from the current project's brand boundary. Do not carry a previous client's logo, system details, revision, or date into another project.

The included renderer and CSS reproduce the proven design: spacious monochrome cover, optional partner mark, clear type hierarchy, A4 pages, compact linked contents with page numbers, chapter bookmarks, running headers/footers, wrapped code and repeated table headings. Supply local licensed fonts and assets through a JSON manifest. The skill intentionally bundles no client logos or proprietary documentation.

Save Markdown, the manifest, generated HTML and versioned PDF in the project. Do not edit the PDF manually. For a version bump, change the manifest and regenerate so the filename, cover, metadata and headers agree.

## Validate and deliver

Run the included PDF checker, inspect its contact sheets, and view the cover, contents, widest table, longest code block and final page at readable resolution. Fix clipped text, unreadable tables, orphan headings and nearly empty contents spill pages, then rebuild. A long contents section may span full pages; do not shrink it until unreadable just to force one page. Automated geometry checks cannot detect all overlaps or bad typography.

Check chapter completeness, internal links and bookmarks, version consistency, and source-link revision. Treat missing anchors and unembedded resources as build errors. Report unresolved source links and unavailable live verification honestly.

Deliver a clickable PDF link, briefly describe coverage, and mention any material limitation. Publish or commit only within the user's authorized scope. Keep generated QA images out of the published skill package unless explicitly requested.
