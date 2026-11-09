// Prints Fitz's private address for making review links (/review/invite?key=…), from REVIEW_SECRET in .env.local.
// The same address is at the bottom of every review email and every enquiry email carries a ready-made link for that customer.
//   node scripts/review-invite-link.mjs [https://fitzferalhunters.com]
import fs from 'node:fs';
for (const line of (fs.existsSync('.env.local') ? fs.readFileSync('.env.local', 'utf8') : '').split('\n')) {
  const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim());
  if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^"(.*)"$/, '$1');
}
const { inviteAdminLink } = await import('../api/_lib/reviews.js');
const base = (process.argv[2] || process.env.SITE_URL || 'https://fitzferalhunters.com').replace(/\/$/, '');
const link = inviteAdminLink(base);
if (!link) { console.error('REVIEW_SECRET is missing or shorter than 16 characters. Run `vercel env pull .env.local` first.'); process.exit(1); }
console.log(link);
