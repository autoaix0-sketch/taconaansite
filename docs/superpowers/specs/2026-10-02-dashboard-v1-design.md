# Taco Naan — Owner Dashboard v1 (offers & site content)

## Context

Taco Naan's site (`taconaansite/`) is a static one-page site (plain HTML/JS, FR/ES/EN) deployed to Vercel by `git push` from a **public** GitHub repo (`autoaix0-sketch/taconaansite`). Today every change — a price, a photo, opening hours — needs a developer editing `data/menu.js` or `assets/js/site.js` on a PC. Hours are hard-coded (`SERVICES` in `assets/js/site.js:29` + three i18n strings + JSON-LD in `index.html:63`), there is no way to announce an offer or an exceptional closure.

The user wants a back-office for Taco Naan (social media, visuals, offers, AI agents). That is four subsystems; this spec covers only the first, chosen by the user: **the owner, on a phone, manages offers, menu prices/items, photos, and hours/closures, and the live site updates within ~1 minute.** Social posting, visual generation, the AI assistant and in-dashboard undo are explicitly later specs.

### Decisions taken with the user
- Audience: Taco Naan only (not multi-restaurant).
- Operator: the owner, non-technical, on a phone → hosted web app with login.
- V1 scope: offers (new site section) + menu prices/items + photos + hours & closures.
- Translation: owner writes French; Claude drafts ES/EN; owner sees and can edit all 3 before publishing.
- Architecture **A — git-backed**: dashboard commits to the site repo via GitHub API; Vercel redeploys. Site stays static, no runtime dependency.
- Dashboard = **separate private repo + Vercel project** `taconaan-admin`; password login.

Constraints from existing project rules (`docs/ATELIER.md` §6, user memory): repo is public → no secret ever in either repo; nothing customer-facing is published without the owner seeing it; never rerun `tools/optimize_images.py`; never commit/push/deploy without the user asking; verify in the browser pane (1440 + 375) before claiming done.

---

## Architecture

```
Owner's phone ──► taconaan-admin (private repo, own Vercel project, password login)
                     /api/login      → signed session cookie
                     /api/state      → read current data files from GitHub
                     /api/publish    → ONE commit to taconaansite (allowlisted paths)
                     /api/photo      → sharp: AVIF+WebP 480/960 → returned as pending files
                     /api/translate  → Claude: FR → ES/EN drafts
                                ▼
              taconaansite (public) ──► Vercel redeploy (~1 min) ──► live site
```

Env vars (Vercel, `taconaan-admin` only): `ADMIN_PASSWORD_HASH` (scrypt), `SESSION_SECRET`, `GITHUB_TOKEN` (fine-grained PAT, repo `taconaansite` only, Contents: read/write), `GITHUB_REPO`, `GITHUB_BRANCH` (`dashboard-test` during dev, `main` in prod), `ANTHROPIC_API_KEY`. **The user creates the tokens and sets them** — Claude never handles secret values.

---

## Part 1 — Site changes (`taconaansite/`, done once by Claude)

### Data files (same `<script>` + `window.TACONAAN_*` pattern, no build step)
All dashboard-written files use **JSON-literal bodies**: `/* header */\nwindow.TACONAAN_X = <JSON>;\n` so the dashboard parses them by stripping prefix/suffix + `JSON.parse` (no JS eval).

- `data/menu.js` — convert existing object literal to JSON-literal form, **data unchanged**. The French how-to comments move to `README.md`. New optional fields: item `hidden: true`; category `photo: '<uploads key>'` (overrides `image`).
- `data/offers.js` (new) — `window.TACONAAN_OFFERS = { offers: [{ id, title{fr,es,en}, text{fr,es,en}, price|null, photo|null, start:'YYYY-MM-DD', end:'YYYY-MM-DD' }] }`, starts empty.
- `data/hours.js` (new) — `window.TACONAAN_HOURS = { week: { mon:[['11:30','15:00'],['18:00','23:30']], … sun:[…] }, closures: [{ from, to, note{fr,es,en} }] }`, seeded from today's `SERVICES`.
- `assets/img/uploads.js` (new) — `window.TACONAAN_UPLOADS = { key: { stem, kind:'photo', sizes:[[w,h],…] } }` (same shape as `assets/img/manifest.js`), starts `{}`. Files in `assets/img/uploads/`.
- Add `<script>` tags for the three new files in `index.html` and `404.html` (before `site.js`).

