// Service adapters for the Fitz Feral Hunters site. Every adapter is optional: it checks for its
// environment variables and reports "not configured" instead of failing, so the site runs with no
// keys at all (mockup) and gains each capability the moment a key is dropped into Vercel.
// No npm dependencies — every service here has a plain HTTPS REST API.

export const config = () => ({
  mail: !!process.env.RESEND_API_KEY,
  autoReply: process.env.AUTO_REPLY === '1' && !!process.env.RESEND_API_KEY,
  store: !!(process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL),
  turnstile: !!process.env.TURNSTILE_SECRET_KEY,
  blob: !!process.env.BLOB_READ_WRITE_TOKEN,
});

// ---------------------------------------------------------------- email (Resend)
// Until a domain is verified in Resend, mail goes from Resend's test sender, which only delivers to the
// address the Resend account was created with. Set ENQUIRY_FROM (e.g. "Fitz Feral Hunters <enquiries@fitzferalhunters.com>")
// once fitzferalhunters.com is verified. See docs/resend-setup.md.
const RESEND = 'https://api.resend.com/emails';
export const TEST_SENDER = 'Fitz Feral Hunters website <onboarding@resend.dev>';
export const fromAddress = () => (process.env.ENQUIRY_FROM || '').trim() || TEST_SENDER;
export function fromCheck() {
  const raw = (process.env.ENQUIRY_FROM || '').trim();
  if (!raw) return { set: false, domain: 'resend.dev', note: 'test sender: delivers only to the Resend account owner' };
  const m = raw.match(/<([^<>\s@]+)@([^<>\s@]+\.[^<>\s@]+)>$/) || raw.match(/^([^<>\s@]+)@([^<>\s@]+\.[^<>\s@]+)$/);
  return m ? { set: true, domain: m[2].toLowerCase(), valid: true } : { set: true, valid: false, note: 'ENQUIRY_FROM should look like: Fitz Feral Hunters <enquiries@fitzferalhunters.com>' };
}

/** A plain-words reason for a Resend failure, for the function logs. */
export function resendHint(status, body) {
  const t = String(body || '');
  if (status === 401 || /api key is invalid|missing api key/i.test(t)) return 'the API key is wrong or was revoked: create a new one in Resend and update RESEND_API_KEY';
  if (status === 403 && /resend\.dev|testing emails|own email address/i.test(t)) return 'the test sender only delivers to the Resend account owner: verify fitzferalhunters.com and set ENQUIRY_FROM, or create the Resend account with the ENQUIRY_TO address';
  if (status === 403 && /not verified|verify/i.test(t)) return 'the ENQUIRY_FROM domain is not verified in Resend yet: check its DNS records';
  if (status === 403) return 'the API key cannot send from this address (a key restricted to another domain?)';
  if (status === 422) return 'Resend rejected the message fields (often a badly formatted ENQUIRY_FROM)';
  if (status === 429) return 'Resend rate limit reached: wait a moment';
  return 'see the Resend dashboard → Logs';
}

export async function sendMail({ to, subject, text, html, replyTo, from, idempotencyKey, tags }) {
  if (!process.env.RESEND_API_KEY) return { sent: false, reason: 'RESEND_API_KEY not set' };
  const headers = { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' };
  // Resend keeps an idempotency key for 24 hours: a retried request with the same key is not sent twice.
  if (idempotencyKey) headers['Idempotency-Key'] = String(idempotencyKey).slice(0, 256);
  const r = await fetch(RESEND, {
    method: 'POST', headers,
    body: JSON.stringify({ from: from || fromAddress(), to: Array.isArray(to) ? to : [to], reply_to: replyTo || undefined, subject, text, html: html || undefined, tags: tags || undefined }),
  });
  if (!r.ok) {
    const body = await r.text();
    const err = new Error(`Resend ${r.status}: ${body.slice(0, 300)} — ${resendHint(r.status, body)}`);
    err.status = r.status;
    throw err;
  }
  const j = await r.json();
  return { sent: true, id: j.id };
}

// ---------------------------------------------------------------- store (Upstash Redis REST — Vercel KV / Marketplace Upstash)
// Used for: the enquiry log (nothing is lost if mail fails), per-IP rate limiting, idempotency.
function redisEnv() {
  const url = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
  return url && token ? { url, token } : null;
}
export async function redis(...cmd) {
  const env = redisEnv(); if (!env) return null;
  const r = await fetch(env.url, { method: 'POST', headers: { Authorization: `Bearer ${env.token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(cmd) });
  if (!r.ok) throw new Error(`Redis ${r.status}: ${await r.text()}`);
  return (await r.json()).result;
}
export async function logEnquiry(record, ttlSec = 90 * 86400) {
  if (!redisEnv()) return { stored: false, reason: 'no store configured' };
  const id = `enq:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
  await redis('SET', id, JSON.stringify(record), 'EX', ttlSec);      // enquiries are kept 90 days (see the privacy note)
  await redis('LPUSH', 'enquiries', id);
  await redis('LTRIM', 'enquiries', 0, 999);            // keep the last 1,000 ids in the index
  return { stored: true, id };
}
/** Sliding-window-ish rate limit: at most `limit` hits per `windowSec` for a key (an IP). Returns {ok, remaining}. */
export async function rateLimit(key, limit = 5, windowSec = 600) {
  if (!redisEnv()) return { ok: true, remaining: limit, reason: 'no store configured' };
  const k = `rl:${key}:${Math.floor(Date.now() / 1000 / windowSec)}`;
  const n = await redis('INCR', k);
  if (n === 1) await redis('EXPIRE', k, windowSec);
  return { ok: n <= limit, remaining: Math.max(0, limit - n) };
}

// ---------------------------------------------------------------- bot check (Cloudflare Turnstile)
export async function verifyTurnstile(token, ip) {
  if (!process.env.TURNSTILE_SECRET_KEY) return { ok: true, reason: 'not configured' };
  if (!token) return { ok: false, reason: 'missing token' };
  const body = new URLSearchParams({ secret: process.env.TURNSTILE_SECRET_KEY, response: token, remoteip: ip || '' });
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body });
  const j = await r.json();
  return { ok: !!j.success, reason: j['error-codes'] && j['error-codes'].join(',') };
}

// ---------------------------------------------------------------- media (Vercel Blob)
// Uploads happen from scripts/upload-media.py (or a future admin page); the site only reads public blob URLs.
export function blobConfigured() { return !!process.env.BLOB_READ_WRITE_TOKEN; }

export const redisConfigured = () => !!redisEnv();

export function clientIp(req) {
  return (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || req.socket?.remoteAddress || '';
}
