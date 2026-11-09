#!/usr/bin/env python3
"""Generate the Fitz Feral Hunters site (Paddock composition, D700 SP-01b) from content/site.json.

    python3 src/build.py                    # writes public/*.html, sitemap, robots, favicon
    python3 src/build.py --artifact FILE    # single-document review build (hash-routed) for the claude.ai artifact

Spec-first: every component carries data-per with the catalogue records it honours; the spec sheet
dialog lists the full cited set. The D700 corpus itself is not in this repo — names of cited entries
ship in src/cited-names.json. The contour field is generated deterministically at build time (src/topo.py).
"""
import re, json, html, pathlib, datetime, sys, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from css import CSS
import cites, topo

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(__file__).resolve().parent
PUB = ROOT / 'public'
S = json.loads((ROOT / 'content' / 'site.json').read_text())
NAMES = json.loads((SRC / 'cited-names.json').read_text())
STAMP = "D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses"
X = cites.PADDOCK
SEED = "fitzferalhunters-paddock"
ARTIFACT = '--artifact' in sys.argv
SHEET = bool(S.get('sheet_layer', False))   # the v0.2 topographic layer: off from v0.3.1 at the client's request
SHEET_MAP = SHEET and bool(S.get('sheet_map', False))   # the locality map + key: off at the client's request from v0.3.1
SHEET_KEYS = {'topo', 'meta', 'scalebar', 'map', 'legend'}
MAP_KEYS = {'map', 'legend'}
TOPO_SCALE = 0.5   # v0.3.2: the 1200px tile is drawn at 600px — 3× the line density of v0.2
# v1.0: production is the default build. `--review` (and the artifact) bring back the mockup chrome:
# the varbar, spec sheet, X-ray, placeholder flags and data-per citations.
REVIEW = ARTIFACT or '--review' in sys.argv
MEDIA = {i['id']: i for i in json.loads((ROOT / 'content' / 'media.json').read_text())['items']}
REPORT = json.loads((ROOT / 'content' / 'report.json').read_text())
TURNSTILE = S.get('turnstile_site_key', '')
from urllib.parse import quote as urlquote

def esc(s): return html.escape(str(s), quote=True)

def flag(text, style=''):
    """A dashed placeholder note — review build only; production renders nothing."""
    return f' <span class="flag"{style}>{esc(text)}</span>' if REVIEW else ''

def per(key):
    if not REVIEW: return ''
    if key in SHEET_KEYS and not SHEET: return ''
    if key in MAP_KEYS and not SHEET_MAP: return ''
    ids = list(cites.SHARED.get(key, [])) + list(X.get(key, []))
    ds = [i for i in ids if re.match(r'^D\d{4}$', i)]
    return f' data-per="{" ".join(dict.fromkeys(ds))}"' if ds else ''

# ---------------------------------------------------------------- tokens + stylesheet
TOKENS = """
  /* PALCAND "FFH Card" — sampled from the client's card: green #1b2622, gold #a07a48, champagne #cdb682, near-white type; ground kept from PAL Noma Forest Season */
  --bg:#f8f6f2; --surface:#f1eee8; --surface-2:color-mix(in srgb, var(--bg), var(--ink) 7%);
  --ink:#1b2622; --ink-2:color-mix(in srgb, var(--ink) 80%, var(--bg)); --ink-3:color-mix(in srgb, var(--ink) 38%, var(--bg));
  --chrome:#1b2622; --chrome-2:color-mix(in srgb, var(--chrome), #ffffff 7%);
  --gold:#a07a48; --gold-light:#cdb682; --gold-ink:color-mix(in srgb, var(--gold), var(--ink) 32%);
  --accent:color-mix(in srgb, var(--chrome), #ffffff 12%); --accent-ink:#f8f6f2;
  --line:color-mix(in srgb, var(--ink) 15%, transparent); --line-strong:color-mix(in srgb, var(--ink) 40%, transparent);
  --wash:color-mix(in srgb, var(--ink) 8%, transparent); --wash-press:color-mix(in srgb, var(--ink) 16%, transparent);
  --accent-hover:color-mix(in srgb, var(--accent), #ffffff 8%); --accent-press:color-mix(in srgb, var(--accent), var(--ink) 18%);
  --focus:#2c84db; --focus-dark:#7cb8ff; --err:#9b2c20; --ok:#2E6E4E;
  --foot-bg:var(--chrome); --foot-ink:#f8f6f2; --foot-line:color-mix(in srgb, #f8f6f2 18%, transparent);
  --grain-blend:multiply; --grain-alpha:.16; --body-track:0; --ring:none;
  --scrim:linear-gradient(to top, rgb(27 38 34 / .82), rgb(27 38 34 / 0) 70%);
  --sp:"SP-01c PADDOCK";
"""
GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 1 0'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
TOPO_SVG = topo.contour_svg(seed=SEED, color='#1b2622', cells=120, interval=1/30, minor_width=1.3, index_width=2.2, minor_alpha=0.11, index_alpha=0.17)
TOPO_URI = topo.svg_data_uri(TOPO_SVG) if ARTIFACT else '/topo-tile.svg'
import base64
def asset(path):
    """Brand asset URL: a site path, or a data URI in the single-file artifact build."""
    if not ARTIFACT: return path
    p = PUB / path.lstrip('/'); mime = 'image/png' if p.suffix == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()
css = (CSS.replace('@@TOKENS@@', TOKENS).replace('@@STAMP@@', STAMP).replace('@@GRAIN@@', GRAIN)
          .replace('@@TOPO@@', TOPO_URI).replace('@@SCHEME@@', 'light')
          .replace('background-size:1200px 1200px,', f'background-size:{int(1200*TOPO_SCALE)}px {int(1200*TOPO_SCALE)}px,')
          .replace('background-size:900px 900px;--topo-alpha:.8', f'background-size:{int(900*TOPO_SCALE)}px {int(900*TOPO_SCALE)}px;--topo-alpha:.85'))
if not SHEET:
    css = re.sub(r'body::after\{[^}]*\}', '', css)                       # the contour/grid field
    css = css.replace("[data-sheet='off'] body::after{display:none}", '')
    css = re.sub(r'@media \(max-width:699px\)\{body::after[^}]*\}\}', '', css)
    css = css.replace('.band.alt{background:color-mix(in srgb, var(--surface) 86%, transparent)}', '')
    css = css.replace('.tile,.ghost,.field input,.field textarea,.confirm,.summary{background:color-mix(in srgb, var(--bg) 92%, transparent)}', '').replace('.tile{background:color-mix(in srgb, var(--bg) 94%, transparent)}', '')
css += """
.varbar .hide{margin-inline-start:4px}
.varbar[hidden]{display:none}
.notfound{padding-block:96px}
@layer components{
/* v1.0 · real photos and video in the registration-tick frame */
figure.slot{margin:0}
.slot.photo picture{display:contents}
.slot.photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.slot.video{background:var(--chrome)}
.slot.video::before,.slot.video::after{display:none}
.slot.video video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:var(--chrome);z-index:1}
.slot .corner,.slot .plate,.slot .dur{pointer-events:none}
.slot.video .corner.bl,.slot.video .corner.br{display:none}
.slot.video .plate{color:var(--gold-light);background:color-mix(in srgb, var(--chrome) 78%, transparent)}
.slot.photo::before,.slot.photo::after{display:none}
.slot.video .corner.tl{display:none}
.slot.video .play{position:absolute;inset:0;z-index:3;display:grid;place-items:center;background:transparent;border:0;padding:0;margin:0;cursor:pointer;border-radius:var(--radius)}
.slot.video .play span{width:68px;height:68px;border-radius:50%;background:var(--gold-light);display:grid;place-items:center;transition:background-color var(--t-hover,.2s) cubic-bezier(.165,.84,.44,1)}
.slot.video .play span::before{content:"";margin-left:6px;border-style:solid;border-width:13px 0 13px 21px;border-color:transparent transparent transparent var(--chrome)}
.slot.video .play:hover span{background:color-mix(in srgb, var(--gold-light), #ffffff 18%)}
.slot.video .play:focus-visible{outline:3px solid var(--focus-dark);outline-offset:-6px}
.slot .dur{position:absolute;left:10px;top:10px;z-index:2;font:600 11px/1 var(--font-mono);letter-spacing:.04em;color:var(--foot-ink);background:color-mix(in srgb, var(--chrome) 78%, transparent);padding:5px 7px;border-radius:3px}
.vid.is-playing .dur,.vid.is-playing .plate{display:none}
.vid{margin:0;display:grid;gap:10px;min-width:0;align-content:start}
.vid figcaption{font-size:var(--fs-small);color:var(--ink-2);max-width:60ch}
.vid figcaption b{display:block;color:var(--ink);font:700 var(--fs-h3)/1.05 var(--font-cond);text-transform:uppercase;margin-bottom:4px}
.band.drone .vid figcaption{color:color-mix(in srgb, var(--foot-ink) 78%, transparent)}
.band.drone .vid figcaption b{color:var(--foot-ink)}
.vids{list-style:none;margin:0;padding:0;display:grid;gap:28px;align-items:start}
.vids .slot.video video{object-fit:cover}
.vids .vid.is-playing .slot.video video{object-fit:contain}
@media (min-width:700px){.vids{grid-template-columns:repeat(2,minmax(0,1fr))}}
.job-grid{display:grid;gap:24px}
.job-grid .side{display:grid;gap:24px;align-content:start}
@media (min-width:800px){.job-grid{grid-template-columns:minmax(0,.62fr) minmax(0,1fr);align-items:start}}
@media (max-width:799px){.vid.tall .slot{--ar:4/5 !important}}
h2.sub{font-size:var(--fs-h3);font-family:var(--font-cond);margin:8px 0 0}
.stack>h2.sub+ul{margin-block-start:16px}
dialog.lightbox .slot.in-lb{aspect-ratio:auto;height:min(72vh,720px)}
dialog.lightbox .slot.in-lb img{object-fit:contain;background:var(--chrome)}
.about-photos .slot{--ar:4/5 !important}
/* v1.1 · seven nav links: tighten between the drawer breakpoint and the full width */
@media (min-width:900px) and (max-width:1199px){.site-head .datum{display:none !important}.nav a:not(.btn){padding:0 8px}.nav .nav-cta{margin-inline-start:4px}}
@media (min-width:900px) and (max-width:1023px){.nav a:not(.btn){padding:0 6px;font-size:16px}.nav .nav-cta .btn{padding-inline:12px !important}}
.faq-index ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:10px}
.faq-index a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line-strong);border-radius:var(--radius);text-decoration:none;font-weight:600;transition:background-color var(--t-hover) var(--ease-out)}
.faq-index a:hover{background:var(--wash)}
.faq-group,.g-block{scroll-margin-top:calc(var(--head-h) + 16px)}
.faq-index .count{margin-inline-start:8px;font-weight:500;color:var(--ink-2)}
.faq-group h2.sub{margin-bottom:8px}
.cred-card h3{margin:0}
details.faq p a{color:var(--ink);text-underline-offset:.16em}
/* v1.0 final · About: the bio with one square portrait */
.bio{display:grid;gap:24px;align-items:start}
.bio .slot{max-width:640px;width:100%}
.bio .slot .plate{display:none}
.bio .lede{margin:0}

/* v1.0 final · mobile pass */
html{text-size-adjust:100%;-webkit-tap-highlight-color:color-mix(in srgb, var(--gold) 22%, transparent)}
.nf-links{list-style:none;padding:0;display:grid;gap:0}
.nf-links a{display:flex;align-items:center;min-height:44px}
.cta-bar .ico{width:18px;height:18px;flex:none}
.cta-bar .btn{white-space:nowrap;gap:8px}
.cta-bar{transition:translate .2s cubic-bezier(.165,.84,.44,1),visibility 0s linear 0s}
.cta-bar[data-off]{translate:0 calc(100% + 2px);visibility:hidden;transition:translate .2s cubic-bezier(.895,.03,.685,.22),visibility 0s linear .2s}
@media (prefers-reduced-motion:reduce){.cta-bar,.cta-bar[data-off]{transition:none}}
.contact-list .kv .row a.tel,.contact-list .kv .row a.mail,.site-foot p a.tel,.site-foot p a.mail{display:inline-block;padding-block:11px;margin-block:-11px}
.site-foot .cols{display:grid;gap:28px}
@media (max-width:699px){
  .site-foot .cols>div:nth-child(2) ul{grid-template-columns:1fr 1fr;column-gap:16px}
  .contact-line{gap:4px 20px}
  .contact-line .kv{flex-wrap:wrap;row-gap:0}
  .contact-line .kv span a{overflow-wrap:normal;word-break:normal}
  .contact-line .kv b{font-size:13px}
  .tile{padding:18px 18px 12px;gap:8px}
  .tile .btn{min-height:44px;padding:0;border:0;background:none;text-decoration:underline;text-underline-offset:.18em;font-size:var(--fs-small);flex-direction:row;flex-wrap:nowrap;gap:6px}
  .tile .btn::after{content:"→";position:static;inset:auto;text-decoration:none;display:inline-block}
  .tile .btn:hover{background:none;color:var(--gold-ink)}
  .proof-link{width:100%}
}
@media (max-width:359px){
  .cta-bar .bar-long{display:none}
  .cta-bar .btn{padding-inline:8px;font-size:16px}
  .cta-row .btn{flex:1 1 100%}
}
@media (orientation:landscape) and (max-height:500px){
  .site-head{position:relative}
  .cta-bar{padding-top:6px;padding-bottom:calc(6px + env(safe-area-inset-bottom,0px))}
  .cta-bar .btn{min-height:44px}
}
/* v1.1 · the sample report as proof: a hero link and a card that looks like the report's first page */
.proof-link{display:inline-flex;align-items:center;gap:10px;min-height:48px;padding:8px 16px;border-radius:var(--radius);background:color-mix(in srgb, var(--gold-light) 30%, var(--bg));box-shadow:inset 0 0 0 1.5px var(--gold);color:var(--ink);text-decoration:none;font-size:var(--fs-small);justify-self:start;width:fit-content;max-width:100%;transition:background-color var(--t-hover) var(--ease-out)}
.proof-link b{font-weight:700}
.proof-link:hover{background:color-mix(in srgb, var(--gold-light) 55%, var(--bg))}
.rc-ico{width:20px;height:20px;flex:none;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round}
.report-card{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:20px;align-items:center;padding:16px;border-radius:var(--radius);background:color-mix(in srgb, var(--gold-light) 18%, var(--bg));box-shadow:inset 0 0 0 2px var(--gold);color:var(--ink);text-decoration:none;max-width:40rem;transition:background-color var(--t-hover) var(--ease-out)}
.report-card:hover{background:color-mix(in srgb, var(--gold-light) 34%, var(--bg))}
.report-card:hover .rc-cta{background:color-mix(in srgb, var(--gold-light), #ffffff 14%)}
.band.drone .report-card:focus-visible{outline-color:var(--focus-dark)}
.rc-sheet{display:grid;gap:6px;align-content:start;background:#fbfaf7;border-top:3px solid var(--gold);border-radius:3px;padding:10px 10px 12px;box-shadow:inset 0 0 0 1px var(--line),0 1px 0 var(--line)}
.rc-run{font:600 8.5px/1.2 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.rc-title{font:700 13px/1.05 var(--font-display);text-transform:uppercase;letter-spacing:.01em;color:var(--ink)}
.rc-meta{display:grid;grid-template-columns:auto minmax(0,1fr);font-size:9px;line-height:1.3;box-shadow:inset 0 0 0 1px var(--line)}
.rc-k{background:var(--chrome);color:var(--foot-ink);font-weight:600;padding:3px 6px;border-bottom:1px solid var(--foot-line)}
.rc-v{padding:3px 6px;border-bottom:1px solid var(--line);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rc-sheet img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:2px}
.rc-body{display:grid;gap:8px;align-content:center;justify-items:start}
.rc-tag{display:inline-flex;align-items:center;gap:6px;font:600 var(--fs-eyebrow)/1.3 var(--font-body);letter-spacing:.09em;text-transform:uppercase;color:var(--gold-ink)}
.rc-tag .rc-ico{width:16px;height:16px}
.rc-head{font:700 var(--fs-h3)/1.05 var(--font-cond);text-transform:uppercase;color:var(--ink)}
.rc-text{font-size:var(--fs-small);color:var(--ink-2)}
.rc-cta{margin-top:4px;white-space:nowrap}
.contact-list .kv .row .hint-copy{font:500 var(--fs-caption)/1.3 var(--font-body);color:var(--ink-2)}
.band.drone .report-card{background:var(--bg);box-shadow:inset 0 0 0 2px var(--gold-light)}
.band.drone .report-card:hover{background:color-mix(in srgb, var(--gold-light) 22%, var(--bg))}
.band.drone .report-card .rc-head{color:var(--ink)}
@media (max-width:520px){.report-card{grid-template-columns:1fr;gap:14px}.rc-sheet{max-width:210px}.rc-meta{display:none}}
/* v1.1 · the sample report: a document sheet on the topo ground */
.report{background:var(--bg);box-shadow:inset 0 0 0 1px var(--line-strong);border-top:3px solid var(--gold);border-radius:var(--radius);padding:clamp(20px,4vw,48px);max-width:52rem;display:grid;gap:14px}
.report>*{margin:0}
.report h2{font-size:var(--fs-h2)}
.report h3{margin-top:14px;font-size:var(--fs-h3)}
.report h4{font:700 15px/1.3 var(--font-body);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);margin-top:4px}
.report ul,.report ol{padding-left:22px;display:grid;gap:6px}
.report-run{font:600 11px/1.3 var(--font-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin:0}
.report-head{display:grid;gap:8px;padding-bottom:16px;border-bottom:1px solid var(--line)}
.report-head>*{margin:0}
.report-sub{color:var(--ink-2)}
.report-meta{display:grid;grid-template-columns:minmax(110px,auto) minmax(0,1fr);gap:0;margin:8px 0 0;font-size:var(--fs-small);box-shadow:inset 0 0 0 1px var(--line)}
.report-meta dt{font-weight:600;background:var(--chrome);color:var(--foot-ink);padding:8px 12px;border-bottom:1px solid var(--foot-line)}
.report-meta dd{margin:0;padding:8px 12px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}
.report-fig{margin:6px 0;max-width:34rem;display:grid;gap:8px}
.report-fig figcaption{font-size:var(--fs-caption);color:var(--ink-2);font-style:italic}
.report-foot{border-top:1px solid var(--line);padding-top:16px;display:grid;gap:10px;margin-top:10px}
.report-foot p{margin:0}
.stack>h2.sub+ol.creds{margin-block-start:24px}
@media (min-width:700px){.creds.creds-6{grid-template-columns:repeat(3,minmax(0,1fr))}}
.cred-card .eyebrow{margin:0}
/* v1.0 · phone numbers and the toast */
a.tel{white-space:nowrap;color:inherit;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.18em;font-weight:600}
a.tel:hover{color:var(--gold-ink)}
.site-foot a.tel:hover,.band.invert a.tel:hover{color:var(--gold-light)}
.contact-list .kv .row a.tel,.contact-list .kv .row a.mail{font:600 clamp(20px, 1rem + 1vw, 26px)/1.2 var(--font-body);overflow-wrap:anywhere}
.contact-list .kv .row a.mail{font-size:19px}
a.mail{color:inherit}
.hint-copy{display:none;font-size:var(--fs-caption);color:var(--ink-2);font-weight:500}
@media (hover:hover) and (pointer:fine){.hint-copy{display:inline}.touch-only{display:none !important}}
.toast{position:fixed;left:50%;bottom:calc(24px + env(safe-area-inset-bottom,0px));translate:-50% 0;z-index:60;background:var(--chrome);color:var(--foot-ink);padding:12px 18px;border-radius:var(--radius);font-weight:600;font-size:var(--fs-small);box-shadow:inset 0 0 0 1px var(--gold);max-width:calc(100vw - 32px);opacity:0;visibility:hidden;transition:opacity .2s cubic-bezier(.165,.84,.44,1),visibility 0s linear .2s}
.toast.on{opacity:1;visibility:visible;transition:opacity .2s cubic-bezier(.165,.84,.44,1),visibility 0s}
@media (max-width:899px){.toast{bottom:calc(84px + env(safe-area-inset-bottom,0px))}}
@media (prefers-reduced-motion:reduce){.toast,.toast.on{transition:none}}
/* v1.0 · the receipt dialog */
dialog.sent{border:0;padding:0;background:var(--bg);color:var(--ink);width:min(94vw,600px);max-width:none;max-height:min(90vh,820px);border-radius:var(--radius);box-shadow:inset 0 0 0 2px var(--ok);overscroll-behavior:contain}
dialog.sent[data-state="fallback"],dialog.sent[data-state="failed"]{box-shadow:inset 0 0 0 2px var(--gold)}
dialog.sent::backdrop{background:rgb(27 38 34 / .62)}
dialog.sent .frame{display:grid;gap:14px;padding:24px}
dialog.sent h2{margin:0;font-size:var(--fs-h2)}
dialog.sent h2:focus-visible{outline:none}
dialog.sent #sent-lede{margin:0}
dialog.sent .eyebrow{margin:0;color:var(--ok)}
dialog.sent[data-state="fallback"] .eyebrow,dialog.sent[data-state="failed"] .eyebrow{color:var(--gold-ink)}
.sent-list{display:grid;grid-template-columns:auto minmax(0,1fr);gap:8px 16px;margin:0;padding:14px 16px;background:var(--surface);border-radius:var(--radius);font-size:var(--fs-small)}
.sent-list dt{font-weight:600;color:var(--ink-2);text-transform:uppercase;font-size:12px;letter-spacing:.06em;padding-top:2px}
.sent-list dd{margin:0;overflow-wrap:anywhere;white-space:pre-wrap}
#sent-ref:empty,#sent-actions[hidden]{display:none}
dialog.sent[data-state="fallback"] #sent-close,dialog.sent[data-state="failed"] #sent-close{background:transparent;color:var(--ink);border-color:var(--line-strong)}
dialog.sent[data-state="fallback"] #sent-close:hover,dialog.sent[data-state="failed"] #sent-close:hover{background:var(--wash)}
/* v1.0 · reviews */
.review{border-radius:var(--radius);padding:20px;display:grid;gap:10px;align-content:start;background:var(--bg);box-shadow:inset 0 0 0 1px var(--line);margin:0;min-width:0}
.review blockquote{margin:0}
.review .who{font-size:var(--fs-caption);letter-spacing:.04em;text-transform:uppercase;color:var(--ink-2);font-weight:600}
.review .caption{margin:0}
.review .reply{margin:0;border-left:2px solid var(--gold);padding-left:12px;font-size:var(--fs-small);color:var(--ink-2)}
.review-empty,.review-closed{grid-column:1/-1;box-shadow:inset 0 0 0 1px var(--line-strong)}
.reviews-write{display:grid;gap:24px;max-width:44rem}
.field select{width:100%;min-height:48px;padding:10px 12px;border:1.5px solid var(--line-strong);border-radius:var(--radius);background:var(--bg);color:var(--ink);font:inherit}
.field select:hover{border-color:var(--ink-2)}
.consent label{display:flex;gap:12px;align-items:flex-start;font-weight:500;cursor:pointer}
.consent input{width:22px;height:22px;margin:2px 0 0;flex:none;accent-color:var(--accent)}
.cf-turnstile{min-height:65px}
/* v1.2 · one gold Contact button in the nav and drawer */
.drawer li.drawer-cta{padding-top:12px}
.drawer li.drawer-cta a.btn{justify-content:center;box-shadow:none;color:var(--chrome);font-weight:700;padding:0 20px}
.drawer li.drawer-cta a.btn:hover,.drawer li.drawer-cta a.btn[aria-current="page"]{color:var(--chrome)}
/* v1.2 · reviews: stars, verified jobs, photos */
.rv-stars{display:inline-flex;gap:2px;color:var(--gold)}
.rv-stars svg{width:18px;height:18px;fill:currentColor;stroke:currentColor;stroke-width:1.4;stroke-linejoin:round}
.rv-stars svg.off{fill:transparent}
.rv-top{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px}
.rv-verified{display:inline-flex;align-items:center;gap:5px;font-size:var(--fs-caption);font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--ok)}
.rv-verified svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.rv-photos,.rv-picks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;list-style:none;margin:0;padding:0;max-width:22rem}
.rv-photos a{display:block;border-radius:var(--radius);overflow:hidden;box-shadow:inset 0 0 0 1px var(--line);min-height:44px}
.rv-photos img,.rv-picks img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:var(--radius);background:var(--surface)}
.rv-sum{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px}
.rv-sum .rv-stars svg{width:24px;height:24px}
.rv-sum b{font:700 var(--fs-h3)/1 var(--font-cond);letter-spacing:.01em}
.rv-sum span:last-child{color:var(--ink-2);font-size:var(--fs-small)}
.rv-how{border-radius:var(--radius);padding:20px;background:var(--surface);box-shadow:inset 0 0 0 1px var(--line-strong);display:grid;gap:10px}
.rv-how ol{margin:0;padding-left:20px;display:grid;gap:6px;font-size:var(--fs-small)}
.rv-invite{display:flex;gap:10px;align-items:flex-start;padding:14px 16px;border-radius:var(--radius);box-shadow:inset 0 0 0 2px var(--ok);background:var(--surface);margin:0}
.rv-invite .ico{color:var(--ok);margin-top:3px}
.rv-invite.is-old{box-shadow:inset 0 0 0 2px var(--gold)}
.rv-invite.is-old .ico{color:var(--gold)}
.rate .opts{display:flex;gap:2px;margin-inline-start:-6px;position:relative}
.rate .row{display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px}
.rate label{display:grid;place-items:center;width:48px;height:48px;border-radius:var(--radius);cursor:pointer}
.rate label svg{width:34px;height:34px;fill:transparent;stroke:var(--ink-2);stroke-width:1.4;stroke-linejoin:round;transition:fill var(--t-hover) var(--ease-out),stroke var(--t-hover) var(--ease-out)}
:where(.rate:has(input[value="1"]:checked)) .opts label:nth-of-type(-n+1) svg,
:where(.rate:has(input[value="2"]:checked)) .opts label:nth-of-type(-n+2) svg,
:where(.rate:has(input[value="3"]:checked)) .opts label:nth-of-type(-n+3) svg,
:where(.rate:has(input[value="4"]:checked)) .opts label:nth-of-type(-n+4) svg,
:where(.rate:has(input[value="5"]:checked)) .opts label:nth-of-type(-n+5) svg{fill:var(--gold);stroke:var(--gold)}
@media (hover:hover){.rate .opts:hover label svg{fill:transparent;stroke:var(--ink-2)}.rate .opts label:hover svg,.rate .opts label:has(~ label:hover) svg{fill:var(--gold-light);stroke:var(--gold)}}
.rate input:focus-visible + label{outline:2px solid var(--focus);outline-offset:-2px}
.rate legend,#r-photos-field legend{padding:0}
.rate-out{font-weight:600;color:var(--ink-2);font-size:var(--fs-small)}
.field.rate.has-err label svg{stroke:var(--err)}
.field .count{font-size:var(--fs-caption);color:var(--ink-2);font-variant-numeric:tabular-nums}
.field .count.is-ok{color:var(--ok);font-weight:600}
.pick-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.pick-in:focus-visible + .btn{outline:2px solid var(--focus);outline-offset:2px}
.rv-picks:empty{display:none}
.rv-picks li{display:grid;gap:4px}
.rv-picks .rm{min-height:44px;border:1.5px solid var(--line-strong);border-radius:var(--radius);background:transparent;cursor:pointer;font-weight:600;font-size:var(--fs-small);transition:background-color var(--t-hover) var(--ease-out)}
.rv-picks .rm:hover{background:var(--wash)}
.rv-head-cta{justify-self:start}
}
"""

