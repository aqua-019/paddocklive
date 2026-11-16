# Splash preview (SP-09, branch `splash-preview`)

The real home page with the proposed splash, packaged as a claude.ai artifact so it can be reviewed and tweaked in chat. It plays on open and has a **Replay splash** button. Reduced motion still turns it off. Record: `docs/SP-09-ffh-splash-preview.md`.

```
python3 src/build.py && python3 mockups/splash/build_splash.py
```

This writes `dist/splash.html` (the artifact page) and `dist/files.json` (the images published beside it, mapped to their sources in `public/`). The gallery videos point at the live site and don't play in the preview.
