# SP-09 · Fitz Feral Hunters · Home splash (PREVIEW branch `splash-preview`, not on production)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses

**Brief** (Aqua, 16 Nov 2026): "a splash page with the logo… a sequence splash that bleeds transparent into the homepage". Under consideration, so it's built on a branch and deployed as a Vercel preview. Production (main) is unchanged.

**Switch:** `"splash": true` in `content/site.json`. With it absent or false, no markup, CSS or script ships.

## The sequence (home page only, about 2.3 s)

1. **0–1.1 s:** the page's own contour map traces itself in gold on the ink (Aqua, 16 Nov 2026: "topographical maps with lines extending in real time and fast", colours to match).
   - It uses the same tile as the page's background, at the same size and origin (600 px, or 450 px under 700 px wide, from the top-left), so as the ink clears the gold lines hand over to the page's own contours.
   - Each contour grows both ways from its point nearest the badge, so the map spreads outward from it: delay = distance ÷ farthest distance × 560 ms, and each half takes 260–620 ms depending on its length.
   - Colours are gold `#5d4f36` (ordinary contours, 0.9 px) and champagne `#8a7d5b` (index contours, 1.5 px). These are the site's gold and champagne mixed into the ink, so there are no darker dots where pieces join.
   - It's drawn on a canvas that adds only each frame's new piece of line. Long frames measured with the contours on match those with them off; they come from the page's own load.
   - At the same time, Fitz's badge settles in on top, scaling 0.9 → 1 and fading in (D4246).
2. **0.9–1.3 s:** hold, with the map complete.
3. **1.3–2.3 s:** the badge flies to the header logo and lands on it to the pixel (D5131, measured Δ 0 px). Meanwhile the ink bleeds away from where the badge sat: a soft circle opens like a scope and fades, uncovering the home page that has been underneath the whole time.
4. The cover is removed, and the header badge (hidden during the run) shows.

One easing voice throughout: the site's `--ease-out` (LAW-16).

## Guards

- **It runs only if all of these hold:**
  - JavaScript is on
  - `prefers-reduced-motion` is "no-preference" (D3453)
  - there's no `#hash` in the address
  - this browser session hasn't seen it yet (`sessionStorage`)
- **`?splash`** replays it for review (still never under reduced motion).
- **It plays only on the home page.** Other pages never get it.
- **Any tap, key, wheel, touch-move or scroll skips it** (a 240 ms fade). There's also a Skip button.
- **The badge image isn't ready within 900 ms:** the splash is skipped rather than holding an empty ink screen.
- **The page is already scrolled past 40 px:** no splash.
- **Failsafes in CSS alone:**
  - the cover fades out at 4.5 s
  - the header badge reappears at 4.8 s, even if the script never runs to the end
- **The cover is `aria-hidden`.** The page underneath is in the DOM and readable from the start; the Skip button isn't in the tab order (any key skips).
- **Stacking:** `--z-splash: 9999`, a named top token (D4252).

## Measured (local preview, 17 Nov 2026)

```
VERIFIED :: home (1280) :: first visit plays; lands on the header logo (Δx 0 Δy 0 Δw 0); cover removed; header badge shows
VERIFIED :: home / services :: once per session; any key skips (319 ms); #hash and /services never show it
VERIFIED :: home (reduced motion) :: off, even with ?splash
VERIFIED :: home (no JS) :: cover never shows
VERIFIED :: home (iPhone 13) :: plays and clears; no overflow
VERIFIED :: all :: 0 console errors
```

## Decision before it goes to production

- **CLAUDE.md says "nothing autoplays".** Shipping this means changing that rule, for example to "nothing autoplays except the first-visit home splash (SP-09)".
- **D4252 notes that product estates have no loader at all.** A splash adds about 2.3 s before a first-time visitor can read the page. It's skippable, and it shows only once per session.
- **Search engines and link previews are unaffected.** The content is in the HTML from the start, and the share card is a separate image.

FOLD :: D5131 → a splash that ends where the logo lives (FLIP from the centre to the header badge, measured to 0px) reads as arrival, not delay; hide the real logo during the run and let the flying one become it :: Fitz Feral Hunters SP-09 preview
FOLD :: D4246 → gate a first-visit splash on a decoded image with a short deadline; if the mark isn't ready, skip, because an empty ink screen is the worst frame a splash can show :: Fitz Feral Hunters SP-09 preview
