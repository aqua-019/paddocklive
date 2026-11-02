# SP-02 · Fitz Feral Hunters · LIVE v1.0 — working site over the frozen Paddock design (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Measured state before the diff: SP-01e PADDOCK v0.3.2, client-approved (paddock1 docs/verdicts-v3-2.txt, 9/9).
Brief: separate repo and deployment; the buttons work (email the owner); numbers tap-to-call on phones and copy on desktop; a working reviews section; Fitz's MP4s and photos on the site; a "sent" popup showing what was submitted; Resend wired so it works the moment the account exists.
Lenses: LENS-02 leads the new work (a receipt never claims "sent" when it wasn't; review policy stated in plain words; media plates say what is withheld), LENS-04 governs every control, LENS-06 the weight (nothing downloads until play), LENS-14 unchanged.

Delta:
- production build by default: varbar, spec sheet, X-ray, placeholder flags and data-per removed (kept behind `--review`)
- real photos (hero, about, gallery) in the registration-tick frame, no scrim on real photos
- eight videos: native player under a play button, posters, preload none, text descriptions, one plays at a time
- every phone number is one `tel:` component: touch dials, a fine pointer copies with a toast (input-modality attribute on `<html>`)
- receipt dialog (native `<dialog>`) for enquiries and reviews in three states: sent · not sent yet (mail off: pre-filled email + call) · failed
- reviews: pending → Fitz moderates from a signed link (GET shows, POST acts) → published cards on /reviews and home; ACCC-style policy text; no stars, no AggregateRating
- media pipeline strips all metadata and fails if any location tag or extra stream survives

SP-02 :: Fitz Feral Hunters :: SURFACES=home · services · about · gallery · contact · reviews (new) · moderation (function) :: CITES=SP-01e set + D2211 · D0404 · D2201 · D6523 · D0441 · D0381 · D0979 · D0592 · D2184 · D0642 · D0883 · D0367 · D0860 · D0386 · D2300 · D3813 :: FLOOR=unchanged + 19 delta asserts

## ASSERT lines (delta)
ASSERT :: all :: production carries no review chrome (varbar, spec, .flag, data-per = 0 on every page) :: PER=production mode
ASSERT :: home, gallery :: no video bytes until play; posters, preload=none, a text description per video :: PER=D6523 · D0404 · LAW-23
ASSERT :: gallery :: a play button over each poster hands over to native controls; without JS the native controls show :: PER=D0441 · D0381
ASSERT :: all (desktop) :: clicking any phone number copies 0499 866 580 and announces "Number copied" in a polite status region; URL unchanged; Enter does the same :: PER=D0386 · D0642 · D2300
ASSERT :: all (touch) :: tapping a number is not intercepted — the dialler opens :: PER=D2300
ASSERT :: contact :: with mail off, the receipt says "Not sent yet", lists the enquiry and offers a pre-filled email to Fitz and Call; closing keeps the form filled :: PER=D0979 · LENS-02
ASSERT :: contact :: with mail on, the receipt says "Sent to Fitz" with a reference; Esc closes to the inline confirmation :: PER=D0979 · D2184 · D0592
ASSERT :: contact :: server field errors land on the matching field :: PER=LAW-23
ASSERT :: reviews :: a review goes to Fitz with a signed link; opening it changes nothing; Publish shows it on /reviews and home :: PER=D0367 · D0883
ASSERT :: all :: hover recolours only (play, numbers, buttons, copy, socials) :: PER=D3171 · LAW-03
ASSERT :: home, gallery :: captions ≥ 7:1, video titles ≥ 12:1, drone-band captions ≥ 7:1, review meta ≥ 4.5:1 :: PER=D0192 · LENS-15
ASSERT :: all (390px) :: no horizontal scroll; play target 68px :: PER=LENS-15 · LAW-23
ASSERT :: media :: every output re-probed: one video stream, no location/creation/make/model tags :: PER=D2211 · LENS-07

MEASURE :: probe rounds=3 (round 1: probe picked a region that isn't on the list; round 2: memory store carried a review over from round 1 — fresh server) · final 19/19 VERIFIED (docs/verdicts-v1-0.txt) · npm test 13/13 · media 27 MB total (8 videos 0.7–9.0 MB, 4 photos) · rig: Playwright Chromium against scripts/dev.mjs

FOLD :: D0979 → a receipt is only honest if it can say "not sent": design the three states (sent · not yet · failed) before the happy path, and make the not-yet state useful (pre-filled email) rather than an apology :: Fitz Feral Hunters v1.0
FOLD :: D2300 → decide tel: behaviour by input modality (hover:none + pointer:coarse), never by user agent; leave the link a plain tel: so no-JS and touch both dial :: Fitz Feral Hunters v1.0
FOLD :: D6523 → for a small business with a handful of clips, preload=none + a poster + a play button costs nothing until intent; it beats a third-party player on weight and privacy :: Fitz Feral Hunters v1.0
