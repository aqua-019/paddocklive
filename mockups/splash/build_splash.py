#!/usr/bin/env python3
"""SP-09 splash, as a claude.ai artifact for review in chat: the real home page (production build on the
splash-preview branch) with the splash playing on open and a Replay button. Images ship as files beside the
page; videos point at the live site (they don't play inside the artifact, and the splash doesn't need them).

    python3 src/build.py && python3 mockups/splash/build_splash.py
    → mockups/splash/dist/splash.html + the file list for the publish (dist/files.txt)
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUB = ROOT / 'public'
LIVE = 'https://fitzferalhunters.com.au'

src = (PUB / 'index.html').read_text()
head, body = src.split('<body>', 1)
body = body.rsplit('</body>', 1)[0]
assert 'class="splash"' in body, 'build with "splash": true first'

def one(pattern, text):
    m = re.findall(pattern, text, re.S); assert len(m) == 1, (pattern, len(m)); return m[0]

css = one(r'<style>(.*?)</style>', head)
splash_head = one(r'(<script>try\{\(function\(\)\{var r=document\.documentElement.*?</script>)', head)

# the review copy always plays on open (no once-per-session, no hash rule); reduced motion still turns it off
splash_head = splash_head.replace("if(!q&&(location.hash||sessionStorage.getItem('ffh-splash')))return;", '')
assert 'sessionStorage' not in splash_head

def relink(html):
    html = re.sub(r'(<source src=")/(media/video/[^"]+")', lambda m: f'{m.group(1)}{LIVE}/{m.group(2)}', html)   # videos stay on the live site
    html = re.sub(r'href="/(?!/)([^"]*)"', lambda m: f'href="{LIVE}/{m.group(1)}"', html)                        # site pages open the live site
    html = re.sub(r'(src|poster)="/(?!/)', r'\1="', html)                                                       # images ship beside the page
    html = re.sub(r'(srcset="[^"]*")', lambda m: re.sub(r'(^srcset="|, )/', r'\1', m.group(1)), html)
    html = html.replace('url("/topo-tile.svg")', 'url("topo-tile.svg")')
    html = html.replace("'/brand/fitz-badge-768.webp'", "'brand/fitz-badge-768.webp'").replace("'/topo-tile.svg'", "'topo-tile.svg'")
    return html

css, splash_head, body = relink(css), relink(splash_head), relink(body)
tpl = one(r'(<div class="splash" aria-hidden="true">.*?</div><img class="sp-badge"[^>]*><button type="button" class="sp-skip"[^>]*>Skip</button></div>)', body)

REPLAY = """
<style>
.sp-replay{position:fixed;left:max(16px, env(safe-area-inset-left,0px));bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:60;display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px;border:0;border-radius:999px;background:var(--chrome);color:var(--foot-ink);font:600 15px/1 var(--font-body);cursor:pointer;box-shadow:0 0 0 1px var(--gold);transition:background-color var(--t-hover) var(--ease-out),color var(--t-hover) var(--ease-out)}
.sp-replay:hover{background:var(--gold);color:var(--chrome)}
.sp-replay svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
@media (max-width:899px){.sp-replay{bottom:calc(84px + env(safe-area-inset-bottom,0px))}}
html.sp-on .sp-replay{visibility:hidden}
</style>
<template id="sp-tpl">""" + tpl + """</template>
<button type="button" class="sp-replay" id="sp-replay"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4"/></svg>Replay splash</button>
<script>
document.getElementById('sp-replay').addEventListener('click', function(){
  var t=document.querySelector('.toast');
  if(!matchMedia('(prefers-reduced-motion: no-preference)').matches){ if(t){ t.textContent='Your device asks for reduced motion, so the splash stays off.'; t.classList.add('on'); setTimeout(function(){ t.classList.remove('on'); },3200); } return; }
  var old=document.querySelector('div.splash'); if(old) old.remove();
  window.scrollTo(0,0);
  window.__ffhTopo=window.__ffhTopo||fetch('topo-tile.svg').then(function(x){ return x.ok?x.text():''; }).catch(function(){ return ''; });
  document.body.prepend(document.getElementById('sp-tpl').content.firstElementChild.cloneNode(true));
  var root=document.documentElement; root.classList.remove('sp-on'); void root.offsetWidth; root.classList.add('sp-on');
  setTimeout(function(){ window.ffhSplash(); }, 60);
});
</script>
"""

page = f'''<title>Fitz Feral Hunters Splash</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="robots" content="noindex, nofollow">
{splash_head}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{css}</style>
{body}
{REPLAY}'''

# every local file the page asks for, published beside it at the same relative path
refs = set(re.findall(r'(?:src|poster)="((?:brand|media|icons)/[^"]+)"', page))
for ss in re.findall(r'srcset="([^"]+)"', page):
    refs |= {p.strip().split(' ')[0] for p in ss.split(',') if not p.strip().startswith('http')}
refs |= {'topo-tile.svg', 'brand/fitz-badge-768.webp'}
missing = [r for r in refs if not (PUB / r).exists()]
assert not missing, missing
assert not re.search(r'(?:src|srcset|poster)="/(?!/)', page), 'an absolute path survived'

dist = HERE / 'dist'; dist.mkdir(exist_ok=True)
(dist / 'splash.html').write_text(page)
files = {r: str((PUB / r).relative_to(ROOT)) for r in sorted(refs)}
(dist / 'files.json').write_text(json.dumps(files, indent=1))
print(f'splash preview → {dist / "splash.html"} ({len(page) // 1024} KB) + {len(files)} files ({sum((PUB / r).stat().st_size for r in refs) // 1024} KB)')
