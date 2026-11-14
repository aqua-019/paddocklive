// SP-07 shop mockup: CAP-24 verdicts. node check.js <preview.html> <outdir>
const { chromium, devices } = require('playwright');
const path = require('path');
const FILE = 'file://' + path.resolve(process.argv[2]); const OUT = process.argv[3];
const out = []; let failed = 0;
function V(ok, where, what, claimed, measured, per) { if (!ok) failed++; out.push(`${ok ? 'VERIFIED' : 'FAILED'} :: SP-07 :: ${where} :: ${what} :: claimed=${claimed} measured=${measured} :: PER=${per}`); }
const go = async (p, h) => { await p.evaluate(x => { location.hash = x; }, h); await p.waitForTimeout(250); };

(async () => {
  const b = await chromium.launch();
  const errs = [];
  const watch = p => { p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/fonts\.(googleapis|gstatic)/.test(m.text())) errs.push(m.text()); }); };

  // ---------- desktop
  const dc = await b.newContext({ viewport: { width: 1280, height: 900 } }); const d = await dc.newPage(); watch(d);
  await d.goto(FILE); await d.waitForTimeout(500);
  const fonts = await d.evaluate(() => document.fonts.check('700 20px Cinzel') && document.fonts.check('600 16px Barlow'));
  const grid = await d.evaluate(() => document.querySelectorAll('#grid .pcard').length);
  await d.click('[data-filter="Headwear"]'); const hw = await d.evaluate(() => [...document.querySelectorAll('#grid .pcard h3')].map(h => h.textContent).join('/'));
  await d.click('[data-filter="all"]');
  V(grid === 6 && hw === 'Trucker cap/Beanie', 'shop (1280)', 'grid of six sample products; the Headwear filter shows the two hats', '6 · Trucker cap/Beanie', `${grid} · ${hw} · fonts ${fonts ? 'loaded' : 'FALLBACK'}`, 'D3762 · D3815');
  // nav fit at three desktop widths
  const fit = [];
  for (const w of [900, 1024, 1280]) { await d.setViewportSize({ width: w, height: 900 }); await d.waitForTimeout(150);
    fit.push(await d.evaluate(() => { const h = document.querySelector('.site-head .wrap'), n = document.querySelector('.nav ul'), c = document.getElementById('cart-btn'); const r = h.getBoundingClientRect(), cr = c.getBoundingClientRect(); const items=[...n.children].map(li=>li.getBoundingClientRect()); const oneRow=items.every(x=>Math.abs(x.top-items[0].top)<2)&&Math.abs(cr.top-r.top-(r.height-cr.height)/2)<3; return Math.round(r.height) <= 80 && oneRow && cr.right <= r.right + 1 && document.documentElement.scrollWidth <= innerWidth; })); }
  V(fit.every(Boolean), 'header (900/1024/1280)', 'eight nav links, the gold Contact button and the cart fit on one row', 'one row, no overflow', fit.join('/'), 'LENS-15');
  await d.setViewportSize({ width: 1280, height: 900 });

  // product page: size required, colour swaps the picture, sold-out size, qty, add → drawer
  await go(d, 'item-logo-tee');
  const h1 = await d.evaluate(() => document.getElementById('h-item').textContent);
  await d.click('#add-btn'); const sizeErr = await d.evaluate(() => getComputedStyle(document.getElementById('e-size')).display !== 'none' && document.activeElement.name === 'size');
  await d.click('label[for="col-bone"]'); const sold = await d.evaluate(() => document.getElementById('sz-3XL').disabled && document.getElementById('colour-name').textContent);
  await d.click('label[for="col-olive"]'); await d.click('label[for="sz-L"]'); await d.click('[data-step="1"]');
  const addTotal = await d.evaluate(() => document.getElementById('add-total').textContent);
  await d.click('#add-btn'); await d.waitForTimeout(450);
  const dr = await d.evaluate(() => { const dl = document.getElementById('cart-drawer'); return { open: dl.open, line: dl.querySelector('.ln-var')?.textContent, q: dl.querySelector('[data-q]')?.value, sub: document.getElementById('cd-sub').textContent, free: document.getElementById('cd-free').textContent, count: document.getElementById('cart-count').textContent, focus: document.activeElement.id }; });
  V(h1 === 'Logo tee' && sizeErr && sold === 'Bone' && addTotal === '$90.00' && dr.open && dr.line === 'Olive · Size L' && dr.q === '2' && dr.sub === '$90.00' && dr.count === '2' && dr.focus === 'cd-title',
    'item → drawer', 'size is required, Bone 3XL is sold out, quantity 2 adds Olive L to the cart and the drawer opens on its title', 'error+focus · 3XL off · $90.00 · drawer Olive · Size L ×2 · count 2',
    `err ${sizeErr} · ${sold} 3XL off · ${addTotal} · open ${dr.open} · "${dr.line}" ×${dr.q} · ${dr.sub} · "${dr.free}" · count ${dr.count} · focus #${dr.focus}`, 'D3762 · D0382 · D0381');
  await d.screenshot({ path: OUT + '/d-drawer.png' });

  // drawer → cart page; + makes it 3, free postage unlocks; remove leaves the empty state
  await d.click('#cart-drawer a[href="#cart"]'); await d.waitForTimeout(300);
  const cp1 = await d.evaluate(() => ({ view: !document.getElementById('v-cart').hidden, lines: document.querySelectorAll('#cart-body .line').length, drawer: document.getElementById('cart-drawer').open }));
  await d.click('#cart-body [data-inc]'); await d.waitForTimeout(100);
  const cp2 = await d.evaluate(() => ({ q: document.querySelector('#cart-body [data-q]').value, total: document.querySelector('#cart-body dd.grand').textContent, free: !!document.querySelector('#cart-body .free.done'), focus: document.activeElement.hasAttribute('data-inc') }));
  V(cp1.view && cp1.lines === 1 && !cp1.drawer && cp2.q === '3' && cp2.total === 'AUD$135.00' && cp2.free && cp2.focus, 'cart', 'View cart closes the drawer; + adds one, keeps focus on +, and free postage unlocks over $100', 'cart · 1 line · 3 · $135.00 · free · focus kept',
    `view ${cp1.view} · ${cp1.lines} line · drawer ${cp1.drawer} · q ${cp2.q} · ${cp2.total} · free ${cp2.free} · focus ${cp2.focus}`, 'D3763 · D0330');

  // checkout: empty submit → summary; sample details; Express; WELCOME10; pick-up; pay → confirmation
  await go(d, 'checkout');
  await d.click('#co-pay'); await d.waitForTimeout(150);
  const e1 = await d.evaluate(() => ({ n: document.querySelectorAll('#co-err-list li').length, focus: document.activeElement.id, inv: document.querySelectorAll('#co-form [aria-invalid="true"]').length }));
  await d.click('#co-fill'); await d.click('label:has(#s-express)');
  await d.fill('#disc-d', 'welcome10'); await d.click('#co-sum-d .disc button'); await d.waitForTimeout(100);
  const t1 = await d.evaluate(() => [...document.querySelectorAll('#co-sum-d .totals dt, #co-sum-d .totals dd')].map(x => x.textContent).join('|') + ' ' + document.querySelector('#co-sum-d .gst-line').textContent);
  await d.click('label:has(#m-pickup)'); await d.waitForTimeout(100);
  const pk = await d.evaluate(() => ({ ship: document.getElementById('ship-fields').hidden, post: document.getElementById('sec-postage').hidden, bill: !document.getElementById('bill-fields').hidden, same: document.getElementById('bill-same-row').hidden, total: document.querySelector('#co-sum-d dd.grand').textContent }));
  await d.click('label:has(#m-ship)'); await d.click('label:has(#pm-afterpay)');
  const ap = await d.evaluate(() => document.getElementById('afterpay-note').textContent);
  await d.screenshot({ path: OUT + '/d-checkout.png', fullPage: true });
  await d.click('#co-pay'); await d.waitForTimeout(1300);
  const dn = await d.evaluate(() => ({ hash: location.hash, h1: document.getElementById('h-done')?.textContent, no: document.querySelector('#done-body .eyebrow')?.textContent, count: document.getElementById('cart-count').textContent, focus: document.activeElement.id }));
  V(e1.n === 7 && e1.focus === 'co-err' && e1.inv === 7, 'checkout', 'Pay now on an empty form lists every missing detail and focuses the list', '7 errors · focus #co-err · 7 aria-invalid', `${e1.n} errors · focus #${e1.focus} · ${e1.inv} aria-invalid`, 'D0310');
  V(/Subtotal\|\$135\.00\|Discount WELCOME10\|−\$13\.50\|Express Post\|\$16\.95\|Total\|AUD\$138\.45/.test(t1) && /\$12\.59/.test(t1), 'checkout', 'totals: discount, Express Post and GST worked out (GST = total ÷ 11)', '135 − 13.50 + 16.95 = 138.45 · GST 12.59', t1, 'D3815 · D3761');
  V(pk.ship && pk.post && pk.bill && pk.same && pk.total === 'AUD$121.50' && ap.indexOf('$'+(Math.round(138.45/4*100)/100).toFixed(2))>-1, 'checkout', 'pick-up hides the address and postage, asks for a billing address and drops postage; Afterpay shows four payments', 'hidden · hidden · billing · $121.50 · 4 × $34.61 (Express total $138.45)',
    `${pk.ship} · ${pk.post} · billing ${pk.bill} (same hidden ${pk.same}) · ${pk.total} · "${ap}"`, 'D3764 · D3781');
  V(dn.hash === '#done' && dn.h1 === 'Thanks, Sam' && /FFH-1001/.test(dn.no) && dn.count === '0' && dn.focus === 'h-done', 'done', 'Pay now (mockup) shows the confirmation, empties the cart and focuses the heading', '#done · Thanks, Sam · FFH-1001 · 0 · focus', `${dn.hash} · ${dn.h1} · "${dn.no}" · ${dn.count} · #${dn.focus}`, 'D0979');
  await d.screenshot({ path: OUT + '/d-done.png', fullPage: true });
  await go(d, 'shop'); await d.click('[data-add="sticker-pack"]'); await d.waitForTimeout(300); await d.keyboard.press('Escape'); await go(d, 'checkout');
  const xp = await d.evaluate(() => [...document.querySelectorAll('.xp-row .btn')].map(b => b.textContent).join('/') + ' first=' + (document.querySelector('#co-form').firstElementChild.nextElementSibling.className));
  await d.click('[data-xp="Apple Pay"]'); await d.waitForTimeout(100); const xt = await d.evaluate(() => document.querySelector('.toast.on')?.textContent || '');
  V(/^Apple Pay\/Google Pay\/PayPal first=express/.test(xp) && /Apple Pay opens here/.test(xt), 'checkout', 'express wallets lead the checkout; in the mockup they explain themselves', 'Apple Pay/Google Pay/PayPal first · toast', xp + ' · "' + xt + '"', 'D3764');
  // quick add from the grid
  await go(d, 'shop'); await d.click('[data-add="stubby-holder"]'); await d.waitForTimeout(350);
  const qa = await d.evaluate(() => ({ open: document.getElementById('cart-drawer').open, name: [...document.querySelectorAll('#cd-lines .ln-name')].map(x=>x.textContent).join('+'), count: document.getElementById('cart-count').textContent }));
  V(qa.open && qa.name === 'Sticker pack+Stubby holder' && qa.count === '2', 'shop', 'one-option items add straight from the grid', 'drawer · Sticker pack+Stubby holder · 2', `${qa.open} · ${qa.name} · ${qa.count}`, 'D3762');
  await d.keyboard.press('Escape');
  await go(d, 'shop'); await d.screenshot({ path: OUT + '/d-shop.png' });
  await go(d, 'item-trucker-cap'); await d.screenshot({ path: OUT + '/d-item.png' });

  // hover census on desktop: colour only
  const census = [];
  for (const hsh of ['shop', 'item-logo-tee', 'cart', 'checkout']) {
    await go(d, hsh);
    const n = await d.evaluate(() => { const els = [...document.querySelectorAll('main a, main button, main label, main summary, .site-head a, .site-head summary')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && r.top >= 0 && r.bottom <= innerHeight; }); els.forEach((e, i) => e.setAttribute('data-hc', i)); return els.length; });
    for (let i = 0; i < n; i++) {
      const sel = `[data-hc="${i}"]`; const before = await d.$eval(sel, e => { const s = getComputedStyle(e); return s.transform + '|' + s.boxShadow + '|' + s.translate + '|' + s.scale; });
      try { await d.hover(sel, { timeout: 500 }); } catch (e) { continue; }
      await d.waitForTimeout(240);
      const after = await d.$eval(sel, e => { const s = getComputedStyle(e); return s.transform + '|' + s.boxShadow + '|' + s.translate + '|' + s.scale; });
      if (before !== after) census.push(hsh + ' ' + await d.$eval(sel, e => e.outerHTML.slice(0, 80)));
      await d.mouse.move(2, 2);
    }
  }
  V(census.length === 0, 'shop, item, cart, checkout', 'hover recolours only (no transform or shadow change)', '0 changed', census.length + ' changed ' + census.slice(0, 3).join(' ; '), 'D3171 · LAW-03');

  // ---------- phone (iPhone 13, 390px) and 320px
  const views = ['shop', 'item-logo-tee', 'cart', 'checkout', 'done'];
  const mc = await b.newContext({ ...devices['iPhone 13'] }); const m = await mc.newPage(); watch(m);
  await m.goto(FILE); await m.waitForTimeout(400);
  await m.evaluate(() => { localStorage.clear(); });
  await go(m, 'cart'); await m.click('[data-sample]'); await m.waitForTimeout(200);
  const over = [], small = [], tiny = [];
  for (const v of views) {
    await go(m, v);
    if (v === 'checkout') { await m.click('#co-fill'); await m.click('label:has(#b-other)'); }
    over.push(await m.evaluate(() => document.documentElement.scrollWidth - innerWidth));
    const r = await m.evaluate(() => {
      const bad = [], txt = [];
      document.querySelectorAll('main a, main button, main summary, main input, main select, main .sizes label, main .swatches label, main .choice .row, .site-head a, .site-head summary').forEach(e => {
        const b = e.getBoundingClientRect(); if (!b.width || !b.height) return;
        if (e.matches('.vh, .dots i, main .lines a.thumb, input[type=radio], input[type=checkbox]')) return;
        if (e.closest('details:not([open])') && !e.matches('summary')) return; // inside a closed menu or summary
        if (e.closest('.choice .row') && e.tagName === 'INPUT') return;
        if (e.matches('a') && getComputedStyle(e).display === 'inline' && e.closest('p, li') && !e.closest('.crumbs')) return; // inline text links
        if (b.height < 43.5 || b.width < 43.5) bad.push(e.tagName + '.' + (e.className || e.id || e.textContent.trim().slice(0, 14)) + ' ' + Math.round(b.width) + '×' + Math.round(b.height));
      });
      document.querySelectorAll('main input:not([type=radio]):not([type=checkbox]), main select').forEach(e => { if (e.getBoundingClientRect().width && parseFloat(getComputedStyle(e).fontSize) < 16) txt.push(e.id + ' ' + getComputedStyle(e).fontSize); });
      return { bad, txt };
    });
    small.push(...r.bad.map(x => v + ' ' + x)); tiny.push(...r.txt.map(x => v + ' ' + x));
    await m.screenshot({ path: `${OUT}/m-${v}.png`, fullPage: v !== 'checkout' });
  }
  // drawer on the phone
  await go(m, 'shop'); await m.click('[data-add="sticker-pack"]'); await m.waitForTimeout(450);
  const mdr = await m.evaluate(() => { const r = document.querySelector('#cart-drawer .cd-frame').getBoundingClientRect(); return { w: Math.round(r.width), over: document.documentElement.scrollWidth - innerWidth }; });
  await m.screenshot({ path: OUT + '/m-drawer.png' });
  await m.keyboard.press('Escape');
  V(over.every(x => x <= 0) && mdr.over <= 0 && mdr.w === 390, 'all views (iPhone 13)', 'no horizontal scroll; the drawer fills the phone width', '0px ×5 · drawer 390', over.join('/') + 'px · drawer ' + mdr.w + ' wide, ' + mdr.over + 'px', 'LENS-15');
  V(small.length === 0, 'all views (iPhone 13)', 'tap targets ≥ 44px', '0 under 44', small.length + ' ' + small.slice(0, 6).join(' ; '), 'D0551');
  V(tiny.length === 0, 'checkout, item, cart (iPhone 13)', 'no form text under 16px (iOS zoom)', '0', tiny.length + ' ' + tiny.join(' ; '), 'D4002');
  const nc = await b.newContext({ viewport: { width: 320, height: 640 }, isMobile: true, hasTouch: true }); const n = await nc.newPage(); watch(n);
  await n.goto(FILE); await n.waitForTimeout(300); await n.evaluate(() => localStorage.clear()); await go(n, 'cart'); await n.click('[data-sample]');
  const o320 = []; for (const v of views) { await go(n, v); o320.push(await n.evaluate(() => document.documentElement.scrollWidth - innerWidth)); }
  V(o320.every(x => x <= 0), 'all views (320px)', 'no horizontal scroll at 320px', '0px ×5', o320.join('/') + 'px', 'LENS-15');

  // ---------- contrast of the new text (WCAG 2 ratio against the resolved background)
  await go(d, 'item-logo-tee'); await d.click('label[for="sz-M"]'); await d.click('#add-btn'); await d.waitForTimeout(400); await d.keyboard.press('Escape');
  const cons = [];
  for (const [hsh, sels] of [['shop', ['.mock-strip span', '.filters button[aria-pressed=false]', '.filters button[aria-pressed=true]', '.pcard .price', '.ship-strip p', '.meta']], ['item-logo-tee', ['.crumbs a', '.gst', '.specs dd', '.pimg .ptag', '.opt legend span', '.posted']], ['cart', ['.ln-var', '.sumbox .small', '.totals dt', '.helper span']], ['checkout', ['.handoff p', '.choice .row small', '.disc-msg', '.field .hint', '.gst-line', '.co-form .note']]]) {
    await go(d, hsh);
    const r = await d.evaluate((sels) => {
      const cv = document.createElement('canvas').getContext('2d');
      const rgb = c => { const cs = c.match(/^color\(srgb ([\d.e-]+) ([\d.e-]+) ([\d.e-]+)(?: \/ ([\d.]+))?\)/); if (cs) return [cs[1]*255, cs[2]*255, cs[3]*255, cs[4] === undefined ? 1 : +cs[4]]; cv.fillStyle = '#000'; cv.fillStyle = c; const s = cv.fillStyle; if (s[0] === '#') return [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16), 1]; const m = s.match(/[\d.]+/g).map(Number); return [m[0], m[1], m[2], m[3] ?? 1]; };
      const L = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
      const bgOf = el => { const layers = []; for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c[3] > 0) { layers.push(c); if (c[3] >= 1) break; } } let base = [248, 246, 242]; for (const c of layers.reverse()) base = base.map((v, i) => v * (1 - c[3]) + c[i] * c[3]); return base; };
      return sels.map(s => { const el = document.querySelector(s); if (!el) return [s, null]; const fg = rgb(getComputedStyle(el).color), bg = bgOf(el); const f = fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3])); const a = L(f), b = L(bg); return [s, +(((Math.max(a, b) + .05) / (Math.min(a, b) + .05)).toFixed(2))]; });
    }, sels);
    cons.push(...r);
  }
  const low = cons.filter(([s, v]) => v === null || v < 4.5);
  V(low.length === 0, 'shop, item, cart, checkout', 'new text meets 4.5:1', 'all ≥ 4.5', 'min ' + Math.min(...cons.map(c => c[1] || 0)) + ' · ' + (low.length ? 'LOW ' + low.map(x => x.join(' ')).join(', ') : cons.length + ' checked'), 'D0192');

  // ---------- reduced motion: the drawer doesn't slide
  const rc = await b.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' }); const rp = await rc.newPage(); watch(rp);
  await rp.goto(FILE + '#shop'); await rp.waitForTimeout(300); await rp.click('[data-add="stubby-holder"]'); await rp.waitForTimeout(50);
  const rm = await rp.evaluate(() => { const s = getComputedStyle(document.getElementById('cart-drawer')); return s.transitionDuration + ' ' + s.translate; });
  V(/^0s/.test(rm) && !/24px/.test(rm), 'drawer (reduced motion)', 'the cart drawer appears without sliding', 'no transition', rm, 'D3453');
  V(errs.length === 0, 'all', 'console/page errors', '0', errs.length + ' ' + errs.slice(0, 3).join(' | '), 'contract');

  console.log(out.join('\n')); console.log(`\n${out.length} verdicts · ${failed} FAILED`);
  await b.close();
})();
