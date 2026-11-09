// Reviews endpoint.
//   GET  → { enabled, photos, summary:{count, average}, reviews[] } (cached at the edge for a minute)
//   POST → a new review (1–5 stars, 250+ characters, up to 3 photos), stored pending; Fitz is emailed a signed link
//          to publish or decline it. A review sent through Fitz's review link is marked as a verified job straight away;
//          any other review is matched to a job by Fitz before it can be published.
// Needs Redis (Upstash via the Vercel Marketplace). Without it GET says enabled:false and the site shows "Reviews open soon".
// Photos need a private Vercel Blob store (BLOB_READ_WRITE_TOKEN). Without it GET says photos:false and the picker stays hidden.
import * as reviews from './_lib/reviews.js';
import * as photos from './_lib/photos.js';
import { sendMail, rateLimit, verifyTurnstile, clientIp, config } from './_lib/services.js';
import { page, esc, clean, oneLine, parseBody, wantsJson, siteBase, OWNER_EMAIL } from './_lib/page.js';

const truthy = v => v === true || v === 'yes' || v === 'true' || v === 'on';

/** A job month: "YYYY-MM" from the last few years, not in the future, or "earlier". */
export function okMonth(m, now = new Date()) {
  if (m === 'earlier') return true;
  const x = reviews.MONTH_RE.exec(String(m || ''));
  if (!x) return false;
  const n = (+x[1]) * 12 + (+x[2] - 1), cur = now.getUTCFullYear() * 12 + now.getUTCMonth();
  return n <= cur + 1 && n >= cur - 60;      // +1: it's already next month in Melbourne before it is in UTC
}

export function validate(b) {
  const digits = String(b.phone || '').replace(/[^\d]/g, '');
  const r = {
    name: oneLine(b.name, 40), region: oneLine(b.region, 60), property: oneLine(b.property, 40),
    service: oneLine(b.service, 60), text: clean(b.text, reviews.MAX_TEXT + 50), email: oneLine(b.email, 200),
    phone: oneLine(b.phone, 30), rating: parseInt(b.rating, 10), jobMonth: oneLine(b.jobMonth, 10),
    consent: truthy(b.consent),
  };
  const errs = [];
  if (r.name.length < 2) errs.push('Enter your first name and last initial.');
  if (!(r.rating >= 1 && r.rating <= 5)) errs.push('Choose a star rating from 1 to 5.');
  if (!r.region) errs.push('Choose a region.');
  if (!r.property) errs.push('Choose a property type.');
  if (!r.service) errs.push('Choose the work Fitz did.');
  if (!okMonth(r.jobMonth)) errs.push('Choose the month of the job.');
  if (r.text.length < reviews.MIN_TEXT) errs.push(`Write at least ${reviews.MIN_TEXT} characters (you have ${r.text.length}).`);
  if (r.text.length > reviews.MAX_TEXT) errs.push(`Keep it under ${reviews.MAX_TEXT} characters.`);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(r.email)) errs.push('Enter a valid email address.');
  if (r.phone && (digits.length < 8 || digits.length > 15)) errs.push('Check the phone number, or leave it blank.');
  if (!r.consent) errs.push('Tick to agree to publishing.');
  return { r, errs };
}

/** Decode, check and strip each photo. Returns { list:[{buf,w,h}], err } */
export function readPhotos(raw) {
  const arr = Array.isArray(raw) ? raw : raw ? [raw] : [];
  if (!arr.length) return { list: [] };
  if (!photos.enabled()) return { err: "Photos can't be attached at the moment. Remove them and send the review again." };
  if (arr.length > photos.MAX_PHOTOS) return { err: `Attach up to ${photos.MAX_PHOTOS} photos.` };
  const list = [];
  for (let i = 0; i < arr.length; i++) {
    const buf = photos.decode(arr[i]);
    const s = buf && photos.stripJpeg(buf);
    if (!s) return { err: `Photo ${i + 1} couldn't be read. Use a JPEG or PNG photo, or leave it off.` };
    list.push({ buf: s.buf, w: s.width, h: s.height });
  }
  return { list };
}