PAGES = [("home", "/", "Home"), ("services", "/services", "Services"), ("credentials", "/credentials", "Credentials"), ("about", "/about", "About"), ("gallery", "/gallery", "Gallery"), ("faq", "/faq", "FAQ"), ("reviews", "/reviews", "Reviews"), ("contact", "/contact", "Contact")]
EXTRA_PAGES = [("drone-report", "/drone-report", "Sample drone report")]     # linked from home, services, footer and sitemap; not in the main nav
NAV_BUTTON = "contact"      # v1.2: Contact is the one gold button at the end of the nav, not a text link as well
HREF = {k: h for k, h, _ in PAGES + EXTRA_PAGES}
def href(key, anchor=''):
    if ARTIFACT: return f'#{key}'
    return HREF[key] + (f'#{anchor}' if anchor else '')
def route_attr(key): return f' data-route="{key}"' if ARTIFACT else ''

TITLES = {
  "home": (f"{S['name']} · Pest & vermin control, Victoria", "Professional pest control across Victoria: deer control, kangaroo culling, pigs, foxes, rabbits and wild dogs for farmers and landholders. Licensed, insured, humane. Based in Warragul, Gippsland."),
  "services": (f"Services · {S['name']}", "Deer control, kangaroo culling, feral pigs, foxes, rabbits and wild dogs anywhere in Victoria. Night and thermal work, planned, insured and humane under the Victorian codes."),
  "about": (f"About · {S['name']}", f"Based in {S['base']}, working across {S['region']}. Licensed, insured, accountable. AHCPMG304 humane dispatch."),
  "gallery": (f"Gallery · {S['name']}", "Thermal images, night work, property damage and gear from pest control jobs across Victoria."),
  "contact": (f"Contact · {S['name']}", f"Ring {S['phone_display']} or send an enquiry. Based in {S['base']}, working across {S['region']}."),
  "credentials": (f"Credentials and insurance · {S['name']}", f"Licensed and insured feral animal control: firearms and Game licences, SSAA Farmer Assist, First Aid, AHCPMG304 humane dispatch and $20 million public liability with {S['insurer']}. Certificates on request."),
  "faq": (f"FAQ · {S['name']}", "How quotes are worked out, carcass disposal, stock safety, neighbours and night noise, farm security, insurance and kangaroo permits: straight answers from Fitz Feral Hunters."),
  "drone-report": (f"Sample drone survey report · {S['name']}", "A real drone survey report from a rural property in Gippsland, with the property's details removed: what was seen, the habitat, findings and recommendations."),
  "reviews": (f"Reviews · {S['name']}", "Star-rated reviews from farmers and landholders Fitz Feral Hunters has worked for, each matched to a real job and published good or bad. Leave a review of a job."),
}

# real grid references (MGA zone 55) for the base and every locality on the chips
GR = {name: topo.grid_ref(la, lo) for name, la, lo in topo.LOCALITIES}
BASE_GR = GR[S['base']][0] if S['base'] in GR else ''

SPRITE = '''<svg hidden aria-hidden="true" focusable="false"><symbol id="i-phone" viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></symbol><symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></symbol><symbol id="i-ext" viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/></symbol><symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/></symbol><symbol id="i-doc" viewBox="0 0 24 24"><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 11h7M9 14.5h7M9 18h4"/></symbol><symbol id="i-star" viewBox="0 0 24 24"><path d="M12 2.8l2.75 5.9 6.45.75-4.8 4.4 1.3 6.35L12 17l-5.7 3.2 1.3-6.35-4.8-4.4 6.45-.75z"/></symbol><symbol id="i-check" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5"/></symbol><symbol id="i-north" viewBox="0 0 24 24"><path d="M12 3v18M8 21h8"/><path class="fill" d="M12 3l4.5 9h-9z"/></symbol></svg>'''
def ico(name, cls="ico"): return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'

def north(label="N"):
    if not SHEET: return ''
    return f'<span class="datum" title="Grid: MGA zone 55, GDA2020"><svg class="north" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-north"/></svg><span>{label} · MGA 55</span></span>'

def scalebar(stack=False, unit='1 km'):
    return (f'<figure class="scalebar{" stack" if stack else ""}" aria-label="Scale bar: 150 pixels represent 1 kilometre at this sheet scale"{per("scalebar")}>'
            f'<div><div class="bar"><i></i><i></i><i></i><i></i></div><div class="ticks"><span>0</span><span>250</span><span>500</span><span>750</span><span>m</span></div></div>'
            f'<span class="unit">{unit}</span></figure>')

def meta(sheet, extra=''):
    if not SHEET: return ''
    return f'<p class="meta"{per("meta")}><b>Sheet</b><span>{esc(sheet)}</span><span class="lead" aria-hidden="true"></span><span>GR <span class="num">{BASE_GR}</span></span><span>MGA 55 · GDA2020</span>{extra}</p>'

def corners():
    return '<i class="corner tl" aria-hidden="true"></i><i class="corner tr" aria-hidden="true"></i><i class="corner bl" aria-hidden="true"></i><i class="corner br" aria-hidden="true"></i>'

def slot(kind, label, src="", ar=None, tag="Photo slot"):
    """A ratio-locked photo with registration ticks and a privacy plate. With a src it renders a real lazy image."""
    style = f' style="--ar:{ar}"' if ar else ''
    plate = '<span class="plate">Location withheld</span>'
    if src:
        return (f'<figure class="slot photo"{per("slot")}{per("frame")} style="margin:0{";--ar:"+ar if ar else ""}">'
                f'<img src="{esc(src)}" alt="{esc(label)}" loading="lazy" decoding="async" width="1600" height="1200" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0">{corners()}{plate}</figure>')
    cls = 'slot thermal' if kind == 'thermal' else 'slot'
    mark = {'thermal': 'Thermal', 'night': 'Night', 'property': 'Property', 'gear': 'Gear'}.get(kind, 'Photo')
    tag_html = f'<span class="tag">{esc(tag)} · client supplies</span>' if REVIEW else ''
    small = f'<small>{esc(kind)} · jpg/avif · alt text written per photo</small>' if REVIEW else ''
    return (f'<div class="{cls}"{style}{per("slot")}{per("frame")} role="img" aria-label="{esc(label)}">'
            f'<span class="mark" aria-hidden="true">{mark}</span>{tag_html}{plate}{corners()}'
            f'<span class="label">{esc(label)}{small}</span></div>')

def photo(mid, ar=None, sizes='(min-width:900px) 45vw, 100vw', eager=False):
    """A real photo from content/media.json in the registration-tick frame. WebP with a JPEG fallback, sized srcset."""
    m = MEDIA[mid]
    sj = ', '.join(f'{j} {w}w' for w, j, _ in m['srcset']); sw = ', '.join(f'{wp} {w}w' for w, _, wp in m['srcset'])
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return (f'<figure class="slot photo"{per("slot")}{per("frame")}{per("media")} style="--ar:{ar or str(m["width"]) + "/" + str(m["height"])}" data-ratio="{m["width"]}/{m["height"]}">'
            f'<picture><source type="image/webp" srcset="{sw}" sizes="{sizes}"><img src="{m["src"]}" srcset="{sj}" sizes="{sizes}" alt="{esc(m["alt"])}" width="{m["width"]}" height="{m["height"]}" decoding="async"{load}></picture>'
            f'{corners()}<span class="plate">Location withheld</span></figure>')

