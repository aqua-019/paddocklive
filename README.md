# Fitz Feral Hunters: the live site

This is a static multi-page site with Vercel functions for Fitz Feral Hunters (Warragul, Gippsland, covering all of Victoria). It's the production version of the D700 Paddock composition, which the client approved at mockup v0.3.2 (`aqua-019/paddock1`).

## What works in v1.0

- **Phone numbers.** Tapping a number on a phone opens the dialler. Clicking one on a desktop copies it and shows a "Number copied" note. Email addresses open the mail app and have a Copy button.
- **Enquiry form.** It emails Fitz through Resend with the customer set as reply-to. When it's sent, a receipt dialog shows the visitor exactly what was sent, with a reference.
  - Until the Resend key is set, the receipt says it **hasn't** been sent yet. It offers an "Email it to Fitz" button with everything pre-filled, plus Call.
- **Reviews.**
  - Customers submit a review at `/reviews`. Fitz gets an email with a signed link and publishes or declines it from his phone.
  - Published reviews appear on `/reviews` and on the home page.
  - The policy (genuine reviews go up, good or bad; none are edited) is shown beside them, following ACCC guidance.
- **Video and photos.** There are eight clips (thermal drone, trail cameras, deer) and four photos.
  - Videos play in the native player with a play button over the poster. Nothing downloads until you press play.
  - Every file is re-encoded with all metadata stripped (GPS included).

- **Pages:** Home, Services, Credentials, About, Gallery, FAQ, Contact (main nav), plus Reviews (footer and home). The FAQ and Credentials content is Fitz's own, from 3 Nov 2026.

## Layout

```
content/site.json     copy, owner, insurer, credentials, services, clients, faq_groups, regions, photo ids, google_review_url, turnstile_site_key
content/media.json    every photo and video: alt text, captions, descriptions (encoder fills in sizes and paths)
src/build.py          generator → public/   (python3 src/build.py · --review for the mockup chrome)
src/css.py · topo.py · cites.py
scripts/media.py      encode media-src/ → public/media/ (ffmpeg + Pillow; strips metadata; content-hashed names)
scripts/dev.mjs       local preview with the functions: node scripts/dev.mjs → http://localhost:3000
api/enquiry.js        contact form → email Fitz
api/reviews.js        GET published reviews · POST a new (pending) review
api/review-moderate.js, api/review-action.js   Fitz's publish/decline screens (signed links)
api/_lib/             services (Resend, Upstash, Turnstile), store, reviews, page helpers
tests/api.test.mjs    npm test
docs/                 SP records, probe verdicts, the v1.0 prompt series, the Google Business Profile kit
```

## Switching things on (Vercel → Settings → Environment Variables)

| To get | Set | Notes |
|---|---|---|
| Enquiries emailed to Fitz | `RESEND_API_KEY`, `ENQUIRY_TO` | Create the Resend account **with fitzferalhunters1@gmail.com**. Until there's a verified domain, Resend can only deliver to the account's own address. |
| Mail from the domain, plus customer auto-replies | `ENQUIRY_FROM`, `AUTO_REPLY=1` | After verifying the domain in Resend (DNS records). |
| Reviews, enquiry log, rate limits | Upstash Redis | Add it from Vercel → Storage → Marketplace. It sets `KV_REST_API_URL` / `KV_REST_API_TOKEN` itself. |
| Review moderation links | `REVIEW_SECRET` | Any 32 or more random characters. |
| Bot check (optional) | `TURNSTILE_SECRET_KEY` plus `turnstile_site_key` in site.json | Free Cloudflare Turnstile site. |

Redeploy after changing variables.

## Adding photos and videos

1. Put the originals in `media-src/`. It's gitignored, so originals are never committed.
2. Add an entry to `content/media.json`: `id`, `type`, `kind`, `source`, `title`, `caption`, plus `alt` (photos) or `description` (videos). Optionally add `trim`, `poster_at`, or `home: true` (puts a video on the home page).
3. Run `python3 scripts/media.py`, then `python3 src/build.py`. Commit and push.

Before publishing, check each clip for burned-in coordinates, property names, number plates, and faces of people who haven't agreed.

## Launch checklist

1. Domain, then set `url` in site.json and `SITE_URL`.
2. Set `"indexable": true` (this removes `noindex` and opens robots.txt).
3. ABN in site.json.
4. Verify the domain in Resend; set `ENQUIRY_FROM` and `AUTO_REPLY=1`.
5. Add a privacy page.
6. See Prompt 6 in `docs/v1.0-prompts.md`.

Compiled against STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
