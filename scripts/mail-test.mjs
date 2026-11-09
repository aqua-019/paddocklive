#!/usr/bin/env node
// Sends one test email through Resend with the same settings the site uses, and explains any error.
//   vercel env pull .env.local      (or put RESEND_API_KEY, ENQUIRY_TO, ENQUIRY_FROM in .env.local yourself)
//   node scripts/mail-test.mjs
// Nothing here is committed: .env.local is gitignored.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const envFile = path.join(ROOT, '.env.local');
if (fs.existsSync(envFile)) for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*"?(.*?)"?\s*$/); if (m && !(m[1] in process.env)) process.env[m[1]] = m[2];
}
const { sendMail, fromAddress, fromCheck } = await import('../api/_lib/services.js');

if (!process.env.RESEND_API_KEY) {
  console.error('RESEND_API_KEY is not set. Run `vercel env pull .env.local` or add it to .env.local.');
  process.exit(1);
}
const to = process.env.ENQUIRY_TO || 'fitzferalhunters1@gmail.com';
const fc = fromCheck();
console.log(`From: ${fromAddress()}${fc.note ? `  (${fc.note})` : ''}`);
console.log(`To:   ${to}`);
try {
  const r = await sendMail({
    to, subject: '[TEST] Fitz Feral Hunters website email is working',
    text: `This is a test from the website's mail setup, sent ${new Date().toISOString()}.\n\nIf you can read this, enquiries from the contact form will reach this inbox.\nIf it landed in Spam, mark it "Not spam" so the real ones don't.`,
    tags: [{ name: 'type', value: 'test' }],
  });
  console.log(`Sent. Resend id ${r.id}. Check the inbox (and Spam) for "[TEST] Fitz Feral Hunters website email is working".`);
} catch (err) {
  console.error(`Not sent. ${err.message}`);
  process.exit(1);
}
