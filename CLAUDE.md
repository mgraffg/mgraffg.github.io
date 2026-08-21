# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is Mario Graff's academic portfolio site, built with Jekyll on the [academicpages](https://github.com/academicpages/academicpages.github.io) theme (a fork of minimal-mistakes) and deployed via GitHub Pages at `mgraffg.github.io`. Content changes (adding a talk, a software entry, a publication) are almost always plain Markdown/HTML front-matter edits, not Ruby/logic changes.

Instructions to Claude may be given in Spanish or English, but all published site content must be in English, with one exception: **Course Textbooks** and **Talks** titles may stay in their original Spanish when that's the title's true source language. Even then, the surrounding description/excerpt text must still be written in English, and must include a short note flagging that the underlying content (book/talk) is in Spanish. Commit messages may remain in Spanish per existing repo convention.

## Development

Local dev is intended to run inside the provided Dev Container (Ruby 3.3 + Node), which runs `bundle install` automatically on create/start.

- Serve the site locally: `bundle exec jekyll serve` then open http://localhost:4000
- Build only: `bundle exec jekyll build`
- Live-reload variant: `bundle exec jekyll serve -l -H localhost` (note: `_config.yml` is NOT reloaded automatically — restart the server after editing it)

There are no JS/Node build steps, package.json, linters, or test suites in this repo — it's a static Jekyll site plus vendored theme assets. There is no CI (no `.github/workflows`); publishing happens via GitHub Pages building the pushed branch.

## Content architecture

Site content lives in Jekyll collections declared in `_config.yml`, each with its own permalink and shared `defaults` (layout, `author_profile`, `share`, `comments`):

- `_talks/` → collection `talks`, layout `talk` — one file per talk (see `_talks/1_talk.md` for the minimal front matter shape: `title`, `excerpt`, `collection: talks`, `type`, `link`).
- `_software/` → collection `software`, layout `single` — one file per project. Front matter includes `category`, which must match a key under `software_category` in `_config.yml` (currently `legalia`, `compstats`, `textclassification`); the category description shown on `/software/` also lives in that config block.
- `_teaching/` → collection `teaching`, layout `single` — analogous per-collection files.
- `publications` and `alumni` collections are configured in `_config.yml` (permalink, defaults, and for publications a `publication_category` taxonomy) but currently have **no** collection directory/content files. `_pages/publications.html` expects `publications` to be filled by an automated Google Scholar import (tracked in issue #7); until then it renders a placeholder message. `_pages/alumni.html` similarly loops over `site.alumni`, which is empty until an `_alumni/` collection is added.
- `_pages/*.html|md` → standalone pages (About, Software, Publications, Alumni, Talks, Course Textbooks, 404), most using `layout: archive` and looping over a collection or category map from `_config.yml`.
- `_data/navigation.yml` → controls the header link order/labels; keep this in sync when adding/removing top-level sections (order was agreed in issue #9).
- `_data/authors.yml` → placeholder/template data, not the site author (site author fields live under `author:` in `_config.yml`).

When adding a new content type or category, the pattern is: add the collection file with correct front matter → confirm/add the category under the relevant `*_category` map in `_config.yml` → confirm the section is linked from `_data/navigation.yml` if it's a top-level nav item.

## Rendering layer

- `_layouts/` — page skeletons (`default`, `single`, `archive`, `archive-taxonomy`, `talk`, `splash`, `cv-layout`, `compress`).
- `_includes/` — reusable partials. Per-collection card partials follow the `archive-single*.html` naming convention (e.g. `archive-single-software.html`, `archive-single-talk.html`, `archive-single-cv.html`) — when a collection needs a distinct card layout on its index page, add a new `archive-single-<name>.html` and include it from the corresponding `_pages/*.html`, mirroring `_pages/software.html` and `_pages/publications.html`.
- A separate "CV" rendering path exists (`_layouts/cv-layout.html`, `_includes/cv-template.html`, `_includes/archive-single-cv.html`, `_includes/archive-single-talk-cv.html`, `_sass/layout/_json_cv.scss`) for a printable/JSON-driven CV view, distinct from the normal site chrome.
- `_sass/theme/` holds multiple light/dark theme variants (air, contrast, mint, sunrise, dirt, default); `_sass/_custom.scss` and `_sass/layout/_custom.scss`-style files are where site-specific overrides belong rather than editing vendored theme partials directly.
- `assets/js/_main.js` and `assets/js/plugins`/`vendor` are excluded from the Jekyll build output (see `exclude:` in `_config.yml`) — they're sources bundled into `assets/js/main.min.js`/`theme.js`, not files Jekyll serves directly.

## Workflow

Work happens directly on the `migrate-academicpages-issue-5` branch: commit changes there as the migration progresses. Do not create a new branch and do not open a pull request — this continues until the site migration is complete.

## Site configuration notes

- `_config.yml` is the single source of truth for site metadata, author/social links, nav category taxonomies (`publication_category`, `software_category`), collections, and defaults — check it first before assuming a value is hardcoded in a template.
- `comments`, `atom_feed`, and `analytics` providers are currently disabled (`provider: false`).
- `perfil.json` at the repo root contains Mario Graff's full CV data (raw export from an external research-output system, SECIHTI/CONACYT) and is used as a local source for populating the publications section. It is **sensitive personal data and must never be committed to git under any circumstance** — it is listed in `.gitignore`; never remove that entry, never `git add`/force-add it, and never include its contents in a commit, PR, or any generated public output. It is not itself consumed by the Jekyll build.
