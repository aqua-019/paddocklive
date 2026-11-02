#!/usr/bin/env python3
"""Encode the site's photos and videos from media-src/ into public/media/ and fill in content/media.json.

    python3 scripts/media.py            # encode anything new or changed
    python3 scripts/media.py --force    # re-encode everything

Needs ffmpeg/ffprobe (Windows: winget install Gyan.FFmpeg · macOS: brew install ffmpeg) and Pillow.
Every output is stripped of metadata: phone and drone footage carries GPS, and the site promises
"Location withheld". The script re-probes each video and fails if any tag, subtitle or data stream survives.
Originals in media-src/ are never committed. Output names carry a content hash, so they can be cached forever.
"""
import hashlib, io, json, pathlib, subprocess, sys, tempfile
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'media-src'
OUT = ROOT / 'public' / 'media'
MANIFEST = ROOT / 'content' / 'media.json'
FORCE = '--force' in sys.argv
MAX_W = 1280            # long-edge cap for video; sources from phones and trail cams are smaller anyway
PHOTO_WIDTHS = (1280, 640)
WARN_MB = 25

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: sys.exit(f'command failed: {" ".join(cmd)}\n{p.stderr[-2000:]}')
    return p.stdout

def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))

def h8(path): return hashlib.sha256(path.read_bytes()).hexdigest()[:8]

def save_image(img, stem, widths):
    """JPEG + WebP at each width (never upscaled). No EXIF is written. Returns [(w, h, jpg, webp)]."""
    img = ImageOps.exif_transpose(img).convert('RGB')
    out = []
    for w in widths:
        if w >= img.width and out: continue
        im = img if w >= img.width else img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
        jb, wb = io.BytesIO(), io.BytesIO()
        im.save(jb, 'JPEG', quality=82, optimize=True, progressive=True)
        im.save(wb, 'WEBP', quality=78, method=6)
        tag = hashlib.sha256(jb.getvalue()).hexdigest()[:8]
        jp, wp = OUT / 'photo' / f'{stem}-{im.width}-{tag}.jpg', OUT / 'photo' / f'{stem}-{im.width}-{tag}.webp'
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_bytes(jb.getvalue()); wp.write_bytes(wb.getvalue())
        out.append((im.width, im.height, '/' + str(jp.relative_to(ROOT / 'public')), '/' + str(wp.relative_to(ROOT / 'public'))))
    return out

def grab_frame(video, t):
    with tempfile.TemporaryDirectory() as d:
        png = pathlib.Path(d) / 'f.png'
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(video), '-frames:v', '1', str(png)])
        return Image.open(png).copy()

def clean_check(path):
    """Fail if location/identifying metadata or extra streams survived."""
    p = probe(path)
    kinds = [s['codec_type'] for s in p['streams']]
    if kinds != ['video']: sys.exit(f'{path.name}: unexpected streams {kinds}')
    tags = {k.lower(): v for k, v in (p['format'].get('tags') or {}).items()}
    for s in p['streams']: tags.update({k.lower(): v for k, v in (s.get('tags') or {}).items()})
    bad = [k for k in tags if any(x in k for x in ('location', 'xyz', 'gps', 'creation_time', 'make', 'model', 'com.apple', 'com.android'))]
    if bad: sys.exit(f'{path.name}: metadata survived: {bad}')
    return p

def encode_video(item):
    src = SRC / item['source']
    start, end = (item.get('trim') or [0, None])
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d) / 'out.mp4'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(src)]
        if start: cmd += ['-ss', str(start)]
        if end: cmd += ['-to', str(end)]
        cmd += ['-map', '0:v:0', '-an', '-sn', '-dn', '-map_metadata', '-1', '-map_chapters', '-1',
                '-vf', f"scale='min({MAX_W},iw)':-2:flags=lanczos,fps=30",
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '25', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '-metadata:s:v:0', 'handler_name=', '-fflags', '+bitexact', str(tmp)]
        run(cmd)
        p = clean_check(tmp)
        dest = OUT / 'video' / f"{item['id']}-{h8(tmp)}.mp4"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(tmp.read_bytes())
    v = p['streams'][0]
    poster = save_image(grab_frame(dest, item.get('poster_at', 0.5)), item['id'] + '-poster', (MAX_W,))[0]
    mb = dest.stat().st_size / 1e6
    if mb > WARN_MB: print(f'  ! {item["id"]}: {mb:.1f} MB — consider a shorter trim', file=sys.stderr)
    item.update({'src': '/' + str(dest.relative_to(ROOT / 'public')), 'width': v['width'], 'height': v['height'],
                 'duration': round(float(p['format']['duration']), 1), 'bytes': dest.stat().st_size,
                 'poster': poster[2], 'poster_webp': poster[3]})

def encode_photo(item):
    src = SRC / item['source']
    img = grab_frame(src, item['frame_at']) if 'frame_at' in item else Image.open(src)
    outs = save_image(img, item['id'], PHOTO_WIDTHS)
    big = outs[0]
    item.update({'src': big[2], 'src_webp': big[3], 'width': big[0], 'height': big[1],
                 'srcset': [[w, j, wp] for w, _, j, wp in outs], 'bytes': (ROOT / 'public' / big[2].lstrip('/')).stat().st_size})

def main():
    m = json.loads(MANIFEST.read_text())
    for item in m['items']:
        src = SRC / item['source']
        have = item.get('src') and (ROOT / 'public' / item['src'].lstrip('/')).exists()
        if have and not FORCE: continue
        if not src.exists():
            if have: continue
            sys.exit(f"missing original media-src/{item['source']} for {item['id']}")
        print(f"encoding {item['id']} ← {item['source']}")
        (encode_video if item['type'] == 'video' else encode_photo)(item)
    # drop outputs nothing references any more
    keep = set()
    for i in m['items']:
        for k in ('src', 'src_webp', 'poster', 'poster_webp'):
            if i.get(k): keep.add(i[k])
        for _, j, w in i.get('srcset', []): keep.update((j, w))
    for f in OUT.rglob('*'):
        if f.is_file() and '/' + str(f.relative_to(ROOT / 'public')) not in keep: f.unlink()
    MANIFEST.write_text(json.dumps(m, indent=1, ensure_ascii=False) + '\n')
    total = sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file())
    print(f"{len(m['items'])} items · public/media {total/1e6:.1f} MB")

if __name__ == '__main__':
    main()
