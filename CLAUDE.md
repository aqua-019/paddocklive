# fitzferalhunters (repo: paddocklive)

The live website for **Fitz Feral Hunters**: licensed, insured feral animal and vermin control for farmers and landholders. Based in Warragul, Gippsland, covering **all of Victoria**.

- Phone `0499 866 580` (`+61499866580`), email `fitzferalhunters1@gmail.com`, Instagram `@gippsland_gunner`.
- Domain: **fitzferalhunters.com** (attached to the Vercel project; `url` in site.json). Still `indexable: false` until launch.
- Owner: Robert Fitzgerald (grew up in Korumburra, based in Warragul). Insurer: Elders Insurance, $20m public liability.
- Built from Aqua's D700 design catalogue: the Paddock composition, SP-01 → SP-01e (mockups v0.1–0.3.2, repo `aqua-019/paddock1`), then SP-02 (v1.0) and SP-03 (v1.1, client content, FAQ and Credentials pages) in this repo.
- The build plan is `docs/v1.0-prompts.md`. Prompts 1–5 are done in v1.0. Prompt 6 (Resend domain, privacy page, launch) is what's left; the domain and ABN are in.

## The design is frozen

The client approved v0.3.2 exactly. Don't change tokens, type, the topographic sheet or the card colourway (ink `#1b2622`, gold `#a07a48`, champagne `#cdb682`, cream `#f8f6f2`).

| Item | Rule |
|---|---|
| Type | Cinzel 700 for h1/h2; Barlow Condensed for h3, plates and labels; Barlow for body. |
| Body text | 17px |
| New components | Reuse existing tokens and patterns: `.band`, `.slot` frame with registration ticks and "Location withheld" plate, `.btn-*`, `.review`, `dialog.sent`. |
| Hover | Colour changes only; no transform or shadow changes on hover. |
| Tap targets | ≥ 44px |
| Small screens | No horizontal scroll at 390px. |
| Motion | `prefers-reduced-motion` respected; nothing autoplays. |
| D700 records | New visible components go through the `d700-compose` skill in diff mode (next record SP-06), with citations added to `src/cites.py`. |

## Build and run

| Command | What it does |
|---|---|
| `python3 src/build.py` | Production build into `public/`. Public is committed; Vercel has no build step. |
| `python3 src/build.py --review` | The mockup chrome: varbar, spec sheet, X-ray, placeholder flags, `data-per`. Rebuild production before committing. |
| `python3 scripts/media.py` | Encodes new photos and videos from `media-src/` (gitignored) into `public/media/`. Strips all metadata, GPS included. Fills in `content/media.json`. |
| `node scripts/dev.mjs` | Local preview at http://localhost:3000 with the functions running. In-memory review store; mail off unless `.env.local` has keys. |
| `npm test` | Function tests (`node --test`, fetch stubbed, no keys needed). |
| `node scripts/mail-test.mjs` | One real test email through Resend, using `.env.local` (`vercel env pull .env.local`). |

Content lives in two files:
- `content/site.json`: copy, owner, insurer, credentials, services, clients, `faq_groups` (the /faq page), regions, photo ids, `google_review_url`, `turnstile_site_key`.
- `content/media.json`: every photo and video, with alt text and descriptions.

The runtime has **no npm dependencies**. Functions call Resend, Upstash and Turnstile over plain `fetch` (`api/_lib/services.js`). Dev-only tools can be devDependencies.

## Functions (`api/`)

**`enquiry.js`: the contact form.**
- Handler order: honeypot → Turnstile (if `TURNSTILE_SECRET_KEY`) → rate limit (if Redis) → validate → log to Redis (90-day TTL) → email Fitz via Resend.
- Without `RESEND_API_KEY` it returns `delivered:false`. The page's receipt dialog then says "not sent yet" and offers a pre-filled email to Fitz. **Never show "sent" when it wasn't.**
- Setup steps for the key and the domain: `docs/resend-setup.md`. `GET /api/health` shows what's switched on (booleans only); `node scripts/mail-test.mjs` sends one test email.
- Every send carries a Resend idempotency key (`enquiry/<ref>`, `review/<id>`), and a refusal is logged with a plain-words reason.

**`reviews.js`, `review-moderate.js`, `review-action.js`: reviews.**
- A submitted review is stored as pending. Fitz is emailed a signed link (HMAC with `REVIEW_SECRET`, valid 30 days).
- The moderation page changes nothing when opened with GET, because email scanners open links. Publish and decline happen by POST.
- Reviews are never edited or deleted. They are only declined for spam, non-customers, abuse, or a named location or person. This is ACCC guidance; keep the policy text on the page.
- No star ratings and no AggregateRating schema.
- Reviews need Redis. Without it the form shows "Reviews open soon".

## Client decisions (3 Nov 2026)

- ABN 22 477 254 408 shows in the footer and as `taxID` in the schema (approved by Aqua, 3 Nov 2026). It stays off the sample report.
- **Never publish licence or membership numbers.** Certificates and currency documents are "available on request".
- Works for farms and private landholders, and councils and land managers. Region priority: Gippsland first, then all of Victoria.
- Google Business Profile: service-area business, address hidden. Setup kit in `docs/google-business-profile.md`.
- The sample drone report (visual RGB survey, Oct 2026) is live at `/drone-report` from `content/report.json`. It's published without the ABN, the "Confidential" mark or the exact date, and the figures are cropped clean from his report.

## Mobile

- The call bar (`.cta-bar`) hides while the home hero's own buttons or the enquiry form are on screen; the footer carries the bar's height as bottom padding, so nothing sits under it.
- Checked at 320, 360, 390, 430 wide and 844×390 landscape: no overflow, tap targets ≥ 44px, no form text under 16px (iOS zoom).
- Media captions are the client's words (9 Nov 2026 edits). The home hero is `fitz-hero` (Fitz at sunset); the About bio is one large square `fitz-portrait` showing his full figure, not just his face.
- Every gallery video sits in the same 16:9 frame; thumbnails fill it (cover) and the clip shows uncropped once playing.

## Rules

- Secrets are never committed. `.env.example` lists every variable.
- Every change ends with: build → `npm test` → Playwright check (no review chrome in production, no console errors, 390px, hover census, contrast) → commit → push → confirm the Vercel deployment is READY.
- Media:
  - Never commit originals.
  - Check every new clip for burned-in coordinates, property names, number plates, and faces of people who haven't agreed.
  - Ask before publishing any clip that shows an animal being shot.