def pic(ref, label='', ar=None, **kw):
    """A media id renders the real photo; anything else falls back to the labelled placeholder slot."""
    if isinstance(ref, str) and ref in MEDIA: return photo(ref, ar=ar, **kw)
    kind, lab, src = ref if isinstance(ref, (list, tuple)) else ('photo', label, '')
    return slot(kind, lab, src, ar=ar)

def mmss(s): s = round(s); return f'{s // 60}:{s % 60:02d}'

def video_fig(mid, ar=None, cls=''):
    """Native player, nothing downloaded until play (preload=none), poster, text description for screen readers."""
    m = MEDIA[mid]
    ar = ar or f'{m["width"]}/{m["height"]}'
    return (f'<figure class="vid{" " + cls if cls else ""}"{per("video")}>'
            f'<div class="slot video" style="--ar:{ar}"><video controls preload="none" playsinline poster="{m["poster_webp"]}" width="{m["width"]}" height="{m["height"]}" aria-label="Video: {esc(m["title"])}" aria-describedby="vd-{mid}">'
            f'<source src="{m["src"]}" type="video/mp4"><a href="{m["src"]}">Download the video ({mmss(m["duration"])})</a></video>'
            f'{corners()}<span class="plate">Location withheld</span><span class="dur num" aria-hidden="true">{mmss(m["duration"])}</span></div>'
            f'<figcaption><b>{esc(m["title"])}</b> {esc(m["caption"])}</figcaption><p class="sr" id="vd-{mid}">{esc(m["description"])} Length {mmss(m["duration"])}, no sound.</p></figure>')

def videos(kind=None, home=None):
    return [i['id'] for i in MEDIA.values() if i['type'] == 'video' and (kind is None or i['kind'] == kind) and (home is None or bool(i.get('home')) == home)]

def tel(label=None, cls='tel num'):
    """Every phone number on the site. Touch phones dial; desktop copies (see the script)."""
    return f'<a class="{cls}" href="tel:{S["phone_e164"]}">{label or S["phone_display"]}</a>'

def mailto(cls='mail'):
    return f'<a class="{cls}" href="mailto:{S["email"]}?subject={urlquote("Enquiry from the website")}">{S["email"]}</a>'

def nav_links(current, skip=(NAV_BUTTON,)):
    return ''.join(f'<li><a href="{href(k)}"{route_attr(k)}{" aria-current=page" if (k == current and not ARTIFACT) else ""}>{t}</a></li>' for k, h, t in PAGES if k not in skip)

def contact_button(current, drawer=False):
    """The one gold Contact button (nav and drawer). Other pages' "Request a quote" buttons still go straight to the form."""
    cur = ' aria-current="page"' if current == 'contact' and not ARTIFACT else ''
    if drawer: return f'<li class="drawer-cta"><a class="btn btn-gold" href="{href("contact")}"{route_attr("contact")}{cur}>Contact</a></li>'
    return f'<li class="nav-cta"><a class="btn btn-gold" href="{href("contact")}"{route_attr("contact")}{cur} style="min-height:44px;padding-inline:20px">Contact</a></li>'

def contact_line():
    return f'''<div class="contact-line"{per("contactline")}>
        <div class="kv"><b>{ico("i-phone")}Phone</b><span>{tel()}</span><span class="hint-copy">Click to copy</span></div>
        <div class="kv"><b>{ico("i-mail")}Email</b><span>{mailto()}</span><button type="button" class="copy" data-copy="{S['email']}" aria-label="Copy email address">Copy</button></div>
        <div class="kv"><b>{ico("i-ext")}Follow</b><span><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram</a> · <a href="{S['facebook']}" target="_blank" rel="noopener">Facebook</a></span></div>
      </div>'''

def cta_row(extra_style='', gold=False):
    return f'''<div class="cta-row"{per("cta")}>
        <a class="btn {'btn-gold' if gold else 'btn-primary'}" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a>
        <a class="btn btn-secondary num" href="tel:{S['phone_e164']}"{extra_style}>Call {S['phone_display']}</a>
      </div>'''

def header(current):
    return f'''
<div class="skips"{per("skip")}><a href="#main">Skip to content</a><a href="{href('contact','enquiry')}"{route_attr('contact')}>Skip to contact</a></div>
<header class="site-head"{per("header")}>
  <div class="wrap">
    <a class="logo" href="{href('home')}"{route_attr('home')}{per("wordmark")}{per("logo")}><img src="{asset('/brand/logo-lockup.png')}" alt="{esc(S['name'])} — {esc(S['tagline'])}" width="640" height="181" decoding="async" fetchpriority="high"></a>
    {north()}
    <nav class="nav" aria-label="Primary"{per("nav")}><ul>{nav_links(current)}{contact_button(current)}</ul></nav>
    <details class="drawer" id="drawer"{per("burger")}><summary aria-label="Menu" aria-expanded="false">Menu</summary><ul>{nav_links(current)}{contact_button(current, drawer=True)}</ul></details>
  </div>
</header>'''

def footer():
    abn = esc(S['abn']) if S['abn'] else flag('to be supplied', ' style="border-color:var(--foot-line);color:inherit"').strip()
    abn_span = f'<span>ABN {abn}</span>' if abn else ''
    return f'''
<footer class="site-foot" id="footer"{per("footer")}>
  <div class="wrap">
    <div class="cols">
      <div class="stack" style="--gap:12px">
        <a class="logo foot-logo" href="{href('home')}"{route_attr('home')}{per("logo")}><img src="{asset('/brand/logo-lockup.png')}" alt="{esc(S['name'])} — {esc(S['tagline'])}" width="640" height="181" loading="lazy" decoding="async"></a>
        <p class="small" style="max-width:36ch">Licensed, insured feral animal control for farmers and landholders across {esc(S['region'])}.</p>
        <p class="small">{tel()} · {mailto()}</p>
      </div>
      <div><h4>Pages</h4><ul>{nav_links(None, skip=())}<li><a href="{href('drone-report')}">Sample drone report</a></li></ul></div>
      <div><h4>Elsewhere</h4><ul><li><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {esc(S['instagram_handle'])}</a></li><li><a href="{S['facebook']}" target="_blank" rel="noopener">Facebook</a></li><li><a href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a></li></ul></div>
    </div>
    <div class="cred-strip" aria-label="Credentials">{''.join(f'<span>{esc(t)}</span>' for t, _ in S['credentials'][:7])}</div>
    {f'<div class="margin"{per("topo")}{per("meta")}><svg class="north" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-north"/></svg><span>Grid MGA zone 55 · datum GDA2020</span><span>Contour interval 10 m · index 50 m</span><span>Base GR <span class="num">{BASE_GR}</span></span>{scalebar()}<span>Sheet styling after Victorian 1:25 000 topographic maps · field seed <span class="num">{esc(SEED)}</span></span></div>' if SHEET else ''}
    <div class="legal"><span>&copy; {datetime.date.today().year} {esc(S['name'])}</span><span>{esc(S['base'])} VIC</span>{abn_span}<span>Work carried out under Victorian codes of practice</span></div>
  </div>
</footer>'''

def ctabar():
    return f'''
<div class="cta-bar" id="ctabar"{per("ctabar")}>
  <a class="btn btn-secondary num" href="tel:{S['phone_e164']}">{ico("i-phone")}<span class="bar-long">Call</span>{S['phone_display']}</a>
  <a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a>
</div>'''

def varbar():
    if not REVIEW: return ''
    other = esc(S['night_shift_url'])
    return f'''
<div class="varbar" id="varbar"{per("varbar")} role="region" aria-label="Mockup controls">
  <div class="wrap">
    <span><strong>D700 mockup · {'SP-01e PADDOCK v0.3.2' if SHEET else 'SP-01d PADDOCK v0.3.1'}</strong><span class="long"> · card colourway (green · gold · cream){' · dense topographic sheet, no map · seed ' + esc(SEED) if SHEET else ' · all of Victoria'}</span></span>
    <span class="grow"></span>
    <button type="button" id="t-motion" aria-pressed="false" title="Emulates the reduced-motion twin (D4980); the real gate is the media query (D3453)"><span class="long">Motion: on</span><span class="short">Motion</span></button>
    {'<button type="button" id="t-topo" aria-pressed="true" title="Toggle the contour field and grid (D2410) to compare against v1"><span class="long">Sheet: on</span><span class="short">Sheet</span></button>' if SHEET else ''}
    <button type="button" id="t-xray" aria-pressed="false" title="Outline every component and show the D-ids it honours"><span class="long">X-ray</span><span class="short">X-ray</span></button>
    <button type="button" id="t-spec" command="show-modal" commandfor="spec"><span class="long">Spec sheet</span><span class="short">Spec</span></button>
    <a href="{other}" target="_blank" rel="noopener"><span class="long">Other mockup: </span>Night Shift &rarr;</a>
    <button type="button" class="hide" id="t-hide" aria-label="Hide mockup controls">&times;</button>
  </div>
</div>'''

def spec_dialog():
    if not REVIEW: return ''
    spfile = (ROOT / 'docs' / ('SP-01e-ffh-paddock-v3-2.md' if SHEET else 'SP-01d-ffh-paddock-v3-1.md'))
    spfile = spfile.read_text() if spfile.exists() else '(SP record not found in docs/)'
    allids = []
    for grp in (cites.SHARED, X, cites.TOP):
        for k, ids in grp.items():
            if k in SHEET_KEYS and not SHEET: continue
            if k in MAP_KEYS and not SHEET_MAP: continue
            allids += ids
    uniq = list(dict.fromkeys(allids))
    d_entries = sorted(i for i in uniq if re.match(r'^D\d{4}$', i))
    laws = sorted((i for i in uniq if i.startswith('LAW-')), key=lambda s: int(s.split('-')[1]))
    pairs = sorted((i for i in uniq if i.startswith('PAIR-')), key=lambda s: int(s.split('-')[1]))
    nopairs = sorted((i for i in uniq if i.startswith('NOPAIR-')), key=lambda s: int(s.split('-')[1]))
    pals = [i for i in uniq if i.startswith('PAL ') or i.startswith('CPAIR') or i.startswith('PALRULE')]
    lenses = [i for i in uniq if i.startswith('LENS') or i.startswith('DOC') or i.startswith('TENSION')]
    tops = [i for i in uniq if re.match(r'^(TP|DY|MK)', i)]
    ids_li = ''.join(f'<li>{i} · {esc(NAMES.get(i, ""))}</li>' for i in d_entries)
    counts = f'''<span>{len(d_entries)} entries</span><span>{len(laws)} laws</span><span>{len(pairs)} pairs</span><span>{len(nopairs)} anti-pairs resolved</span><span>{len(pals)} palette records</span><span>{len(lenses)} doctrine records</span><span>{len(tops)} templates/dynamics/kits</span><span>{len(uniq)} citations total</span>'''
    return f'''
<dialog class="spec" id="spec"{per("spec")} aria-labelledby="spec-title">
  <div class="bar"><h2 id="spec-title">{'SP-01e · PADDOCK v0.3.2' if SHEET else 'SP-01d · PADDOCK v0.3.1'} · spec sheet</h2><button type="button" class="btn btn-secondary" id="spec-close" aria-label="Close spec sheet">&times;</button></div>
  <div class="inner">
    <p class="counts">{counts}</p>
    <p>Compiled against <span class="mono">{esc(STAMP)}</span>. Every component on the page carries a <span class="mono">data-per</span> attribute naming the records it honours; switch on X-ray and hover any outlined component to read them. {'The v0.2 topographic sheet layer is switched off behind <span class="mono">sheet_layer</span> in content/site.json.' if not SHEET else 'The topographic sheet layer (seeded contour field, MGA-style 1 km grid, real zone-55 grid references, scale bars, marginalia, photo registration frames) runs at 3× the v0.2 line density: the same 1200px tile drawn at 600px with 29 levels; the locality map and key are off at the client\'s request (<span class="mono">sheet_map</span>).'}</p>
    <h3>Templates, dynamics, motion kit</h3><p class="mono">{' · '.join(tops)}</p>
    <h3>Palettes and colour rules</h3><p class="mono">{' · '.join(pals)}</p>
    <h3>Doctrine lenses</h3><p class="mono">{' · '.join(lenses)}</p>
    <h3>Laws honoured</h3><p class="mono">{' · '.join(laws)}</p>
    <h3>Pairs honoured</h3><p class="mono">{' · '.join(pairs)}</p>
    <h3>Anti-pairs swept and resolved</h3><p class="mono">{' · '.join(nopairs)}</p>
    <h3>Entries ({len(d_entries)})</h3><ul class="ids">{ids_li}</ul>
    <h3>Surface plan record</h3><pre>{esc(spfile)}</pre>
    <h3>What Fitz supplies before launch</h3>
    <ul style="margin:0;padding-left:18px;display:grid;gap:4px"><li>A vector or larger logo file if one exists (the current lockup is cut from the card).</li><li>Photos: hero, two about shots, nine gallery shots at 1600px wide, with a one-line description each for alt text.</li><li>Instagram bio wording for the hero lede.</li><li>Testimonials with name, property type and locality (or a Google Business reviews link).</li><li>Pricing line for the first FAQ, ABN for the footer, and whether thermal drone services stay on the Services page.</li></ul>
  </div>
</dialog>'''

# ---------------------------------------------------------------- locality map + key (service-area section)
def locality_map():
    pts = {name: topo.latlon_to_mga55(la, lo) for name, la, lo in topo.LOCALITIES}
    E0, E1, N0, N1 = 384000, 574000, 5722000, 5822000   # 190 km × 100 km window
    W, H = 760, 400
    sx = W / (E1 - E0); sy = H / (N1 - N0)
    def xy(E, N): return (E - E0) * sx, H - (N - N0) * sy
    grid = ''
    for E in range(400000, E1, 20000):
        x, _ = xy(E, N0); grid += f'<line class="grid" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}"/><text class="edge" x="{x+3:.1f}" y="10">{E//1000}</text>'
    for N in range(5740000, N1, 20000):
        _, y = xy(E0, N); grid += f'<line class="grid" x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/><text class="edge" x="4" y="{y-3:.1f}">{N//1000}</text>'
    bx, by = xy(*pts[S['base']])
    def ring(r):
        rr = r * 1000 * sx; lx, ly = bx + rr * 0.71 + 3, by - rr * 0.71 - 3
        label = f'<text class="edge" x="{lx:.1f}" y="{ly:.1f}">{r} km</text>' if 0 < lx < W - 40 and 12 < ly < H else ''
        return f'<circle class="ring" cx="{bx:.1f}" cy="{by:.1f}" r="{rr:.1f}"/>' + label
    rings = ''.join(ring(r) for r in (25, 50, 100))
    towns = ''
    for name, (E, N) in pts.items():
        x, y = xy(E, N)
        if name == S['base']:
            towns += f'<rect class="base" x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10"/><text x="{x+9:.1f}" y="{y-6:.1f}" font-weight="700">{esc(name)} · base</text>'
        else:
            dx, dy = (-9, 4) if name in ('Bairnsdale', 'Drouin') else (9, 4)
            anchor = ' text-anchor="end"' if dx < 0 else ''
            towns += f'<circle class="town" cx="{x:.1f}" cy="{y:.1f}" r="3.6"/><text x="{x+dx:.1f}" y="{y+dy:.1f}"{anchor}>{esc(name)}</text>'
    km25 = 25000 * sx
    scale = f'<g transform="translate({W-km25-16:.1f} {H-22})"><line class="scale" x1="0" y1="0" x2="{km25:.1f}" y2="0"/><line class="scale" x1="0" y1="-4" x2="0" y2="4"/><line class="scale" x1="{km25/2:.1f}" y1="-3" x2="{km25/2:.1f}" y2="3"/><line class="scale" x1="{km25:.1f}" y1="-4" x2="{km25:.1f}" y2="4"/><text class="edge" x="0" y="14">0</text><text class="edge" x="{km25:.1f}" y="14" text-anchor="end">25 km</text></g>'
    northg = f'<g transform="translate({W-30} 18)"><use href="#i-north" width="20" height="20" x="-10" y="-10" style="stroke:var(--ink);fill:none;stroke-width:1.4"/><text class="edge" x="-3" y="24">N</text></g>'
    tile = f'<pattern id="topo-p" patternUnits="userSpaceOnUse" width="600" height="600"><image href="{TOPO_URI}" width="600" height="600"/></pattern>'
    names_list = ', '.join(n for n, _, _ in topo.LOCALITIES)
    return f'''<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-label="Schematic map of the service area: {esc(S['base'])} as base with 25, 50 and 100 kilometre rings, and the localities {esc(names_list)}. Positions approximate."{per("map")}>
  <defs>{tile}</defs>
  <rect width="{W}" height="{H}" fill="url(#topo-p)" opacity=".9"/>
  {grid}{rings}{towns}{scale}{northg}
  <rect class="frame" x=".5" y=".5" width="{W-1}" height="{H-1}"/>
</svg>'''

