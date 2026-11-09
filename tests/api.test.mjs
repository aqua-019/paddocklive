// node --test tests/   — the functions, with fetch stubbed (no network, no keys needed).
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';

process.env.FFH_MEMORY_STORE = '1';
delete process.env.VERCEL;
process.env.REVIEW_SECRET = 'test-secret-0123456789abcdef';

const calls = [];
let resendStatus = 200;
let resendBody = '';
globalThis.fetch = async (url, opts = {}) => {
  let body = null; try { body = typeof opts.body === 'string' ? JSON.parse(opts.body) : opts.body ? String(opts.body) : null; } catch { body = String(opts.body); }
  calls.push({ url: String(url), body, headers: opts.headers || {} });
  if (String(url).includes('api.resend.com')) return new Response(resendStatus === 200 ? JSON.stringify({ id: 'em_1' }) : (resendBody || JSON.stringify({ message: 'error' })), { status: resendStatus });
  if (String(url).includes('turnstile')) return new Response(JSON.stringify({ success: String(opts.body).includes('response=good') }));
  return new Response('{}');
};

const { default: enquiry } = await import('../api/enquiry.js');
const { default: reviewsApi } = await import('../api/reviews.js');
const { default: moderate } = await import('../api/review-moderate.js');
const { default: action } = await import('../api/review-action.js');
const { default: health } = await import('../api/health.js');
const { default: photoApi } = await import('../api/review-photo.js');
const { default: inviteApi } = await import('../api/review-invite.js');
const photos = await import('../api/_lib/photos.js');
const services = await import('../api/_lib/services.js');
const reviews = await import('../api/_lib/reviews.js');
const store = await import('../api/_lib/store.js');

function call(handler, { method = 'POST', body = {}, json = true, query = {}, headers = {} } = {}) {
  return new Promise(resolve => {
    const req = { method, body, query, headers: { 'content-type': json ? 'application/json' : 'application/x-www-form-urlencoded', accept: json ? 'application/json' : 'text/html', host: 'example.test', 'x-forwarded-for': '203.0.113.9', ...headers }, socket: {} };
    const res = { statusCode: 200, headers: {}, setHeader(k, v) { this.headers[k.toLowerCase()] = v; }, getHeader(k) { return this.headers[k.toLowerCase()]; },
      status(c) { this.statusCode = c; return this; }, json(o) { resolve({ status: this.statusCode, json: o, headers: this.headers }); return this; }, send(s) { resolve({ status: this.statusCode, html: s, headers: this.headers }); return this; } };
    handler(req, res);
  });
}

const good = { name: 'Sam Taylor', phone: '0412 345 678', email: 'sam@example.com', location: 'Neerim South', help: ['Deer', 'Foxes'], message: 'Deer in the lucerne most nights.' };

beforeEach(() => { calls.length = 0; resendStatus = 200; resendBody = ''; delete process.env.ENQUIRY_FROM; delete process.env.RESEND_API_KEY; delete process.env.TURNSTILE_SECRET_KEY; delete process.env.VERCEL_ENV; store._resetMemory(); photos._resetMemory(); });

test('enquiry without a mail key: ok, not delivered, nothing sent, receipt echoed', async () => {
  const r = await call(enquiry, { body: good });
  assert.equal(r.status, 200); assert.equal(r.json.ok, true); assert.equal(r.json.delivered, false);
  assert.match(r.json.ref, /^FFH-/); assert.equal(r.json.received.location, 'Neerim South');
  assert.equal(calls.filter(c => c.url.includes('resend')).length, 0);
});

test('enquiry with a mail key: emails Fitz with reply-to the customer and a [TEST] subject off production', async () => {
  process.env.RESEND_API_KEY = 're_test';
  const r = await call(enquiry, { body: good });
  assert.equal(r.json.delivered, true);
  const m = calls.find(c => c.url.includes('resend')).body;
  assert.deepEqual(m.to, ['fitzferalhunters1@gmail.com']);
  assert.equal(m.reply_to, 'sam@example.com');
  assert.match(m.subject, /^\[TEST\] New job enquiry — Deer, Foxes — Neerim South$/);
  assert.match(m.html, /tel:0412345678/);
});

