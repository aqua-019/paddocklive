# Citation manifest for the Fitz Feral Hunters mockups.
# Every component key maps to the catalogue records it honours. D-ids go into data-per;
# LAW/PAIR/PAL/LENS/NOPAIR/TP/DY/MK ids go into the spec sheet. build.py validates all of them
# against D700.md / names.txt before writing a byte of HTML. Only records the build actually
# implements are listed — a record cited here and not honoured is a FOLD-able failure.

SHARED = {
  # document / meta / delivery
  "doc": ["D1749","D6548","D2519","D4311","D3135","D2114","D0228","D2113","D2041","D1214",
          "D2044","D1278","D2647","D1268","D0054","D2037","D0081","D1251","D0080","D0083",
          "D2045","D2046","D2744","D2450","D1737","D0447","D4987","D1784","D2121","D5641",
          "D0745","D4657","D1201","D1248","D1296","D1336","D2213","D0580","D0594","D0597",
          "LAW-05","LAW-14","LENS-05","LENS-06","LENS-16","LENS-19","LENS-20"],
  "tokens": ["D0158","D3009","D0153","D3432","D1011","D3006","D4198","D0400","D0162","D0161",
             "D0166","D0033","D2018","D0168","D2019","D0192","D0191","D0197","D0157","D1243",
             "D1038","D2510","D1150","D3373","D1227","D2504",
             "LAW-06","LAW-83","PALRULE-02","PALRULE-03","PALRULE-05","PAIR-958","PAIR-1075"],
  "focus": ["D3007","D0644","D2147","D0581","D0582","LAW-32","PAIR-173","PAIR-199"],
  "type": ["D0106","D0108","D2668","D0101","D1323","D3193","D3458","D0144","D0076","D0149",
           "D0063","D0142","D3017","D0141","D0140","D2069","D1333","D2052","D1350",
           "LAW-07","LAW-37","PAIR-266","PAIR-357","NOPAIR-04","LENS-09"],
  "motion": ["D3051","D3468","D3052","D3171","D0651","D0652","D2335","D0673","D2248","D2327",
             "D0693","D0643","D2343","D0488","D2249","D3453","D0594","D2301","D2342","D0694",
             "D4656","D4980","D0453","D3425","D2227","D0451","D0665","D0666","D2347","D2035",
             "D1222","D1225","D0668",
             "LAW-02","LAW-03","LAW-12","LAW-16","LAW-17","LAW-27","LAW-28","LAW-29","LAW-31",
             "LAW-41","LAW-44","LAW-113","MK-01","DY01",
             "PAIR-25","PAIR-168","PAIR-191","PAIR-796","NOPAIR-02","NOPAIR-59","NOPAIR-01"],
  # chrome
  "varbar": ["D4980","D3245","D4657","D0264","D2126"],
  "skip": ["D0228","D2113","D0583","D2114"],
  "header": ["D0201","D2108","D2050","D4262","PAIR-388","PAIR-509","NOPAIR-85","NOPAIR-176"],
  "wordmark": ["D0106","D0141"],
  "nav": ["D3404","D0282","D2124","D2139","D0300","D0551","D0745","D5641","D2121","D0220",
          "D0494","D1493","D2244","LAW-113","LAW-02"],
  "burger": ["D0207","D2122","D0377","NOPAIR-185"],
  "ctabar": ["D0280","D0248","D0553","D0552","D2044","D1278","D0300","D2137","D2298","PAIR-1132"],
  "footer": ["D0226","D0087","D4187","D3135","D2124","D0859"],
  # home
  "hero": ["D0144","D0141","D3193","D0297","D0061","LENS-03"],
  "lede": ["D0076","D0149","LAW-37"],
  "cta": ["D0251","D0252","D0253","D0601","D0300","D0551","D2138","D2139","D0595","D2282",
          "D2137","D2298","D0591","D0297","LAW-33","LAW-34","LAW-46","D3428","PAIR-1142"],
  "contactline": ["D0142","D0615","D2318","D2312","D0282","D2213"],
  "slot": ["D0408","D2193","D0401","D0402","D0404","D2202","D0448","D0443","D0433","D2212",
           "D2078","D0039","D0371","PAIR-422","LENS-02"],
  "creds": ["D3187","D3128","D4653","D4187","D4225","D3780","D0142","D0353","DY10",
            "PAIR-125","LAW-23","NOPAIR-129"],
  "services-grid": ["D0067","D0083","D0351","D3428","D3465","D2188","D0353","D3040","D0080",
                    "D2186","DY07","PAIR-26"],
  "howitworks": ["D3790","D0093","D4653","LAW-20"],
  "triad": ["D4225","D2018","D0168","LENS-04","LENS-02"],
  "testimonials": ["D0367","D0374","D0860","D3796","PAIR-88","LENS-02","LENS-07"],
  "area": ["D2124","D0140","LENS-14"],
  "strip": ["D0297","D0282","D0615"],
  # services / about
  "services": ["D0063","D0076","D0375","D0377","D3821","D3813","D4225","D0141"],
  "about": ["D0063","D0076","D3821","D4225","D0141","D0859","D3128"],
  # gallery
  "gallery": ["D0067","D2187","D2193","D0408","D0404","D0401","D0402","D0443","D0433","D0446",
              "D0585","D0416","D5639","D0381","D2185","D2184","D2324","D0593","D0592","D2276",
              "D0589","D0642","D2233","D0260","D0665","D0666","D2347",
              "NOPAIR-237","NOPAIR-450","LAW-40"],
  # contact
  "form": ["D0301","D0307","D2152","D0310","D0895","D0387","D0323","D2165","D2160","D0598",
           "D0346","D0347","D2156","D2171","D1649","D0603","D0265","D0878","D0590","D0642",
           "D2306","D2313","D0867","D3792","D2175","D3746","D0344","D0876","D1674","D2314",
           "D0311","D2318","D1226","D1300","D1227",
           "LAW-18","LAW-20","LAW-25","LAW-26","LENS-07","LENS-15"],
  "confirm": ["D3792","LAW-20","D2312","D0642","D0867"],
  "socials": ["D0282","D2124","D2139","D2213"],
  "privacy": ["D3813","D3821","LENS-07"],
  "faq": ["D0375","D0377","D2035","D1222","D1225","D0668"],
  # spec sheet
  "spec": ["D3245","D4657","D2126"],
}

