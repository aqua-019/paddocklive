# SP-04 · Fitz Feral Hunters · the sample report as proof (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Measured state before the diff: SP-03 LIVE v1.1, 25/25 VERIFIED.
Brief (Aqua, 3 Nov 2026): put more visual weight on the sample drone report, for a client on the fence between Fitz and a competitor. None of the five competitors offers drone scouting or a written deliverable (competitor review), so the report is the one piece of proof nobody else can show.
Lenses: LENS-02 (the proof is real and says so: "Real job · sample report"), LENS-04 (one gold card per page; it never competes with Request a quote), LENS-15.

Delta:
- report card: a cream card with a gold rule, holding a miniature of the report's first page (run line, title, three meta rows in the report's dark cells, figure 1), plus a tag, a heading, one sentence and a gold "Read the report" button. The whole card is one link.
  - home: it leads the dark drone band, replacing the plain button row
  - Services: under the drone service
  - Contact: under the contact details, headed "Still deciding?"
- hero proof link: a gold-outlined chip under Request a quote / Call ("Real job: see a sample drone survey report"), so the report is offered in the first screen
- phones: the card stacks and drops the meta rows (420px tall on the home band)
- fix: the contact page's "Click to copy" hint was inheriting the 26px number size; it's now caption size

SP-04 :: Fitz Feral Hunters :: SURFACES=home (hero, drone band) · services · contact :: CITES=SP-03 set + D0293 (Social-proof inline CTA) · D4643 (Evidence-count chip row) · D3813 · D0433 :: FLOOR=unchanged + 2 delta asserts

## ASSERT lines (delta)
ASSERT :: home, services, contact :: one report card per page; hero proof link in the first screen, ≥ 44px; card ≤ 640px tall on a 390px phone :: PER=D0293 · D4643
ASSERT :: all :: hover recolours only, incl. the card and the proof link (23 controls) :: PER=D3171 · LAW-03

MEASURE :: probe rounds=2 (round 1: the v1.1 check still looked for the old drone-band button; updated to the card) · final 26/26 VERIFIED (docs/verdicts-v1-1.txt) · npm test 13/13

FOLD :: D0293 → when one piece of proof is unique in the market, give it a shape (a miniature of the real document) rather than a louder button; a picture of the deliverable is read before any label :: Fitz Feral Hunters v1.1