test('production subject has no [TEST] prefix', async () => {
  process.env.RESEND_API_KEY = 're_test'; process.env.VERCEL_ENV = 'production';
  await call(enquiry, { body: good });
  assert.match(calls.find(c => c.url.includes('resend')).body.subject, /^New job enquiry/);
});

test('form-encoded (no JavaScript) path returns an HTML page', async () => {
  process.env.RESEND_API_KEY = 're_test';
  const r = await call(enquiry, { body: { ...good, help: 'Deer' }, json: false });
  assert.equal(r.status, 200); assert.match(r.html, /Sent to Fitz/);
});

test('honeypot: looks successful, sends nothing', async () => {
  process.env.RESEND_API_KEY = 're_test';
  const r = await call(enquiry, { body: { ...good, company: 'spam inc' } });
  assert.equal(r.json.ok, true); assert.equal(calls.length, 0);
});

test('validation: per-field errors', async () => {
  const r = await call(enquiry, { body: { ...good, email: 'nope', help: [] } });
  assert.equal(r.status, 400); assert.ok(r.json.fields.email); assert.ok(r.json.fields.help);
});

test('mail failure: 502, not delivered, receipt still echoed for the email fallback', async () => {
  process.env.RESEND_API_KEY = 're_test'; resendStatus = 500;
  const r = await call(enquiry, { body: good });
  assert.equal(r.status, 502); assert.equal(r.json.delivered, false); assert.equal(r.json.received.name, 'Sam Taylor');
});

test('turnstile: rejected without a good token when configured', async () => {
  process.env.TURNSTILE_SECRET_KEY = 'ts';
  assert.equal((await call(enquiry, { body: good })).status, 400);
  assert.equal((await call(enquiry, { body: { ...good, 'cf-turnstile-response': 'good' } })).status, 200);
});