def legend():
    k = lambda d, extra='': f'<svg viewBox="0 0 56 18" aria-hidden="true"><path class="k" d="{d}"{extra}/></svg>'
    rows = [
      (k("M0 11 C14 2 28 16 56 7"), "<b>Contour</b> · 10 m interval"),
      (k("M0 12 C14 3 28 17 56 8", ' stroke-width="2"'), "<b>Index contour</b> · every 50 m"),
      (k("M0 9h56 M8 6v6 M20 6v6 M32 6v6 M44 6v6"), "<b>Fence line</b> · where deer and dogs cross"),
      (k("M0 9h56", ' stroke-dasharray="6 4"'), "<b>Vehicle track</b> · access agreed before the job"),
      (k("M0 9 C8 4 12 14 20 9 S32 4 40 9 S52 14 56 9", ' stroke-dasharray="2 3"'), "<b>Dam / watercourse</b> · pig and fox sign"),
      (k("M2 9h2 M10 9h2 M18 9h2 M26 9h2 M34 9h2 M42 9h2 M50 9h2", ' stroke-width="3"'), "<b>Tree line / scrub</b> · thermal work"),
      ('<svg viewBox="0 0 56 18" aria-hidden="true"><rect x="23" y="4" width="10" height="10" fill="var(--accent)" stroke="var(--ink)" stroke-width="1.2"/></svg>', f"<b>Base</b> · {esc(S['base'])}"),
      ('<svg viewBox="0 0 56 18" aria-hidden="true"><circle cx="28" cy="9" r="3.6" fill="var(--bg)" stroke="var(--ink)" stroke-width="1.6"/></svg>', "<b>Locality</b> · with its six-figure grid reference"),
    ]
    return f'''<div class="legend"{per("legend")}><p class="eyebrow">Map key</p><dl>{''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in rows)}</dl>
      <p class="caption">Grid references are MGA zone 55 (GDA2020), read eastings then northings to 100 m, the way a Victorian 1:25 000 sheet is read. Town positions are approximate; the map is for orientation, not navigation.</p></div>'''

# ---------------------------------------------------------------- marginalia (facts beside prose)
NOTES = {
  "services": [
    ("Sambar", "Introduced to Victoria in the 1860s; now the main deer species on the state's bush edge."),
    ("Fallow", "In Australia since the 1830s; paddock and plantation damage, often in daylight."),
    ("Foxes", "Released in Victoria in the 1850s for hunting; lambing losses follow the season."),
    ("Rabbits", "Twenty-four released at Barwon Park, Winchelsea, in 1859. The rest is history."),
    ("ATCW", "Authority to Control Wildlife, issued by the Victorian government under the Wildlife Act 1975."),
    ("Game Licence", "Issued by the Game Management Authority; deer are a game species in Victoria."),
  ],
  "about": [
    ("Warragul", (f"Base of operations, grid reference {BASE_GR} on the MGA zone 55 grid." if SHEET else "Base of operations in West Gippsland; jobs anywhere in Victoria by arrangement.")),
    ("AHCPMG304", "A nationally recognised unit for humane dispatch; the standard every job is held to."),
    ("Codes", "Victorian codes of practice for the humane control of each species govern the method."),
    ("Insurance", f"$20 million public liability with {S['insurer']}; a certificate of currency is available on request before work starts."),
  ],
}
def margin_notes(key):
    rows = ''.join(f'<p><sup>{i+1}</sup><span><b style="font-weight:600;color:var(--ink)">{esc(t)}.</b> {esc(d)}</span></p>' for i, (t, d) in enumerate(NOTES[key]))
    return f'<aside class="margin-notes" aria-label="Notes"{per("marginalia")}><h4>Notes</h4>{rows}</aside>'
def fn(n): return f'<sup class="fn" aria-label="note {n}">{n}</sup>'

# ---------------------------------------------------------------- page bodies
def divider(label):
    if not SHEET: return ''
    return f'<div class="wrap divider"{per("scalebar")}><span class="mono">{esc(label)}</span>{scalebar()}</div>'

def drone_band():
    if not S.get('thermal_drone'): return ''
    return f'''
{divider("Thermal drone")}
<section class="band drone"{per("drone")}>
  <div class="wrap drone-grid">
    <div class="stack reveal" style="--gap:16px">
      <p class="eyebrow">New capability</p>
      <h2>Thermal drone scouting with a DJI Matrice 4T</h2>
      <p class="measure">Before a program starts, the drone finds the mob, counts it and maps where it moves, by day or at night. Fewer wasted trips, a better plan, and a record you can keep.</p>
      <ul class="drone-list"><li><b>Scouting</b> where the deer, pigs or dogs actually are</li><li><b>Counts</b> you can use for permits and planning</li><li><b>Night work</b> ahead of the ground team</li><li><b>Stock and property checks</b> after storms or fire</li></ul>
      {report_card("on-dark")}
      <p style="margin:0"><a class="btn btn-quiet" href="{href('services','svc-drone')}"{route_attr('services')} data-focus="svc-drone">Drone scouting details</a></p>
    </div>
    {video_fig("drone-thermal-mob") if "drone-thermal-mob" in MEDIA else slot("gear", "DJI Matrice 4T thermal drone on the tailgate", "", ar="4/3")}
  </div>
</section>'''

REVIEW_POLICY = ("Every genuine review from someone Fitz has worked for goes up, good or bad, whatever the star rating, and each one is matched to a real job first. "
                 "The only ones held back are spam, reviews from people he hasn't worked for, abuse, and anything that names a property's location or a person who hasn't agreed to it. "
                 "Reviews are never edited. A photo that shows where a property is, a number plate or someone's face is left off.")

def review_cards(limit):
    """Testimonials Fitz supplies directly (content/site.json) are baked in; reviews published through the site are added by the script."""
    cards = ''.join(f'<figure class="review reveal"><blockquote><q>{esc(q)}</q></blockquote><figcaption class="who">{esc(w)}</figcaption></figure>' for q, w in S['testimonials'][:limit])
    empty = '' if S['testimonials'] else (f'<div class="review review-empty" id="review-empty"><b>No reviews on the site yet.</b>'
                                          f'<p class="small" style="color:var(--ink-2);margin:0">If Fitz has done a job for you, yours can be the first. <a href="{href("reviews", "write")}">Leave a review</a>.</p></div>')
    return cards + empty

def jobs_band():
    tall, *side = (videos(home=True) + [None, None, None])[:3]
    if not tall: return ''
    return f'''
{divider("From the job")}
<section class="band"{per("video")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">From the job</p><h2>Drone, thermal and trail camera</h2>
      <p class="measure">Real footage from properties across Victoria. Locations are never shown. Nothing plays or downloads until you press play.</p></div>
    <div class="job-grid">
      {video_fig(tall, cls="tall") if MEDIA[tall]['height'] > MEDIA[tall]['width'] else video_fig(tall)}
      <div class="side">{''.join(video_fig(v) for v in side if v)}</div>
    </div>
    <div class="cta-row"><a class="btn btn-secondary" href="{href('gallery')}"{route_attr('gallery')}>All videos and photos</a></div>
  </div>
</section>'''

def home_body():
    hp = S['hero_photo']
    creds_li = ''.join(
        f'<li{" class=note" if i == 7 else ""}><span class="eyebrow">{"Note" if i == 7 else "Credential"}</span><b class="num">{esc(t)}</b><p>{esc(d)}</p></li>'
        for i, (t, d) in enumerate(S['credentials']))
    tiles = ''.join(f'''
    <article class="tile reveal">
      <h3>{esc(t)}</h3><p>{esc(d)}</p>
      <a class="stretch" href="{href('services','svc-'+k)}"{route_attr('services')} data-focus="svc-{k}" aria-hidden="true" tabindex="-1"></a>
      <a class="btn btn-secondary" href="{href('services','svc-'+k)}"{route_attr('services')} data-focus="svc-{k}">Details<span class="sr"> for {esc(t)}</span></a>
    </article>''' for k, t, d in [(k, t, d) for k, t, d, _ in S['services']] + EXTRA_TILES)
    steps = ''.join(f'<li class="reveal"><b>{esc(t)}</b><p>{esc(d)}</p></li>' for t, d in S['steps'])
    status_flag = '' if S.get('credentials_current') else flag('status line Fitz can edit')
    lede_flag = flag(S['lede_flag']) if S.get('lede_flag') else ''
    chips = ''.join(f'<li>{esc(a)}{"<span class=gr>GR " + GR[a][0] + "</span>" if (SHEET and a in GR) else ""}</li>' for a in S['area'])
    return f'''
<section class="hero wrap"{per("hero")}{per("hero-layout")}>
  <div class="hero-grid">
    <div class="stack" style="--gap:22px">
      {meta("Home")}
      <p class="eyebrow"{per("wordmark")}>{esc(S['base'])}, Gippsland · covering all of Victoria</p>
      <h1 id="h-home" tabindex="-1">{esc(S['headline'])}</h1>
      <p class="lede"{per("lede")}>{esc(S['lede'])}{lede_flag}</p>
      <p class="descriptors"{per("brand")}>{' <span aria-hidden="true">·</span> '.join(esc(x) for x in S['descriptors'])}</p>
      {cta_row()}
      {proof_link()}
      {contact_line()}
    </div>
    {pic(hp, ar="4/5", sizes="(min-width:900px) 40vw, 100vw", eager=True) if isinstance(hp, str) else slot(hp[0], hp[1], hp[2], ar="4/5")}
  </div>
</section>
{divider("Credentials")}
<section class="band alt"{per("creds")}{per("setpiece")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal">
      <p class="eyebrow">Licensed · insured · accountable</p>
      <h2>The paperwork is in order before the 4WD leaves the shed</h2>
      <p class="status"><i aria-hidden="true"></i> {esc(S['status_line'])}{status_flag}</p>
      {'<p class="caption"><span class="flag">more credentials to come from Fitz</span> They slot into this wall as plates when they arrive.</p>' if REVIEW else ''}
    </div>
    <ol class="creds reveal" aria-label="Credentials">{creds_li}</ol>
    <div class="cta-row"><a class="btn btn-secondary" href="{href('credentials')}"{route_attr('credentials')}>Credentials and insurance in full</a></div>
  </div>
</section>
{divider("Services")}
<section class="band"{per("services-grid")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">Services</p><h2>What I'm called out for</h2>
      <p class="measure">Deer, rabbit and fox work is most of it. The rest is kangaroos, pigs and wild dogs. Night and thermal where it counts.</p></div>
    <div class="grid grid-3">{tiles}</div>
  </div>
</section>
{drone_band()}
{divider("How it works")}
<section class="band alt"{per("howitworks")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">How it works</p><h2>Four steps, no surprises</h2></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>
{divider("Standards")}
<section class="band"{per("triad")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">Why landholders call Fitz</p><h2>Turns up. Does it properly. Leaves it as found.</h2></div>
    <div class="triad reveal">
      <div><b>Licensed and insured</b><p>Firearms and Game licences, SSAA Farmer Assist, First Aid and $20 million public liability with {esc(S['insurer'])}. Certificates on request.</p></div>
      <div><b>Planned, not improvised</b><p>Every job starts with a walk of the property and a written plan: stock, neighbours, access, safe lines of fire, dates.</p></div>
      <div><b>Humane under the codes</b><p>AHCPMG304 humane dispatch. Clean, legal and professional is the standard, not the upsell.</p></div>
    </div>
  </div>
</section>
{jobs_band()}
{divider("Reviews")}
<section class="band alt" id="reviews-home"{per("testimonials")}{per("reviews")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head reveal"><p class="eyebrow">Reviews</p><h2>What landholders say</h2>
      <p class="measure small" style="color:var(--ink-2)">{esc(REVIEW_POLICY)}</p></div>
    <div class="rv-sum" data-review-summary hidden></div>
    <div class="grid grid-3" data-reviews="3" aria-live="polite">{review_cards(3)}</div>
    <div class="cta-row"><a class="btn btn-secondary" href="{href('reviews', 'write')}">Leave a review</a><a class="btn btn-quiet" href="{href('reviews')}">Read all reviews</a></div>
  </div>
</section>
{divider("Service area")}
<section class="band"{per("area")}{per("topo")}>
  <div class="wrap stack" style="--gap:24px">
    <div class="sec-head reveal"><p class="eyebrow">Service area</p><h2>Based in {esc(S['base'])}, covering all of Victoria</h2>
      <p class="measure">Gippsland comes first: it's home ground. Beyond it the ute goes anywhere in the state, for farms and private landholders, councils and land managers. Ring and we'll work out the trip.</p></div>
    {'<div class="area-grid reveal"><div class="map-scroll">' + locality_map() + '</div>' + legend() + '</div>' if SHEET_MAP else ''}
    <ul class="chips reveal" aria-label="Regions served">{chips}</ul>
  </div>
</section>
<section class="band invert"{per("strip")}>
  <div class="wrap stack" style="--gap:20px">
    <h2 style="max-width:16ch">Got deer on the fence line? Get in touch.</h2>
    {cta_row(' style="border-color:var(--foot-line);color:var(--foot-ink)"', gold=True)}
    <p class="caption">{S['email']} · Instagram {esc(S['instagram_handle'])} · Facebook {esc(S['facebook_label'])}</p>
  </div>
</section>'''

def services_body():
    notes = {k: i + 1 for i, (k, _) in enumerate(NOTES['services'])}
    def row(k, t, d, bullets):
        marks = {'deer': fn(notes['Sambar']) + fn(notes['Fallow']), 'kangaroos': fn(notes['ATCW']), 'foxes': fn(notes['Foxes']), 'rabbits': fn(notes['Rabbits'])}.get(k, '')
        return f'''
    <article class="service" id="svc-{k}">
      <div class="stack" style="--gap:8px"><h3 tabindex="-1">{esc(t)}{marks}</h3><p class="small" style="color:var(--ink-2)">{esc(d)}</p></div>
      <ul>{''.join(f'<li>{esc(x)}</li>' for x in bullets)}</ul>
    </article>'''
    rows = ''.join(row(k, t, d, b) for k, t, d, b in S['services'])
    drone = f'''
      <article class="service" id="svc-drone"><div class="stack" style="--gap:8px"><h3 tabindex="-1">Thermal drone scouting</h3><p class="small" style="color:var(--ink-2)">A DJI Matrice 4T thermal drone for scouting, counts and night work: find the mob, map where it moves and plan the program before anyone walks in.</p></div>
        <ul><li>Pre-program counts and mob location</li><li>Night scouting ahead of ground work</li><li>Finding stock after a storm or fire</li><li>Mapping movement corridors and access</li></ul><div style="grid-column:1/-1">{report_card()}</div></article>''' if S.get('thermal_drone') else ''
    faqs = ''.join(f'<details class="faq"><summary>{esc(g[1][0][0])}</summary><p>{answer(g[1][0][1])}</p></details>' for g in S['faq_groups'])
    clients = ''.join(f'<article class="tile"><h3>{esc(t)}</h3><p>{esc(d)}</p></article>' for t, d in S['clients'])
    return f'''
<section class="page" aria-labelledby="h-services"{per("services")}>
  <div class="wrap stack" style="--gap:36px">
    <div class="sec-head">{meta("Services")}<p class="eyebrow">Services</p><h1 id="h-services" tabindex="-1" style="font-size:var(--fs-h2)">Pest and vermin control across Victoria</h1>
      <p class="measure">Every job is planned, insured and carried out humanely under the relevant Victorian codes of practice. Deer control on farms and kangaroo culling are the two most common call-outs; the rest of the list is below.</p></div>
    <div class="stack" style="--gap:16px"{per("clients")}><h2 class="sub">Who I work for</h2><div class="grid grid-2">{clients}</div></div>
    <div class="notes-layout">
      <div>{rows}
        <article class="service" id="svc-night"><div class="stack" style="--gap:8px"><h3 tabindex="-1">Night work and thermal</h3><p class="small" style="color:var(--ink-2)">Most feral animals move after dark. Thermal optics let me find them, count them and take them cleanly without lighting up the whole paddock.</p></div>
          <ul><li>Thermal spotting and shooting</li><li>Quiet, planned movements around stock</li><li>Counts you can use for permits and planning</li></ul></article>{drone}
      </div>
      {margin_notes('services')}
    </div>
    <div class="prose"{per("privacy")}>
      <h3>What a job includes</h3>
      <ul><li>A site visit and a written plan: stock, neighbours, access, dates and safety.</li><li>Humane dispatch to AHCPMG304 and the code for each species.</li><li>Carcass handling and disposal as agreed with you.</li><li>A short report afterwards and a follow-up if the numbers call for it.</li></ul>
      <h3>Permits and codes, in plain language</h3>
      <p class="small" style="color:var(--ink-2)">Kangaroo control on private land needs an Authority to Control Wildlife{fn(notes['ATCW'])} from the Victorian government; I can help with the application. Deer are a game species and are taken under a Game Licence{fn(notes['Game Licence'])}. All work follows the relevant Victorian codes of practice for the humane control of the species involved.</p>
    </div>
    <div class="stack" style="--gap:12px;margin-top:36px"{per("faq")}><h2 class="sub">Common questions</h2><div>{faqs}</div><p><a class="btn btn-secondary" href="{href('faq')}"{route_attr('faq')}>All questions and answers</a></p></div>
    <div class="cta-row"{per("cta")}><a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a><a class="btn btn-quiet num" href="tel:{S['phone_e164']}">or call {S['phone_display']}</a></div>
  </div>
</section>'''

