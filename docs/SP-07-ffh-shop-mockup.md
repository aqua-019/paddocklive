# SP-07 · Fitz Feral Hunters · Shop mockup: product grid, product page, cart, checkout (diff-mode SP, D700 §0D)

Compiled against: STAMP :: D700 · 4 Oct 2026 · 6511 entries D0001-D6558 · 218 laws · 387 capsules · 466 groups · 1824 pairs · 499 anti-pairs · 457 palettes · 21 lenses
Measured state before the diff: v1.2 live on fitzferalhunters.com.au, probe 35/35 (SP-06 plus the 10 Nov client edits).
Brief (Aqua, 14 Nov 2026):
- Fitz wants a shop on the site where clients, friends and customers can buy his merchandise.
- The real shop will run on Shopify (Australian store; Fitz will set up the account).
- For now, a mockup of what the shop would look like, with:
  - add to cart
  - a cart
  - a checkout page
  - billing and shipping details

**Status: mockup only.** Nothing in `public/` changed. The mockup lives in `mockups/shop/` (Vercel serves `public/` only) and is published as a claude.ai artifact for review with Fitz.

## Audit (before)

- No shop or merchandise anywhere on the site.
- The nav was seven text links plus the gold Contact button (SP-06), fitting one row at 900, 1024 and 1280.

## Delta (mockup)

**Shell.** Generated from the production Services page by `mockups/shop/build_mock.py`, so tokens, type, the topo sheet, header, footer and site script are the shipped ones byte for byte. Site links open the live site; the shop links stay in the page.

**Header**
- **Shop** is the eighth nav link, after Reviews.
- A cart button follows the nav on desktop and sits beside Menu on a phone:
  - bag icon and a gold count
  - the count is hidden while the cart is empty
  - its label is "Cart, N items"
- At 900 to 1023px, nav links tighten from 6px to 4px side padding, so everything still fits one row. At 900px the row needed about 28px back.
- No call bar on the shop pages, and the footer drops the bar's padding.

**Shop** (`#shop`)
- Sheet meta line, eyebrow and h1 "Caps, tees and gear".
- Filter chips: All, Apparel, Headwear, Accessories. Each is an `aria-pressed` button.
- Six sample products: logo tee, trucker cap, field hoodie, beanie, stubby holder and sticker pack.
- Each card shows:
  - a 4:5 `.slot` with registration ticks
  - the name as an h3 in Barlow Condensed
  - the price
  - colour dots, as `role=img` with the colour names
  - one button: "Choose size", "Choose colour", or "Add to cart" when the item has only one option
- A postage strip under the grid states the costs up front (D3815):
  - $10.95 by Parcel Post, free over $100
  - pick-up in Warragul is free
  - swaps within 30 days
- Product pictures are a colour field per variant standing in for Fitz's photos:
  - the transparent lockup on dark colours
  - the lockup plate as a "patch" on light colours (Sand, Bone, Blaze orange)
  - a "Sample image" tag on the product page

**Product page** (`#item-<handle>`, D3762)
- Breadcrumb (D0216): Shop / category / name. The current page is not a link.
- Sticky picture, with colour thumbnails that switch it.
- h1 name, price with "AUD, GST included", and a short description.
- **Colour:** radio swatches with the chosen name in the legend.
- **Size:** radio tiles.
  - Sold-out sizes come from per-variant data (`out`), not a counter (NOPAIR-19). They're disabled, dashed and struck through, with "sold out" in screen-reader text.
  - Adding without a size shows "Choose a size." and focuses the first size.
- Size guide in centimetres, in a disclosure.
- Quantity stepper, 1 to 10 (D0330), and an "Add to cart · $total" button.
- Specs list, a disclosure for postage, pick-up and swaps, and "More from the shop".

**Cart drawer** (D0382, D0381)
- A native `<dialog>` from the right, full height.
- Its footer is fixed, with Subtotal, a free-postage line, Checkout and View cart.
- Three ways to close it: overlay, the close button, and Esc.
- It slides 24px only with `prefers-reduced-motion: no-preference`.
- Focus goes to its title.
- One-option items add straight from the grid.

**Cart page** (`#cart`, D3763)
- Every line shows the variant ("Olive · Size L") so the cart matches what was chosen.
- A stepper and Remove on each line. Focus stays on + or − after a change.
- Summary:
  - a free-postage meter (`role=progressbar`)
  - the subtotal with GST included
  - the postage rule in words
  - Checkout
- Empty state, with a "Mockup helper: Add two sample items" button.

**Checkout** (`#checkout`, D3764)
- Opens with a note: on the live shop this step is Shopify's secure checkout, and the mockup has no card fields.
- Express wallets first: Apple Pay, Google Pay and PayPal, as plain text buttons. In the mockup each one shows a toast explaining what it does.
- Contact: email, plus an opt-in that's unchecked by default (D3819, NOPAIR-22).
- Delivery: "Post it to me" or "Pick up in Warragul", as selectable rows (D3781).
  - **Post:** country, first and last name, street address, unit, suburb, state select, postcode (4 digits) and phone. Every field carries its `autocomplete` token.
  - **Pick-up:** names and a mobile number. No address.
- Postage: Parcel Post $10.95 (it reads "Free" over $100) or Express Post $16.95.
- Payment: card, PayPal or Afterpay.
  - The card panel says Shopify's card form goes there; the mockup deliberately has none.
  - The Afterpay panel shows four payments of total ÷ 4.