const now = new Date();
const thisMonth = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, '0')}`;
const TEXT = 'Turned up when he said he would, walked the boundary with me first and worked out where the deer were coming in. ' +
  'Two nights on the thermal and the damage to the lucerne stopped. Clean, quiet, no fuss with the neighbours, and he rang the next morning to say how it went.';
const review = { name: 'Sam T.', region: 'Gippsland', property: 'Beef', service: 'Deer control', rating: 5, jobMonth: thisMonth, text: TEXT, email: 'sam@example.com', consent: true };
const modSig = id => { const exp = Date.now() + 86400000; return { id, exp: String(exp), sig: reviews.sign(id, exp) }; };

/** A JPEG-shaped file: JFIF, an EXIF block carrying a fake GPS marker, a 640×480 frame header and some scan data. */
function fakeJpeg() {
  const seg = (m, body) => { const b = Buffer.from(body); const h = Buffer.from([0xff, m, 0, 0]); h.writeUInt16BE(b.length + 2, 2); return Buffer.concat([h, b]); };
  const sof = Buffer.from([8, 0, 0, 0, 0, 3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1]); sof.writeUInt16BE(480, 1); sof.writeUInt16BE(640, 3);
  return Buffer.concat([Buffer.from([0xff, 0xd8]), seg(0xe0, 'JFIF\0\x01\x01\0\0\x01\0\x01\0\0'), seg(0xe1, 'Exif\0\0GPS-SECRET -38.16,145.93'), seg(0xfe, 'shot on my phone'),
    seg(0xc0, sof), seg(0xda, Buffer.from([3, 1, 0, 2, 0x11, 3, 0x11, 0, 0x3f, 0])), Buffer.alloc(900, 0x2a), Buffer.from([0xff, 0xd9])]);
}
const dataUrl = buf => 'data:image/jpeg;base64,' + buf.toString('base64');

test('review: submit → pending, not public', async () => {
  const r = await call(reviewsApi, { body: review });
  assert.equal(r.status, 200); assert.equal(r.json.pending, true); assert.equal(r.json.verified, false);
  const list = await call(reviewsApi, { method: 'GET' });
  assert.equal(list.json.enabled, true); assert.equal(list.json.reviews.length, 0); assert.equal(list.json.summary.count, 0);
});

test('review: needs a 1–5 rating, 250+ characters, a job month and consent', async () => {
  const r = await call(reviewsApi, { body: { ...review, consent: false, text: 'short', rating: 0, jobMonth: '' } });
  assert.equal(r.status, 400);
  assert.match(r.json.error, /star rating/); assert.match(r.json.error, /at least 250 characters \(you have 5\)/); assert.match(r.json.error, /month of the job/); assert.match(r.json.error, /publishing/);
  assert.equal((await call(reviewsApi, { body: { ...review, rating: 6 } })).status, 400);
  assert.equal((await call(reviewsApi, { body: { ...review, text: 'x'.repeat(249) } })).status, 400);
  assert.equal((await call(reviewsApi, { body: { ...review, text: 'x'.repeat(250) } })).status, 200);
  assert.equal((await call(reviewsApi, { body: { ...review, jobMonth: '2099-01' } })).status, 400);
  assert.equal((await call(reviewsApi, { body: { ...review, jobMonth: 'earlier' } })).status, 200);
  assert.equal((await call(reviewsApi, { body: { ...review, phone: '12' } })).status, 400);
});

test('signing: valid, tampered, expired', () => {
  const exp = Date.now() + 60000, sig = reviews.sign('abcdefabcdef', exp);
  assert.equal(reviews.verify('abcdefabcdef', exp, sig).ok, true);
  assert.equal(reviews.verify('abcdefabcdef', exp + 1, sig).ok, false);
  const old = Date.now() - 1; assert.equal(reviews.verify('abcdefabcdef', old, reviews.sign('abcdefabcdef', old)).ok, false);
});

test('moderation: GET changes nothing; publishing needs Fitz to match the job; bad signature is 403', async () => {
  const sub = await call(reviewsApi, { body: review });
  const m = modSig(sub.json.id), { id } = m;
  const view = await call(moderate, { method: 'GET', query: m });
  assert.equal(view.status, 200); assert.match(view.html, /Publish/); assert.match(view.html, /5 out of 5/); assert.match(view.html, /Not matched to a job yet/);
  assert.equal((await reviews.get(id)).status, 'pending');
  assert.equal((await call(action, { method: 'GET' })).status, 405);
  assert.equal((await call(action, { json: false, body: { ...m, sig: '0'.repeat(64), action: 'publish' } })).status, 403);
  const unchecked = await call(action, { json: false, body: { ...m, action: 'publish', reply: 'Thanks Sam.' } });
  assert.equal(unchecked.status, 400); assert.equal((await reviews.get(id)).status, 'pending');
  const pub = await call(action, { json: false, body: { ...m, action: 'publish', reply: 'Thanks Sam.', checked: 'yes' } });
  assert.equal(pub.status, 200);
  const list = await call(reviewsApi, { method: 'GET' });
  const [shown] = list.json.reviews;
  assert.equal(list.json.reviews.length, 1); assert.equal(shown.reply, 'Thanks Sam.'); assert.equal(shown.rating, 5);
  assert.equal(shown.verified, true); assert.equal(shown.via, 'fitz'); assert.equal(shown.jobMonth, thisMonth);
  assert.equal(shown.email, undefined); assert.equal(shown.phone, undefined);
  assert.deepEqual(list.json.summary, { count: 1, average: 5, reviews: 1 });
  const dec = await call(action, { json: false, body: { ...m, action: 'decline', reason: 'Spam' } });
  assert.equal(dec.status, 200);
  assert.equal((await call(reviewsApi, { method: 'GET' })).json.reviews.length, 0);
});

test('summary: the average comes with the number of reviews, low ratings included', async () => {
  for (const rating of [5, 4, 1]) {
    const { json } = await call(reviewsApi, { body: { ...review, rating } });
    await reviews.publish(json.id, { checked: true });
  }
  const { json } = await call(reviewsApi, { method: 'GET' });
  assert.deepEqual(json.summary, { count: 3, average: 3.3, reviews: 3 });
  assert.deepEqual(json.reviews.map(r => r.rating).sort(), [1, 4, 5]);
});

test('review link: verified job, single use, tamper-proof', async () => {
  const token = reviews.makeInvite({ name: 'Sam T.', service: 'Deer control', month: thisMonth });
  assert.equal(reviews.readInvite(token).ok, true); assert.equal(reviews.readInvite(token).name, 'Sam T.');
  const first = await call(reviewsApi, { body: { ...review, invite: token } });
  assert.equal(first.json.verified, true);
  assert.equal((await reviews.get(first.json.id)).verified, 'link');
  const again = await call(reviewsApi, { body: { ...review, invite: token } });
  assert.equal(again.status, 200); assert.equal(again.json.verified, false); assert.match(again.json.note, /already been used/);
  const [payload, sig] = token.split('.');
  const forged = Buffer.from(JSON.stringify({ ...JSON.parse(Buffer.from(payload, 'base64url')), j: 'ffffffffff' })).toString('base64url') + '.' + sig;
  assert.equal(reviews.readInvite(forged).ok, false);
  const bad = await call(reviewsApi, { body: { ...review, invite: forged } });
  assert.equal(bad.json.verified, false);
  assert.equal(reviews.readInvite(reviews.makeInvite({}, -1)).ok, false);
  // a link-verified review publishes without the extra tick
  const m = modSig(first.json.id);
  assert.equal((await call(action, { json: false, body: { ...m, action: 'publish' } })).status, 200);
  assert.equal((await call(reviewsApi, { method: 'GET' })).json.reviews[0].via, 'link');
});

test('review-link page: needs the key, makes a working link, changes nothing on GET', async () => {
  assert.equal((await call(inviteApi, { method: 'GET', query: {} })).status, 403);
  assert.equal((await call(inviteApi, { method: 'GET', query: { key: 'f'.repeat(32) } })).status, 403);
  const key = reviews.adminKey();
  const page = await call(inviteApi, { method: 'GET', query: { key } });
  assert.equal(page.status, 200); assert.match(page.html, /Make a review link/);
  const made = await call(inviteApi, { json: false, body: { key, name: 'Jo B.', service: 'Foxes', month: thisMonth } });
  assert.equal(made.status, 200);
  const token = /invite=([A-Za-z0-9_.-]+)/.exec(made.html)[1];
  const inv = reviews.readInvite(token);
  assert.equal(inv.ok, true); assert.equal(inv.service, 'Foxes'); assert.equal(inv.month, thisMonth);
  assert.match(made.html, /sms:/);
});

test('photos: metadata stripped, size read, private until published with photos', async () => {
  const s = photos.stripJpeg(fakeJpeg());
  assert.equal(s.width, 640); assert.equal(s.height, 480);
  assert.equal(s.buf.includes('GPS-SECRET'), false); assert.equal(s.buf.includes('shot on my phone'), false); assert.equal(s.buf.includes('JFIF'), true);
  assert.equal(photos.decode('data:image/png;base64,AAAA'), null);

  const sub = await call(reviewsApi, { body: { ...review, photos: [dataUrl(fakeJpeg()), dataUrl(fakeJpeg())] } });
  assert.equal(sub.status, 200); assert.equal(sub.json.photos, 2);
  const id = sub.json.id, m = modSig(id);
  assert.equal((await call(photoApi, { method: 'GET', query: { r: id, i: '0' } })).status, 404);           // pending: not public
  const priv = await call(photoApi, { method: 'GET', query: { r: id, i: '0', exp: m.exp, sig: m.sig } });
  assert.equal(priv.status, 200); assert.equal(priv.headers['cache-control'], 'private, no-store');
  assert.equal(Buffer.from(priv.html).includes('GPS-SECRET'), false);
  assert.match((await call(moderate, { method: 'GET', query: m })).html, /Show the photos too/);

  await call(action, { json: false, body: { ...m, action: 'publish', checked: 'yes' } });               // photos box unticked
  assert.deepEqual((await call(reviewsApi, { method: 'GET' })).json.reviews[0].photos, []);
  assert.equal((await call(photoApi, { method: 'GET', query: { r: id, i: '0' } })).status, 404);
  await call(action, { json: false, body: { ...m, action: 'publish', checked: 'yes', withPhotos: 'yes' } });
  const shown = (await call(reviewsApi, { method: 'GET' })).json.reviews[0].photos;
  assert.equal(shown.length, 2); assert.equal(shown[0].w, 640);
  const pub = await call(photoApi, { method: 'GET', query: { r: id, i: '1' } });
  assert.equal(pub.status, 200); assert.match(pub.headers['cache-control'], /^public/);
  assert.equal((await call(photoApi, { method: 'GET', query: { r: id, i: '2' } })).status, 404);
});

test('photos: more than 3, or not a JPEG, is refused with a plain reason', async () => {
  const four = await call(reviewsApi, { body: { ...review, photos: Array(4).fill(dataUrl(fakeJpeg())) } });
  assert.equal(four.status, 400); assert.match(four.json.error, /up to 3/);
  const junk = await call(reviewsApi, { body: { ...review, photos: ['data:image/jpeg;base64,' + Buffer.alloc(800, 1).toString('base64')] } });
  assert.equal(junk.status, 400); assert.match(junk.json.error, /Photo 1 couldn't be read/);
});

test('enquiry email carries a review link for that customer', async () => {
  process.env.RESEND_API_KEY = 're_test';
  await call(enquiry, { body: { ...good, help: ['Deer control', 'Foxes'] } });
  const m = calls.find(c => c.url.includes('resend')).body;
  const token = /\/reviews\?invite=([A-Za-z0-9_.-]+)#write/.exec(m.text)[1];
  const inv = reviews.readInvite(token);
  assert.equal(inv.ok, true); assert.equal(inv.name, 'Sam T.'); assert.equal(inv.service, 'Deer control');
  assert.match(m.html, /review link/);
});

test('reviews off without a store', async () => {
  process.env.FFH_MEMORY_STORE = '0';
  const r = await call(reviewsApi, { method: 'GET' });
  assert.equal(r.json.enabled, false);
  assert.equal((await call(reviewsApi, { body: review })).status, 503);
  process.env.FFH_MEMORY_STORE = '1';
});

test('mail: each enquiry email carries an idempotency key and a type tag', async () => {
  process.env.RESEND_API_KEY = 're_test';
  const r = await call(enquiry, { body: good });
  const c = calls.find(x => x.url.includes('resend'));
  assert.equal(c.headers['Idempotency-Key'], `enquiry/${r.json.ref}`);
  assert.deepEqual(c.body.tags, [{ name: 'type', value: 'enquiry' }]);
  assert.match(c.body.from, /onboarding@resend\.dev/);
});

test('mail: ENQUIRY_FROM is used once set; auto-reply goes out only with AUTO_REPLY=1', async () => {
  process.env.RESEND_API_KEY = 're_test'; process.env.ENQUIRY_FROM = 'Fitz Feral Hunters <enquiries@fitzferalhunters.com>'; process.env.AUTO_REPLY = '1';
  await call(enquiry, { body: good });
  const sent = calls.filter(x => x.url.includes('resend'));
  assert.equal(sent.length, 2);
  assert.equal(sent[0].body.from, 'Fitz Feral Hunters <enquiries@fitzferalhunters.com>');
  assert.deepEqual(sent[1].body.to, ['sam@example.com']);
  delete process.env.AUTO_REPLY;
});

test('mail: a Resend refusal is explained in plain words in the error', async () => {
  process.env.RESEND_API_KEY = 're_test'; resendStatus = 403;
  resendBody = JSON.stringify({ message: 'You can only send testing emails to your own email address' });
  await assert.rejects(services.sendMail({ to: 'x@example.com', subject: 's', text: 't' }), /test sender only delivers to the Resend account owner/);
  assert.match(services.resendHint(403, 'The fitzferalhunters.com domain is not verified'), /not verified/);
  assert.match(services.resendHint(401, ''), /API key/);
});

test('health: reports what is switched on, never a secret', async () => {
  process.env.RESEND_API_KEY = 're_secret_value'; process.env.ENQUIRY_FROM = 'Fitz Feral Hunters <enquiries@fitzferalhunters.com>';
  const r = await call(health, { method: 'GET' });
  assert.equal(r.status, 200); assert.equal(r.json.mail.configured, true);
  assert.match(r.json.mail.sender, /fitzferalhunters\.com/);
  assert.equal(JSON.stringify(r.json).includes('re_secret_value'), false);
  assert.equal(r.headers['cache-control'], 'no-store');
  process.env.ENQUIRY_FROM = 'enquiries at fitz';
  assert.match((await call(health, { method: 'GET' })).json.mail.sender, /badly formatted/);
  delete process.env.RESEND_API_KEY;
  assert.match((await call(health, { method: 'GET' })).json.enquiries, /not emailed yet/);
});