def about_body():
    cur = esc(S['credentials_current']) if S.get('credentials_current') else flag('month year').strip()
    current_line = (f'Credentials current as at {cur}. ' if cur else '') + 'Certificates of currency supplied on request before work starts.'
    portrait = S['about_photos'][0]
    ledger = ''.join(f'<li><b>{esc(t)}</b><span class="lead" aria-hidden="true"></span><span>{esc(d)}</span></li>' for t, d in S['credentials'][:7])
    return f'''
<section class="page" aria-labelledby="h-about"{per("about")}>
  <div class="wrap">
    <div class="notes-layout">
      <div class="prose">
        {meta("About")}
        <p class="eyebrow">About</p>
        <h1 id="h-about" tabindex="-1" style="font-size:var(--fs-h2)">Based in {esc(S['base'])}{fn(1)}, working across all of Victoria</h1>
        <div class="bio"{per("bio")}>{photo(portrait, ar="1/1", sizes="(min-width:700px) 640px, 100vw", eager=True)}<p class="lede">{esc(S['about_story'])}</p></div>
        <p>The standard is clean, legal and professional: a plan before the first night, humane dispatch to AHCPMG304{fn(2)}, and a short report after. No trophies, no mess, no surprises for the neighbours{fn(3)}.</p>
        <p>I'm insured with {esc(S['insurer'])} for $20 million public liability{fn(4)}, and I work for farms and private landholders, councils and land managers: Gippsland first, then anywhere in Victoria.</p>
        <h3>Credentials</h3>
        <ul class="ledger num"{per("ledger")}>{ledger}</ul>
        <p class="caption">{current_line}</p>
        <p><a class="btn btn-secondary" href="{href('credentials')}"{route_attr('credentials')}>Credentials and insurance in full</a></p>
        <figure class="card-figure"{per("brand")}><img src="{asset('/brand/fitz-card.jpg')}" alt="The Fitz Feral Hunters card: rifle mark, Protecting Victoria's Farms, contract pest control, deer and feral management, thermal hunting, farm security, fully insured, 0499 866 580" width="1280" height="755" loading="lazy" decoding="async"><figcaption class="caption">The card, as supplied. The site's green, gold and cream are sampled from it.</figcaption></figure>
      </div>
      {margin_notes('about')}
    </div>
  </div>
</section>'''

def gallery_photos():
    return [p for p in S.get('gallery_photos', []) if p in MEDIA]

def gallery_body():
    g = gallery_photos()
    vids = ''.join(f'<li>{video_fig(v, ar="16/9")}</li>' for v in videos())   # one frame size for every clip
    items = ''.join(f'''<li><figure style="margin:0"><button type="button" data-lb="{i}" aria-label="Open photo {i+1} of {len(g)}: {esc(MEDIA[p]['title'])}">{photo(p, ar="4/3", sizes="(min-width:700px) 33vw, 50vw")}</button><figcaption><span class="mono" style="color:var(--ink-2)">Fig. {i+1:02d}</span> · {esc(MEDIA[p]['caption'])}</figcaption></figure></li>''' for i, p in enumerate(g))
    lb = '' if not g else f'''
<dialog class="lightbox" id="lightbox" closedby="any" aria-labelledby="lb-cap" data-lightbox-state="closed"{per("gallery")}>
  <div class="frame">
    <div class="bar"><span class="eyebrow num" id="lb-pos">1 of {len(g)}</span>
      <div style="display:flex;gap:8px"><button type="button" class="btn btn-secondary" id="lb-prev" aria-label="Previous photo">&larr;</button><button type="button" class="btn btn-secondary" id="lb-next" aria-label="Next photo">&rarr;</button><button type="button" class="btn btn-secondary" id="lb-close" aria-label="Close">&times;</button></div></div>
    <div id="lb-slot"></div>
    <p id="lb-cap" class="caption">{esc(MEDIA[g[0]]['caption'])}</p>
  </div>
</dialog>'''
    return f'''
<section class="page" aria-labelledby="h-gallery"{per("gallery")}>
  <div class="wrap stack" style="--gap:28px">
    <div class="sec-head">{meta("Gallery")}<p class="eyebrow">Gallery</p><h1 id="h-gallery" tabindex="-1" style="font-size:var(--fs-h2)">From the job</h1>
      <p class="measure">Drone, thermal and trail camera footage, and photos from the field. No property locations are shown and nobody appears without their say-so; every frame carries the plate that says so.</p>
      <p><a class="btn btn-secondary" href="{href('drone-report')}">See a sample drone report</a></p></div>
    <nav class="faq-index" aria-label="Gallery sections"><ul><li><a href="#g-video">Video <span class="count num">{len(videos())}</span></a></li><li><a href="#g-photos">Photos <span class="count num">{len(g)}</span></a></li></ul></nav>
    <div class="stack g-block" id="g-video" style="--gap:16px"><h2 class="sub">Video</h2><ul class="vids">{vids}</ul></div>
    <div class="stack g-block" id="g-photos" style="--gap:16px;margin-top:48px"><h2 class="sub">Photos</h2><ul class="gal">{items}</ul></div>
  </div>
</section>{lb}'''

def contact_body():
    checks = ''.join(f'<label><input type="checkbox" name="help" value="{esc(x)}"> {esc(x)}</label>' for x in ["Deer", "Kangaroos", "Pigs", "Foxes", "Rabbits", "Wild dogs", "Not sure yet"])
    action = '#contact' if ARTIFACT else '/api/enquiry'
    note = (('Mockup: this review build does not send. On the live site the form posts to a server function that emails ' if ARTIFACT else 'Review build: enquiries are received by the site\'s server function and emailed to ') + S['email'] + (' and shows the confirmation below.' if ARTIFACT else ' once the mail key is configured.') + ' Without script the plain form still submits.') if REVIEW else ''
    ts = f'<div class="cf-turnstile" data-sitekey="{esc(TURNSTILE)}" data-theme="light" data-size="flexible"></div>' if TURNSTILE else ''
    return f'''
<section class="page" aria-labelledby="h-contact">
  <div class="wrap contact-grid">
    <div class="stack" style="--gap:28px">
      <div class="sec-head" style="margin:0">{meta("Contact")}<p class="eyebrow">Contact</p><h1 id="h-contact" tabindex="-1" style="font-size:var(--fs-h2)">Ring, email or send the form</h1>
        <p class="measure">Phone is quickest. If I'm out on a job I'll ring back the same day where I can.</p></div>
      <div class="contact-list"{per("contactline")}>
        <div class="kv"><b>{ico("i-phone")}Phone</b><div class="row"><span>{tel()}</span><span class="hint-copy">Click to copy</span><a class="btn btn-secondary touch-only" href="tel:{S['phone_e164']}" aria-label="Call {S['phone_display']}">Call</a></div></div>
        <div class="kv"><b>{ico("i-mail")}Email</b><div class="row"><span style="font-size:19px">{mailto()}</span><button type="button" class="copy" data-copy="{S['email']}" aria-label="Copy email address">Copy</button></div></div>
        <div class="kv"><b>{ico("i-pin")}Based in</b><div class="row"><span style="font-size:19px">{esc(S['base'])}, Gippsland VIC</span>{'<span class="mono" style="color:var(--ink-2)">GR <span class="num">' + BASE_GR + '</span> · MGA 55</span>' if SHEET else '<span class="mono" style="color:var(--ink-2)">Jobs anywhere in Victoria</span>'}</div></div>
        <div class="kv"{per("socials")}><b>Follow the work</b><div class="socials"><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {esc(S['instagram_handle'])} {ico("i-ext")}</a><a href="{S['facebook']}" target="_blank" rel="noopener">Facebook · {esc(S['facebook_label'])} {ico("i-ext")}{flag('confirm page URL')}</a></div></div>
      </div>
      <div class="stack" style="--gap:12px;margin-top:28px"><p class="eyebrow" style="margin:0">Still deciding?</p>{report_card()}</div>
    </div>
    <div>
      <form class="form" id="enquiry" action="{action}" method="post"{per("form")} aria-describedby="form-note">
        <p class="note" id="draft-note" role="status" hidden>Restored the enquiry you started earlier. Nothing has been sent.</p>
        <div class="summary" id="err-summary" role="alert" tabindex="-1" hidden><b>Fix the following to send your enquiry</b><ul id="err-list"></ul></div>
        <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" type="text" autocomplete="name" required enterkeyhint="next" maxlength="120"><span class="err" id="e-name">Enter your name so I know who to ask for.</span></div>
        <div class="field"><label for="f-phone">Phone</label><span class="hint">Mobile is best. Any format is fine, e.g. 0412 345 678.</span><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required enterkeyhint="next" pattern="[0-9+\\(\\)\\s\\-]{{8,}}" maxlength="40"><span class="err" id="e-phone">Enter a phone number with at least eight digits.</span></div>
        <div class="field"><label for="f-email">Email <span style="font-weight:400;color:var(--ink-2)">(optional)</span></label><input id="f-email" name="email" type="email" autocomplete="email" inputmode="email" enterkeyhint="next" maxlength="200"><span class="err" id="e-email">That email address doesn't look right. Check it or leave it blank.</span></div>
        <div class="field"><label for="f-loc">Property location</label><span class="hint">Town or nearest locality, e.g. Neerim South. No street address needed.</span><input id="f-loc" name="location" type="text" autocomplete="address-level2" required enterkeyhint="next" maxlength="120"><span class="err" id="e-loc">Tell me the town or locality so I can plan the trip.</span></div>
        <fieldset class="field" id="f-help"><legend>What do you need help with?</legend><span class="hint">Tick everything that applies.</span><div class="checks">{checks}</div><span class="err" id="e-help">Tick at least one. "Not sure yet" is fine.</span></fieldset>
        <div class="field"><label for="f-msg">Anything else <span style="font-weight:400;color:var(--ink-2)">(optional)</span></label><span class="hint">Damage, numbers, timing, access: whatever you've noticed.</span><textarea id="f-msg" name="message" enterkeyhint="done" maxlength="2000"></textarea></div>
        <div class="sr" aria-hidden="true"><label for="f-company">Leave this field empty</label><input id="f-company" name="company" type="text" tabindex="-1" autocomplete="off"></div>
        {ts}
        <div class="cta-row"><button type="submit" class="btn btn-primary" id="f-submit"><span class="spin" aria-hidden="true"></span><span class="lbl">Send enquiry</span></button><span class="note" id="form-note">Your details go to Fitz only. No mailing list, nothing shared.</span></div>
        {f'<p class="note">{note}</p>' if note else ''}
      </form>
      <div class="confirm" id="confirm" role="status" tabindex="-1" hidden{per("confirm")}>
        <b>Enquiry received</b>
        <p>Thanks, <span id="confirm-name">there</span>. Fitz will ring the number you gave, usually within two business days.</p>
        <p class="small" style="color:var(--ink-2)"><b style="font-weight:600;color:var(--ink)">What happens next:</b> a quick phone chat about the property and the animals, then a site visit if it's a fit. If it's urgent, call <a class="num" href="tel:{S['phone_e164']}">{S['phone_display']}</a>.</p>
        <p class="small"><a href="{href('contact','enquiry')}" id="confirm-reset">Send another enquiry</a></p>
      </div>
    </div>
  </div>
</section>{sent_dialog()}'''

def sent_dialog():
    """The receipt that opens over the page after a form is sent: what was sent, whether it reached Fitz, and a way through if it didn't."""
    return f'''
<dialog class="sent" id="sent" aria-labelledby="sent-title" aria-describedby="sent-lede" data-state="sent"{per("sent")}>
  <div class="frame">
    <p class="eyebrow" id="sent-kicker">Enquiry</p>
    <h2 id="sent-title" tabindex="-1">Sent to Fitz</h2>
    <p id="sent-lede"></p>
    <dl class="sent-list" id="sent-list"></dl>
    <p class="caption num" id="sent-ref"></p>
    <div class="cta-row" id="sent-actions"></div>
    <div class="cta-row"><button type="button" class="btn btn-primary" id="sent-close">Done</button></div>
  </div>
</dialog>'''

REGIONS = S['area'] + ['Elsewhere in Victoria']
PROPERTY_TYPES = ['Beef', 'Dairy', 'Sheep', 'Mixed farming', 'Lifestyle block', 'Horticulture or vineyard', 'Other']

REVIEW_SERVICES = [t for _, t, _, _ in S['services']] + (['Thermal drone scouting'] if S.get('thermal_drone') else []) + ['Other']
STAR_WORDS = ['', 'Poor', 'Fair', 'Good', 'Very good', 'Excellent']

def month_options():
    """The last 24 months, newest first, then "earlier". The page script rebuilds this list from today's date."""
    t = datetime.date.today(); y, m = t.year, t.month; out = []
    for _ in range(24):
        out.append(f'<option value="{y}-{m:02d}">{datetime.date(y, m, 1).strftime("%B %Y")}</option>')
        m -= 1
        if m == 0: y, m = y - 1, 12
    return ''.join(out) + '<option value="earlier">More than two years ago</option>'

def reviews_body():
    opt = lambda xs: ''.join(f'<option>{esc(x)}</option>' for x in xs)
    google = f'<a class="btn btn-secondary" href="{esc(S["google_review_url"])}" target="_blank" rel="noopener">Review us on Google {ico("i-ext")}</a>' if S.get('google_review_url') else ''
    ts = f'<div class="cf-turnstile" data-sitekey="{esc(TURNSTILE)}" data-theme="light" data-size="flexible"></div>' if TURNSTILE else ''
    stars = ''.join(f'<input class="sr" type="radio" name="rating" id="r-star-{n}" value="{n}" required><label for="r-star-{n}"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-star"/></svg><span class="sr">{n} star{"s" if n > 1 else ""}, {STAR_WORDS[n].lower()}</span></label>' for n in range(1, 6))
    return f'''
<section class="page" aria-labelledby="h-reviews"{per("reviews")}>
  <div class="wrap stack" style="--gap:32px">
    <div class="sec-head">{meta("Reviews")}<p class="eyebrow">Reviews</p><h1 id="h-reviews" tabindex="-1" style="font-size:var(--fs-h2)">What landholders say</h1>
      <p class="measure">{esc(REVIEW_POLICY)}</p>
      <div class="rv-sum" data-review-summary hidden></div>
      <a class="btn btn-secondary rv-head-cta" href="#write">Leave a review</a></div>
    <div class="grid grid-2" data-reviews="50" aria-live="polite">{review_cards(50)}</div>
    <div class="reviews-write" id="write">
      <div class="sec-head" style="margin:0"><h2>Leave a review</h2>
        <p class="measure small" style="color:var(--ink-2)">For landholders Fitz has worked for. It goes to Fitz first and is published once he's matched it to your job. Your email and phone number are only used for that check and are never shown.</p>
        {google}</div>
      <div class="rv-how"{per("verify")}><h3>How Fitz knows it's a real job</h3>
        <ol><li><b>Got a review link from Fitz after the job?</b> Use that. Your review shows as a verified job.</li>
          <li><b>No link?</b> Tell us the month of the job and the phone number or email you booked with. Fitz matches it to his records before anything goes up.</li>
          <li>Reviews that can't be matched to a job he did aren't published.</li></ol></div>
      <form class="form" id="review-form" action="/api/reviews" method="post" novalidate{per("form")}>
        <p class="rv-invite" id="r-invite-note" hidden>{ico("i-check")}<span id="r-invite-text">You're using Fitz's review link, so your review will show as a <b>verified job</b>.</span></p>
        <input type="hidden" name="invite" id="r-invite" value="">
        <div class="summary" id="rv-summary" role="alert" tabindex="-1" hidden><b>Fix the following to send your review</b><ul id="rv-errs"></ul></div>
        <fieldset class="field rate" id="r-rating"><legend>Your rating</legend><span class="hint">Every rating is published, from one star to five.</span>
          <div class="row"><div class="opts">{stars}</div><span class="rate-out" id="r-rate-out" aria-hidden="true">Tap a star</span></div>
          <span class="err">Choose a star rating from 1 to 5.</span></fieldset>
        <div class="field"><label for="r-name">Your name</label><span class="hint">First name and last initial, e.g. Sam T.</span><input id="r-name" name="name" type="text" autocomplete="given-name" required maxlength="40"><span class="err">Enter your first name and last initial.</span></div>
        <div class="grid grid-2" style="gap:20px">
          <div class="field"><label for="r-region">Region</label><select id="r-region" name="region" required><option value="">Choose…</option>{opt(REGIONS)}</select><span class="err">Choose a region.</span></div>
          <div class="field"><label for="r-property">Property type</label><select id="r-property" name="property" required><option value="">Choose…</option>{opt(PROPERTY_TYPES)}</select><span class="err">Choose a property type.</span></div>
          <div class="field"><label for="r-service">Work Fitz did</label><select id="r-service" name="service" required><option value="">Choose…</option>{opt(REVIEW_SERVICES)}</select><span class="err">Choose the work Fitz did.</span></div>
          <div class="field"><label for="r-month">When was the job?</label><select id="r-month" name="jobMonth" required><option value="">Choose…</option>{month_options()}</select><span class="err">Choose the month of the job.</span></div>
        </div>
        <div class="field"><label for="r-text">Your review</label><span class="hint" id="r-text-hint">What the problem was, what Fitz did, and how it went. At least 250 characters, about four or five sentences. Please don't name the property or where it is.</span><textarea id="r-text" name="text" required minlength="250" maxlength="2000" rows="7" aria-describedby="r-text-hint r-count"></textarea><span class="count" id="r-count">At least 250 characters</span><span class="err">Write at least 250 characters.</span></div>
        <fieldset class="field" id="r-photos-field" hidden{per("photos")}><legend>Photos (optional, up to 3)</legend>
          <span class="hint">The problem, the job or the result. Location details are stripped from the files, and Fitz checks every photo before it goes up, so leave out faces, number plates and anything that shows where the property is.</span>
          <ul class="rv-picks" id="r-picks"></ul>
          <div class="pick-row"><input class="sr pick-in" type="file" id="r-photos" accept="image/*" multiple><label class="btn btn-secondary" for="r-photos" id="r-photos-btn">Add photos</label></div>
          <span class="err" id="r-photos-err"></span></fieldset>
        <div class="grid grid-2" style="gap:20px">
          <div class="field"><label for="r-email">Email</label><span class="hint">Only so Fitz can match your job. Never shown.</span><input id="r-email" name="email" type="email" autocomplete="email" inputmode="email" required maxlength="200"><span class="err">Enter a valid email address.</span></div>
          <div class="field"><label for="r-phone">Phone you booked with <span style="font-weight:400">(optional)</span></label><span class="hint">Helps Fitz match your job. Never shown.</span><input id="r-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="30"><span class="err">Check the number, or leave it blank.</span></div>
        </div>
        <div class="field consent"><label><input type="checkbox" id="r-consent" name="consent" value="yes" required> OK to publish this review on this website with my star rating, first name and initial, region, property type, the month of the job, and any photos Fitz approves.</label><span class="err">Tick to agree to publishing.</span></div>
        <div class="sr" aria-hidden="true"><label for="r-company">Leave this field empty</label><input id="r-company" name="company" type="text" tabindex="-1" autocomplete="off"></div>
        {ts}
        <div class="cta-row"><button type="submit" class="btn btn-primary" id="r-submit"><span class="spin" aria-hidden="true"></span><span class="lbl">Send review</span></button></div>
      </form>
      <div class="review review-closed" id="review-closed" hidden><b>Reviews open soon</b><p class="small" style="margin:0;color:var(--ink-2)">The review form isn't switched on yet. In the meantime, call {tel()} or email {mailto()}.</p></div>
    </div>
  </div>
</section>{sent_dialog()}'''

