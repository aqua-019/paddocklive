// Reviews: stored pending, published or declined by Fitz from a signed link, never edited, never deleted.
//
// Every published review is tied to a real job, one of two ways:
//   'link' — the customer used a review link Fitz sent after the job (an HMAC-signed invite, single use);
//   'fitz' — Fitz matched the name, job month and contact details to his own records before publishing.
// A review he can't match is declined as "Not a customer". Ratings are 1–5 and every one is published, good or bad.
import crypto from 'node:crypto';
import * as store from './store.js';

export const enabled = () => !!store.kind();
const key = id => `review:${id}`;
const DAY = 86400000;
export const LINK_DAYS = 30;          // moderation links in Fitz's email
export const INVITE_DAYS = 180;       // review links Fitz sends customers
export const MIN_TEXT = 250;
export const MAX_TEXT = 2000;

export const newId = () => crypto.randomBytes(6).toString('hex');

export async function create(r, id = newId()) {
  const rec = { ...r, id, status: 'pending', created: Date.now() };
  await store.set(key(rec.id), JSON.stringify(rec));
  await store.zadd('reviews:pending', rec.created, rec.id);
  return rec;
}

export async function get(id) {
  if (!/^[0-9a-f]{12}$/.test(String(id))) return null;
  const v = await store.get(key(id));
  return v ? JSON.parse(v) : null;
}

async function save(r) { await store.set(key(r.id), JSON.stringify(r)); return r; }

/**
 * Publish (or re-publish with a new reply). `checked` is Fitz confirming he matched it to a job; it's needed unless
 * the review came through his review link. `withPhotos` false publishes the words and rating but keeps the photos private.
 */
export async function publish(id, { reply = '', withPhotos = true, checked = false } = {}) {
  const r = await get(id); if (!r) return null;
  if (!r.verified && !checked) return { ...r, needsCheck: true };
  if (!r.verified) r.verified = 'fitz';
  r.status = 'published'; r.published = r.published || Date.now(); r.reply = reply; delete r.reason;
  r.photosShown = !!(withPhotos && r.photos && r.photos.length);
  await save(r);
  await store.zrem('reviews:pending', id);
  await store.zadd('reviews:published', r.published, id);
  return r;
}

export async function decline(id, reason) {
  const r = await get(id); if (!r) return null;
  r.status = 'declined'; r.reason = reason; r.declined = Date.now(); r.photosShown = false;
  await save(r);
  await store.zrem('reviews:pending', id);
  await store.zrem('reviews:published', id);
  return r;
}

export const photoUrl = (id, i) => `/api/review-photo?r=${id}&i=${i}`;

export const publicView = r => ({
  id: r.id, name: r.name, region: r.region, property: r.property, service: r.service,
  text: r.text, reply: r.reply || '', date: new Date(r.published || r.created).toISOString(),
  rating: r.rating || null, jobMonth: r.jobMonth || null, verified: !!r.verified, via: r.verified || null,
  photos: r.photosShown ? (r.photos || []).map((p, i) => ({ src: photoUrl(r.id, i), w: p.w, h: p.h })) : [],
});

export async function listPublished(n = 50) {
  const ids = await store.zrevrange('reviews:published', 0, Math.max(0, n - 1));
  const vals = await store.mget(ids.map(key));
  return vals.filter(Boolean).map(v => JSON.parse(v)).filter(r => r.status === 'published').map(publicView);
}

/** The average is shown only beside the number of reviews it comes from (ACCC). Older reviews without a rating don't count. */
export function summarise(list) {
  const rated = list.filter(r => r.rating >= 1 && r.rating <= 5);
  if (!rated.length) return { count: 0, average: null, reviews: list.length };
  const avg = rated.reduce((a, r) => a + r.rating, 0) / rated.length;
  return { count: rated.length, average: Math.round(avg * 10) / 10, reviews: list.length };
}

// ---- signed moderation links (HMAC-SHA256 over id.exp with REVIEW_SECRET)
function secret() {
  const s = process.env.REVIEW_SECRET;
  return s && s.length >= 16 ? s : null;
}
const hmac = (data, enc = 'hex') => crypto.createHmac('sha256', secret()).update(data).digest(enc);