### `assets/js/site.js`
- **Offers section**: new `<section class="offres" id="offres">` between `.hero` (index.html:110) and `#carte` (index.html:207). Rendered from `TACONAAN_OFFERS`, filtered to offers where Paris-date ∈ [start, end] (reuse the `Intl … timeZone:'Europe/Paris'` approach of `parisMinutes()`, site.js:383). Hidden entirely when none active. Brand style: `#0a0c0c`, single `#ffc61a` accent, Instrument Serif titles, square corners; respects `prefers-reduced-motion`. All text via existing `escapeHtml`. Re-renders on language switch like the menu.
- **Hours**: replace `SERVICES` + the three `'venir.hours.v'` strings with rendering from `TACONAAN_HOURS` (group identical days: "Tous les jours …" when all 7 equal, else per-day lines). `openState()` (site.js:404) uses today's weekday schedule and closures; during a closure → badge "Fermé exceptionnellement" + a dismissible banner at the top with the note. "opens tomorrow" logic walks forward to the next open day. The `fact.4` "Ouvert 7j/7" string becomes conditional on all 7 days open.
- **Menu**: skip `hidden` items; resolve category `photo` through `TACONAAN_UPLOADS` with the existing image/`<picture>` helper.
- Add `--offres` nav link only when an offer is active (optional; keep if trivial).

### `index.html` JSON-LD
Wrap the whole `<script type="application/ld+json">` block (index.html:40) between HTML comments `<!-- LDJSON:START -->` / `<!-- LDJSON:END -->`. The dashboard regenerates that block (same content, `openingHoursSpecification` rebuilt from `hours.js`, upcoming closures as `specialOpeningHoursSpecification`); nothing outside the markers is ever changed.

### Caching
Add `vercel.json` with `Cache-Control: no-cache` for `/data/(.*)` and `/assets/img/uploads.js`. Verify with `curl -I` on a preview deploy. Keep `?v=` bumps only for `site.js`/`site.css` changes (README updated accordingly).

### Docs
Update `README.md` ("Le seul fichier à modifier" → the dashboard; developer must `git pull` before working because the dashboard commits to `main`) and add a §9 "Le tableau de bord" to `docs/ATELIER.md`.

---

## Part 2 — Dashboard (`C:\Users\sakka\Desktop\taconaansite\taconaan-admin\`, new)

