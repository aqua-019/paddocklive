// Enquiry endpoint (Vercel Node function). The contact form posts here two ways:
//   JSON from the enhanced form → JSON { ok, delivered, ref, received } — the page shows a receipt dialog
//   form-encoded (no JavaScript) → a plain HTML page
// Order: honeypot → bot check (if TURNSTILE_SECRET_KEY) → rate limit (if Redis) → validate → log (if Redis) → email Fitz.
// Without RESEND_API_KEY nothing is emailed: the response says delivered:false and the page offers the visitor
// a pre-filled email to Fitz instead, so no visitor is ever told "sent" when it wasn't.
import { sendMail, logEnquiry, rateLimit, verifyTurnstile, clientIp, config } from './_lib/services.js';
import { page, esc, clean, oneLine, parseBody, wantsJson, PHONE, PHONE_E164, OWNER_EMAIL } from './_lib/page.js';

const TO = () => process.env.ENQUIRY_TO || OWNER_EMAIL;
const isTest = () => process.env.VERCEL_ENV !== 'production';

export function validate(b) {
  const help = (Array.isArray(b.help) ? b.help : b.help ? [b.help] : []).map(x => oneLine(x, 40)).filter(Boolean).slice(0, 8);
  const e = {
    name: oneLine(b.name, 120), phone: oneLine(b.phone, 40), email: oneLine(b.email, 200),
    location: oneLine(b.location, 120), help, message: clean(b.message, 2000),
  };
  const fields = {};
  if (!e.name) fields.name = 'Enter your name so Fitz knows who to ask for.';
  if (e.phone.replace(/\D/g, '').length < 8) fields.phone = 'Enter a phone number with at least eight digits.';
  if (e.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.email)) fields.email = "That email address doesn't look right. Check it or leave it blank.";
  if (!e.location) fields.location = 'Tell Fitz the town or locality so he can plan the trip.';
  if (!help.length) fields.help = 'Tick at least one thing you need help with. "Not sure yet" is fine.';
  return { e, fields };
}

const ref = () => 'FFH-' + Date.now().toString(36).slice(-5).toUpperCase() + Math.random().toString(36).slice(2, 4).toUpperCase();

function melbourneTime(d = new Date()) {
  try { return d.toLocaleString('en-AU', { timeZone: 'Australia/Melbourne', weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }); }
  catch { return d.toISOString(); }
}

export function ownerEmail(e, r) {
  const subject = `${isTest() ? '[TEST] ' : ''}New job enquiry — ${e.help.join(', ')} — ${e.location}`;
  const when = melbourneTime();
  const telHref = 'tel:' + e.phone.replace(/[^\d+]/g, '');
  const text = [
    `New enquiry from the website (${r}, ${when})`, '',
    `Name: ${e.name}`, `Phone: ${e.phone}`, `Email: ${e.email || '(not given)'}`, `Location: ${e.location}`,
    `Help with: ${e.help.join(', ')}`, '', e.message || '(no message)', '',
    e.email ? 'Reply to this email to answer them directly.' : 'No email given: ring them back.',
  ].join('\n');
  const row = (k, v) => `<tr><td style="padding:6px 14px 6px 0;color:#4a5550;font:600 12px/1.4 Arial,sans-serif;text-transform:uppercase;letter-spacing:.06em;vertical-align:top">${k}</td><td style="padding:6px 0;font:16px/1.45 Arial,sans-serif;color:#1b2622">${v}</td></tr>`;
  const html = `<div style="max-width:560px;font-family:Arial,sans-serif;color:#1b2622">
<p style="font:700 20px/1.2 Arial,sans-serif;margin:0 0 4px">New job enquiry</p>
<p style="margin:0 0 16px;color:#4a5550;font-size:14px">${esc(r)} · ${esc(when)}</p>
<table role="presentation" style="border-collapse:collapse">
${row('Name', esc(e.name))}
${row('Phone', `<a href="${esc(telHref)}" style="color:#1b2622;font-weight:700">${esc(e.phone)}</a>`)}
${row('Email', e.email ? `<a href="mailto:${esc(e.email)}" style="color:#1b2622">${esc(e.email)}</a>` : '(not given)')}
${row('Location', esc(e.location))}
${row('Help with', esc(e.help.join(', ')))}
${row('Message', esc(e.message || '(no message)').replace(/\n/g, '<br>'))}
</table>
<p style="margin:18px 0 0;font-size:14px;color:#4a5550">${e.email ? 'Hit Reply to answer them directly.' : 'No email given: tap the number to ring them back.'}</p></div>`;
  return { subject, text, html };
}

function customerReply(e) {
  const first = e.name.split(' ')[0];
  return {
    subject: 'Thanks for your enquiry — Fitz Feral Hunters',
    text: `Hi ${first},\n\nThanks for getting in touch. I've got your enquiry about ${e.help.join(', ').toLowerCase()} near ${e.location} and I'll get back to you within a day, usually by phone on ${e.phone}.\n\nIf it's urgent, ring me on ${PHONE}.\n\nFitz\nFitz Feral Hunters · Protecting Victoria's Farms`,
  };
}