export function sign(id, exp) {
  return secret() ? hmac(`${id}.${exp}`) : null;
}

export function verify(id, exp, sig) {
  const good = sign(id, exp);
  if (!good) return { ok: false, reason: 'Moderation links are not set up (REVIEW_SECRET is missing).' };
  if (!/^[0-9a-f]{64}$/.test(String(sig || ''))) return { ok: false, reason: 'This link is incomplete.' };
  if (!crypto.timingSafeEqual(Buffer.from(good, 'hex'), Buffer.from(String(sig), 'hex'))) return { ok: false, reason: 'This link is not valid.' };
  if (!(Number(exp) > Date.now())) return { ok: false, reason: 'This link has expired. Ask for a new one.' };
  return { ok: true };
}

export function moderationQuery(id) {
  const exp = Date.now() + LINK_DAYS * DAY;
  const sig = sign(id, exp);
  return sig ? `id=${id}&exp=${exp}&sig=${sig}` : null;
}

export function moderationLink(base, id) {
  const q = moderationQuery(id);
  return q ? `${base}/review/moderate?${q}` : null;
}

// ---- review links Fitz sends customers after a job (signed, single use, no record kept until one is used)
export const MONTH_RE = /^(20\d\d)-(0[1-9]|1[0-2])$/;

export function makeInvite({ name = '', service = '', month = '' } = {}, days = INVITE_DAYS) {
  if (!secret()) return null;
  const body = { j: crypto.randomBytes(5).toString('hex'), e: Date.now() + days * DAY };
  if (name) body.n = String(name).slice(0, 40);
  if (service) body.s = String(service).slice(0, 60);
  if (MONTH_RE.test(month)) body.m = month;
  const payload = Buffer.from(JSON.stringify(body)).toString('base64url');
  return `${payload}.${hmac('invite.' + payload, 'base64url').slice(0, 22)}`;
}

export function readInvite(token) {
  if (!secret()) return { ok: false, reason: 'Review links are not set up.' };
  const m = /^([A-Za-z0-9_-]{10,400})\.([A-Za-z0-9_-]{22})$/.exec(String(token || ''));
  if (!m) return { ok: false, reason: 'That review link is incomplete.' };
  const good = Buffer.from(hmac('invite.' + m[1], 'base64url').slice(0, 22));
  if (!crypto.timingSafeEqual(good, Buffer.from(m[2]))) return { ok: false, reason: "That review link isn't valid." };
  let b; try { b = JSON.parse(Buffer.from(m[1], 'base64url').toString()); } catch { return { ok: false, reason: "That review link isn't valid." }; }
  if (!(b.e > Date.now())) return { ok: false, reason: 'That review link has expired.' };
  return { ok: true, job: String(b.j), name: b.n || '', service: b.s || '', month: b.m || '' };
}

/** Marks an invite used. Returns false if another review already used it. */
export const claimInvite = (job, reviewId) => store.setnx(`invite:${job}`, reviewId);

export function inviteLink(base, info) {
  const t = makeInvite(info);
  return t ? `${base}/reviews?invite=${t}#write` : null;
}

/** Fitz's private key for the page that makes review links (/review/invite?key=…). Derived from REVIEW_SECRET. */
export const adminKey = () => (secret() ? hmac('invite-admin').slice(0, 32) : null);
export function checkAdminKey(k) {
  const good = adminKey();
  if (!good || !/^[0-9a-f]{32}$/.test(String(k || ''))) return false;
  return crypto.timingSafeEqual(Buffer.from(good), Buffer.from(String(k)));
}
export const inviteAdminLink = base => (adminKey() ? `${base}/review/invite?key=${adminKey()}` : null);

/** "2026-10" → "October 2026" */
export function monthLabel(m) {
  const x = MONTH_RE.exec(String(m || ''));
  if (!x) return m === 'earlier' ? 'More than two years ago' : '';
  return new Date(Date.UTC(+x[1], +x[2] - 1, 15)).toLocaleDateString('en-AU', { month: 'long', year: 'numeric', timeZone: 'UTC' });
}

export const stars = n => '★★★★★'.slice(0, n) + '☆☆☆☆☆'.slice(0, 5 - n);
