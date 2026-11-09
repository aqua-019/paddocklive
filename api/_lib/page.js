// Small shared helpers for the functions: HTML escaping, the plain no-JS pages, and request parsing.
import querystring from 'node:querystring';

export const PHONE = '0499 866 580';
export const PHONE_E164 = '+61499866580';
export const OWNER_EMAIL = 'fitzferalhunters1@gmail.com';

export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const clean = (v, max) => String(v == null ? '' : v).replace(/[\u0000-\u0008\u000b-\u001f\u007f]+/g, ' ').replace(/\r\n?/g, '\n').trim().slice(0, max);
export const oneLine = (v, max) => clean(v, max).replace(/\s+/g, ' ');

/** Vercel parses JSON and form bodies for us; the dev server does the same. Accept a raw string too. */
export function parseBody(req) {
  const ct = String(req.headers['content-type'] || '');
  const raw = req.body;
  if (raw && typeof raw === 'object' && !Buffer.isBuffer(raw)) return raw;
  const str = Buffer.isBuffer(raw) ? raw.toString() : String(raw || '');
  if (ct.includes('application/json')) return str ? JSON.parse(str) : {};
  if (ct.includes('application/x-www-form-urlencoded')) return querystring.parse(str);
  return {};
}

export const wantsJson = req => String(req.headers['accept'] || '').includes('application/json') || String(req.headers['content-type'] || '').includes('application/json');

export function siteBase(req) {
  if (process.env.SITE_URL) return process.env.SITE_URL.replace(/\/$/, '');
  const host = req.headers['x-forwarded-host'] || req.headers.host || 'localhost';
  const proto = req.headers['x-forwarded-proto'] || (String(host).startsWith('localhost') ? 'http' : 'https');
  return `${proto}://${host}`;
}

/** The plain page used by the no-JS fallbacks and the moderation screens. Same tokens as the site. */
export function page(title, body) {
  return `<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · Fitz Feral Hunters</title><meta name="robots" content="noindex, nofollow"><meta name="format-detection" content="telephone=no">
<style>
:root{--bg:#f8f6f2;--surface:#f1eee8;--ink:#1b2622;--ink-2:color-mix(in srgb,#1b2622 80%,#f8f6f2);--gold:#a07a48;--ok:#2E6E4E;--err:#9b2c20;--line:color-mix(in srgb,#1b2622 40%,transparent)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 Barlow,system-ui,sans-serif;padding:16px}
main{max-width:40rem;margin:40px auto;border-radius:4px;padding:24px;background:var(--surface);box-shadow:inset 0 0 0 2px var(--ok);display:grid;gap:14px}
main.warn{box-shadow:inset 0 0 0 2px var(--gold)}
h1{font:700 1.7rem/1.05 "Barlow Condensed","Arial Narrow",sans-serif;text-transform:uppercase;margin:0}
p{margin:0}a{color:inherit}.muted{color:var(--ink-2);font-size:15px}
dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:0;padding:14px;background:var(--bg);border-radius:4px;font-size:15px}dt{font-weight:600;color:var(--ink-2);text-transform:uppercase;font-size:12px;letter-spacing:.06em;padding-top:2px}dd{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}
form{display:grid;gap:12px}label{font-weight:600;display:grid;gap:6px}select,textarea,input[type=text],input[type=month],input[type=url]{font:inherit;padding:10px 12px;border:1.5px solid var(--line);border-radius:4px;background:var(--bg);color:var(--ink);min-height:48px}
.row{display:flex;flex-wrap:wrap;gap:10px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 20px;border-radius:4px;border:1.5px solid var(--line);font:600 16px/1 Barlow,system-ui,sans-serif;text-decoration:none;color:var(--ink);background:transparent;cursor:pointer}
.btn.go{background:#2c3a35;border-color:#2c3a35;color:#f8f6f2}.btn.no{border-color:var(--err);color:var(--err)}
label.check{display:flex;gap:10px;align-items:flex-start;min-height:44px}label.check input{width:22px;height:22px;margin:2px 0 0;flex:none;accent-color:#2c3a35}
.stars{color:var(--gold);letter-spacing:2px;font-size:20px}.ok{color:var(--ok);font-weight:600}.gold{color:var(--gold);font-weight:600}
.ph{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin:0;padding:0;list-style:none}.ph a{display:block}.ph img{width:100%;height:auto;aspect-ratio:1;object-fit:cover;border-radius:4px;display:block;background:var(--bg)}
.link{font:15px/1.4 ui-monospace,Menlo,monospace;padding:12px;background:var(--bg);border-radius:4px;overflow-wrap:anywhere;user-select:all}
</style></head><body><main${/class="warn"/.test(body) ? ' class="warn"' : ''}>${body.replace('class="warn"', '')}</main></body></html>`;
}
