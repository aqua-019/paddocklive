# Shop mockup (SP-07)

A clickable mockup of a Fitz Feral Hunters shop: product grid, product page, cart drawer, cart, checkout and confirmation. Sample products and prices; nothing is charged or sent. Not deployed (Vercel serves `public/` only). Record: `docs/SP-07-ffh-shop-mockup.md`.

| File | What it is |
|---|---|
| `shop.html`, `shop.css`, `shop.js` | The shop: markup, styles (site tokens only) and behaviour (sample products in `P`) |
| `build_mock.py` | Wraps the shop in the production shell taken from `public/services.html` |
| `dist/shop-mockup.html` | The single-file page published as the claude.ai artifact |
| `dist/preview.html` | The same page in a full document, for local checks |
| `check.js` | Playwright checks (CAP-24): `node mockups/shop/check.js mockups/shop/dist/preview.html <outdir>` |

Rebuild after any change: `python3 src/build.py && python3 mockups/shop/build_mock.py`.