EXTRA_TILES = [("night", "Night work and thermal", "Most feral animals move after dark. Thermal optics find them, count them and take them cleanly, without lighting up the paddock.")] + (
    [("drone", "Thermal drone scouting", "A DJI Matrice 4T finds the mob, counts it and maps where it moves before anyone walks in.")] if S.get('thermal_drone') else [])

def slug(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

def credentials_body():
    creds = [c for c in S['credentials'] if c[0] not in ('$20m public liability', 'Certificates on request')]
    li = ''.join(f'<li><span class="eyebrow">Credential</span><b class="num">{esc(t)}</b><p>{esc(d)}</p></li>' for t, d in creds)
    return f'''
<section class="page" aria-labelledby="h-credentials"{per("creds")}>
  <div class="wrap stack" style="--gap:36px">
    <div class="sec-head">{meta("Credentials")}<p class="eyebrow">Credentials</p><h1 id="h-credentials" tabindex="-1" style="font-size:var(--fs-h2)">Licensed, insured and accountable</h1>
      <p class="measure">Every job is done under current licences, a humane dispatch qualification and $20 million public liability insurance with {esc(S['insurer'])}. Certificates and currency documents are available on request, before any work starts.</p></div>
    <div class="stack" style="--gap:16px"><h2 class="sub">Licences and accreditations</h2><ol class="creds creds-6" aria-label="Licences and accreditations">{li}</ol></div>
    <div class="grid grid-2"{per("cred-detail")}>
      <article class="tile cred-card"><p class="eyebrow">Insurance</p><h3>$20 million public liability</h3><p>Insured with {esc(S['insurer'])} for every job. A certificate of currency is available on request.</p></article>
      <article class="tile cred-card"><p class="eyebrow">Paperwork</p><h3>Certificates on request</h3><p>Certificates and currency documents are supplied on request, before work starts. Licence and membership numbers are shared with you directly rather than published here.</p></article>
    </div>
    <div class="prose"{per("privacy")}>
      <h2 class="sub">Codes and permits</h2>
      <p>All work follows the relevant Victorian codes of practice for the humane control of each species, and every animal is dispatched to the standard of AHCPMG304, a nationally recognised unit.</p>
      <p>Deer are a game species in Victoria and are taken under a Game Licence. Kangaroo control on private land needs an Authority to Control Wildlife (ATCW) from the Victorian government; I can help with the application.</p>
    </div>
    <div class="cta-row"{per("cta")}><a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a><a class="btn btn-quiet" href="{href('faq')}"{route_attr('faq')}>Read the FAQ</a></div>
  </div>
</section>'''

def answer(a):
    """FAQ answer text, escaped, with [text](/path) turned into a link to one of the site's own pages."""
    return re.sub(r'\[([^\]]+)\]\((/[a-z0-9\-#/]*)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', esc(a))

def plain(a): return re.sub(r'\[([^\]]+)\]\((/[a-z0-9\-#/]*)\)', r'\1', a)

def faq_body():
    groups = S['faq_groups']
    index = ''.join(f'<li><a href="#faq-{slug(g)}">{esc(g)}</a></li>' for g, _ in groups)
    body = ''.join(f'''
    <div class="faq-group" id="faq-{slug(g)}"><h2 class="sub">{esc(g)}</h2><div>{''.join(f'<details class="faq"><summary>{esc(q)}</summary><p>{answer(a)}</p></details>' for q, a in qs)}</div></div>''' for g, qs in groups)
    return f'''
<section class="page" aria-labelledby="h-faq"{per("faq")}>
  <div class="wrap stack" style="--gap:32px">
    <div class="sec-head">{meta("FAQ")}<p class="eyebrow">FAQ</p><h1 id="h-faq" tabindex="-1" style="font-size:var(--fs-h2)">Questions landholders ask</h1>
      <p class="measure">Pricing, carcasses, stock, neighbours, paperwork. Anything not covered here, ring {tel()}.</p></div>
    <nav class="faq-index" aria-label="Question topics"><ul>{index}</ul></nav>
    {body}
    <div class="cta-row"{per("cta")}><a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Request a quote</a><a class="btn btn-quiet" href="{href('credentials')}"{route_attr('credentials')}>Credentials and insurance</a></div>
  </div>
</section>'''

def report_card(where=''):
    """The sample report as a card that looks like the report's first page: the one piece of proof no competitor offers."""
    R, f = REPORT, MEDIA['report-fig1']
    rows = [r for r in R['meta'] if r[0] in ('Report date', 'Drone platform', 'Location')]
    meta_rows = ''.join(f'<span class="rc-k">{esc(k)}</span><span class="rc-v">{esc(v.replace(" (withheld)", ""))}</span>' for k, v in rows)
    return f'''<a class="report-card{" " + where if where else ""}" href="{href('drone-report')}"{per("report-card")}>
      <span class="rc-sheet" aria-hidden="true"><span class="rc-run">Fitz Feral Hunters · Drone survey report</span><span class="rc-title">{esc(R['title'])}</span><span class="rc-meta">{meta_rows}</span><img src="{f['src']}" alt="" width="{f['width']}" height="{f['height']}" loading="lazy" decoding="async"></span>
      <span class="rc-body"><span class="rc-tag">{ico("i-doc", "rc-ico")}Real job · sample report</span><span class="rc-head">See what a drone survey gives you</span><span class="rc-text">A real report from a Gippsland property: what was seen, the habitat, findings and next steps. Property details removed.</span><span class="btn btn-gold rc-cta">Read the report <span aria-hidden="true">&rarr;</span></span></span>
    </a>'''

def proof_link():
    return f'<a class="proof-link" href="{href("drone-report")}"{per("report-card")}>{ico("i-doc", "rc-ico")}<span><b>Real job:</b> see a sample drone survey report</span><span aria-hidden="true">&rarr;</span></a>'

def report_fig(mid):
    m = MEDIA[mid]
    return (f'<figure class="report-fig"><div class="slot photo" style="--ar:{m["width"]}/{m["height"]}"><picture><source type="image/webp" srcset="{m["src_webp"]}">'
            f'<img src="{m["src"]}" alt="{esc(m["alt"])}" width="{m["width"]}" height="{m["height"]}" loading="lazy" decoding="async"></picture>{corners()}<span class="plate">Location withheld</span></div>'
            f'<figcaption>{esc(m["caption"])}</figcaption></figure>')

def report_body():
    R = REPORT
    meta_rows = ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in R['meta'])
    return f'''
<section class="page" aria-labelledby="h-drone-report"{per("report")}>
  <div class="wrap stack" style="--gap:32px">
    <div class="sec-head">{meta("Sample report")}<p class="eyebrow">Drone scouting · sample report</p><h1 id="h-drone-report" tabindex="-1" style="font-size:var(--fs-h2)">What a drone survey gives you</h1>
      <p class="measure">A real report from a drone survey on a rural property in Gippsland, October 2026, with the property's details removed. Every scouting job ends with a report like this: what was seen, what the ground is like, and what to do next.</p>
      <p class="caption measure">This survey used a standard visual (RGB) camera. Thermal surveys with the DJI Matrice 4T use the same format and add heat signatures, which find animals in cover and at night.</p></div>
    <article class="report" aria-labelledby="report-title">
      <header class="report-head">
        <p class="report-run">Fitz Feral Hunters · Drone survey report</p>
        <h2 id="report-title">{esc(R['title'])}</h2>
        <p class="report-sub">{esc(R['subtitle'])}</p>
        <dl class="report-meta">{meta_rows}</dl>
      </header>
      <h3>1. Executive summary</h3><p>{esc(R['summary'])}</p>
      <h3>2. Key observations</h3>
      <h4>Animal sightings</h4><p>{esc(R['sightings'])}</p>{report_fig('report-fig1')}
      <h4>Habitat and terrain</h4><p>{esc(R['habitat'])}</p>{report_fig('report-fig2')}
      <h3>3. Findings</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in R['findings'])}</ul>
      <h3>4. Recommendations</h3><ol>{''.join(f'<li>{esc(x)}</li>' for x in R['recommendations'])}</ol>
      <h3>5. Conclusion</h3><p>{esc(R['conclusion'])}</p>
      <footer class="report-foot"><p><b>Prepared by</b><br>{'<br>'.join(esc(x) for x in R['prepared'])}</p><p class="caption">{esc(R['disclaimer'])}</p></footer>
    </article>
    <div class="cta-row"{per("cta")}><a class="btn btn-primary" href="{href('contact','enquiry')}"{route_attr('contact')} data-focus="enquiry">Ask for a drone survey</a><a class="btn btn-quiet" href="{href('services','svc-drone')}"{route_attr('services')}>Drone scouting details</a></div>
  </div>
</section>'''

def extra_ld(key):
    if key != 'faq': return ''
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for _, qs in S['faq_groups'] for q, a in qs]}
    return '\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'

def notfound_body():
    return f'''
<section class="page notfound" aria-labelledby="h-404">
  <div class="wrap prose">
    <p class="eyebrow">404</p>
    <h1 id="h-404" style="font-size:var(--fs-h2)">That page isn't here</h1>
    <p>The address may have been mistyped, or the page has moved. The main pages are below, and the phone always works.</p>
    <ul class="nf-links">{''.join(f'<li><a href="{h}">{t}</a></li>' for _, h, t in PAGES)}</ul>
    <p>Call {tel()}</p>
  </div>
</section>'''