- Billing address defaults to the delivery address (D3764). Pick-up requires a billing address.
- Errors (D0310): a summary list at the top that takes focus, with links that focus each field. Each field gets its own message and `aria-invalid`.
- Order summary:
  - pinned on desktop
  - a collapsible bar with the total on a phone
  - lines with quantity badges
  - promo field (D3761): try WELCOME10; an applied code becomes a removable chip and an unknown one gets an error
  - subtotal, discount, postage method, total in AUD, and "Including $X in GST" (total ÷ 11)
- "Pay now · $total" leads to the confirmation.

**Confirmation** (`#done`, D0979)
- Order number (FFH-1001…), "Thanks, Sam", and what happens next (posted within two business days, or Fitz texts for pick-up).
- A box saying this was a mockup.
- Contact, delivery and payment cards, then the lines and totals.

**NOPAIR sweep** (commerce): every one is clear.
- NOPAIR-18: no countdowns.
- NOPAIR-19: sold-out comes from data, and there's no stock counter.
- NOPAIR-22: the opt-in is unchecked.
- NOPAIR-25: GST is included everywhere, and postage is stated on the grid and the product page before checkout.
- NOPAIR-35: nothing is added that the user didn't choose. The sample-items helper is user-initiated and labelled.
- NOPAIR-159: one motion only, the drawer, and it's off under reduced motion.

## ASSERT lines (delta)

ASSERT :: header :: Shop is the eighth nav link and current; the cart button follows; nav, Contact and cart fit one row at 900/1024/1280 with no page overflow :: PER=LENS-15
ASSERT :: shop :: six products; filter chips narrow the grid; prices include GST and postage is stated before checkout :: PER=D3762 · D3815
ASSERT :: item :: size is required with a named error and focus; sold-out sizes come from variant data; colour swaps the picture; quantity updates the button total :: PER=D3762 · D0330 · NOPAIR-19
ASSERT :: drawer :: opens on add, focused title, three closes, fixed footer; no slide under reduced motion :: PER=D0382 · D0381 · D3453
ASSERT :: cart :: variant on every line; steppers keep focus; free-postage meter flips at $100 :: PER=D3763 · D0330
ASSERT :: checkout :: express wallets first; billing defaults to delivery; pick-up hides address and postage; error summary takes focus and links each field; opt-in unchecked :: PER=D3764 · D3781 · D0310 · D3819
ASSERT :: checkout :: totals = subtotal − promo + postage; GST = total ÷ 11; Afterpay = total ÷ 4 :: PER=D3815 · D3761
ASSERT :: all (iPhone 13, 320px) :: no horizontal scroll; tap targets ≥ 44px; no form text under 16px :: PER=D0551 · D4002 · LENS-15
ASSERT :: all :: hover recolours only; new text ≥ 4.5:1; no console errors :: PER=D3171 · LAW-03 · D0192

MEASURE :: mockups/shop/check.js 18/18 VERIFIED (docs/verdicts-sp07-shop.txt), against mockups/shop/dist/preview.html, 14 Nov 2026

## The real build on Shopify (when Fitz's store is ready)

**Recommended route: our pages + Shopify's checkout.**
- The shop pages in this mockup become real pages in `src/build.py`, in the site's design.
- Products, prices, variants, stock and the cart come from the Shopify **Storefront API**. Access is through the **Headless** sales channel in Fitz's Shopify admin.
- The site uses the channel's **public** access token. Shopify designs that token for the browser.
- The **private** token is a secret and isn't needed.
- Checkout hands off to **Shopify's own checkout**.

**What Shopify's checkout allows**
- **All plans:** the checkout can be branded with Fitz's logo, colours, basic fonts and background, through the checkout editor.
- **Shopify Plus only:** changing the steps themselves (custom blocks or fields on information, shipping and payment).
- This mockup's checkout shows the details Shopify will ask for. It is not something we build.

**What Fitz provides (no passwords in chat or email)**
1. **Access for Aqua.** In Shopify admin → Settings → Users → Security, he copies the 4-digit **collaborator request code**. Aqua sends a collaborator request from a Shopify Partner account. Fitz approves it and can remove it any time.
2. **Product list:** names, photos (we encode them through `scripts/media.py`), prices, colours, sizes and stock.
3. **Decisions:**
   - postage rates and the free-postage threshold
   - pick-up in Warragul (yes or no)
   - swap and returns policy
   - payment methods (Shopify Payments for cards, Apple Pay and Google Pay; PayPal; Afterpay)
   - **whether he is registered for GST.** Prices can only say "includes GST", and receipts can only show GST, if he is.

**Open design decision:** the nav rule in CLAUDE.md says seven text links. The mockup makes Shop the eighth and tightens link padding at 900 to 1023px. The alternative is a Shop band on the home page plus the footer link, with the cart button only.

FOLD :: D3764 → when the platform owns checkout (Shopify), mock it to show the buyer what will be asked and say so on the page; never build card fields in a mockup, and keep the "this step is Shopify's" note above the form :: Fitz Feral Hunters shop mockup
FOLD :: D3815 → state postage and GST on the grid and the product page, not first at checkout; an all-in price is a layout decision made before the cart exists :: Fitz Feral Hunters shop mockup
FOLD :: LENS-15 → adding one nav item to a full row costs about 30px at the breakpoint; measure the row at the breakpoint width before adding, and take the space from link padding in that band only :: Fitz Feral Hunters shop mockup
