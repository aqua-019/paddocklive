#!/usr/bin/env python3
"""SP-07 shop mockup. Builds a single-file page from the production Services page (same CSS, header, footer and site
script) with the shop in <main>. Nothing here is deployed: Vercel serves public/ only.

    python3 src/build.py                    # production build first, so the shell is current
    python3 mockups/shop/build_mock.py      # → mockups/shop/dist/shop-mockup.html (artifact page) + dist/preview.html (local check)
"""
import base64, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUB = ROOT / 'public'
LIVE = 'https://fitzferalhunters.com.au'

def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()

def one(pattern, text, flags=re.S):
    m = re.findall(pattern, text, flags)
    assert len(m) == 1, (pattern, len(m))
    return m[0]

src = (PUB / 'services.html').read_text()
head, body = src.split('<body', 1)
css = one(r'<style>(.*?)</style>', head)
sprite = one(r'(<svg hidden aria-hidden="true" focusable="false">.*?</svg>)', body)
header = one(r'(<header class="site-head">.*?</header>)', body)
footer = one(r'(<footer class="site-foot" id="footer">.*?</footer>)', body)
site_js = one(r'<script>(.*?)</script>', body)

LOGO = data_uri(PUB / 'brand/logo-lockup.png', 'image/png')
PLATE = data_uri(PUB / 'brand/logo-lockup-plate.jpg', 'image/jpeg')
TOPO = data_uri(PUB / 'topo-tile.svg', 'image/svg+xml')

# the site CSS, with its two file references made self-contained
assert css.count('url("/topo-tile.svg")') >= 1
css = css.replace('url("/topo-tile.svg")', 'var(--topo-tile)')
css = f':root{{--topo-tile:url("{TOPO}")}}\n' + css
assert '/topo-tile.svg' not in css and 'url("/' not in css

def live_links(html):
    """Site pages open on the live site; the shop's own links stay in the page."""
    return re.sub(r'href="/([^"#]*)(#[^"]*)?"', lambda m: f'href="{LIVE}/{m.group(1)}{m.group(2) or ""}"', html)

# header: Shop joins the nav after Reviews (and is the current page); a cart button follows the nav / sits beside Menu
header = header.replace(' aria-current=page', '')
shop_li = '<li><a href="#shop" aria-current="page">Shop</a></li>'
assert header.count('<li><a href="/reviews">Reviews</a></li>') == 2
header = header.replace('<li><a href="/reviews">Reviews</a></li>', '<li><a href="/reviews">Reviews</a></li>' + shop_li)
header = live_links(header).replace('src="/brand/logo-lockup.png"', f'src="{LOGO}"')
cart_btn = ('<a class="cart-btn" id="cart-btn" href="#cart" aria-label="Cart, 0 items"><svg class="i" aria-hidden="true"><use href="#i-bag"/></svg>'
            '<span class="count" id="cart-count" data-zero aria-hidden="true">0</span></a>')
assert header.count('</details>') == 1
header = header.replace('</details>', '</details>\n    ' + cart_btn)

footer = footer.replace('<li><a href="/reviews">Reviews</a></li>', '<li><a href="/reviews">Reviews</a></li><li><a href="#shop">Shop</a></li>')
footer = live_links(footer).replace('src="/brand/logo-lockup.png"', f'src="{LOGO}"')

ICONS = ('<symbol id="i-bag" viewBox="0 0 24 24"><path d="M5 8h14l-1.3 12.1a1 1 0 0 1-1 .9H7.3a1 1 0 0 1-1-.9z"/><path d="M9 10V7a3 3 0 0 1 6 0v3"/></symbol>'
         '<symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10" rx="1.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/></symbol>'
         '<symbol id="i-x" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></symbol>'
         '<symbol id="i-minus" viewBox="0 0 24 24"><path d="M5 12h14"/></symbol>'
         '<symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>'
         '<symbol id="i-truck" viewBox="0 0 24 24"><path d="M3 6.5h11v9.5H3zM14 9.5h4l3 3V16h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></symbol>'
         '<symbol id="i-swap" viewBox="0 0 24 24"><path d="M4 8h13l-3-3M20 16H7l3 3"/></symbol>')
sprite = sprite.replace('</svg>', ICONS + '</svg>')

shop_css = (HERE / 'shop.css').read_text() + f'\n.art-logo{{background-image:url("{LOGO}")}}\n.art-plate{{background-image:url("{PLATE}")}}\n'
shop_html = (HERE / 'shop.html').read_text()
shop_js = (HERE / 'shop.js').read_text()

page = f'''<title>Fitz Feral Hunters Shop</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>{css}
{shop_css}</style>
{sprite}
<div class="skips"><a href="#main">Skip to content</a></div>
{header}
<main id="main">
{shop_html}
</main>
{footer}
<script>{site_js}</script>
<script>{shop_js}</script>
'''
dist = HERE / 'dist'; dist.mkdir(exist_ok=True)
(dist / 'shop-mockup.html').write_text(page)
# local check: the same page inside the document skeleton the artifact host adds
skeleton = ('<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>'
            '</head><body>' + page + '</body></html>')
(dist / 'preview.html').write_text(skeleton)
print(f'shop mockup → {dist / "shop-mockup.html"} ({len(page)/1024:.0f} KB)')
