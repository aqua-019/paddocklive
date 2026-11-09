// Publish or decline a review. POST only, from the buttons on the moderation page; the signature and expiry are checked again here.
import * as reviews from './_lib/reviews.js';
import { page, esc, oneLine, clean, parseBody } from './_lib/page.js';

const REASONS = ['Spam', 'Not a customer', 'Abusive', 'Names a location or a person'];
const yes = v => v === 'yes' || v === 'on' || v === 'true' || v === true;

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Referrer-Policy', 'no-referrer');
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).send(page('Use the buttons', '<h1 class="warn">Use the buttons</h1><p>Open the link from the email and use the Publish or Decline button.</p>')); }
  let b; try { b = parseBody(req); } catch { b = {}; }
  const v = reviews.verify(b.id, b.exp, b.sig);
  if (!v.ok) return res.status(403).send(page('Link not valid', `<h1 class="warn">Link not valid</h1><p>${esc(v.reason)}</p>`));
  if (!reviews.enabled()) return res.status(503).send(page('Not available', '<h1 class="warn">Reviews are not switched on</h1>'));
  const backLink = `<p class="muted"><a href="/review/moderate?id=${esc(b.id)}&amp;exp=${esc(b.exp)}&amp;sig=${esc(b.sig)}">Back to this review</a> · <a href="/reviews">See the reviews page</a></p>`;

  if (b.action === 'publish') {
    const r = await reviews.publish(b.id, { reply: oneLine(clean(b.reply, 400), 400), withPhotos: yes(b.withPhotos), checked: yes(b.checked) });
    if (!r) return res.status(404).send(page('Not found', '<h1 class="warn">That review no longer exists</h1>'));
    if (r.needsCheck) return res.status(400).send(page('Match it to a job first', `<h1 class="warn">Match it to a job first</h1><p>Tick the box to confirm you've matched ${esc(r.name)}'s review to a job you did. If you can't, decline it as "Not a customer".</p>${backLink}`));
    const pics = r.photos?.length ? (r.photosShown ? ` with ${r.photos.length === 1 ? 'its photo' : `its ${r.photos.length} photos`}` : ', without the photos') : '';
    return res.status(200).send(page('Published', `<h1>Published</h1><p>${esc(r.name)}'s review is on the site${pics}. It can take a minute to appear.</p>${backLink}`));
  }
  if (b.action === 'decline') {
    const reason = oneLine(b.reason, 60);
    if (!REASONS.includes(reason)) return res.status(400).send(page('Choose a reason', `<h1 class="warn">Choose a reason</h1><p>Pick why it's being declined.</p>${backLink}`));
    const r = await reviews.decline(b.id, reason);
    if (!r) return res.status(404).send(page('Not found', '<h1 class="warn">That review no longer exists</h1>'));
    return res.status(200).send(page('Declined', `<h1 class="warn">Declined</h1><p>${esc(r.name)}'s review won't be shown. Reason recorded: ${esc(reason)}.</p>${backLink}`));
  }
  return res.status(400).send(page('Unknown action', `<h1 class="warn">Unknown action</h1>${backLink}`));
}