# ---------------------------------------------------------------- script
SCRIPT = r"""
<script>
(function(){
  var root=document.documentElement;
  var ARTIFACT=%%ARTIFACT%%;
  /* hash router (artifact build only): five sections, bare tokens */
  if(ARTIFACT){
    var pages=[].slice.call(document.querySelectorAll('[data-page]')), tokens=pages.map(function(p){return p.id});
    var titles=%%TITLES%%;
    var live=document.getElementById('route-live');
    function current(){var h=(location.hash||'#home').slice(1);return tokens.indexOf(h)>-1?h:'home'}
    function show(tok,focusId){
      pages.forEach(function(p){p.hidden=(p.id!==tok)});
      [].forEach.call(document.querySelectorAll('[data-route]'),function(a){ if(a.closest('.nav, .drawer, .site-foot')){ if(a.getAttribute('data-route')===tok && !a.classList.contains('btn')) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); } });
      var d=document.getElementById('drawer'); if(d) d.removeAttribute('open');
      document.title=titles[tok]||document.title; if(live) live.textContent=(titles[tok]||'').split(' · ')[0];
      var target=focusId?document.getElementById(focusId):null;
      if(target){ target.scrollIntoView({block:'start'}); (target.querySelector('input')||target).focus({preventScroll:true}); }
      else { window.scrollTo({top:0,behavior:'instant'}); var h=document.getElementById('h-'+tok); if(h) h.focus({preventScroll:true}); }
    }
    document.addEventListener('click',function(e){ var a=e.target.closest('a[data-route]'); if(!a) return; var tok=a.getAttribute('data-route'); e.preventDefault(); var f=a.getAttribute('data-focus'); if(location.hash!=='#'+tok){ history.pushState(null,'','#'+tok); } show(tok,f); });
    window.addEventListener('hashchange',function(){show(current())}); window.addEventListener('popstate',function(){show(current())});
    show(current());
  }
  var PHONE=%%PHONE%%, E164=%%E164%%, EMAIL=%%EMAIL%%;
  /* toast: one shared polite live region, created at load so the first message is announced */
  var toastEl=document.createElement('div'), toastT=null; toastEl.className='toast'; toastEl.setAttribute('role','status'); toastEl.setAttribute('aria-live','polite'); document.body.appendChild(toastEl);
  function toast(msg){ toastEl.textContent=msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT=setTimeout(function(){ toastEl.classList.remove('on'); },2400); }
  function selectText(el){ try{ var r=document.createRange(); r.selectNodeContents(el); var s=getSelection(); s.removeAllRanges(); s.addRange(r); }catch(e){} }
  function copyText(txt,ok,fail){ try{ navigator.clipboard.writeText(txt).then(ok,fail); }catch(err){ fail(); } }
  /* copy buttons (email) */
  [].forEach.call(document.querySelectorAll('.copy'),function(b){
    b.addEventListener('click',function(){
      var txt=b.getAttribute('data-copy'), done=function(){b.setAttribute('data-state','copied');b.textContent='Copied';toast('Copied — '+txt);setTimeout(function(){b.removeAttribute('data-state');b.textContent='Copy'},1600)};
      function fallback(){ var el=b.previousElementSibling; if(el) selectText(el); toast('Press Ctrl+C (⌘C on Mac) to copy'); }
      copyText(txt,done,fallback);
    });
  });
  /* phone numbers: touch phones dial (the plain tel: link); anything with a fine pointer copies the number instead */
  var touch=window.matchMedia?matchMedia('(hover: none) and (pointer: coarse)'):{matches:true};
  function telLabels(){ root.setAttribute('data-input',touch.matches?'touch':'pointer'); [].forEach.call(document.querySelectorAll('a[href^="tel:"]'),function(a){ a.setAttribute('aria-label',(touch.matches?'Call ':'Copy phone number ')+PHONE); if(!touch.matches) a.title='Click to copy '+PHONE; else a.removeAttribute('title'); }); }
  telLabels(); if(touch.addEventListener) touch.addEventListener('change',telLabels);
  document.addEventListener('click',function(e){
    var a=e.target.closest && e.target.closest('a[href^="tel:"]'); if(!a) return;
    if(touch.matches || e.defaultPrevented || e.button!==0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    copyText(PHONE,function(){ toast('Number copied — '+PHONE); },function(){ selectText(a); toast('Press Ctrl+C (⌘C on Mac) to copy '+PHONE); });
  });
  /* videos: a play button over the poster (native controls take over once playing; without script the native controls show), one at a time */
  [].forEach.call(document.querySelectorAll('.vid video'),function(v){
    var b=document.createElement('button'); b.type='button'; b.className='play'; b.setAttribute('aria-label','Play video: '+(v.getAttribute('aria-label')||'').replace(/^Video: /,'')); b.innerHTML='<span aria-hidden="true"></span>';
    v.controls=false; v.parentNode.appendChild(b);
    b.addEventListener('click',function(){ v.controls=true; b.remove(); var pr=v.play(); if(pr&&pr.catch) pr.catch(function(){}); try{ v.focus({preventScroll:true}); }catch(e){} });
    v.addEventListener('play',function(){ [].forEach.call(document.querySelectorAll('.vid video'),function(o){ if(o!==v && !o.paused) o.pause(); }); var f=v.closest('.vid'); if(f) f.classList.add('is-playing'); }); });
  /* bot check loads only where a form asks for it */
  if(document.querySelector('.cf-turnstile')){ var ts=document.createElement('script'); ts.src='https://challenges.cloudflare.com/turnstile/v0/api.js'; ts.async=true; ts.defer=true; document.head.appendChild(ts); }
  /* the receipt dialog shared by the enquiry and review forms */
  var sent=document.getElementById('sent'), sentClose=null;
  function openSent(o){
    if(!sent) return;
    sent.setAttribute('data-state',o.state);
    document.getElementById('sent-kicker').textContent=o.kicker; document.getElementById('sent-title').textContent=o.title; document.getElementById('sent-lede').textContent=o.lede;
    var dl=document.getElementById('sent-list'); dl.replaceChildren(); (o.rows||[]).forEach(function(r){ if(!r[1]) return; var dt=document.createElement('dt'), dd=document.createElement('dd'); dt.textContent=r[0]; dd.textContent=r[1]; dl.appendChild(dt); dl.appendChild(dd); });
    document.getElementById('sent-ref').textContent=o.ref||'';
    var ac=document.getElementById('sent-actions'); ac.replaceChildren(); (o.actions||[]).forEach(function(x){ var a=document.createElement('a'); a.className='btn '+(x.cls||'btn-secondary'); a.href=x.href; a.textContent=x.label; ac.appendChild(a); }); ac.hidden=!(o.actions&&o.actions.length);
    sentClose=o.onClose||null;
    if(sent.showModal){ if(!sent.open) sent.showModal(); } else { sent.setAttribute('open',''); }
    document.getElementById('sent-title').focus();
  }
  if(sent){
    document.getElementById('sent-close').addEventListener('click',function(){ if(sent.close) sent.close(); else { sent.removeAttribute('open'); sent.dispatchEvent(new Event('close')); } });
    sent.addEventListener('click',function(e){ if(e.target===sent) sent.close(); });
    sent.addEventListener('close',function(){ var f=sentClose; sentClose=null; if(f) f(); });
  }
  function mailHref(subject,rows){ var b='Hi Fitz,\n\n'+rows.filter(function(r){return r[1]}).map(function(r){return r[0]+': '+r[1]}).join('\n')+'\n\n(written on the website)'; if(b.length>1600) b=b.slice(0,1600)+'…'; return 'mailto:'+EMAIL+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(b); }
  function stamp(){ try{ return new Date().toLocaleString('en-AU',{weekday:'short',day:'numeric',month:'short',hour:'numeric',minute:'2-digit'}); }catch(e){ return ''; } }
  /* mobile CTA bar exits while the form is in view */
  var bar=document.getElementById('ctabar'), form=document.getElementById('enquiry'), heroCta=document.querySelector('.hero .cta-row');
  if(bar && 'IntersectionObserver' in window){
    var seen=new Map();
    var io=new IntersectionObserver(function(es){ es.forEach(function(x){ seen.set(x.target, x.target===form ? (x.isIntersecting && x.intersectionRatio>0.15) : x.isIntersecting); });
      var off=false; seen.forEach(function(v){ if(v) off=true; }); bar.toggleAttribute('data-off', off); bar.inert=off; },{threshold:[0,0.15,0.5]});
    if(form) io.observe(form); if(heroCta) io.observe(heroCta);
  }
  /* the mobile menu closes on Escape, on a tap outside it, and after choosing a page */
  var drawer=document.getElementById('drawer');
  if(drawer){
    document.addEventListener('keydown',function(e){ if(e.key==='Escape' && drawer.open){ drawer.open=false; drawer.querySelector('summary').focus(); } });
    document.addEventListener('click',function(e){ if(drawer.open && !drawer.contains(e.target)) drawer.open=false; });
    drawer.addEventListener('toggle',function(){ drawer.querySelector('summary').setAttribute('aria-expanded', drawer.open?'true':'false'); });
  }
  /* lightbox */
  var lb=document.getElementById('lightbox'), caps=%%CAPS%%, idx=0, invoker=null;
  function paint(i){ idx=(i+caps.length)%caps.length; var s=document.getElementById('lb-slot'); var src=document.querySelector('[data-lb="'+idx+'"] .slot'); if(src){ var c=src.cloneNode(true); c.classList.add('in-lb'); [].forEach.call(c.querySelectorAll('img,source'),function(x){ x.setAttribute('sizes','96vw'); x.removeAttribute('loading'); }); s.replaceChildren(c);} document.getElementById('lb-cap').textContent=caps[idx]; document.getElementById('lb-pos').textContent=(idx+1)+' of '+caps.length; }
  if(lb && lb.showModal){
    [].forEach.call(document.querySelectorAll('[data-lb]'),function(b){ b.addEventListener('click',function(){ invoker=b; paint(+b.getAttribute('data-lb')); lb.setAttribute('data-lightbox-state','open'); lb.showModal(); document.getElementById('lb-close').focus(); }); });
    document.getElementById('lb-prev').addEventListener('click',function(){paint(idx-1)});
    document.getElementById('lb-next').addEventListener('click',function(){paint(idx+1)});
    document.getElementById('lb-close').addEventListener('click',function(){lb.close()});
    lb.addEventListener('keydown',function(e){ if(e.key==='ArrowLeft') paint(idx-1); if(e.key==='ArrowRight') paint(idx+1); });
    lb.addEventListener('click',function(e){ if(e.target===lb) lb.close(); });
    lb.addEventListener('close',function(){ lb.setAttribute('data-lightbox-state','closed'); if(invoker) invoker.focus(); });
  }
  /* form: progressive enhancement over the native form */
  if(form){
    form.setAttribute('novalidate','');
    var fields=[['f-name','e-name',function(el){return el.value.trim().length>0}],
                ['f-phone','e-phone',function(el){return el.value.replace(/\D/g,'').length>=8}],
                ['f-email','e-email',function(el){return el.value.trim()===''||el.checkValidity()}],
                ['f-loc','e-loc',function(el){return el.value.trim().length>0}]];
    var KEY='ffh-enquiry-draft';
    try{ var draft=JSON.parse(localStorage.getItem(KEY)||'null'); if(draft){ var restored=false; Object.keys(draft).forEach(function(k){ var el=document.getElementById(k); if(el && el.value==='' && draft[k]){ el.value=draft[k]; restored=true; } }); if(restored){ document.getElementById('draft-note').hidden=false; } } }catch(e){}
    var saveT=null;
    form.addEventListener('input',function(){ clearTimeout(saveT); saveT=setTimeout(function(){ try{ var o={}; fields.forEach(function(f){o[f[0]]=document.getElementById(f[0]).value}); o['f-msg']=document.getElementById('f-msg').value; localStorage.setItem(KEY,JSON.stringify(o)); }catch(e){} },300); });
    function mark(el,errId,ok){ var w=el.closest('.field'); if(!w) return; w.classList.toggle('has-err',!ok); el.setAttribute('aria-invalid',ok?'false':'true'); if(!ok) el.setAttribute('aria-describedby',errId); }
    fields.forEach(function(f){ var el=document.getElementById(f[0]); el.addEventListener('blur',function(){ if(el.value!=='') mark(el,f[1],f[2](el)); }); });
    var sum=document.getElementById('err-summary'), list=document.getElementById('err-list');
    function showErrors(errs){ list.replaceChildren(); errs.forEach(function(x){ var li=document.createElement('li'), a=document.createElement('a'); a.href='#'+x[0]; a.textContent=x[1]; a.addEventListener('click',function(ev){ev.preventDefault(); var t=document.getElementById(x[0]); (t.querySelector('input')||t).focus(); t.scrollIntoView({block:'center'})}); li.appendChild(a); list.appendChild(li); }); sum.hidden=false; sum.focus(); }
    function succeed(){ var c=document.getElementById('confirm'); document.getElementById('confirm-name').textContent=document.getElementById('f-name').value.trim().split(' ')[0]||'there'; form.hidden=true; c.hidden=false; c.focus(); try{localStorage.removeItem(KEY)}catch(e){} }
    var FIELD_IDS={name:'f-name',phone:'f-phone',email:'f-email',location:'f-loc',help:'f-help',message:'f-msg'};
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var errs=[];
      fields.forEach(function(f){ var el=document.getElementById(f[0]); var ok=f[2](el); mark(el,f[1],ok); if(!ok) errs.push([f[0],document.getElementById(f[1]).textContent]); });
      var anyHelp=form.querySelectorAll('input[name="help"]:checked').length>0; var hf=document.getElementById('f-help'); hf.classList.toggle('has-err',!anyHelp); if(!anyHelp) errs.push(['f-help',document.getElementById('e-help').textContent]);
      if(errs.length){ showErrors(errs); return; }
      sum.hidden=true;
      var btn=document.getElementById('f-submit'); btn.style.width=btn.getBoundingClientRect().width+'px'; btn.classList.add('is-busy'); btn.setAttribute('aria-disabled','true'); btn.disabled=true; btn.querySelector('.lbl').textContent='Sending';
      function reset(){ btn.classList.remove('is-busy'); btn.disabled=false; btn.removeAttribute('aria-disabled'); btn.style.width=''; btn.querySelector('.lbl').textContent='Send enquiry'; }
      var fd=new FormData(form), payload={}; fd.forEach(function(v,k){ if(k==='help'){ (payload.help=payload.help||[]).push(v);} else payload[k]=v; });
      var rows=[['Name',payload.name],['Phone',payload.phone],['Email',payload.email],['Location',payload.location],['Help with',(payload.help||[]).join(', ')],['Message',payload.message]];
      var first=(payload.name||'').trim().split(' ')[0]||'there', subject='Enquiry: '+(payload.help||[]).join(', ')+' near '+payload.location;
      var fallbackActions=function(){ return [{href:mailHref(subject,rows),label:'Email it to Fitz',cls:'btn-primary'},{href:'tel:'+E164,label:'Call '+PHONE}]; };
      function delivered(ref){ openSent({state:'sent',kicker:'Enquiry sent',title:'Sent to Fitz',lede:'Thanks, '+first+'. Fitz has your enquiry and will ring '+payload.phone+', usually within two business days. This is what he received:',rows:rows,ref:(ref?'Reference '+ref+' · ':'')+stamp(),onClose:succeed}); }
      function notYet(){ openSent({state:'fallback',kicker:'Not sent yet',title:'One more step',lede:'The website’s email isn’t switched on yet, so this hasn’t reached Fitz. Send it from your own email with the button below (it’s all filled in), or ring '+PHONE+'.',rows:rows,actions:fallbackActions()}); }
      function failed(msg){ openSent({state:'failed',kicker:'Not sent',title:'That didn’t go through',lede:(msg||'Something went wrong sending it.')+' Nothing reached Fitz. Send it from your own email, or ring '+PHONE+'.',rows:rows,actions:fallbackActions()}); }
      if(ARTIFACT){ setTimeout(function(){ reset(); delivered('FFH-DEMO'); },900); return; }
      fetch(form.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)})
        .then(function(r){ return r.json().then(function(j){ return {status:r.status, j:j||{}}; },function(){ return {status:r.status, j:{}}; }); })
        .then(function(res){ reset(); var j=res.j;
          if(res.status===400 && j.fields){ showErrors(Object.keys(j.fields).map(function(k){ return [FIELD_IDS[k]||'f-submit', j.fields[k]]; })); return; }
          if(j.ok && j.delivered){ delivered(j.ref); return; }
          if(j.ok){ notYet(); return; }
          failed(j.error); })
        .catch(function(){ reset(); failed('No connection.'); });
    });
    document.getElementById('confirm-reset').addEventListener('click',function(e){ e.preventDefault(); form.reset(); document.getElementById('confirm').hidden=true; form.hidden=false; document.getElementById('f-name').focus(); });
  }
  /* reviews: stars, verified jobs and photos. Published reviews are added beside the baked-in ones; the form posts to the review queue */
  var rlists=document.querySelectorAll('[data-reviews]'), rform=document.getElementById('review-form'), rsums=document.querySelectorAll('[data-review-summary]'), pfield=document.getElementById('r-photos-field');
  var SVGNS='http://www.w3.org/2000/svg', WORDS=['','Poor','Fair','Good','Very good','Excellent'];
  function svgUse(id,cls){ var v=document.createElementNS(SVGNS,'svg'); v.setAttribute('viewBox','0 0 24 24'); v.setAttribute('aria-hidden','true'); if(cls) v.setAttribute('class',cls); var u=document.createElementNS(SVGNS,'use'); u.setAttribute('href','#'+id); v.appendChild(u); return v; }
  function starRow(n,label){ var s=document.createElement('span'); s.className='rv-stars'; if(label){ s.setAttribute('role','img'); s.setAttribute('aria-label',label); } else s.setAttribute('aria-hidden','true'); for(var i=1;i<=5;i++) s.appendChild(svgUse('i-star',i>n?'off':'')); return s; }
  function monthName(m,long){ var x=/^(\d{4})-(\d\d)$/.exec(m||''); if(!x) return m==='earlier'?'More than two years ago':''; try{ return new Date(+x[1],+x[2]-1,15).toLocaleDateString('en-AU',{month:long?'long':'short',year:'numeric'}); }catch(e){ return m; } }
  function reviewCard(r){ var f=document.createElement('figure'); f.className='review';
    if(r.rating || r.verified){ var top=document.createElement('div'); top.className='rv-top'; if(r.rating) top.appendChild(starRow(r.rating,'Rated '+r.rating+' out of 5'));
      if(r.verified){ var v=document.createElement('span'); v.className='rv-verified'; v.appendChild(svgUse('i-check')); v.appendChild(document.createTextNode('Verified job')); v.title=r.via==='link'?'Sent through the review link Fitz gave the customer after the job':'Fitz matched this review to a job he did'; top.appendChild(v); }
      f.appendChild(top); }
    var bq=document.createElement('blockquote'), q=document.createElement('q'); q.textContent=r.text; bq.appendChild(q); f.appendChild(bq);
    if(r.photos && r.photos.length){ var ul=document.createElement('ul'); ul.className='rv-photos'; r.photos.forEach(function(p,i){ var li=document.createElement('li'), a=document.createElement('a'), im=document.createElement('img'); a.href=p.src; a.target='_blank'; a.rel='noopener'; a.setAttribute('aria-label','Photo '+(i+1)+' from '+r.name+'’s review, full size'); im.src=p.src; im.alt=''; im.loading='lazy'; im.decoding='async'; if(p.w){ im.width=p.w; im.height=p.h; } a.appendChild(im); li.appendChild(a); ul.appendChild(li); }); f.appendChild(ul); }
    var who=document.createElement('figcaption'); who.className='who'; who.textContent=[r.name,r.property,r.region].filter(Boolean).join(' · '); f.appendChild(who);
    var m=document.createElement('p'); m.className='caption'; var d=r.jobMonth&&r.jobMonth!=='earlier'?'Job '+monthName(r.jobMonth):''; if(!d){ try{ d=r.date?new Date(r.date).toLocaleDateString('en-AU',{month:'short',year:'numeric'}):''; }catch(e){} } m.textContent=[r.service,d].filter(Boolean).join(' · '); f.appendChild(m);
    if(r.reply){ var rp=document.createElement('p'); rp.className='reply'; rp.textContent='Fitz: '+r.reply; f.appendChild(rp); } return f; }
  function fillSummary(s){ if(!s || !s.count) return; [].forEach.call(rsums,function(el){ el.replaceChildren(); var b=document.createElement('b'), t=document.createElement('span'); b.textContent=(Math.round(s.average*10)/10).toFixed(1)+' out of 5'; t.textContent='from '+s.count+' review'+(s.count===1?'':'s'); el.appendChild(starRow(Math.round(s.average))); el.appendChild(b); el.appendChild(t); el.hidden=false; }); }
  if((rlists.length || rform || rsums.length) && !ARTIFACT){
    fetch('/api/reviews',{headers:{Accept:'application/json'}}).then(function(r){ return r.json(); }).then(function(j){
      if(!j.enabled){ if(rform){ rform.hidden=true; document.getElementById('review-closed').hidden=false; } return; }
      fillSummary(j.summary);
      if(j.photos && pfield) pfield.hidden=false;
      [].forEach.call(rlists,function(l){ var n=+l.getAttribute('data-reviews'), have=l.querySelectorAll('.review:not(.review-empty)').length, add=(j.reviews||[]).slice(0,Math.max(0,n-have)); if(!add.length) return; var e=l.querySelector('.review-empty'); if(e) e.remove(); add.forEach(function(r){ l.appendChild(reviewCard(r)); }); });
    }).catch(function(){});
  }
  if(rform){
    var rsum=document.getElementById('rv-summary'), rerrs=document.getElementById('rv-errs'), MIN=250, MAX=2000;
    var rtext=document.getElementById('r-text'), rcount=document.getElementById('r-count'), rout=document.getElementById('r-rate-out'), rmonth=document.getElementById('r-month');
    function count(){ var n=rtext.value.trim().length; rcount.textContent=n<MIN?(n+' of '+MIN+' characters, '+(MIN-n)+' to go'):(n+' characters. That’s enough; up to '+MAX+'.'); rcount.classList.toggle('is-ok',n>=MIN); }
    rtext.addEventListener('input',count); count();
    rform.addEventListener('change',function(e){ if(e.target.name==='rating'){ rout.textContent=e.target.value+' out of 5 · '+WORDS[+e.target.value]; document.getElementById('r-rating').classList.remove('has-err'); } });
    /* the month list, rebuilt from today's date so it never goes stale */
    (function(){ var keep=rmonth.value, now=new Date(), y=now.getFullYear(), m=now.getMonth()+1, o=['<option value="">Choose…</option>'];
      for(var i=0;i<24;i++){ var v=y+'-'+(m<10?'0':'')+m; o.push('<option value="'+v+'">'+monthName(v,true)+'</option>'); if(--m===0){ m=12; y--; } }
      o.push('<option value="earlier">More than two years ago</option>'); rmonth.innerHTML=o.join(''); rmonth.value=keep; })();
    function pick(id,val){ var el=document.getElementById(id); if(!el||!val) return; [].forEach.call(el.options,function(o){ if((o.value||o.textContent)===val) el.value=o.value; }); }
    /* Fitz's review link: ?invite=… (checked on the server; read here only to fill in what he already knows) */
    var inv=''; try{ inv=new URLSearchParams(location.search).get('invite')||''; }catch(e){}
    if(/^[A-Za-z0-9_-]{10,400}\.[A-Za-z0-9_-]{22}$/.test(inv)){
      document.getElementById('r-invite').value=inv; var note=document.getElementById('r-invite-note'); note.hidden=false;
      try{ var pl=JSON.parse(decodeURIComponent(escape(atob(inv.split('.')[0].replace(/-/g,'+').replace(/_/g,'/')))));
        if(pl.n && !document.getElementById('r-name').value) document.getElementById('r-name').value=pl.n; pick('r-service',pl.s); pick('r-month',pl.m);
        if(pl.e && pl.e<Date.now()){ note.classList.add('is-old'); document.getElementById('r-invite-text').textContent='This review link has expired. You can still leave a review; Fitz will match it to the job himself.'; }
      }catch(e){}
    }
    /* photos: shrunk to 1600px JPEG in the browser (which also drops the location data); the server strips again */
    var pin=document.getElementById('r-photos'), plist=document.getElementById('r-picks'), perr=document.getElementById('r-photos-err'), pbtn=document.getElementById('r-photos-btn'), picks=[];
    function shrink(file){ return new Promise(function(ok,no){ var u=URL.createObjectURL(file), im=new Image(); im.onload=function(){ var w=im.naturalWidth, h=im.naturalHeight, k=Math.min(1,1600/Math.max(w,h)), c=document.createElement('canvas'); c.width=Math.max(1,Math.round(w*k)); c.height=Math.max(1,Math.round(h*k)); var x=c.getContext('2d'); x.fillStyle='#ffffff'; x.fillRect(0,0,c.width,c.height); x.drawImage(im,0,0,c.width,c.height); URL.revokeObjectURL(u); var q=.82, d=c.toDataURL('image/jpeg',q); while(d.length*.75>900000 && q>.45){ q-=.12; d=c.toDataURL('image/jpeg',q); } if(d.indexOf('data:image/jpeg')!==0) return no(); ok({data:d,w:c.width,h:c.height}); }; im.onerror=function(){ URL.revokeObjectURL(u); no(); }; im.src=u; }); }
    function drawPicks(){ plist.replaceChildren(); picks.forEach(function(p,i){ var li=document.createElement('li'), im=document.createElement('img'), b=document.createElement('button'); im.src=p.data; im.alt='Photo '+(i+1)+' to attach'; b.type='button'; b.className='rm'; b.textContent='Remove'; b.setAttribute('aria-label','Remove photo '+(i+1)); b.addEventListener('click',function(){ picks.splice(i,1); drawPicks(); (picks.length?plist.querySelector('.rm'):pin).focus(); }); li.appendChild(im); li.appendChild(b); plist.appendChild(li); }); var full=picks.length>=3; pbtn.hidden=full; pin.disabled=full; pbtn.textContent=picks.length?'Add another photo':'Add photos'; }
    function photoErr(t){ perr.textContent=t; pfield.classList.toggle('has-err',!!t); }
    pin.addEventListener('change',function(){ var files=[].slice.call(pin.files||[]), room=3-picks.length; pin.value=''; photoErr(''); if(files.length>room){ photoErr('Up to 3 photos. The first '+room+' '+(room===1?'was':'were')+' added.'); files=files.slice(0,room); }
      Promise.all(files.map(function(f){ return shrink(f).catch(function(){ return null; }); })).then(function(rs){ var bad=0; rs.forEach(function(r){ if(r) picks.push(r); else bad++; }); if(bad) photoErr((bad===1?'One photo':bad+' photos')+' couldn’t be read. Try a JPEG or PNG.'); drawPicks(); }); });
    var rchecks=[['r-name',function(el){return /\S/.test(el.value)}],['r-region',function(el){return el.value!==''}],['r-property',function(el){return el.value!==''}],['r-service',function(el){return el.value!==''}],['r-month',function(el){return el.value!==''}],['r-text',function(el){return el.value.trim().length>=MIN}],['r-email',function(el){return el.value.trim()!=='' && el.checkValidity()}],['r-phone',function(el){ var d=el.value.replace(/\D/g,''); return el.value.trim()==='' || (d.length>=8 && d.length<=15); }]];
    rform.addEventListener('submit',function(e){
      e.preventDefault(); var errs=[];
      var rated=rform.querySelector('input[name="rating"]:checked'), rw=document.getElementById('r-rating'); rw.classList.toggle('has-err',!rated); if(!rated) errs.push(['r-star-1',rw.querySelector('.err').textContent]);
      rchecks.forEach(function(c){ var el=document.getElementById(c[0]), ok=c[1](el), w=el.closest('.field'); w.classList.toggle('has-err',!ok); el.setAttribute('aria-invalid',ok?'false':'true'); if(!ok) errs.push([c[0],c[0]==='r-text'?'Write at least '+MIN+' characters (you have '+el.value.trim().length+').':w.querySelector('.err').textContent]); });
      var cons=rform.querySelector('input[name="consent"]'), cw=cons.closest('.field'); cw.classList.toggle('has-err',!cons.checked); if(!cons.checked) errs.push(['r-consent',cw.querySelector('.err').textContent]);
      if(errs.length){ rerrs.replaceChildren(); errs.forEach(function(x){ var li=document.createElement('li'), a=document.createElement('a'); a.href='#'+x[0]; a.textContent=x[1]; a.addEventListener('click',function(ev){ ev.preventDefault(); var t=document.getElementById(x[0])||cons; t.focus(); (t.closest('.field')||t).scrollIntoView({block:'center'}); }); li.appendChild(a); rerrs.appendChild(li); }); rsum.hidden=false; rsum.focus(); return; }
      rsum.hidden=true;
      var p={}; new FormData(rform).forEach(function(v,k){ if(typeof v==='string') p[k]=v; }); p.consent=cons.checked; p.rating=+rated.value; if(picks.length) p.photos=picks.map(function(x){ return x.data; });
      var rows=[['Rating','★★★★★☆☆☆☆☆'.slice(5-p.rating,10-p.rating)+'  '+p.rating+' out of 5'],['Name',p.name],['Region',p.region],['Property',p.property],['Work',p.service],['Job',monthName(p.jobMonth,true)],['Review',p.text],['Photos',picks.length?picks.length+' attached':'']];
      var btn=document.getElementById('r-submit'); btn.classList.add('is-busy'); btn.disabled=true; btn.querySelector('.lbl').textContent=picks.length?'Sending photos':'Sending';
      function done(){ btn.classList.remove('is-busy'); btn.disabled=false; btn.querySelector('.lbl').textContent='Send review'; }
      var acts=function(){ return [{href:mailHref('A review for Fitz Feral Hunters',rows.concat(picks.length?[['Photos','(attach them to this email)']]:[])),label:'Email it to Fitz',cls:'btn-primary'}]; };
      fetch(rform.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(p)})
        .then(function(r){ return r.json().then(function(j){ return {status:r.status,j:j||{}}; },function(){ return {status:r.status,j:{}}; }); })
        .then(function(res){ done(); var j=res.j;
          if(j.ok){ var lede=(j.verified?'It came through Fitz’s review link, so it’ll show as a verified job once he publishes it.':'Fitz matches it to your job, then publishes it.')+' Every genuine review goes up, good or bad.'+(j.note?' '+j.note:'')+' This is what you sent:';
            openSent({state:'sent',kicker:'Review sent',title:'Thanks, it’s with Fitz',lede:lede,rows:rows,ref:stamp(),onClose:function(){ rform.reset(); picks=[]; drawPicks(); count(); rout.textContent='Tap a star'; }}); return; }
          if(res.status===400 && j.error){ rerrs.replaceChildren(); (j.errors||[j.error]).forEach(function(t){ var li=document.createElement('li'); li.textContent=t; rerrs.appendChild(li); }); rsum.hidden=false; rsum.focus(); return; }
          openSent({state:'failed',kicker:'Not sent',title:'That didn’t go through',lede:(j.error||'Something went wrong sending it.')+' You can email the same review to Fitz instead.',rows:rows,actions:acts()}); })
        .catch(function(){ done(); openSent({state:'failed',kicker:'Not sent',title:'That didn’t go through',lede:'No connection. You can email the same review to Fitz instead.',rows:rows,actions:acts()}); });
    });
  }
  /* reviewer chrome (review build only) */
  var vb=document.getElementById('varbar'), tm=document.getElementById('t-motion'), tt=document.getElementById('t-topo'), tx=document.getElementById('t-xray'), ts2=document.getElementById('t-spec'), th=document.getElementById('t-hide'), spec=document.getElementById('spec');
  if(!vb) return;
  try{ if(localStorage.getItem('ffh-varbar')==='hidden') vb.hidden=true; }catch(e){}
  th.addEventListener('click',function(){ vb.hidden=true; try{localStorage.setItem('ffh-varbar','hidden')}catch(e){} });
  tm.addEventListener('click',function(){ var off=root.getAttribute('data-motion')==='off'; if(off){root.removeAttribute('data-motion');tm.querySelector('.long').textContent='Motion: on';tm.setAttribute('aria-pressed','false')} else {root.setAttribute('data-motion','off');tm.querySelector('.long').textContent='Motion: off (reduced-motion twin)';tm.setAttribute('aria-pressed','true')} });
  if(tt) tt.addEventListener('click',function(){ var off=root.getAttribute('data-sheet')==='off'; if(off){root.removeAttribute('data-sheet');tt.querySelector('.long').textContent='Sheet: on';tt.setAttribute('aria-pressed','true')} else {root.setAttribute('data-sheet','off');tt.querySelector('.long').textContent='Sheet: off (v1 ground)';tt.setAttribute('aria-pressed','false')} });
  var NAMES=%%NAMES%%;
  tx.addEventListener('click',function(){ var on=root.hasAttribute('data-xray'); if(on){root.removeAttribute('data-xray');tx.setAttribute('aria-pressed','false');[].forEach.call(document.querySelectorAll('[data-per]'),function(el){el.removeAttribute('title')})} else {root.setAttribute('data-xray','');tx.setAttribute('aria-pressed','true');[].forEach.call(document.querySelectorAll('[data-per]'),function(el){el.setAttribute('title',el.getAttribute('data-per').split(' ').map(function(i){return i+' '+(NAMES[i]||'')}).join('\n'))})} });
  if(!('commandForElement' in HTMLButtonElement.prototype)){ ts2.addEventListener('click',function(){ if(!spec.open) spec.showModal(); }); }
  document.getElementById('spec-close').addEventListener('click',function(){ spec.close(); });
  spec.addEventListener('click',function(e){ if(e.target===spec) spec.close(); });
})();
</script>"""

