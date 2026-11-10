CSS = r"""
/* Layout: one calm document, five landmark sections hash-routed; fluid headings on a fixed 17px body; one accent, one hover verb (recolour), one curve pair; cascade in named layers. */
@layer base, components, chrome, review, print;
:root{
@@TOKENS@@
  --d700-stamp:"@@STAMP@@";
  --font-display:"Cinzel","Trajan Pro","Palatino Linotype",Georgia,serif;
  --font-cond:"Barlow Condensed","Arial Narrow","Helvetica Neue",system-ui,sans-serif;
  --font-body:"Barlow",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --font-mono:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --ease-out:cubic-bezier(.165,.84,.44,1); --ease-in:cubic-bezier(.895,.03,.685,.22);
  --t-hover:.2s; --t-reveal:.344s; --t-exit:.2s;
  --fs-body:17px; --lh-body:1.5; --fs-small:15px; --fs-caption:13px;
  --fs-h1:clamp(2rem, 1.1rem + 3.4vw, 3.6rem);
  --fs-h2:clamp(1.5rem, 1.1rem + 1.6vw, 2.25rem);
  --fs-h3:clamp(1.3rem, 1.15rem + .7vw, 1.6rem);
  --fs-eyebrow:13px;
  --gutter-l:max(16px, env(safe-area-inset-left, 0px)); --gutter-r:max(16px, env(safe-area-inset-right, 0px));
  --radius:4px; --measure:65ch; --head-h:76px; --wrap:1180px;
  color-scheme:@@SCHEME@@;
  interpolate-size:allow-keywords;
}

/* body stays unlayered: the publish skeleton's own unlayered body reset would otherwise outrank a layered rule */
body{margin:0;background:var(--bg);color:var(--ink);font:400 var(--fs-body)/var(--lh-body) var(--font-body);letter-spacing:var(--body-track);font-variant-numeric:lining-nums proportional-nums;font-feature-settings:"pnum","lnum","liga";-webkit-font-smoothing:antialiased;text-wrap:pretty}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--chrome)}

@layer base{
*,*::before,*::after{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
h1,h2,h3,h4{font-family:var(--font-display);font-weight:700;line-height:1.06;margin:0;text-wrap:balance;text-transform:uppercase;text-box:trim-both cap alphabetic}
h1{font-size:var(--fs-h1);letter-spacing:.015em}
h2{font-size:var(--fs-h2);letter-spacing:.02em}
h3{font-family:var(--font-cond);font-size:var(--fs-h3);letter-spacing:.01em;line-height:1.05}
p{margin:0}
a{color:inherit;text-decoration-thickness:from-font;text-underline-offset:.14em}
img,svg{max-width:100%;height:auto;display:block}
button,input,select,textarea{font:inherit;letter-spacing:inherit;color:inherit}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
h1[tabindex="-1"]:focus-visible,h3[tabindex="-1"]:focus-visible,.confirm:focus-visible,.summary:focus-visible{outline:none}
::selection{background:color-mix(in srgb, var(--accent) 35%, transparent)}
[tabindex="-1"],.service,[data-page]{scroll-margin-top:calc(var(--head-h) + 24px)}
.wrap{max-width:var(--wrap);margin-inline:auto;padding-left:var(--gutter-l);padding-right:var(--gutter-r)}
.stack>*+*{margin-block-start:var(--gap,16px)}
.measure{max-width:var(--measure)}
.eyebrow{font:600 var(--fs-eyebrow)/1.3 var(--font-body);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-2)}
.small{font-size:var(--fs-small)}
.caption{font-size:var(--fs-caption);line-height:1.45;color:var(--ink-2)}
.num{font-variant-numeric:tabular-nums lining-nums;font-feature-settings:"tnum","lnum"}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
.mono{font-family:var(--font-mono);font-size:12px;letter-spacing:0}
.ico{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
}

@layer components{
/* skip links */
.skips{position:absolute;inset-inline-start:var(--gutter-l);top:0;z-index:40;display:flex;gap:8px}
.skips a{position:absolute;left:-9999px;top:0;background:var(--ink);color:var(--bg);padding:10px 14px;border-radius:0 0 var(--radius) var(--radius);white-space:nowrap}
.skips a:focus{position:static;left:auto}

/* header */
.site-head{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--chrome);color:var(--foot-ink);box-shadow:inset 0 -1px 0 var(--foot-line)}
.site-head :focus-visible{outline-color:var(--focus-dark)}
.logo{display:inline-flex;align-items:center;min-height:44px;flex:none}
.logo img{height:56px;width:auto;display:block}
@media (max-width:899px){.logo img{height:40px}}
.foot-logo img{height:64px}
@supports (animation-timeline: scroll()){
  .site-head{box-shadow:none;animation:scrolled-line linear both;animation-timeline:scroll(root);animation-range:0 96px}
  @keyframes scrolled-line{from{box-shadow:inset 0 -1px 0 var(--foot-line)}to{box-shadow:inset 0 -1px 0 var(--gold),0 1px 0 var(--line)}}
}
.site-head .wrap{display:flex;align-items:center;gap:16px;min-height:var(--head-h)}
.wordmark{display:flex;flex-direction:column;text-decoration:none;line-height:1;min-height:44px;justify-content:center}
.wordmark b{font:700 22px/1 var(--font-display);text-transform:uppercase;letter-spacing:.01em}
.wordmark small{font:600 11px/1.2 var(--font-body);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2);margin-top:3px}
.logo-slot{width:44px;height:44px;border:1px dashed var(--line-strong);border-radius:var(--radius);display:grid;place-items:center;font:600 9px/1.1 var(--font-mono);text-align:center;color:var(--ink-2);text-transform:uppercase;letter-spacing:.04em;flex:none}
.nav{margin-inline-start:auto}
.nav ul{list-style:none;margin:0;padding:0;display:flex;gap:2px;align-items:center}
.nav a:not(.btn){display:inline-flex;align-items:center;min-height:44px;padding:0 12px;text-decoration:none;color:var(--foot-ink);font-weight:500;box-shadow:inset 0 -2px 0 transparent;transition:color var(--t-hover) var(--ease-out),box-shadow var(--t-hover) var(--ease-out)}
.nav a:not(.btn):hover{color:var(--gold-light)}
.nav a[aria-current="page"]{box-shadow:inset 0 -2px 0 var(--gold);font-weight:600}
.nav .nav-cta{margin-inline-start:8px}
.drawer{margin-inline-start:auto;display:none}
.drawer summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 12px;border:1px solid var(--foot-line);border-radius:var(--radius);font-weight:600;color:var(--foot-ink);transition:background-color var(--t-hover) var(--ease-out)}
.drawer summary::-webkit-details-marker{display:none}
.drawer summary:hover{background:color-mix(in srgb, var(--foot-ink) 10%, transparent)}
.drawer[open] summary{background:color-mix(in srgb, var(--foot-ink) 10%, transparent)}
.drawer ul{list-style:none;margin:0;padding:8px var(--gutter-r) 12px var(--gutter-l);position:absolute;inset-inline:0;top:100%;background:var(--chrome);color:var(--foot-ink);box-shadow:inset 0 1px 0 var(--foot-line),0 1px 0 var(--line)}
.drawer li a{display:flex;align-items:center;min-height:48px;text-decoration:none;font-weight:500;padding:0 4px;box-shadow:inset 0 -1px 0 var(--foot-line);transition:color var(--t-hover) var(--ease-out)}
.drawer li a:hover{color:var(--gold-light)}
.drawer li a[aria-current="page"]{font-weight:700;color:var(--gold-light)}
@media (max-width:899px){.nav{display:none}.drawer{display:block;position:static}}

/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:48px;padding:0 22px;border-radius:var(--radius);border:1.5px solid transparent;font-weight:600;text-decoration:none;cursor:pointer;background:transparent;position:relative;transition:background-color var(--t-hover) var(--ease-out),color var(--t-hover) var(--ease-out),border-color var(--t-hover) var(--ease-out)}
.btn::after{content:"";position:absolute;inset:-4px}
.btn-primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.btn-primary:hover{background:var(--accent-hover);border-color:var(--accent-hover)}
.btn-primary:active{background:var(--accent-press);border-color:var(--accent-press)}
.btn-gold{background:var(--gold-light);color:var(--chrome);border-color:var(--gold-light)}
.btn-gold:hover{background:color-mix(in srgb, var(--gold-light), #ffffff 14%);border-color:color-mix(in srgb, var(--gold-light), #ffffff 14%)}
.btn-gold:active{background:var(--gold);border-color:var(--gold)}
.btn-secondary{border-color:var(--line-strong);color:var(--ink)}
.btn-secondary:hover{background:var(--wash)}
.btn-secondary:active{background:var(--wash-press)}
.btn-quiet{min-height:44px;padding:0 12px;color:var(--ink-2);text-decoration:underline;text-underline-offset:.16em}
.btn-quiet:hover{color:var(--ink)}
.btn[disabled],.btn[aria-disabled="true"]{opacity:.7;cursor:progress}
.btn .spin{width:16px;height:16px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:spin 1s linear infinite;display:none}
.btn.is-busy .spin{display:inline-block}
@keyframes spin{to{rotate:1turn}}
.copy{display:inline-flex;align-items:center;gap:6px;min-height:44px;min-width:44px;padding:0 10px;border:1px solid var(--line-strong);border-radius:var(--radius);background:transparent;font:600 13px/1 var(--font-body);letter-spacing:.04em;text-transform:uppercase;cursor:pointer;transition:background-color var(--t-hover) var(--ease-out),color var(--t-hover) var(--ease-out),border-color var(--t-hover) var(--ease-out)}
.copy:hover{background:var(--wash)}
.copy[data-state="copied"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.contact-line{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center}
.contact-line .kv{display:flex;align-items:center;gap:10px;min-width:0}
.contact-line .kv b{font-weight:600;font-size:var(--fs-small);color:var(--ink-2);letter-spacing:.06em;text-transform:uppercase;display:inline-flex;align-items:center;gap:6px}
.contact-line .kv span{font-weight:500;overflow-wrap:anywhere}
.contact-line .kv span a,.confirm .small a,.form .note a,.gal figcaption a{display:inline-block;padding-block:12px;margin-block:-12px}
@media (pointer:coarse){.copy,.nav a:not(.btn){min-height:48px}}

/* sections */
.page{padding-block:56px 72px;content-visibility:auto;contain-intrinsic-size:auto 900px}
.page+.page{box-shadow:inset 0 1px 0 var(--line)}
.band{padding-block:56px}
.band.alt{background:var(--surface)}
.band+.band{box-shadow:inset 0 1px 0 var(--line)}
.band.invert{background:var(--foot-bg);color:var(--foot-ink)}
.band.invert .eyebrow,.band.invert .caption{color:color-mix(in srgb, var(--foot-ink) 70%, transparent)}
.sec-head{display:grid;gap:12px;margin-block-end:32px;max-width:52rem}
.grid{display:grid;gap:24px}
@media (min-width:700px){.grid-2{grid-template-columns:repeat(2,minmax(0,1fr))}.grid-3{grid-template-columns:repeat(3,minmax(0,1fr))}.grid-4{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:699px){.grid-4{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (min-width:900px){.grid-3{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:899px) and (min-width:700px){.grid-3{grid-template-columns:repeat(2,minmax(0,1fr))}}

/* hero */
.hero{padding-block:48px 56px}
.hero-grid{display:grid;gap:32px;align-items:start}
@media (min-width:900px){.hero-grid{grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:48px}.hero{padding-block:64px 72px}}
.hero h1{max-width:14ch}
.hero .lede{font-size:clamp(17px, 1rem + .35vw, 21px);line-height:1.45;max-width:var(--measure);color:var(--ink)}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.descriptors{font:600 13px/1.6 var(--font-body);letter-spacing:.08em;text-transform:uppercase;color:var(--gold-ink)}
.descriptors span{color:var(--gold);padding-inline:2px}
.card-figure{margin:12px 0 0;display:grid;gap:8px}
.card-figure img{width:100%;height:auto;border-radius:var(--radius);box-shadow:inset 0 0 0 1px var(--line)}
.flag{display:inline-block;font:600 11px/1.2 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);border:1px dashed var(--line-strong);border-radius:var(--radius);padding:3px 6px;vertical-align:middle}

/* photo slots: honest placeholders, ratio-locked */
.slot{position:relative;background:var(--surface-2);border-radius:var(--radius);overflow:hidden;aspect-ratio:var(--ar,4/3);max-width:100%;box-shadow:var(--ring);isolation:isolate}
.slot::before{content:"";position:absolute;inset:0;background-image:url("@@GRAIN@@");background-size:160px;opacity:var(--grain-alpha);mix-blend-mode:var(--grain-blend)}
.slot::after{content:"";position:absolute;inset:0;background:var(--scrim);z-index:1;pointer-events:none}
.slot .tag{position:absolute;top:10px;left:10px;z-index:2;font:600 10px/1.2 var(--font-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);border:1px dashed var(--line-strong);background:color-mix(in srgb, var(--bg) 70%, transparent);padding:3px 6px;border-radius:3px}
.slot .label{position:absolute;inset-inline:12px;bottom:12px;z-index:2;color:var(--foot-ink);font:600 14px/1.3 var(--font-body)}
.slot .label small{display:block;font:500 12px/1.3 var(--font-body);letter-spacing:.04em;opacity:.8;text-transform:uppercase}
.slot .mark{position:absolute;inset:0;display:grid;place-items:center;z-index:0;color:var(--ink-3);font:700 clamp(28px,6vw,56px)/1 var(--font-cond);text-transform:uppercase;letter-spacing:.02em;opacity:.5}
.slot.thermal{--slot-tint:color-mix(in srgb, var(--surface-2), var(--chrome) 22%);background:var(--slot-tint)}

/* credentials wall */
.creds{list-style:none;margin:0;padding:0;display:grid;gap:20px 24px}
@media (min-width:700px){.creds{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:699px){.creds{grid-template-columns:repeat(2,minmax(0,1fr))}}
.creds li{border-top:2px solid var(--gold);padding-top:12px;display:grid;gap:4px;min-width:0}
.creds .eyebrow{color:var(--ink-2)}
.creds b{font:700 var(--fs-h3)/1.05 var(--font-cond);text-transform:uppercase;overflow-wrap:anywhere}
.creds p{font-size:var(--fs-small);color:var(--ink-2)}
.creds li.note{border-top-style:dashed;border-top-width:1px;border-top-color:var(--line-strong)}
.status{display:inline-flex;align-items:center;gap:8px;font-weight:600;font-size:var(--fs-small)}
.status i{width:10px;height:10px;border-radius:50%;background:var(--ok);flex:none}

/* service tiles */
.tile{position:relative;display:grid;gap:12px;padding:20px;border-radius:var(--radius);background:var(--bg);box-shadow:inset 0 0 0 1px var(--line);min-width:0;container-type:inline-size;contain:layout paint}
@container (min-width:340px){.tile{padding:24px}}
.tile p{color:var(--ink-2);font-size:var(--fs-small)}
.tile .stretch{position:absolute;inset:0;border-radius:inherit}
.tile .btn{justify-self:start;position:relative;z-index:1}

/* how it works */
.steps{list-style:none;margin:0;padding:0;display:grid;gap:24px;counter-reset:step}
@media (min-width:900px){.steps{grid-template-columns:repeat(4,minmax(0,1fr))}}
.steps li{counter-increment:step;display:grid;gap:8px;position:relative;padding-left:0;min-width:0}
.steps li::before{content:counter(step,decimal-leading-zero);font:700 15px/1 var(--font-mono);color:var(--ink-2);letter-spacing:.06em}
.steps li::after{content:"";height:2px;background:var(--chrome);order:-1}
@media (max-width:899px){.steps{border-left:2px solid var(--chrome);padding-left:20px}.steps li::after{display:none}}
.steps b{font:700 var(--fs-h3)/1.05 var(--font-cond);text-transform:uppercase}
.steps p{font-size:var(--fs-small);color:var(--ink-2)}

/* drone feature band */
.band.drone{background:var(--chrome);color:var(--foot-ink)}
.band.drone .eyebrow,.band.drone .caption{color:var(--gold-light)}
.band.drone h2{color:var(--foot-ink)}
.band.drone .measure{color:color-mix(in srgb, var(--foot-ink) 85%, transparent)}
.drone-grid{display:grid;gap:32px;align-items:center}
@media (min-width:900px){.drone-grid{grid-template-columns:minmax(0,6fr) minmax(0,5fr);gap:48px}}
.drone-list{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.drone-list li{display:flex;gap:10px;align-items:baseline;font-size:var(--fs-small);color:color-mix(in srgb, var(--foot-ink) 82%, transparent);border-top:1px solid var(--foot-line);padding-top:8px}
.drone-list li b{color:var(--gold-light);font-weight:600;white-space:nowrap}
.band.drone .btn-primary{background:var(--gold-light);color:var(--chrome);border-color:var(--gold-light)}
.band.drone .btn-primary:hover{background:color-mix(in srgb, var(--gold-light), #ffffff 14%)}
.band.drone .btn-quiet{color:var(--gold-light)}
.band.drone .btn-quiet:hover{color:var(--foot-ink)}
.band.drone :focus-visible{outline-color:var(--focus-dark)}
.band.drone .slot{--scrim:linear-gradient(to top, rgb(27 38 34 / .9), rgb(27 38 34 / .1) 70%);box-shadow:inset 0 0 0 1px var(--foot-line)}
.band.drone .slot .tag{color:var(--gold-light);border-color:var(--foot-line);background:color-mix(in srgb, var(--chrome) 70%, transparent)}

/* trust triad */
.triad{display:grid;gap:24px}
@media (min-width:700px){.triad{grid-template-columns:repeat(3,minmax(0,1fr))}}
.triad div{display:grid;gap:6px;border-top:2px solid var(--gold);padding-top:14px}
.triad b{font:700 var(--fs-h3)/1.05 var(--font-cond);text-transform:uppercase}
.triad p{color:var(--ink-2);font-size:var(--fs-small)}

/* testimonials (slots) */
.ghost{border:1px dashed var(--line-strong);border-radius:var(--radius);padding:20px;display:grid;gap:10px;color:var(--ink-2);min-height:150px}
.ghost q{font-size:var(--fs-body);font-style:italic;quotes:"\201C" "\201D"}
.ghost .who{font-size:var(--fs-caption);letter-spacing:.04em;text-transform:uppercase}

/* area chips */
.chips{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:0;padding:0}
.chips li{border:1px solid var(--line-strong);border-radius:999px;padding:6px 12px;font-size:var(--fs-small);font-weight:500}

/* prose pages */
.prose{max-width:var(--measure);display:grid;gap:18px}
.prose h3{margin-top:12px}
.prose ul{margin:0;padding-left:20px;display:grid;gap:6px}
details.faq{border-top:1px solid var(--line)}
details.faq:last-of-type{border-bottom:1px solid var(--line)}
details.faq summary{cursor:pointer;min-height:48px;display:flex;align-items:center;justify-content:space-between;gap:12px;font-weight:600;list-style:none;padding:8px 0}
details.faq summary::-webkit-details-marker{display:none}
details.faq summary::after{content:"+";font:700 22px/1 var(--font-cond);color:var(--ink-2)}
details.faq[open] summary::after{content:"\2212"}
details.faq p{padding-bottom:16px;color:var(--ink-2);font-size:var(--fs-small)}
details.faq::details-content{height:0;overflow:clip}
details.faq[open]::details-content{height:auto}
.service{display:grid;gap:10px;padding-block:24px;box-shadow:inset 0 1px 0 var(--line)}
@media (min-width:700px){.service{grid-template-columns:minmax(0,2fr) minmax(0,3fr);gap:32px}}
.service ul{margin:0;padding-left:18px;color:var(--ink-2);font-size:var(--fs-small);display:grid;gap:4px}

/* gallery */
.gal{list-style:none;margin:0;padding:0;display:grid;gap:12px;grid-template-columns:repeat(2,minmax(0,1fr))}
@media (min-width:700px){.gal{grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}
.gal li{content-visibility:auto;contain-intrinsic-size:auto 260px}
.gal button{all:unset;display:block;cursor:pointer;border-radius:var(--radius);width:100%}
.gal button:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.gal .slot{--ar:4/3}
.gal figcaption{font-size:var(--fs-caption);color:var(--ink-2);margin-top:6px}
dialog.lightbox{border:0;padding:0;background:var(--bg);color:var(--ink);width:min(96vw, 1100px);max-width:none;border-radius:var(--radius);overscroll-behavior:contain;box-shadow:var(--ring)}
dialog::backdrop{background:rgb(0 0 0 / .62)}
dialog.lightbox .frame{display:grid;gap:12px;padding:16px}
dialog.lightbox .bar{display:flex;align-items:center;gap:8px;justify-content:space-between}
dialog.lightbox .bar .btn{min-width:44px}
dialog.lightbox .slot{--ar:3/2}

/* form */
.form{display:grid;gap:20px;max-width:40rem}
.field{display:grid;gap:6px;min-width:0}
.field label,.field legend{font-weight:600}
.field .hint{font-size:var(--fs-caption);color:var(--ink-2)}
.field input,.field textarea{width:100%;min-height:48px;padding:10px 12px;border:1.5px solid var(--line-strong);border-radius:var(--radius);background:var(--bg);color:var(--ink);transition:border-color var(--t-hover) var(--ease-out),background-color var(--t-hover) var(--ease-out)}
.field textarea{min-height:120px;resize:vertical;field-sizing:content}
.field input:hover,.field textarea:hover{border-color:var(--ink-2)}
.field input:user-invalid,.field textarea:user-invalid,.field .is-invalid{border-color:var(--err)}
.field .err{font-size:var(--fs-caption);color:var(--err);font-weight:600;display:none}
.field.has-err .err{display:block}
fieldset{border:0;padding:0;margin:0;min-width:0}
.checks{display:grid;gap:4px;grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
.checks label{display:flex;align-items:center;gap:10px;min-height:44px;font-weight:500;cursor:pointer}
.checks input{width:20px;height:20px;accent-color:var(--accent);margin:0}
.summary{border:1.5px solid var(--err);border-radius:var(--radius);padding:14px 16px;display:grid;gap:6px}
.summary ul{margin:0;padding-left:18px}
.summary a{color:var(--err);font-weight:600}
.confirm{border:2px solid var(--ok);border-radius:var(--radius);padding:20px;display:grid;gap:10px;background:var(--surface)}
.confirm b{font:700 var(--fs-h3)/1.05 var(--font-cond);text-transform:uppercase}
.form .note{font-size:var(--fs-caption);color:var(--ink-2)}

/* contact page layout */
.contact-grid{display:grid;gap:40px}
@media (min-width:900px){.contact-grid{grid-template-columns:minmax(0,5fr) minmax(0,7fr)}}
.contact-list{display:grid;gap:18px}
.contact-list .kv{display:grid;gap:4px}
.contact-list .kv b{font-weight:600;font-size:var(--fs-small);color:var(--ink-2);letter-spacing:.06em;text-transform:uppercase;display:inline-flex;align-items:center;gap:6px}
.contact-list .kv .row{display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.contact-list .kv .row span{font:600 clamp(20px, 1rem + 1vw, 26px)/1.2 var(--font-body);overflow-wrap:anywhere}
.socials{display:flex;flex-wrap:wrap;gap:12px}
.socials a{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border:1px solid var(--line-strong);border-radius:var(--radius);text-decoration:none;font-weight:600;transition:background-color var(--t-hover) var(--ease-out)}
.socials a:hover{background:var(--wash)}

/* footer */
.site-foot{background:var(--foot-bg);color:var(--foot-ink);padding-block:48px 40px;box-shadow:inset 0 1px 0 var(--gold)}
.site-foot .wrap{display:grid;gap:32px}
@media (min-width:700px){.site-foot .cols{display:grid;grid-template-columns:2fr 1fr 1fr;gap:32px}}
.site-foot h4{font-size:13px;letter-spacing:.1em;color:var(--gold-light);margin-bottom:10px;font-family:var(--font-body);font-weight:600;text-box:normal}
.site-foot ul{list-style:none;margin:0;padding:0;display:grid;gap:2px}
.site-foot li a{display:flex;align-items:center;min-height:44px;min-width:44px;text-decoration:none;transition:color var(--t-hover) var(--ease-out)}
.site-foot li a:hover{color:color-mix(in srgb, var(--foot-ink) 70%, transparent)}
.site-foot .cred-strip{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:var(--fs-small);font-weight:500;color:var(--gold-light);border-top:1px solid var(--gold);padding-top:16px}
.site-foot .legal{font-size:var(--fs-caption);color:color-mix(in srgb, var(--foot-ink) 65%, transparent);display:flex;flex-wrap:wrap;gap:6px 18px}

/* sticky mobile CTA bar */
.cta-bar{position:fixed;inset-inline:0;bottom:0;z-index:15;display:grid;grid-template-columns:1fr 1fr;gap:8px;background:var(--bg);box-shadow:inset 0 1px 0 var(--line-strong);padding:8px var(--gutter-r) calc(8px + env(safe-area-inset-bottom,0px)) var(--gutter-l)}
.cta-bar .btn{min-height:48px;padding-inline:12px}
@media (min-width:900px){.cta-bar{display:none}}
@media (max-width:899px){.site-foot{padding-bottom:calc(40px + 72px + env(safe-area-inset-bottom,0px))}}

/* compare slider (SP-02 set-piece) */
.compare{margin:0;--split:50%}
.compare .frame{position:relative;aspect-ratio:2/1;max-width:100%;border-radius:var(--radius);overflow:hidden;box-shadow:var(--ring)}
@media (max-width:699px){.compare .frame{aspect-ratio:4/3}}
.compare .frame .slot{position:absolute;inset:0;aspect-ratio:auto;border-radius:0}
.compare .frame .top{position:absolute;inset:0;clip-path:inset(0 0 0 var(--split))}
.compare .frame .top .label{inset-inline:auto 12px;text-align:right}
.compare .frame .top .tag{left:auto;right:10px}
.compare .handle{position:absolute;top:0;bottom:0;left:var(--split);width:2px;background:var(--ink);z-index:3;pointer-events:none;translate:-1px 0}
.compare .handle::before{content:"";position:absolute;top:50%;left:50%;translate:-50% -50%;width:40px;height:40px;border-radius:50%;background:var(--bg);border:2px solid var(--ink);box-shadow:0 0 0 4px color-mix(in srgb, var(--bg) 40%, transparent)}
.compare .ctl{display:grid;gap:6px;margin-top:12px}
.compare .ctl input{width:100%;min-height:44px;accent-color:var(--accent);margin:0}
.compare .ctl span{font-size:var(--fs-caption);color:var(--ink-2);display:flex;justify-content:space-between;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.hero-bleed{position:relative}
.hero-bleed .text{position:relative;z-index:2}
.bleed{margin-inline:calc(-1 * var(--gutter-l)) calc(-1 * var(--gutter-r))}
@media (min-width:1212px){.bleed{margin-inline:0}}

/* motion: content reveals only, never chrome; declared only when motion is wanted (hard gate) */
@media (prefers-reduced-motion: no-preference){
  @supports (animation-timeline: view()){
    .reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 35%}
    @keyframes rise{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
  }
  dialog{opacity:0;translate:0 8px;transition:opacity var(--t-exit) var(--ease-in),translate var(--t-exit) var(--ease-in),overlay var(--t-exit) allow-discrete,display var(--t-exit) allow-discrete}
  dialog[open]{opacity:1;translate:0 0;transition-duration:var(--t-reveal);transition-timing-function:var(--ease-out)}
  @starting-style{dialog[open]{opacity:0;translate:0 8px}}
  dialog::backdrop{opacity:0;transition:opacity var(--t-exit) var(--ease-in),overlay var(--t-exit) allow-discrete,display var(--t-exit) allow-discrete}
  dialog[open]::backdrop{opacity:1;transition-duration:var(--t-reveal);transition-timing-function:var(--ease-out)}
  @starting-style{dialog[open]::backdrop{opacity:0}}
  details.faq::details-content{transition:height var(--t-reveal) var(--ease-out),content-visibility var(--t-reveal) allow-discrete}
}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}

/* platform accessibility schemes */
@media (forced-colors: active){
  .btn,.copy,.socials a,.chips li{border:2px solid ButtonText}
  .status i,.steps li::after,.creds li{forced-color-adjust:none}
  .slot::before,.slot::after{display:none}
}
@media (prefers-contrast: more){
  :root{--line:var(--line-strong);--ink-2:var(--ink)}
}
}

@layer components{
/* ---- v2 topographic sheet layer (SP-01b): contour field, MGA grid, map marginalia. Every stroke is bark ink at ≤12% alpha; nothing animates. */
:root{--km:150px; --topo-alpha:1}
body::after{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:var(--topo-alpha);
  background-image:url("@@TOPO@@"),
    repeating-linear-gradient(90deg, color-mix(in srgb, var(--ink) 6%, transparent) 0 1px, transparent 1px var(--km)),
    repeating-linear-gradient(180deg, color-mix(in srgb, var(--ink) 6%, transparent) 0 1px, transparent 1px var(--km));
  background-size:1200px 1200px, var(--km) var(--km), var(--km) var(--km);background-position:0 0, 0 0, 0 0}
@media (max-width:699px){body::after{background-image:url("@@TOPO@@");background-size:900px 900px;--topo-alpha:.8}}
@media print{body::after{display:none}}
.band.alt{background:color-mix(in srgb, var(--surface) 86%, transparent)}

.tile,.ghost,.field input,.field textarea,.confirm,.summary{background:color-mix(in srgb, var(--bg) 92%, transparent)}
.tile{background:color-mix(in srgb, var(--bg) 94%, transparent)}

/* sheet meta line on section heads */
.meta{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;font:500 11px/1.4 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.meta b{font-weight:700;color:var(--ink)}
.meta .lead{flex:1 1 40px;min-width:24px;border-bottom:1px dotted var(--line-strong);translate:0 -4px}
.sec-head .meta{order:-1}

/* north arrow + datum chip in the header */
.datum{display:none;align-items:center;gap:8px;margin-inline-start:12px;font:600 10px/1.2 var(--font-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
@media (min-width:1100px){.datum{display:inline-flex}}
.north{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.4;stroke-linejoin:round}
.north .fill{fill:currentColor;stroke:none}

/* scale bar: 150 px = 1 km at this sheet's scale */
.scalebar{display:flex;align-items:flex-end;gap:0;font:500 10px/1 var(--font-mono);letter-spacing:.06em;color:var(--ink-2);margin:0;user-select:none}
.scalebar .bar{display:flex;height:6px;width:var(--km);box-shadow:inset 0 0 0 1px var(--ink)}
.scalebar .bar i{flex:1;background:var(--ink)}
.scalebar .bar i:nth-child(even){background:transparent}
.scalebar .ticks{display:flex;justify-content:space-between;width:calc(var(--km) + 2.2ch);margin-left:-1.1ch;margin-top:5px}
.scalebar .ticks span{text-align:center;width:2.2ch}
.scalebar .unit{margin-left:10px;margin-bottom:1px}
.scalebar.stack{flex-direction:column;align-items:flex-start}
.divider{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-block:14px;border-top:1px solid var(--line)}
.divider .mono{color:var(--ink-2);font-size:11px;letter-spacing:.06em;text-transform:uppercase}

/* locality map + legend */
.area-grid{display:grid;gap:28px}
@media (min-width:900px){.area-grid{grid-template-columns:minmax(0,7fr) minmax(0,5fr);align-items:start}}
.map-scroll{overflow-x:auto;overscroll-behavior-x:contain;border-radius:var(--radius)}
@media (max-width:699px){.map-scroll .map{min-width:640px}.map-scroll::after{content:"scroll sideways for the whole sheet";display:block;font:500 11px/1.4 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);padding:6px 0 0}}
.map{display:block;width:100%;height:auto;background:color-mix(in srgb, var(--bg) 70%, transparent);box-shadow:inset 0 0 0 1px var(--line-strong);border-radius:var(--radius)}
.map text{font-family:var(--font-mono);font-size:11px;fill:var(--ink);letter-spacing:.04em}
.map .edge{font-size:9.5px;fill:var(--ink-2)}
.map .grid{stroke:var(--ink);stroke-opacity:.14;stroke-width:1}
.map .ring{fill:none;stroke:var(--ink);stroke-width:1;stroke-dasharray:3 4;stroke-opacity:.55}
.map .town{fill:var(--bg);stroke:var(--ink);stroke-width:1.6}
.map .base{fill:var(--accent);stroke:var(--ink);stroke-width:1.2}
.map .frame{fill:none;stroke:var(--ink);stroke-width:1}
.map .scale{stroke:var(--ink);stroke-width:1}
.legend{display:grid;gap:10px;align-content:start}
.legend dl{margin:0;display:grid;grid-template-columns:56px minmax(0,1fr);gap:8px 14px;align-items:center;font-size:var(--fs-small)}
.legend dt{height:18px;display:flex;align-items:center}
.legend dd{margin:0;color:var(--ink-2)}
.legend dd b{color:var(--ink);font-weight:600}
.legend svg{width:56px;height:18px;overflow:visible}
.legend .k{stroke:var(--ink);fill:none;stroke-width:1.2}
.chips li .gr{font:500 11px/1 var(--font-mono);letter-spacing:.04em;color:var(--ink-2);margin-left:8px}

/* marginalia beside prose */
.notes-layout{display:grid;gap:24px}
@media (min-width:900px){.notes-layout{grid-template-columns:minmax(0,1fr) 15rem;gap:48px;align-items:start}}
.margin-notes{display:grid;gap:14px;font-size:var(--fs-caption);line-height:1.45;color:var(--ink-2);border-left:1px solid var(--line-strong);padding-left:16px;position:sticky;top:calc(var(--head-h) + 24px)}
@media (max-width:899px){.margin-notes{position:static;border-left:0;padding-left:0;border-top:1px dotted var(--line-strong);padding-top:14px}}
.margin-notes p{display:grid;grid-template-columns:2ch 1fr;gap:6px}
.margin-notes .n{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.margin-notes h4{font:600 11px/1.3 var(--font-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);text-box:normal}

/* photo frames: registration ticks */
.slot .corner{position:absolute;width:12px;height:12px;z-index:2;border:1.5px solid color-mix(in srgb, var(--foot-ink) 85%, transparent)}
.slot .corner.tl{top:8px;left:8px;border-right:0;border-bottom:0}.slot .corner.tr{top:8px;right:8px;border-left:0;border-bottom:0}
.slot .corner.bl{bottom:8px;left:8px;border-right:0;border-top:0}.slot .corner.br{bottom:8px;right:8px;border-left:0;border-top:0}
.slot .label{inset-inline:22px;bottom:22px}

/* ledger list with dotted leaders */
.ledger{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.ledger li{display:flex;align-items:baseline;gap:8px;font-size:var(--fs-small)}
.ledger li b{font-weight:600;white-space:nowrap}
.ledger li .lead{flex:1;border-bottom:1px dotted var(--line-strong);min-width:16px;translate:0 -4px}
.ledger li span:last-child{color:var(--ink-2);text-align:right}

/* footer marginalia */
.site-foot .margin{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;font:500 11px/1.5 var(--font-mono);letter-spacing:.05em;text-transform:uppercase;color:color-mix(in srgb, var(--foot-ink) 65%, transparent);border-top:1px solid var(--foot-line);padding-top:14px}
.site-foot :focus-visible,.band.invert :focus-visible,.cta-bar :focus-visible{outline-color:var(--focus-dark)}
.site-foot .scalebar{color:color-mix(in srgb, var(--foot-ink) 75%, transparent)}
.site-foot .scalebar .bar{box-shadow:inset 0 0 0 1px var(--foot-ink)}
.site-foot .scalebar .bar i{background:var(--foot-ink)}
.site-foot .scalebar .bar i:nth-child(even){background:transparent}
.site-foot .north{color:color-mix(in srgb, var(--foot-ink) 75%, transparent)}
}

@layer review{
/* reviewer chrome (not part of the site) */
.varbar{background:var(--surface-2);color:var(--ink);font:500 12px/1.4 var(--font-mono);border-bottom:1px solid var(--line)}
.varbar .wrap{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;min-height:40px;padding-block:6px}
.varbar strong{font-weight:700}
.varbar .grow{flex:1 1 auto;min-width:0}
.varbar .short{display:none}
@media (max-width:699px){.varbar .long{display:none}.varbar .short{display:inline}.varbar .wrap{gap:6px 8px}.varbar button,.varbar a{padding:2px 8px}}
.varbar button,.varbar a{font:inherit;min-height:32px;padding:2px 10px;border:1px solid var(--line-strong);border-radius:var(--radius);background:transparent;color:inherit;cursor:pointer;text-decoration:none;transition:background-color var(--t-hover) var(--ease-out),border-color var(--t-hover) var(--ease-out)}
.varbar button:hover,.varbar a:hover{background:var(--wash)}
.varbar button[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.varbar a[aria-disabled="true"]{opacity:.55;pointer-events:none}
@media (pointer:coarse){.varbar button,.varbar a{min-height:44px}}
[data-motion="off"] *{animation:none!important;transition:none!important}
[data-xray] [data-per]{outline:1px dashed color-mix(in srgb, var(--focus) 80%, transparent);outline-offset:-1px}
dialog.spec{border:0;padding:0;width:min(96vw, 920px);max-width:none;max-height:92vh;background:var(--bg);color:var(--ink);border-radius:var(--radius);overscroll-behavior:contain;box-shadow:var(--ring)}
dialog.spec .inner{padding:20px 20px 28px;display:grid;gap:18px;font-size:var(--fs-small)}
dialog.spec h2{font-size:var(--fs-h3)}
dialog.spec h3{font:600 13px/1.3 var(--font-body);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);text-box:normal}
dialog.spec pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.5 var(--font-mono);background:var(--surface);padding:12px;border-radius:var(--radius);margin:0;max-height:40vh;overflow:auto}
dialog.spec .ids{columns:2;column-gap:24px;font:12px/1.5 var(--font-mono);margin:0;padding:0;list-style:none}
@media (min-width:700px){dialog.spec .ids{columns:3}}
dialog.spec .ids li{break-inside:avoid;overflow-wrap:anywhere}
dialog.spec .counts{display:flex;flex-wrap:wrap;gap:8px 20px;font:600 13px/1.4 var(--font-mono)}
dialog.spec .bar{display:flex;justify-content:space-between;align-items:center;gap:12px;position:sticky;top:0;background:var(--bg);padding:12px 20px;box-shadow:inset 0 -1px 0 var(--line);z-index:2}
}

@layer print{
@media print{
  :root{--bg:#ffffff;--surface:#f4f4f4;--surface-2:#ececec;--ink:#111111;--ink-2:#444444;--ink-3:#999999;--line:#cccccc;--line-strong:#999999;--foot-bg:#ffffff;--foot-ink:#111111;--foot-line:#cccccc;--ring:inset 0 0 0 1px #cccccc;--scrim:none;--grain-alpha:0}
  .varbar,.cta-bar,.skips,.drawer,.nav .nav-cta,dialog,.flag{display:none!important}
  [data-page]{display:block!important}
  .page{content-visibility:visible}
  .reveal{animation:none!important;opacity:1!important}
  a[href^="http"]::after{content:" (" attr(href) ")";font-size:11px;color:#444}
}
}
"""
