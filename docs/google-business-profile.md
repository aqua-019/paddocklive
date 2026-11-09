# Google Business Profile: setup kit for Fitz Feral Hunters

Fitz asked (3 Nov 2026) for a Google Business Profile set up as a **service-area business with the address hidden**. He doesn't have one yet.

The profile has to be created and verified from a Google account Fitz controls. Customers can't see a profile until Google has verified it, and the verification step asks for the business owner. Everything below is ready to paste in.

Google's own steps: [Sign up for a Business Profile](https://support.google.com/business/answer/10514137).

## Steps

1. **Account.** Fitz signs in at business.google.com/create with his Google account. fitzferalhunters1@gmail.com is fine.
2. **Business name.** `Fitz Feral Hunters` (exactly as on the card; no keywords added, which Google penalises).
3. **Category.** Start typing "pest" and choose **Pest control service**. If Google offers a closer match for wildlife or animal control, add it as an additional category later.
4. **"Do you want to add a location customers can visit?"** Choose **No**. With no public storefront, the address is not shown.
5. **Service areas.** Google allows up to 20. Start with Gippsland, then wider Victoria (his priority):
   - Warragul, Drouin, Neerim South, Korumburra, Leongatha, Wonthaggi, Moe, Morwell, Traralgon, Sale, Bairnsdale, Yarram, Foster, Pakenham
   - then larger areas if Google offers them, e.g. Gippsland or Victoria
6. **Contact.**
   - Phone: `0499 866 580`
   - Website: the live site URL (the domain once it's set up; until then, leave blank or add later)
7. **Verify.** Choose **Verify now** and follow Google's prompts (often a short video showing the business: vehicle, equipment, tools).
8. **Hours.** Ask Fitz. "Open 24 hours" isn't recommended unless he really answers the phone at night; consider stating calls and texts are welcome any time in the description instead.
9. **Photos.** Upload from `public/media/photo/` (all metadata already stripped):
   - the ute and tripod rig (cover)
   - Fitz on the sticks
   - the thermal scope view
   - the logo: `public/brand/logo-lockup-plate.jpg`

## Description (678 of 750 characters)

```
Licensed, insured feral animal and vermin control for farms, private landholders and land managers. Based in Warragul, working across Gippsland first, then all of Victoria. Deer control, kangaroo control under a valid ATCW, feral pigs, foxes, rabbits and wild dogs, with thermal night work and DJI Matrice 4T thermal drone scouting. Farm security: after-hours monitoring and rapid response for properties with ongoing stock or asset risk. Every job is planned and agreed before the first night, carried out humanely to AHCPMG304 and the Victorian codes of practice, and insured with Elders Insurance for $20 million public liability. Certificates available on request.
```

## Services to list in the profile

Deer control · Kangaroo control · Feral pig control · Fox control · Rabbit control · Wild dog control · Night work and thermal · Thermal drone scouting · Farm security

## After it's verified: connect it to the site

1. In the profile, choose **Ask for reviews** and copy the short review link.
2. Put it in `content/site.json` → `"google_review_url": "<the link>"`.
3. `python3 src/build.py`, commit, push.

A **Review us on Google** button then appears next to the review form on `/reviews`. Add the profile URL to `sameAs` in the site's schema at the same time (`jsonld()` in `src/build.py`).

## Rules that keep the profile safe

- One profile only. Never a second one for the same business in the same area.
- No keywords stuffed into the name.
- Don't offer anything in exchange for reviews. Google's policy forbids it, and so does the ACCC's guidance (see the review policy on the site).