def jsonld():
    return json.dumps({
      "@context": "https://schema.org", "@type": "LocalBusiness", "name": S['name'],
      "description": TITLES['home'][1], "telephone": S['phone_e164'], "email": S['email'], "url": S['url'].rstrip('/') + '/',
      "image": S['url'].rstrip('/') + '/og-1200x630.png',
      "address": {"@type": "PostalAddress", "addressLocality": S['base'], "addressRegion": "VIC", "addressCountry": "AU"},
      "areaServed": ["Gippsland", "Victoria, Australia"], "sameAs": [S['instagram']],
      "founder": {"@type": "Person", "name": S['owner']}, **({"taxID": "ABN " + S['abn']} if S.get('abn') else {}),
      "knowsAbout": ["Deer control", "Kangaroo culling", "Feral pig control", "Fox control", "Rabbit control", "Wild dog control", "Thermal night work", "Thermal drone scouting", "Farm security"],
    }, ensure_ascii=False)

def script():
    src = SCRIPT
    if not REVIEW:   # production: drop the varbar / X-ray / spec-sheet code
        a, z = src.index('  /* reviewer chrome (review build only) */'), src.rindex('})();')
        src = src[:a] + src[z:]
    return (src.replace('%%CAPS%%', json.dumps([MEDIA[p]['caption'] for p in gallery_photos()])).replace('%%NAMES%%', json.dumps(NAMES if REVIEW else {}, ensure_ascii=False))
                  .replace('%%PHONE%%', json.dumps(S['phone_display'])).replace('%%E164%%', json.dumps(S['phone_e164'])).replace('%%EMAIL%%', json.dumps(S['email']))
                  .replace('%%ARTIFACT%%', 'true' if ARTIFACT else 'false').replace('%%TITLES%%', json.dumps({k: TITLES[k][0] for k in TITLES})))

def document(key, body, title, desc):
    path = HREF.get(key, '/404')
    canonical = S['url'].rstrip('/') + ('' if path == '/' else path)
    robots = '' if S.get('indexable') else '<meta name="robots" content="noindex, nofollow">\n'
    sheet_css = css + ("\n[data-sheet='off'] body::after{display:none}\n" if SHEET else "\n")
    return f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="format-detection" content="telephone=no">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<meta name="theme-color" content="#1b2622">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.png" type="image/png" sizes="64x64">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(S['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{S['url'].rstrip('/')}/og-1200x630.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{sheet_css}</style>
<script type="application/ld+json">{jsonld()}</script>{extra_ld(key)}
</head>
<body>
{SPRITE}{varbar()}{header(key)}
<main id="main"{per("doc")}{per("tokens")}{per("type")}{per("motion")}{per("focus")}{per("ground")}{per("topo")}>
{body}
</main>
{footer()}{ctabar()}{spec_dialog()}{script()}
</body>
</html>'''

def artifact_document():
    """Single document for the claude.ai artifact: no skeleton tags, hash-routed sections."""
    sections = ''.join(f'<section data-page="{k}" id="{k}" aria-labelledby="h-{k}">{b}</section>' for k, b in
                       (('home', home_body()), ('services', services_body()), ('credentials', credentials_body()), ('about', about_body()), ('gallery', gallery_body()), ('faq', faq_body()), ('contact', contact_body())))
    sheet_css = css + ("\n[data-sheet='off'] body::after{display:none}\n" if SHEET else "\n")
    return f'''<title>Fitz Feral Hunters Paddock</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{esc(TITLES['home'][1])}">
<meta name="theme-color" content="#1b2622">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{sheet_css}</style>
<script type="application/ld+json">{jsonld()}</script>
{SPRITE}{varbar()}{header(None)}
<main id="main"{per("doc")}{per("tokens")}{per("type")}{per("motion")}{per("focus")}{per("ground")}{per("topo")}>
<p class="sr" id="route-live" aria-live="polite"></p>
{sections}
</main>
{footer()}{ctabar()}{spec_dialog()}{script()}'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#2E6E4E"/><path d="M18 14h30v9H28v9h17v9H28v9H18z" fill="#f8f6f2"/></svg>'''

def main():
    allids = set()
    for grp in (cites.SHARED, X, cites.TOP):
        for k, ids in grp.items():
            if k in SHEET_KEYS and not SHEET: continue
            if k in MAP_KEYS and not SHEET_MAP: continue
            allids.update(ids)
    n_entries = len([i for i in allids if re.match(r"^D\d{4}$", i)])
    if ARTIFACT:
        out = pathlib.Path(sys.argv[sys.argv.index('--artifact') + 1])
        out.write_text(artifact_document())
        print(f'artifact → {out} ({out.stat().st_size/1024:.0f} KB) · {n_entries} entries · {len(allids)} citations · topo tile {len(TOPO_SVG)/1024:.0f} KB')
        return
    PUB.mkdir(exist_ok=True)
    pages = {'home': home_body(), 'services': services_body(), 'credentials': credentials_body(), 'about': about_body(), 'gallery': gallery_body(), 'faq': faq_body(), 'contact': contact_body(), 'reviews': reviews_body(), 'drone-report': report_body()}
    for key, body in pages.items():
        t, d = TITLES[key]
        (PUB / ('index.html' if key == 'home' else f'{key}.html')).write_text(document(key, body, t, d))
    pathlib.Path(__file__).resolve().parent.parent.joinpath('api/_lib/site-options.js').write_text(
        '// Generated by src/build.py from content/site.json. Do not edit by hand.\n'
        f'export const SERVICES = {json.dumps(REVIEW_SERVICES)};\nexport const REGIONS = {json.dumps(REGIONS)};\nexport const PROPERTY_TYPES = {json.dumps(PROPERTY_TYPES)};\n')
    (PUB / '404.html').write_text(document('404', notfound_body(), f"Page not found · {S['name']}", "That page isn't here."))
    (PUB / 'favicon.svg').write_text(FAVICON)
    if SHEET: (PUB / 'topo-tile.svg').write_text(TOPO_SVG)
    elif (PUB / 'topo-tile.svg').exists(): (PUB / 'topo-tile.svg').unlink()
    base = S['url'].rstrip('/'); today = datetime.date.today().isoformat()
    (PUB / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{base}{"" if h == "/" else h}</loc><lastmod>{today}</lastmod></url>\n' for _, h, _ in PAGES + EXTRA_PAGES) + '</urlset>\n')
    (PUB / 'robots.txt').write_text(('User-agent: *\nAllow: /\n' if S.get('indexable') else 'User-agent: *\nDisallow: /\n') + f'Sitemap: {base}/sitemap.xml\n')
    print(f'built {len(pages)+1} pages into public/ ({"review" if REVIEW else "production"}) · {n_entries} entries · {len(allids)} citations · topo tile {len(TOPO_SVG)/1024:.0f} KB')

if __name__ == '__main__':
    main()
