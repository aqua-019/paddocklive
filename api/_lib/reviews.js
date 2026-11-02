// Reviews: stored pending, published or declined by Fitz from a signed link, never edited, never deleted.
import crypto from 'node:crypto';
import * as store from './store.js';

export const enabled = () => !!store.kind();
const key = id => `review:${id}`;
const DAY = 86400000;
export const LINK_DAYS = 30;

export async function create(r) {
  const rec = { ...r, id: crypto.randomBytes(6).toString('hex'), status: 'pending', created: Date.now() };
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

export async function publish(id, reply = '') {
  const r = await get(id); if (!r) return null;
  r.status = 'published'; r.published = r.published || Date.now(); r.reply = reply; delete r.reason;
  await save(r);
  await store.zrem('reviews:pending', id);
  await store.zadd('reviews:published', r.published, id);
  return r;
}

export async function decline(id, reason) {
  const r = await get(id); if (!r) return null;
  r.status = 'declined'; r.reason = reason; r.declined = Date.now();
  await save(r);
  await store.zrem('reviews:pending', id);
  await store.zrem('reviews:published', id);
  return r;
}

export const publicView = r => ({
  id: r.id, name: r.name, region: r.region, property: r.property, service: r.service,
  text: r.text, reply: r.reply || '', date: new Date(r.published || r.created).toISOString(),
});

export async function listPublished(n = 50) {
  const ids = await store.zrevrange('reviews:published', 0, Math.max(0, n - 1));
  const vals = await store.mget(ids.map(key));
  return vals.filter(Boolean).map(v => JSON.parse(v)).filter(r => r.status === 'published').map(publicView);
}

// ---- signed moderation links (HMAC-SHA256 over id.exp with REVIEW_SECRET)
export function sign(id, exp) {
  const s = process.env.REVIEW_SECRET;
  if (!s || s.length < 16) return null;
  return crypto.createHmac('sha256', s).update(`${id}.${exp}`).digest('hex');
}

export function verify(id, exp, sig) {
  const good = sign(id, exp);
  if (!good) return { ok: false, reason: 'Moderation links are not set up (REVIEW_SECRET is missing).' };
  if (!/^[0-9a-f]{64}$/.test(String(sig || ''))) return { ok: false, reason: 'This link is incomplete.' };
  if (!crypto.timingSafeEqual(Buffer.from(good, 'hex'), Buffer.from(String(sig), 'hex'))) return { ok: false, reason: 'This link is not valid.' };
  if (!(Number(exp) > Date.now())) return { ok: false, reason: 'This link has expired. Ask for a new one.' };
  return { ok: true };
}

export function moderationLink(base, id) {
  const exp = Date.now() + LINK_DAYS * DAY;
  const sig = sign(id, exp);
  return sig ? `${base}/review/moderate?id=${id}&exp=${exp}&sig=${sig}` : null;
}
