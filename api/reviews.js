// Reviews endpoint.
//   GET  → published reviews { enabled, reviews[] } (cached at the edge for a minute)
//   POST → a new review, stored pending; Fitz is emailed a signed link to publish or decline it.
// Needs Redis (Upstash via the Vercel Marketplace). Without it GET says enabled:false and the site shows "Reviews open soon".
import * as reviews from './_lib/reviews.js';
import { sendMail, rateLimit, verifyTurnstile, clientIp, config } from './_lib/services.js';
import { page, esc, clean, oneLine, parseBody, wantsJson, siteBase, OWNER_EMAIL } from './_lib/page.js';

export function validate(b) {
  const r = {
    name: oneLine(b.name, 40), region: oneLine(b.region, 60), property: oneLine(b.property, 40),
    service: oneLine(b.service, 60), text: clean(b.text, 800), email: oneLine(b.email, 200),
    consent: b.consent === true || b.consent === 'yes' || b.consent === 'true' || b.consent === 'on',
  };
  const errs = [];
  if (r.name.length < 2) errs.push('Enter your first name and last initial.');
  if (!r.region) errs.push('Choose a region.');
  if (!r.property) errs.push('Choose a property type.');
  if (!r.service) errs.push('Choose the work Fitz did.');
  if (r.text.length < 20) errs.push('Write at least 20 characters.');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(r.email)) errs.push('Enter a valid email address.');
  if (!r.consent) errs.push('Tick to agree to publishing.');
  return { r, errs };
}

export default async function handler(req, res) {
  if (req.method === 'GET') {
    if (!reviews.enabled()) { res.setHeader('Cache-Control', 'public, s-maxage=60'); return res.status(200).json({ enabled: false, reviews: [] }); }
    const n = Math.min(50, Math.max(1, parseInt(req.query?.limit, 10) || 50));
    try {
      const list = await reviews.listPublished(n);
      res.setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=600');
      return res.status(200).json({ enabled: true, reviews: list });
    } catch (err) {
      console.error('[reviews] list failed', err);
      return res.status(200).json({ enabled: true, reviews: [], error: 'unavailable' });
    }
  }
  if (req.method !== 'POST') { res.setHeader('Allow', 'GET, POST'); return res.status(405).json({ ok: false, error: 'GET or POST only' }); }

  const json = wantsJson(req);
  const reply = (status, obj, htmlBody) => json ? res.status(status).json(obj) : res.status(status).send(page(obj.ok ? 'Review sent' : 'Review not sent', htmlBody));
  const back = '<p class="muted"><a href="/reviews#write">Back to the review form</a></p>';

  if (!reviews.enabled()) return reply(503, { ok: false, enabled: false, error: "Reviews aren't switched on yet." }, `<h1 class="warn">Not yet</h1><p>Reviews aren't switched on yet.</p>${back}`);

  let body;
  try { body = parseBody(req); } catch { return reply(400, { ok: false, error: 'Could not read the review.' }, `<h1>Not sent</h1>${back}`); }
  if (oneLine(body.company, 200)) return reply(200, { ok: true, pending: true }, '<h1>Thanks</h1>');

  const ip = clientIp(req);
  const bot = await verifyTurnstile(body['cf-turnstile-response'], ip).catch(() => ({ ok: false }));
  if (!bot.ok) return reply(400, { ok: false, error: "The bot check didn't pass. Refresh the page and try again." }, `<h1>Not sent</h1><p>The bot check didn't pass.</p>${back}`);
  const rl = await rateLimit(`rv:${ip}`, 3, 86400).catch(() => ({ ok: true }));
  if (!rl.ok) return reply(429, { ok: false, error: 'Too many reviews from this connection today.' }, `<h1>Not sent</h1><p>Too many reviews from this connection today.</p>${back}`);

  const { r, errs } = validate(body);
  if (errs.length) return reply(400, { ok: false, error: errs.join(' ') }, `<h1>Fix the following</h1><ul>${errs.map(x => `<li>${esc(x)}</li>`).join('')}</ul>${back}`);

  const rec = await reviews.create({ name: r.name, region: r.region, property: r.property, service: r.service, text: r.text, email: r.email });
  const link = reviews.moderationLink(siteBase(req), rec.id);
  const text = [`New review waiting for you on the website.`, '', `${r.name} · ${r.property} · ${r.region}`, `Work: ${r.service}`, `Email (private): ${r.email}`, '', r.text, '',
    link ? `Publish or decline it here (link works for ${reviews.LINK_DAYS} days):\n${link}` : 'REVIEW_SECRET is not set, so no moderation link could be made.', '',
    'Every genuine review from a customer should go up, good or bad. Decline only spam, people you have not worked for, abuse, or anything naming a location or a person who has not agreed.'].join('\n');
  if (config().mail) {
    await sendMail({ to: process.env.ENQUIRY_TO || OWNER_EMAIL, subject: `${process.env.VERCEL_ENV !== 'production' ? '[TEST] ' : ''}New review from ${r.name}, ${r.region}`, text, replyTo: r.email, idempotencyKey: `review/${rec.id}`, tags: [{ name: 'type', value: 'review' }] })
      .catch(err => console.error('[reviews] notify failed', err.message));
  } else {
    console.log('[reviews] new pending review, not emailed (RESEND_API_KEY not set)\n' + text);
  }
  return reply(200, { ok: true, pending: true, id: rec.id }, `<h1>Thanks, it's with Fitz</h1><p>Every genuine review goes up, good or bad. Fitz checks that you're a customer, then publishes it.</p><p><a href="/reviews">Back to reviews</a></p>`);
}
