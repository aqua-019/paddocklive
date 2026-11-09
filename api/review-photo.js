// Serves a review photo from the private store.
//   /api/review-photo?r=<id>&i=<n>                      → only once the review is published with its photos
//   /api/review-photo?r=<id>&i=<n>&exp=…&sig=…          → Fitz's moderation view (the same signature as his email link)
// Anything else is a 404, so a pending or declined review's photos can't be reached.
import * as reviews from './_lib/reviews.js';
import * as photos from './_lib/photos.js';

export default async function handler(req, res) {
  if (req.method !== 'GET' && req.method !== 'HEAD') { res.setHeader('Allow', 'GET'); return res.status(405).end(); }
  const { r: id, i, exp, sig } = req.query || {};
  const n = parseInt(i, 10);
  const notFound = () => { res.setHeader('Cache-Control', 'no-store'); return res.status(404).send('Not found'); };
  if (!reviews.enabled() || !(n >= 0 && n < photos.MAX_PHOTOS)) return notFound();
  const rec = await reviews.get(id);
  const ref = rec?.photos?.[n]?.ref;
  if (!ref) return notFound();

  const moderator = sig ? reviews.verify(id, exp, sig).ok : false;
  const isPublic = rec.status === 'published' && rec.photosShown;
  if (!isPublic && !moderator) return notFound();

  const buf = await photos.load(ref).catch(() => null);
  if (!buf) return notFound();
  res.setHeader('Content-Type', 'image/jpeg');
  res.setHeader('Content-Length', buf.length);
  res.setHeader('Cache-Control', isPublic && !moderator ? 'public, max-age=3600, s-maxage=86400' : 'private, no-store');
  res.setHeader('Content-Disposition', 'inline');
  if (req.method === 'HEAD') return res.status(200).end();
  return res.status(200).send(buf);
}
