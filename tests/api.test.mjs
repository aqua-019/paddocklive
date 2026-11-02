// node --test tests/   — the functions, with fetch stubbed (no network, no keys needed).
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';

process.env.FFH_MEMORY_STORE = '1';
delete process.env.VERCEL;
process.env.REVIEW_SECRET = 'test-secret-0123456789abcdef';

const calls = [];
let resendStatus = 200;
globalThis.fetch = async (url, opts = {}) => {
  let body = null; try { body = typeof opts.body === 'string' ? JSON.parse(opts.body) : opts.body ? String(opts.body) : null; } catch { body = String(opts.body); }
  calls.push({ url: String(url), body });
  if (String(url).includes('api.resend.com')) return new Response(JSON.stringify({ id: 'em_1' }), { status: resendStatus });
  if (String(url).includes('turnstile')) return new Response(JSON.stringify({ success: String(opts.body).includes('response=good') }));
  return new Response('{}');
};

const { default: enquiry } = await import('../api/enquiry.js');
const { default: reviewsApi } = await import('../api/reviews.js');
const { default: moderate } = await import('../api/review-moderate.js');
const { default: action } = await import('../api/review-action.js');
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

beforeEach(() => { calls.length = 0; resendStatus = 200; delete process.env.RESEND_API_KEY; delete process.env.TURNSTILE_SECRET_KEY; delete process.env.VERCEL_ENV; store._resetMemory(); });

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

const review = { name: 'Sam T.', region: 'West Gippsland', property: 'Beef', service: 'Deer control', text: 'Turned up when he said, sorted the deer in two nights.', email: 'sam@example.com', consent: true };

test('review: submit → pending, not public', async () => {
  const r = await call(reviewsApi, { body: review });
  assert.equal(r.status, 200); assert.equal(r.json.pending, true);
  const list = await call(reviewsApi, { method: 'GET' });
  assert.equal(list.json.enabled, true); assert.equal(list.json.reviews.length, 0);
});

test('review: needs consent and enough text', async () => {
  const r = await call(reviewsApi, { body: { ...review, consent: false, text: 'short' } });
  assert.equal(r.status, 400);
});

test('signing: valid, tampered, expired', () => {
  const exp = Date.now() + 60000, sig = reviews.sign('abcdefabcdef', exp);
  assert.equal(reviews.verify('abcdefabcdef', exp, sig).ok, true);
  assert.equal(reviews.verify('abcdefabcdef', exp + 1, sig).ok, false);
  const old = Date.now() - 1; assert.equal(reviews.verify('abcdefabcdef', old, reviews.sign('abcdefabcdef', old)).ok, false);
});

test('moderation: GET changes nothing; POST publish puts it on the site; bad signature is 403', async () => {
  const sub = await call(reviewsApi, { body: review });
  const id = sub.json.id, exp = Date.now() + 86400000, sig = reviews.sign(id, exp);
  const view = await call(moderate, { method: 'GET', query: { id, exp: String(exp), sig } });
  assert.equal(view.status, 200); assert.match(view.html, /Publish/);
  assert.equal((await reviews.get(id)).status, 'pending');
  assert.equal((await call(action, { method: 'GET' })).status, 405);
  assert.equal((await call(action, { json: false, body: { id, exp: String(exp), sig: '0'.repeat(64), action: 'publish' } })).status, 403);
  const pub = await call(action, { json: false, body: { id, exp: String(exp), sig, action: 'publish', reply: 'Thanks Sam.' } });
  assert.equal(pub.status, 200);
  const list = await call(reviewsApi, { method: 'GET' });
  assert.equal(list.json.reviews.length, 1); assert.equal(list.json.reviews[0].reply, 'Thanks Sam.');
  assert.equal(list.json.reviews[0].email, undefined);
  const dec = await call(action, { json: false, body: { id, exp: String(exp), sig, action: 'decline', reason: 'Spam' } });
  assert.equal(dec.status, 200);
  assert.equal((await call(reviewsApi, { method: 'GET' })).json.reviews.length, 0);
});

test('reviews off without a store', async () => {
  process.env.FFH_MEMORY_STORE = '0';
  const r = await call(reviewsApi, { method: 'GET' });
  assert.equal(r.json.enabled, false);
  assert.equal((await call(reviewsApi, { body: review })).status, 503);
  process.env.FFH_MEMORY_STORE = '1';
});
