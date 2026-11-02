// The page Fitz lands on from the "new review" email (/review/moderate rewrites here).
// Opening it changes nothing — Gmail and Outlook open links automatically to scan them — it only shows the review
// and two buttons. The buttons POST to /api/review-action, which checks the signature again.
import * as reviews from './_lib/reviews.js';
import { page, esc } from './_lib/page.js';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Referrer-Policy', 'no-referrer');
  if (req.method !== 'GET') { res.setHeader('Allow', 'GET'); return res.status(405).send(page('Not allowed', '<h1>Not allowed</h1>')); }
  const { id, exp, sig } = req.query || {};
  const v = reviews.verify(id, exp, sig);
  if (!v.ok) return res.status(403).send(page('Link not valid', `<h1 class="warn">Link not valid</h1><p>${esc(v.reason)}</p>`));
  if (!reviews.enabled()) return res.status(503).send(page('Not available', '<h1 class="warn">Reviews are not switched on</h1>'));
  const r = await reviews.get(id);
  if (!r) return res.status(404).send(page('Not found', '<h1 class="warn">That review no longer exists</h1>'));

  const status = { pending: 'Waiting for you', published: 'Published', declined: `Declined (${r.reason || 'no reason'})` }[r.status] || r.status;
  const hidden = `<input type="hidden" name="id" value="${esc(id)}"><input type="hidden" name="exp" value="${esc(exp)}"><input type="hidden" name="sig" value="${esc(sig)}">`;
  return res.status(200).send(page('Review from ' + r.name, `
<h1>Review from ${esc(r.name)}</h1>
<p class="muted">Status: <b>${esc(status)}</b> · sent ${esc(new Date(r.created).toLocaleDateString('en-AU', { timeZone: 'Australia/Melbourne', day: 'numeric', month: 'short', year: 'numeric' }))}</p>
<dl><dt>Name</dt><dd>${esc(r.name)}</dd><dt>Property</dt><dd>${esc(r.property)}</dd><dt>Region</dt><dd>${esc(r.region)}</dd><dt>Work</dt><dd>${esc(r.service)}</dd><dt>Email</dt><dd>${esc(r.email)} (private)</dd><dt>Review</dt><dd>${esc(r.text)}</dd></dl>
<p class="muted">Every genuine review from a customer goes up, good or bad. Decline only if it's spam, from someone you haven't worked for, abusive, or names a location or a person who hasn't agreed. The words can't be edited.</p>
<form method="post" action="/api/review-action">${hidden}<input type="hidden" name="action" value="publish">
  <label>Short public reply (optional)<textarea name="reply" maxlength="400" rows="3">${esc(r.reply || '')}</textarea></label>
  <div class="row"><button class="btn go" type="submit">${r.status === 'published' ? 'Update reply' : 'Publish'}</button></div>
</form>
<form method="post" action="/api/review-action">${hidden}<input type="hidden" name="action" value="decline">
  <label>Reason for declining<select name="reason" required><option value="">Choose…</option><option>Spam</option><option>Not a customer</option><option>Abusive</option><option>Names a location or a person</option></select></label>
  <div class="row"><button class="btn no" type="submit">Decline</button></div>
</form>`));
}