function mailtoFor(e) {
  const body = `Hi Fitz,\n\nName: ${e.name}\nPhone: ${e.phone}\nEmail: ${e.email}\nLocation: ${e.location}\nHelp with: ${e.help.join(', ')}\n\n${e.message}`.slice(0, 1600);
  return `mailto:${OWNER_EMAIL}?subject=${encodeURIComponent(`Enquiry: ${e.help.join(', ')} near ${e.location}`)}&body=${encodeURIComponent(body)}`;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false, error: 'POST only' }); }
  const json = wantsJson(req);
  const reply = (status, obj, htmlBody) => json ? res.status(status).json(obj) : res.status(status).send(page(obj.ok ? 'Enquiry received' : 'Not sent', htmlBody));
  const back = `<p class="muted"><a href="/contact#enquiry">Back to the form</a> · or call <a href="tel:${PHONE_E164}">${PHONE}</a></p>`;

  let body;
  try { body = parseBody(req); } catch { return reply(400, { ok: false, error: 'Could not read the enquiry.' }, `<h1>Not sent</h1><p>Could not read the enquiry.</p>${back}`); }

  const r = ref();
  if (oneLine(body.company, 200)) { // honeypot filled: look successful, send nothing
    return reply(200, { ok: true, delivered: true, ref: r }, '<h1>Enquiry received</h1><p>Thanks.</p>');
  }

  const ip = clientIp(req);
  const bot = await verifyTurnstile(body['cf-turnstile-response'], ip).catch(() => ({ ok: false }));
  if (!bot.ok) return reply(400, { ok: false, error: "The bot check didn't pass. Refresh the page and try again." }, `<h1>Not sent</h1><p>The bot check didn't pass. Refresh the page and try again.</p>${back}`);

  const rl = await rateLimit(`enq:${ip}`, 5, 600).catch(() => ({ ok: true }));
  if (!rl.ok) return reply(429, { ok: false, error: 'Too many enquiries from this connection in the last few minutes.' }, `<h1>Not sent</h1><p>Too many enquiries from this connection in the last few minutes.</p>${back}`);

  const { e, fields } = validate(body);
  if (Object.keys(fields).length) {
    return reply(400, { ok: false, error: Object.values(fields).join(' '), fields },
      `<h1>Fix the following</h1><ul>${Object.values(fields).map(x => `<li>${esc(x)}</li>`).join('')}</ul>${back}`);
  }

  await logEnquiry({ ...e, ref: r, at: new Date().toISOString() }).catch(err => console.error('[enquiry] log failed', err));

  const received = { name: e.name, phone: e.phone, email: e.email, location: e.location, help: e.help, message: e.message };
  if (!config().mail) {
    console.log(`[enquiry] ${r} received, not emailed (RESEND_API_KEY not set)\n` + ownerEmail(e, r).text);
    return reply(200, { ok: true, delivered: false, ref: r, received, reason: 'mail-not-configured' },
      `<h1 class="warn">One more step</h1><p>The website's email isn't switched on yet, so this hasn't reached Fitz.</p><p><a class="btn go" href="${esc(mailtoFor(e))}">Email it to Fitz</a> <a class="btn" href="tel:${PHONE_E164}">Call ${PHONE}</a></p>${back}`);
  }

  try {
    const m = ownerEmail(e, r);
    await sendMail({ to: TO(), subject: m.subject, text: m.text, html: m.html, replyTo: e.email || undefined });
  } catch (err) {
    console.error('[enquiry] send failed', r, err);
    return reply(502, { ok: false, delivered: false, ref: r, received, error: "The website couldn't send it." },
      `<h1 class="warn">Not sent</h1><p>The website couldn't send it. Nothing reached Fitz.</p><p><a class="btn go" href="${esc(mailtoFor(e))}">Email it to Fitz</a> <a class="btn" href="tel:${PHONE_E164}">Call ${PHONE}</a></p>${back}`);
  }

  if (config().autoReply && process.env.ENQUIRY_FROM && e.email) {
    const c = customerReply(e);
    await sendMail({ to: e.email, subject: c.subject, text: c.text, replyTo: TO() }).catch(err => console.error('[enquiry] auto-reply failed', err));
  }

  return reply(200, { ok: true, delivered: true, ref: r, received },
    `<h1>Sent to Fitz</h1><p>Thanks, ${esc(e.name.split(' ')[0])}. Fitz has your enquiry and will ring ${esc(e.phone)}, usually within two business days.</p><p class="muted">Reference ${esc(r)}. If it's urgent, call <a href="tel:${PHONE_E164}">${PHONE}</a>.</p><p><a href="/">Back to the site</a></p>`);
}
