// GET /api/health — which services are switched on for this deployment. Booleans and domains only:
// no keys, tokens or addresses are ever returned. Open it after adding keys in Vercel and redeploying.
import { config, fromCheck } from './_lib/services.js';
import * as store from './_lib/store.js';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'GET') { res.setHeader('Allow', 'GET'); return res.status(405).json({ ok: false }); }
  const c = config();
  const from = fromCheck();
  let storeOk = null;
  if (store.kind() === 'redis') {
    try { await store.get('health:ping'); storeOk = true; } catch { storeOk = false; }
  }
  const mail = {
    configured: c.mail,
    sender: from.set ? (from.valid ? `custom (${from.domain})` : 'custom, badly formatted') : 'Resend test sender (delivers only to the Resend account owner)',
    recipientSet: !!process.env.ENQUIRY_TO,
    autoReply: c.autoReply && from.set && from.valid,
    ...(from.note ? { note: from.note } : {}),
  };
  const ready = c.mail && (!from.set || from.valid);
  return res.status(200).json({
    ok: true,
    environment: process.env.VERCEL_ENV || 'local',
    region: process.env.VERCEL_REGION || null,
    mail,
    enquiries: ready ? 'emailed to Fitz' : 'not emailed yet: visitors are offered a pre-filled email instead',
    store: { configured: store.kind() === 'redis', reachable: storeOk },
    reviews: { enabled: store.kind() !== null, moderationLinks: !!(process.env.REVIEW_SECRET && process.env.REVIEW_SECRET.length >= 16), reviewLinks: !!(process.env.REVIEW_SECRET && process.env.REVIEW_SECRET.length >= 16), photos: !!(process.env.BLOB_STORE_ID || process.env.BLOB_READ_WRITE_TOKEN) },
    botCheck: c.turnstile,
  });
}