Stack (matches the user's Kebab Lab): Vite + React + TS + Tailwind 4, Vercel Node functions in `api/`, `zod`, `sharp`, `@anthropic-ai/sdk`, vitest. French UI, mobile-first (designed at 375 px), PWA manifest for "add to home screen".

### Server modules (`api/_lib/`)
- `auth.ts` — scrypt verify against `ADMIN_PASSWORD_HASH` (constant-time), HMAC-signed `HttpOnly; Secure; SameSite=Strict` cookie (30 days), `requireSession()` guard on every endpoint; login throttle (per-IP delay + lockout after N failures; in-memory is acceptable for v1, noted). `scripts/hash-password.mjs` for the user to generate the hash locally.
- `github.ts` — Git Data API: get ref → base commit → create blobs (text + base64 binaries) → tree → commit → update ref **non-force**; on 422 (ref moved) rebase onto new head and retry ×3. Commit message `"<Résumé> — via tableau de bord"`.
- `allowlist.ts` — publish rejects any path not matching `data/{menu,offers,hours}.js`, `assets/img/uploads.js`, `assets/img/uploads/*.{avif,webp}`, `index.html` (only the LDJSON block may differ — enforced by diffing outside markers).
- `datafiles.ts` — parse/serialize the JSON-literal data files (strict prefix/suffix check; refuse to write if parse fails); regenerate the LD-JSON block.
- `schemas.ts` — zod: prices 0–100 € step 0.1, text lengths, ISO dates (end ≥ start), times HH:MM, ≤2 services/day, ids/keys `[a-z0-9-]`.
- `images.ts` — sharp: rotate (EXIF), cap 2000 px, outputs `{stem}-{hash8}-{480,960}.{avif,webp}`; returns files + manifest entry.
- `translate.ts` — Claude call (**load the `claude-api` skill before writing it**; pick model there, likely Haiku 4.5 for cost) with a short brand-tone system prompt (reuse tone notes from `tools/reviews-reply/style-reference.md`), returns `{es,en}` via structured output.

### Endpoints
`POST /api/login`, `POST /api/logout`, `GET /api/state` (current menu/offers/hours/uploads + head sha), `POST /api/translate`, `POST /api/photo` (multipart ≤4 MB; client pre-shrinks), `POST /api/publish` (`{ baseSha, changes }` → validates, assembles files, one commit), `GET /api/status` (polls the live site's `data/*.js` until the published content is served → "En ligne ✓").

### Screens (React)
1. **Accueil** — live offers, today's hours/closure, last publish status.
2. **Offres** — list (active / à venir / terminées), form (FR title/text, price, photo via `<input type=file accept="image/*" capture>` with canvas downscale to ~2000 px JPEG, start/end) → **Traduire** (ES/EN editable) → **Aperçu** (same card markup/CSS as the site) → **Publier**; "Terminer maintenant" sets end = yesterday.
3. **Carte** — categories → items; inline price edit, "masqué" toggle, swap category photo.
4. **Horaires** — weekly grid, "Ajouter une fermeture" (dates + note, translated the same way).
One pending-changes model: edits accumulate locally, one **Publier** = one commit.

---

## Build order (each step leaves both projects working)

0. Save this spec to `taconaansite/docs/superpowers/specs/2026-10-02-dashboard-v1-design.md` (commit only if the user asks).
1. **Site data migration**: menu.js → JSON-literal; add empty offers.js / hours.js / uploads.js + script tags. Verify site renders identically (browser pane, `node tools/check-images.mjs`).
2. **Site rendering**: hours from data + closures + banner + JSON-LD markers; hidden items; uploads photos; offers section + CSS. Verify with temporary fixture data (offer active / expired / future, closure today, hidden dish) at 1440 + 375, FR/ES/EN, no console errors, then revert fixtures. `vercel.json` headers.
3. **Dashboard scaffold** + auth + `hash-password` script.
4. `datafiles`, `schemas`, `allowlist` + vitest (round-trip of the real `menu.js` byte-stable after one normalisation, invalid input rejected, allowlist bypass attempts rejected, Paris-date "active today" edge cases).
5. `github.ts` publish against branch `dashboard-test`.
6. `images.ts` + `/api/photo`; `translate.ts` + `/api/translate`.
7. Screens: Offres → Horaires → Carte → Accueil.
8. **User actions** (Claude guides, user does): create private GitHub repo `taconaan-admin`, create fine-grained PAT, create Vercel project + env vars, generate password hash locally. Claude does not create accounts, enter tokens, or push/deploy without explicit go-ahead.
9. End-to-end on `dashboard-test` → Vercel preview of the site; then the user switches `GITHUB_BRANCH=main`.
10. Update `README.md`, `docs/ATELIER.md` §9, and the project memory/handoff.

## Verification

- `npx vitest run` in `taconaan-admin` — all unit tests green.
- Site locally via `.claude/launch.json` (python http.server 4174) in the browser pane: fixture scenarios above at 1440 and 375, all 3 languages, open/closed badge correct for a closure day and a closed weekday, no console errors, no horizontal overflow, `node tools/check-images.mjs` = 0 errors.
- Dashboard dev server in the browser pane at 375 px: login (wrong password throttled), create offer with photo → translate → preview → publish to `dashboard-test`; confirm the commit on GitHub touches only allowlisted paths; confirm the site's preview deployment shows the offer within ~1 min and `curl -I …/data/offers.js` shows `no-cache`; end the offer → it disappears; add a closure → banner + badge + JSON-LD updated; hide a dish → gone from menu.
- Concurrency: push an unrelated commit to `dashboard-test` between "load" and "publish" → publish still succeeds without clobbering it.
