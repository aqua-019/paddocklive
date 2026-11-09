// Fitz's page for making review links (/review/invite?key=… rewrites here). The key comes from REVIEW_SECRET and is in
// every review and enquiry email he gets. Opening the page changes nothing; the Make button POSTs back here.
// A link is signed, single use and lasts 180 days. A review sent through it is marked as a verified job.
// Nothing is stored when a link is made, so making one and not sending it costs nothing.
import * as reviews from './_lib/reviews.js';
import { SERVICES } from './_lib/site-options.js';
import { page, esc, oneLine, parseBody, siteBase } from './_lib/page.js';

const thisMonth = () => {
  const d = new Date(new Date().toLocaleString('en-US', { timeZone: 'Australia/Melbourne' }));
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
};

function form(key, v = {}) {
  const opts = ['', ...SERVICES].map(s => `<option value="${esc(s)}"${s === v.service ? ' selected' : ''}>${s ? esc(s) : 'Choose… (optional)'}</option>`).join('');
  return `<form method="post" action="/review/invite"><input type="hidden" name="key" value="${esc(key)}">
  <label>Customer's first name and initial (optional)<input type="text" name="name" maxlength="40" autocomplete="off" value="${esc(v.name || '')}" placeholder="e.g. Sam T."></label>
  <label>Work you did (optional)<select name="service">${opts}</select></label>
  <label>Month of the job<input type="month" name="month" value="${esc(v.month || thisMonth())}" max="${thisMonth()}"></label>
  <div class="row"><button class="btn go" type="submit">Make a review link</button></div>
</form>`;
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const b = req.method === 'POST' ? (() => { try { return parseBody(req); } catch { return {}; } })() : (req.query || {});
  if (!reviews.checkAdminKey(b.key)) return res.status(403).send(page('Link not valid', `<h1 class="warn">Link not valid</h1><p>${reviews.adminKey() ? 'Use the review-link address from one of your review or enquiry emails.' : 'Review links are not set up (REVIEW_SECRET is missing).'}</p>`));
  const intro = `<h1>Make a review link</h1><p class="muted">Text or email it to a customer after a job. A review sent through it shows as a <b>verified job</b>. Each link works once and lasts ${reviews.INVITE_DAYS / 30} months. Keep this page's address to yourself.</p>`;

  if (req.method === 'GET') return res.status(200).send(page('Make a review link', intro + form(b.key)));
  if (req.method !== 'POST') { res.setHeader('Allow', 'GET, POST'); return res.status(405).send(page('Not allowed', '<h1>Not allowed</h1>')); }

  const v = { name: oneLine(b.name, 40), service: SERVICES.includes(b.service) ? b.service : '', month: reviews.MONTH_RE.test(b.month) ? b.month : '' };
  const link = reviews.inviteLink(siteBase(req), v);
  const first = v.name ? v.name.split(' ')[0] : '';
  const msg = `${first ? `Hi ${first}, ` : 'Hi, '}thanks for having me out${v.month ? ` in ${reviews.monthLabel(v.month).split(' ')[0]}` : ''}. If you've got a minute, I'd appreciate a review: ${link}\n\nFitz`;
  return res.status(200).send(page('Review link ready', `<h1>Review link ready</h1>
<p class="muted">For ${esc(v.name || 'a customer')}${v.service ? ` · ${esc(v.service)}` : ''}${v.month ? ` · ${esc(reviews.monthLabel(v.month))}` : ''}</p>
<p class="link" id="msg">${esc(msg).replace(/\n/g, '<br>')}</p>
<div class="row"><a class="btn go" href="sms:?&amp;body=${esc(encodeURIComponent(msg))}">Text it</a><a class="btn" href="mailto:?subject=${esc(encodeURIComponent('A quick review for Fitz Feral Hunters'))}&amp;body=${esc(encodeURIComponent(msg))}">Email it</a><button class="btn" type="button" id="copy" hidden>Copy message</button></div>
<p class="muted">Just the link: <span class="link" style="display:block;margin-top:6px">${esc(link)}</span></p>
<h2 style="font:700 1.2rem/1.1 'Barlow Condensed',sans-serif;text-transform:uppercase;margin:12px 0 0">Make another</h2>
${form(b.key)}
<script>(function(){var b=document.getElementById('copy');if(!navigator.clipboard)return;b.hidden=false;b.addEventListener('click',function(){navigator.clipboard.writeText(${JSON.stringify(msg).replace(/</g, '\\u003c')}).then(function(){b.textContent='Copied';});});})();</script>`));
}
