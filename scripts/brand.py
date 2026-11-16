#!/usr/bin/env python3
"""Fitz's badge (supplied 16 Nov 2026) → every brand file the site uses. Strips all metadata.

    python3 scripts/brand.py            # reads media-src/brand/fitz-badge.jpg (gitignored original)

Writes:
  public/brand/fitz-badge-{96,160,256,384,512,768}.webp   transparent circle, for <img srcset>
  public/brand/fitz-badge-512.png                        transparent PNG (schema logo, Google Business Profile)
  public/icons/fitz-32.png, fitz-64.png                   browser-tab icons
  public/apple-touch-icon.png + public/icons/fitz-touch-180.png   home-screen icon (badge on ink, square)
  public/og-badge-1200x630.png                           social share card (rendered from HTML with the site's fonts)
"""
import hashlib, pathlib, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'media-src/brand/fitz-badge.jpg'
PUB = ROOT / 'public'
INK = (27, 38, 34)          # --chrome / ink #1b2622

def circle_cut(im):
    """Find the badge's outer gold ring on the white JPEG ground and return an RGBA square with a clean, anti-aliased edge."""
    rgb = im.convert('RGB')
    w, h = rgb.size
    # anything not near-white belongs to the badge
    mask = rgb.point(lambda v: 255 if v < 236 else 0).convert('L')
    r, g, b = rgb.split()
    near = Image.merge('RGB', (r, g, b)).convert('L').point(lambda v: 255 if v < 240 else 0)
    box = near.getbbox()
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    rad = min(box[2] - box[0], box[3] - box[1]) / 2 - 1.5     # step 1.5px inside the ring so no white fringe survives
    S = 4                                                     # supersample the mask for a smooth edge
    big = Image.new('L', (w * S, h * S), 0)
    ImageDraw.Draw(big).ellipse(((cx - rad) * S, (cy - rad) * S, (cx + rad) * S, (cy + rad) * S), fill=255)
    alpha = big.resize((w, h), Image.LANCZOS)
    out = rgb.copy(); out.putalpha(alpha)
    side = int(round(rad * 2)) + 2
    left, top = int(round(cx - side / 2)), int(round(cy - side / 2))
    return out.crop((left, top, left + side, top + side)), (cx, cy, rad, box)

def clean(img):
    """A fresh image with pixels only: no EXIF, GPS, ICC or comments."""
    return Image.frombytes(img.mode, img.size, img.tobytes())

def sized(badge, px):
    im = badge.resize((px, px), Image.LANCZOS)
    if px <= 96: im = im.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=2))
    return clean(im)

def main():
    if not SRC.exists(): sys.exit(f'missing {SRC} (the original badge from Fitz)')
    src = Image.open(SRC)
    badge, (cx, cy, rad, box) = circle_cut(src)
    print(f'badge: source {src.size}, ring box {box}, centre ({cx:.1f},{cy:.1f}), radius {rad:.1f} → {badge.size}')
    (PUB / 'brand').mkdir(exist_ok=True); (PUB / 'icons').mkdir(exist_ok=True)
    for px in (96, 160, 256, 384, 512, 768):
        sized(badge, px).save(PUB / f'brand/fitz-badge-{px}.webp', 'WEBP', quality=90, method=6)
    sized(badge, 512).save(PUB / 'brand/fitz-badge-512.png', 'PNG', optimize=True)
    for px in (32, 64):
        sized(badge, px).save(PUB / f'icons/fitz-{px}.png', 'PNG', optimize=True)
    touch = Image.new('RGB', (180, 180), INK)
    touch.paste(sized(badge, 164), (8, 8), sized(badge, 164))
    touch = clean(touch)
    touch.save(PUB / 'icons/fitz-touch-180.png', 'PNG', optimize=True)
    touch.save(PUB / 'apple-touch-icon.png', 'PNG', optimize=True)      # iOS also asks for this path by itself
    render_og(PUB / 'brand/fitz-badge-768.webp', PUB / 'og-badge-1200x630.png')
    for p in sorted([*(PUB / 'brand').glob('fitz-badge-*'), *(PUB / 'icons').glob('fitz-*'), PUB / 'og-badge-1200x630.png']):
        print(f'  {p.relative_to(ROOT)}  {p.stat().st_size // 1024} KB')

OG_HTML = '''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow:wght@500;600&family=Barlow+Condensed:wght@600&display=swap">
<style>
html,body{margin:0;width:1200px;height:630px;background:#1b2622;color:#f8f6f2;font-family:Barlow,system-ui,sans-serif}
.frame{position:absolute;inset:26px;border:1.5px solid #a07a48;border-radius:4px}
.frame::after{content:"";position:absolute;inset:7px;border:1px solid rgb(160 122 72 / .45);border-radius:2px}
.grid{position:absolute;inset:26px;display:grid;grid-template-columns:392px 1fr;align-items:center;gap:8px;padding:0 56px 0 44px}
img{width:360px;height:360px;display:block;justify-self:center;filter:drop-shadow(0 10px 28px rgb(0 0 0 / .45))}
.name{font:700 22px/1 Cinzel,serif;letter-spacing:.14em;color:#cdb682;margin:0 0 18px}
h1{font:700 44px/1.08 Cinzel,serif;margin:0 0 26px;letter-spacing:.01em}
.creds{display:flex;flex-wrap:wrap;gap:10px 14px;margin:0 0 26px;padding:0;list-style:none}
.creds li{font:600 16.5px/1 "Barlow Condensed",sans-serif;letter-spacing:.04em;text-transform:uppercase;color:#cdb682;padding-top:10px;border-top:1.5px solid #a07a48}
.contact{font:500 22px/1.3 Barlow,sans-serif;color:#e8e2d6;margin:0}
.contact b{font-weight:600;color:#f8f6f2}
</style></head><body><div class="frame"></div><div class="grid"><img src="BADGE" alt="">
<div><p class="name">FITZ FERAL HUNTERS</p><h1>Professional pest &amp; vermin control across Victoria</h1>
<ul class="creds"><li>Firearms licence</li><li>Game Licence</li><li>SSAA Farmer Assist</li><li>AHCPMG304</li><li>$20m public liability</li></ul>
<p class="contact"><b>0499 866 580</b> · Warragul, Gippsland · all of Victoria</p></div></div></body></html>'''

def render_og(badge_path, out):
    """Render the share card with Playwright (headless Chromium is preinstalled; fonts come from Google Fonts)."""
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as d:
        page_path = pathlib.Path(d) / 'og.html'
        page_path.write_text(OG_HTML.replace('BADGE', badge_path.as_uri()))
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
            pg.goto(page_path.as_uri()); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
            fonts = pg.evaluate("document.fonts.check('700 44px Cinzel')")
            tmp = pathlib.Path(d) / 'og.png'; pg.screenshot(path=str(tmp)); b.close()
        if not fonts: sys.exit('share card: Cinzel did not load, refusing to write a fallback-font card')
        clean(Image.open(tmp).convert('RGB')).save(out, 'PNG', optimize=True)

if __name__ == '__main__':
    main()