PADDOCK = {
  "ground": ["D3002","D3003","D3040","D0353","PAL Noma Forest Season","PAL Forest Institutional",
             "PALRULE-01","PALRULE-04","PAIR-356","PAIR-958","D5252"],
  "setpiece": ["D3187","D3128","D4653","LAW-15","LENS-13","LENS-04"],
  "hero-layout": ["D0061"],
  # v2 — the topographic sheet layer (LENS-12 leads, LENS-14 names the reference, TENSION-01/05/06 resolved)
  "topo": ["D2410","D0041","D1851","D1856","D3077","D3359","D0436","D4987","D0191",
           "PAIR-06","PAIR-794","LAW-10","LENS-12","LENS-14","TENSION-01","TENSION-05","TENSION-06"],
  "meta": ["D0140","D0142","D6468","D0041","D2124","PAIR-794"],
  "scalebar": ["D0041","D0142","D0436","D6468"],
  "map": ["D0436","D2213","D0041","D0142","D0191","D3780","D0443","LAW-23","LENS-14","PAIR-125"],
  "legend": ["D0436","D2213","LAW-23","D0191","D0041"],
  "marginalia": ["D0098","D0433","D0140","LENS-14","LENS-02"],
  "frame": ["D0041","D0433","D3813","LENS-07"],
  "ledger": ["D0142","D0041","PAIR-794"],
  # v3 — the card colourway
  "logo": ["D0443","D0401","D0448","D0404","D0408","LENS-14"],
  "drone": ["D5303","D0059","D0297","D3399","D0141","LENS-03","LENS-13"],
  "brand": ["D0159","D0049","D5303","D3399","D3876","D0107","D0106","D1350","D3373","PAIR-184","PAIR-982","LAW-83","LAW-06","PALRULE-05","LENS-14","LENS-02"],
}

NIGHT = {
  "ground": ["D0155","D4268","D4307","D4198","D3003","D2568","D0400","D2196","D5642",
             "PAL Forest Institutional","CPAIR-09","PALRULE-01","LAW-35","PAIR-392","PAIR-412"],
  "setpiece": ["D0421","D0060","D0371","D2744","LAW-15","LENS-13","D2343","NOPAIR-424","NOPAIR-419"],
  "hero-layout": ["D0060","D0077","D0434"],
}

TOP = {
  "templates": ["TP04","DY01","DY07","DY10","MK-01"],
  "lenses": ["LENS-03","LENS-04","LENS-02","LENS-14","LENS-07","LENS-15","LENS-19","LENS-13",
             "LENS-21","LENS-05","LENS-06","LENS-09","LENS-16","LENS-20"],
  "doctrine": ["DOC-01","DOC-02","DOC-03","DOC-04","DOC-05","TENSION-02","TENSION-03","TENSION-06"],
}

# v1.0 (SP-02): live features — real media, tap-to-call / click-to-copy, the receipt dialog, reviews
PADDOCK.update({
    "media":   ["D2211", "D0404", "D2201"],            # EXIF orientation correction · native lazy loading · sized srcset
    "video":   ["D0404", "D6523", "D0441", "D0381"],   # lazy, motion-and-data preview gate (preload none), chaptered player, native controls
    "sent":    ["D0381", "D0979", "D0592", "D2184", "D0642", "D0883"],  # native dialog receipt, focus, closedby, live region, consequence-explicit
    "reviews": ["D0367", "D0860", "D3813", "D0642"],   # testimonial card, first-use empty state, plain-language policy, live region
})

# v1.1 (SP-03): client content — FAQ page, credentials page, who Fitz works for
PADDOCK.update({
    "faq":         ["D0377", "D1225", "D3074", "D3821"],    # native details/summary, ::details-content, disclosure state, body contrast
    "cred-detail": ["D3813", "D0367"],                      # plain-language policy summary, card pattern
    "clients":     ["D3813"],
})

# v1.1b (SP-04): the sample report as proof — hero link and report card
PADDOCK.update({
    "report-card": ["D0293", "D4643", "D3813"],   # social-proof inline CTA, evidence chip, plain-language summary
    "report":      ["D3813", "D0433"],            # plain-language summary, figure captions
})
