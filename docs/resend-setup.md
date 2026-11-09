# Resend setup: switching on the website's email

**Status (9 Nov 2026): done.** Fitz's Resend account (fitzferalhunters1@gmail.com, Aqua invited as a team member), domain fitzferalhunters.com in Tokyo, records added to Vercel DNS, API key (sending access, restricted to the domain) in `RESEND_API_KEY`, plus `ENQUIRY_TO` and `ENQUIRY_FROM`. `AUTO_REPLY` is off until Fitz says yes. If the site's main domain moves to .com.au, add that domain in Resend the same way and change `ENQUIRY_FROM`.

The code is ready. Everything below is account setup, done once with Fitz. Until it's done, the contact form tells visitors their enquiry **hasn't** been sent and offers them a pre-filled email to Fitz instead, so nothing is lost and nobody is told "sent" when it wasn't.

**What switches on:**
- **Enquiries emailed to Fitz.** The customer is set as reply-to, so he just hits Reply.
- **New-review alerts**, with the Publish / Decline link.
- **Optional: an automatic "thanks" to the customer**, from enquiries@fitzferalhunters.com.

**Where things live:**
- **Domain:** fitzferalhunters.com, registered through Vercel and using Vercel DNS (team "aquatic"). DNS currently holds only Vercel's own records, so nothing will conflict.
- **Mail code:**
  - `api/_lib/services.js` (`sendMail`)
  - `api/enquiry.js`
  - `api/reviews.js`
- **Check after any change:** `https://fitzferalhunters.com/api/health` (booleans only, no secrets).

## Part 1 — the account and a key (10 minutes, needs Fitz)

1. **Create the Resend account** at resend.com, signing up **with fitzferalhunters1@gmail.com**. Resend's test sender only delivers to the account owner's address. With this signup, enquiries reach Fitz on day one, even before the domain is verified.
2. **Create an API key:** Resend → API Keys → Create.
   - Name: `fitzferalhunters website`
   - Permission: **Sending access**
   - Domain: "All domains" for now. Restrict it to fitzferalhunters.com after Part 2.
   - Copy the key now. Resend shows it only once.
3. **In Vercel:** paddocklive → Settings → Environment Variables. Add the following for Production and Preview:

   | Name | Value |
   |---|---|
   | `RESEND_API_KEY` | the key (starts `re_`) |
   | `ENQUIRY_TO` | `fitzferalhunters1@gmail.com` |

4. **Redeploy:** Deployments → latest → ⋯ → Redeploy. New variables only reach new deployments.
5. **Check:** open `/api/health`. It should show `"mail": { "configured": true, … }` and `"enquiries": "emailed to Fitz"`.
6. **Send a real enquiry** from `/contact` on your phone.
   - The popup now says **Sent to Fitz**, with a reference number.
   - Fitz should get "New job enquiry — …".
   - First time only: check his Spam folder and mark it **Not spam**.

## Part 2 — send from fitzferalhunters.com (15 minutes plus DNS time)

This makes mail come from `enquiries@fitzferalhunters.com` instead of Resend's test sender. That improves delivery and allows the customer auto-reply.

1. **Add the domain:** Resend → Domains → Add domain.
   - Name: `fitzferalhunters.com`
   - Region: any; Tokyo (ap-northeast-1) is nearest to Australia.
2. **Turn off open and click tracking** in the domain's settings. This is transactional mail to one inbox, and tracking links can trip spam filters.
3. **Copy Resend's DNS records into Vercel:** Vercel → Domains → fitzferalhunters.com → DNS Records → Add. Or let Claude add them through the Vercel connection. Since late 2026 Resend gives three records (sending runs on its "Forge" servers, so the old MX + SPF pair is now two CNAMEs):

   | Type | Name | Value |
   |---|---|---|
   | TXT | `resend._domainkey` | the DKIM key Resend shows (`p=MIGf…`, copy it with the copy button; the table shortens it) |
   | CNAME | `rsend` | `rsend-apne1.forge.rmta.net` (the `apne1` part is the Tokyo region) |
   | CNAME | `send` | `send.forge.rmta.net` |

   Copy the exact values from Resend: the DKIM key is specific to the account. Leave Vercel's own ALIAS and CAA records alone, and don't use Resend's "Auto configure" / "Go to Vercel" button unless the Resend account is linked to the same Vercel team that owns the domain.
4. **Recommended:** add a DMARC record too.

   | Type | Name | Value |
   |---|---|---|
   | TXT | `_dmarc` | `v=DMARC1; p=none;` |

5. **Verify:** Resend → the domain → Verify. It usually goes green within minutes on Vercel DNS.
6. **Back in Vercel env vars**, add these, then redeploy:

   | Name | Value |
   |---|---|
   | `ENQUIRY_FROM` | `Fitz Feral Hunters <enquiries@fitzferalhunters.com>` |
   | `AUTO_REPLY` | `1` (only if Fitz wants customers to get an automatic thanks) |

7. **Restrict the API key to the domain.** Resend → API Keys → the key → Domain: fitzferalhunters.com.
8. **Check again:**
   - `/api/health` should show `"sender": "custom (fitzferalhunters.com)"`.
   - Send another enquiry, this time with your own email in the form, so the auto-reply comes to you.

There's no inbox at enquiries@fitzferalhunters.com and none is needed. Fitz's notification has the customer as reply-to, and the customer's auto-reply has Fitz's Gmail as reply-to. Every reply lands in his Gmail.

## Testing from a computer (optional)

```
vercel env pull .env.local      # pulls the keys into a gitignored file
node scripts/mail-test.mjs      # sends one "[TEST] … email is working" message to ENQUIRY_TO
```

The script prints Resend's answer. If it fails, it says why in plain words: wrong key, test-sender limit, domain not verified, or badly formatted ENQUIRY_FROM.

## Behaviour already built in

- **No key set:**
  - Enquiries are logged in the function logs and kept 90 days in Redis.
  - The visitor sees **Not sent yet** with a pre-filled email to Fitz.
- **Key set but Resend refuses the message:**
  - The visitor sees **That didn't go through**, with the same email and call fallback.
  - The function log says why in plain words, e.g. "the ENQUIRY_FROM domain is not verified in Resend yet".
- **Duplicate protection:** each email carries a Resend idempotency key (`enquiry/<ref>`, `review/<id>`). A retry within 24 hours never sends twice.
- **Subject lines:** preview deployments add `[TEST]`. Production subjects are clean ("New job enquiry — Deer — Neerim South").
- **Spam protection:** the honeypot field and a 5-per-10-minutes rate limit are on now. The Cloudflare Turnstile bot check is optional, and switches on with `TURNSTILE_SECRET_KEY` plus `turnstile_site_key` in `content/site.json`.
