# SP-05 · Fitz Feral Hunters · v1.0 final: mobile pass, client media edits, Resend ready (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Measured state before the diff: SP-04, 26/26 VERIFIED.
Brief (Aqua, 9 Nov 2026): make the phone versions perfect; apply the client's caption edits; add the new clips and photos; the About bio uses one square portrait; have Resend ready for keys.

## Audit (before)

Measured at 320, 360, 390 and 430 wide, plus 844×390 landscape, on 10 pages:
- **Footer under the call bar:** the footer's last lines sat 24–29px under the sticky call bar.
- **Doubled call-to-action:** the call bar duplicated the hero's own Request / Call buttons in the first screen.
- **320px:**
  - the bar's "Call 0499 866 580" wrapped to two lines
  - the hero email broke mid-word ("fitzferalhunters1@g / mail.com")
- **Contact page:** the phone and email links were 23–24px tall.
- **404:** the page links were 20px tall, and the copy said "five pages".
- **Footer on phones:** the Pages heading sat flush under the contact line, and 14 links ran in one long column.
- **Gallery:** upright clips were letterboxed in wide frames, and there were ten videos to scroll past before the photos.
- **Mobile menu:** stayed open on Escape and on an outside tap.
- **Home-screen icon:** none.

## Delta

**Call bar**
- Hidden while the home hero's own buttons (or the enquiry form) are on screen; slides in after (reduced motion: no slide).
- Inert while hidden.
- Phone icon added; on screens under 360px the label drops "Call".
- The footer carries the bar's height as bottom padding.

**Tap targets**
- Phone and email links on the Contact page and in the footer: padded to 44px+.
- 404 links: 44px rows, copy "The main pages are below".

**Phones under 700px**
- **Footer:** the page list runs in two columns.
- **Hero contact line:** wraps whole words.
- **Service tiles:** tighter, with "Details →" as a text link, so the nine tiles are about 30% shorter.
- **Sample report link:** full width.

**Gallery**
- Video / Photos jump links with counts.
- Upright clips in 3:4 frames, square clips in 1:1.

**Mobile menu**
- Closes on Escape and on an outside tap; aria-expanded kept in step.

**Home-screen icon:** a 180px apple-touch-icon, the rifle mark on the card green.

**Landscape phones:** the header doesn't stick, and the bar is slimmer.

**Client edits (9 Nov)**
- Captions:
  - "Sambar deer in the forest" / "A sambar deer located in the forest."
  - "Thermal monocular used to spot deer on the hill."
  - Fig. 02 "Rifle and thermal scope setup."
  - Fig. 03 "Fitz working."
- New clips:
  - "Stock identified on thermal", the first 9.4s of the cattle clip
  - "Deer crossing the hill"
- New photos: two rig photos.
- About: one square portrait, cropped from his graphic (head to waist, scope left out), without the location plate.

**Resend**
- Idempotency keys on every send; tags.
- Plain-words reasons for refusals in the logs.
- `fromCheck()` validates `ENQUIRY_FROM`.
- `GET /api/health` reports booleans only.
- `scripts/mail-test.mjs` sends one test email.
- `docs/resend-setup.md` is the step-by-step for the session with Fitz. The domain is on Vercel DNS with no conflicting records.

SP-05 :: Fitz Feral Hunters :: SURFACES=all (mobile) · about · gallery · api/health :: CITES=SP-04 set + D0553 (Bottom-anchored actions) · D0386 · D0642 :: FLOOR=unchanged + 3 delta asserts

## ASSERT lines (delta)
ASSERT :: mobile (iPhone 13) :: the call bar is hidden beside the hero buttons and back on scroll; it never covers the footer (0px on 4 pages); About shows one square portrait with no plate; the menu closes on an outside tap :: PER=LENS-15 · D0553
ASSERT :: gallery :: the client's caption edits and the new media are present; the jump links resolve :: PER=LENS-02
ASSERT :: api/health :: reports mail off honestly, exposes no secret :: PER=contract

MEASURE :: mobile audit after: 0 overflow and 0 footer overlap at 5 viewports × 10 pages; tap targets ≥ 44px everywhere outside running text; no form text under 16px · probe 29/29 VERIFIED (docs/verdicts-v1-0-final.txt) · npm test 17/17

FOLD :: D0553 → a sticky call bar should give way to the page's own call-to-action, not repeat it: observe the hero buttons and the form, and let the footer carry the bar's height instead of padding main :: Fitz Feral Hunters v1.0
FOLD :: D0386 → when a component already uses ::after (here, a tap-area expander), a decorative arrow on the same pseudo-element inherits its absolute position; reset position or use the other pseudo-element :: Fitz Feral Hunters v1.0
