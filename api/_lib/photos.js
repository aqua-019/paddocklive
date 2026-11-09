// Review photos. Stored in a PRIVATE Vercel Blob store (paddocklive-review-photos, syd1), so nothing a reviewer uploads
// is reachable until Fitz publishes the review; /api/review-photo serves them. In local dev and tests
// (FFH_MEMORY_STORE=1, not on Vercel) they're kept in memory.
// Every photo is re-checked and stripped of metadata here (EXIF, GPS, comments), whatever the browser sent.

import { put, get } from '@vercel/blob';

const mem = globalThis.__ffhPhotos || (globalThis.__ffhPhotos = new Map());
export const MAX_PHOTOS = 3;
export const MAX_BYTES = 1_000_000;      // the browser shrinks photos to about 1600px first; 3 of these stay under Vercel's 4.5 MB request limit

/** On Vercel the SDK signs in with the project's OIDC token + BLOB_STORE_ID first, then falls back to BLOB_READ_WRITE_TOKEN. */
export function kind() {
  if (process.env.BLOB_STORE_ID || process.env.BLOB_READ_WRITE_TOKEN) return 'blob';
  if (!process.env.VERCEL && process.env.FFH_MEMORY_STORE === '1') return 'memory';
  return null;
}
export const enabled = () => !!kind();

/** A JPEG data URL → Buffer, or null if it isn't a JPEG of a sensible size. */
export function decode(dataUrl) {
  const m = /^data:image\/jpeg;base64,([A-Za-z0-9+/=]+)$/.exec(String(dataUrl || ''));
  if (!m) return null;
  const buf = Buffer.from(m[1], 'base64');
  if (buf.length < 600 || buf.length > MAX_BYTES) return null;
  if (buf[0] !== 0xff || buf[1] !== 0xd8 || buf[2] !== 0xff) return null;
  return buf;
}

/**
 * Rebuild a JPEG without its metadata segments (APP1–APP15: EXIF, GPS, XMP, ICC…; COM: comments) and read
 * its size from the frame header. Returns { buf, width, height } or null if the file isn't a well-formed JPEG.
 */
export function stripJpeg(src) {
  if (src[0] !== 0xff || src[1] !== 0xd8) return null;
  const out = [Buffer.from([0xff, 0xd8])];
  let i = 2, width = 0, height = 0;
  while (i + 4 <= src.length) {
    if (src[i] !== 0xff) return null;
    const marker = src[i + 1];
    if (marker === 0xd8 || (marker >= 0xd0 && marker <= 0xd7) || marker === 0x01) { i += 2; continue; }
    if (marker === 0xd9) { out.push(Buffer.from([0xff, 0xd9])); break; }
    const len = src.readUInt16BE(i + 2);
    if (len < 2 || i + 2 + len > src.length) return null;
    const seg = src.subarray(i, i + 2 + len);
    if (marker === 0xda) { out.push(src.subarray(i)); break; }          // start of scan: the image data follows, keep the rest as is
    if ([0xc0, 0xc1, 0xc2, 0xc3].includes(marker)) { height = src.readUInt16BE(i + 5); width = src.readUInt16BE(i + 7); }
    const metadata = (marker >= 0xe1 && marker <= 0xef) || marker === 0xfe;
    if (!metadata) out.push(seg);
    i += 2 + len;
  }
  if (!width || !height) return null;
  return { buf: Buffer.concat(out), width, height };
}

export async function save(reviewId, index, buf) {
  if (kind() === 'blob') {
    const r = await put(`reviews/${reviewId}/${index}.jpg`, buf, { access: 'private', addRandomSuffix: true, contentType: 'image/jpeg', cacheControlMaxAge: 31536000 });
    return r.pathname;
  }
  const ref = `mem:${reviewId}/${index}`;
  mem.set(ref, buf);
  return ref;
}

/** Returns a Buffer, or null if the photo is gone. */
export async function load(ref) {
  if (String(ref).startsWith('mem:')) return mem.get(ref) || null;
  if (kind() !== 'blob') return null;
  const r = await get(ref, { access: 'private' }).catch(() => null);
  if (!r || r.statusCode !== 200 || !r.stream) return null;
  return Buffer.from(await new Response(r.stream).arrayBuffer());
}

export function _resetMemory() { mem.clear(); }
