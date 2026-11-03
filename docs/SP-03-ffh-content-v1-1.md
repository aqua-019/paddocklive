# SP-03 · Fitz Feral Hunters · LIVE v1.1 — client content, FAQ and Credentials pages (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Measured state before the diff: SP-02 LIVE v1.0, 19/19 VERIFIED (docs/verdicts-v1-0.txt).
Brief: the client's written answers of 3 Nov 2026, added and implemented: no licence or membership numbers; insurer Elders Insurance, $20m public liability; farm security as a service; FAQ answers (carcass disposal, quotes, neighbours and night noise, stock safety); his bio; farms plus council / land-manager work; Gippsland first, then Victoria. Aqua: an FAQ page and a Credentials page now, orientation later.
Lenses: LENS-02 leads (his words, his decisions: nothing published he didn't supply or approve; "numbers shared with you directly" says why none appear), LENS-04 for the new disclosures and cards, LENS-14 unchanged.

Delta:
- two pages in the main nav: /credentials (licences wall, insurance and paperwork cards, codes and permits) and /faq (11 answers in three groups, topic links, FAQPage schema)
- the nav carries seven links: between 900 and 1199px the datum hides and link padding tightens so it stays on one row
- Services: "Who I work for" (farms and landholders · councils and land managers), farm security as a service row, the first question of each FAQ group plus a link to the page
- Home: nine service tiles (six species, farm security, night and thermal, thermal drone) for a full 3×3; a "Credentials and insurance in full" link under the wall; triad and service-area copy name Elders and the region priority
- About: Robert Fitzgerald's bio in his words leads; insurance line names Elders; link to the Credentials page
- LocalBusiness schema: founder Robert Fitzgerald; knowsAbout adds thermal drone scouting and farm security
- /drone-report: his real survey report (visual RGB, Gippsland, Oct 2026) rebuilt as a document sheet in the site's type, with the two figures in the location-withheld frame. Removed before publishing: the ABN, the "Confidential" footer, the exact day. Linked as the drone band's main button, a button on the drone service, the gallery intro, the FAQ drone answer and the footer.
- ABN 22 477 254 408 in the footer and as schema taxID (approved by Aqua).

SP-03 :: Fitz Feral Hunters :: SURFACES=credentials (new) · faq (new) · drone-report (new) · services · home · about · header :: CITES=SP-02 set + D0377 · D1225 · D3074 · D3821 · D3813 · D0367 :: FLOOR=unchanged + 5 delta asserts

## ASSERT lines (delta)
ASSERT :: header (900/1024/1280) :: seven nav links and the quote button fit on one row with no overflow :: PER=LENS-15
ASSERT :: faq :: 11 answers as native disclosures; FAQPage schema lists the same 11; every topic link resolves; one H1 :: PER=D0377 · D3074
ASSERT :: credentials, about, services, home :: Elders Insurance named; 0 licence or membership numbers; bio, farm security, clients, nine tiles, founder in schema :: PER=LENS-02 · D3813
ASSERT :: home, about, gallery, credentials, drone-report :: every image loads after scrolling :: PER=D0404
ASSERT :: drone-report :: 5 sections, 2 figures, one H1; no ABN, 'Confidential' or exact date; linked from the drone service :: PER=LENS-02 · LENS-07

MEASURE :: probe rounds=2 (round 1: a review left in the dev server's memory store by an earlier run — fresh server) · final 25/25 VERIFIED (docs/verdicts-v1-1.txt; SP-02 asserts re-run unchanged) · npm test 13/13 · rig: Playwright Chromium against scripts/dev.mjs

FOLD :: LENS-02 → when a client withholds a detail (licence numbers), say on the page why it's absent and how to get it; an unexplained gap reads as something to hide :: Fitz Feral Hunters v1.1
FOLD :: D0377 → a FAQ in the client's own sentences, grouped by the moment the reader is in (pricing, on the job, paperwork), beats a long flat list; keep one question per group on the service page and link the rest :: Fitz Feral Hunters v1.1