export default async function handler(req, res) {
  if (req.method === 'GET') {
    if (!reviews.enabled()) { res.setHeader('Cache-Control', 'public, s-maxage=60'); return res.status(200).json({ enabled: false, photos: false, summary: { count: 0, average: null }, reviews: [] }); }
    const n = Math.min(50, Math.max(1, parseInt(req.query?.limit, 10) || 50));
    try {
      const all = await reviews.listPublished(500);
      res.setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=600');
      return res.status(200).json({ enabled: true, photos: photos.enabled(), summary: reviews.summarise(all), reviews: all.slice(0, n) });
    } catch (err) {
      console.error('[reviews] list failed', err);
      return res.status(200).json({ enabled: true, photos: photos.enabled(), summary: { count: 0, average: null }, reviews: [], error: 'unavailable' });
    }
  }
  if (req.method !== 'POST') { res.setHeader('Allow', 'GET, POST'); return res.status(405).json({ ok: false, error: 'GET or POST only' }); }

  const json = wantsJson(req);
  const reply = (status, obj, htmlBody) => json ? res.status(status).json(obj) : res.status(status).send(page(obj.ok ? 'Review sent' : 'Review not sent', htmlBody));
  const back = '<p class="muted"><a href="/reviews#write">Back to the review form</a></p>';
  const fail = (status, msg, extra = {}) => reply(status, { ok: false, error: msg, ...extra }, `<h1 class="warn">Not sent</h1><p>${esc(msg)}</p>${back}`);

  if (!reviews.enabled()) return fail(503, "Reviews aren't switched on yet.", { enabled: false });

  let body;
  try { body = parseBody(req); } catch { return fail(400, 'Could not read the review.'); }
  if (oneLine(body.company, 200)) return reply(200, { ok: true, pending: true }, '<h1>Thanks</h1>');

  const ip = clientIp(req);
  const bot = await verifyTurnstile(body['cf-turnstile-response'], ip).catch(() => ({ ok: false }));
  if (!bot.ok) return fail(400, "The bot check didn't pass. Refresh the page and try again.");
  const rl = await rateLimit(`rv:${ip}`, 3, 86400).catch(() => ({ ok: true }));
  if (!rl.ok) return fail(429, 'Too many reviews from this connection today.');

  const { r, errs } = validate(body);
  if (errs.length) return reply(400, { ok: false, error: errs.join(' '), errors: errs }, `<h1 class="warn">Fix the following</h1><ul>${errs.map(x => `<li>${esc(x)}</li>`).join('')}</ul>${back}`);

  const ph = readPhotos(body.photos);
  if (ph.err) return fail(400, ph.err);

  const id = reviews.newId();
  let saved = [];
  try {
    for (let i = 0; i < ph.list.length; i++) saved.push({ ref: await photos.save(id, i, ph.list[i].buf), w: ph.list[i].w, h: ph.list[i].h });
  } catch (err) {
    console.error('[reviews] photo upload failed', err.message);
    return fail(502, "The photos couldn't be uploaded. Try again, or send the review without them.");
  }

  // Fitz's review link: valid and unused → a verified job. Anything else still goes to Fitz, who checks it himself.
  let verified = null, inviteNote = '';
  if (body.invite) {
    const inv = reviews.readInvite(body.invite);
    if (!inv.ok) inviteNote = `${inv.reason} Fitz will check the job details himself.`;
    else if (!(await reviews.claimInvite(inv.job, id))) inviteNote = 'That review link has already been used. Fitz will check the job details himself.';
    else verified = 'link';
  }

  const rec = await reviews.create({ name: r.name, region: r.region, property: r.property, service: r.service, text: r.text, email: r.email,
    phone: r.phone, rating: r.rating, jobMonth: r.jobMonth, verified, photos: saved }, id);

  const base = siteBase(req);
  const link = reviews.moderationLink(base, rec.id);
  const admin = reviews.inviteAdminLink(base);
  const text = [
    `New review waiting for you on the website.`, '',
    `${reviews.stars(r.rating)}  ${r.rating} out of 5`,
    `${r.name} · ${r.property} · ${r.region}`,
    `Work: ${r.service} · Job: ${reviews.monthLabel(r.jobMonth)}`,
    verified ? 'Verified job: they used the review link you sent.' : `Not yet matched to a job: check the name, month and contact details against your records before publishing.${inviteNote ? ' (' + inviteNote + ')' : ''}`,
    `Email (private): ${r.email}${r.phone ? `\nPhone (private): ${r.phone}` : ''}`,
    saved.length ? `Photos: ${saved.length} (shown on the review page link below; you can publish without them)` : 'Photos: none', '',
    r.text, '',
    link ? `Publish or decline it here (link works for ${reviews.LINK_DAYS} days):\n${link}` : 'REVIEW_SECRET is not set, so no moderation link could be made.', '',
    'Every genuine review from a customer should go up, good or bad, whatever the star rating. Decline only spam, people you have not worked for, abuse, or anything naming a location or a person who has not agreed.',
    admin ? `\nMake a review link to text a customer after a job (bookmark this, keep it private):\n${admin}` : '',
  ].join('\n');
  if (config().mail) {
    await sendMail({ to: process.env.ENQUIRY_TO || OWNER_EMAIL, subject: `${process.env.VERCEL_ENV !== 'production' ? '[TEST] ' : ''}New ${r.rating}-star review from ${r.name}, ${r.region}`, text, replyTo: r.email, idempotencyKey: `review/${rec.id}`, tags: [{ name: 'type', value: 'review' }] })
      .catch(err => console.error('[reviews] notify failed', err.message));
  } else {
    console.log('[reviews] new pending review, not emailed (RESEND_API_KEY not set)\n' + text);
  }
  const how = verified ? 'It came through Fitz’s review link, so it’s marked as a verified job.' : 'Fitz matches it to the job, then publishes it.';
  return reply(200, { ok: true, pending: true, id: rec.id, verified: !!verified, photos: saved.length, note: inviteNote },
    `<h1>Thanks, it's with Fitz</h1><p>Every genuine review goes up, good or bad. ${esc(how)}</p>${inviteNote ? `<p class="muted">${esc(inviteNote)}</p>` : ''}<p><a href="/reviews">Back to reviews</a></p>`);
}
