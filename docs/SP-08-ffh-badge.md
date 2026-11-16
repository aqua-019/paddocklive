# SP-08 · Fitz Feral Hunters · Fitz's badge as the logo (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses

**Measured state before the diff.** v1.2 live on fitzferalhunters.com.au, probe 35/35. The logo was the rifle lockup:
- `brand/logo-lockup.png`, 198 × 56 px in the header and 64 px tall in the footer
- tab icon: a green "F" square
- share card: the lockup on ink

**Brief** (Aqua, 16 Nov 2026):
- Fitz has made his own logo for the website. Display it abundantly, and intelligently, across the site, then push and redeploy.
- A splash "sequence that bleeds transparent into the homepage" is under consideration. It's built separately as a preview (see the end of this record).

**The badge.** A round emblem on dark green, with a gold ring:
- a lever-action rifle
- FITZ / FERAL HUNTERS
- mountains, pines and a stag

It was supplied as a 952 × 954 JPEG with 15 KB of phone metadata. `scripts/brand.py` cuts the circle 1.5 px inside the ring, using a 4× supersampled mask, so it has a clean anti-aliased edge and no white fringe (the brightest rim channel is 176/255). The script strips all metadata and writes:
- WebP at 96, 160, 256, 384, 512 and 768 px
- a 512 px PNG
- tab icons at 32 and 64 px
- a 180 px home-screen icon (the badge on ink)
- a 1200 × 630 share card, rendered from HTML with Cinzel and Barlow

## Delta

| Where | What |
|---|---|
| Header, every page | Badge (56 px; 44 px under 900) + Cinzel wordmark, FITZ over FERAL HUNTERS, gold-light and cream. 186 px wide at 900–1280, inside the old 198 px, so the nav fit is unchanged. The link's name is "Fitz Feral Hunters, home". |
| Footer, every page | Badge (104 px) + wordmark + the tagline in Barlow Condensed. |
| Home hero | Badge as a seal on Fitz's photo: bottom right, over the grass, 136 px (96 px on a phone), 30 px over the frame's bottom edge, with a soft drop shadow. It never covers Fitz or the tripod. |
| Credentials, Contact | Page head with a seal (`seal_head`). It sits on the right on wide screens (136 px / 104 px) and above the meta line on a phone (76 / 72 px). |
| About | Sign-off after the bio: the badge (88 px), Robert Fitzgerald, and Fitz Feral Hunters · Warragul, Gippsland. |
| Drone report | The badge as letterhead, top right of the report head (80 px; 60 px under 600). |
| 404 | The badge above the eyebrow (120 px). |
| Head | Tab icons 32 and 64 px, a home-screen icon, and the share card `og-badge-1200x630.png`. New file names, because images are cached for 7 days. |
| Schema | `logo` → `/brand/fitz-badge-512.png`; `image` → the new share card. |
| Removed | `favicon.svg` (the old "F") and `og-1200x630.png`. `/favicon.png` is now the 64 px badge. |

**Kept:** the old lockup files in `public/brand/`, for the shop mockup and Fitz's printed card on About. The card still shows the rifle lockup; that's a question for Fitz.

## ASSERT lines (delta)

ASSERT :: all pages :: the badge loads in the header and footer; the wordmark names the business; the badge itself is decorative (alt="") :: PER=D0443 · D0401
ASSERT :: header :: srcset serves a file ≥ 2× the drawn size at 2× and 3× :: PER=D0401
ASSERT :: home hero :: the seal's left edge is ≥ 55% across the photo (clear of Fitz) and inside the page :: PER=D1150
ASSERT :: header/footer/About :: wordmark, tagline and sign-off text ≥ 4.5:1 :: PER=D0192
ASSERT :: header :: lockup ≤ 198px at 900/1024/1280; a 320px phone fits badge, wordmark and Menu :: PER=LENS-15
ASSERT :: head/schema :: icons, share card and schema logo are served as PNG :: PER=D0443
ASSERT :: all :: no change to hover, nav fit, overflow or contrast elsewhere (site probe) :: PER=D3171 · LAW-03

MEASURE :: docs/verdicts-sp08-badge.txt 7/7 VERIFIED · site probe 35/35 (fresh review store) · npm test 23/23 · 17 Nov 2026

FOLD :: D0401 → a detailed round emblem stays recognisable down to 44px as a shape and colour, not as text; pair it with a live-text wordmark in the display face rather than shrinking a lockup image, and the name stays legible and selectable :: Fitz Feral Hunters v1.3
FOLD :: D1150 → a seal earns its place where trust is the job of the page (credentials, contact, the report); on the hero it stamps the photo's empty corner, measured against the subject, never over a face :: Fitz Feral Hunters v1.3
