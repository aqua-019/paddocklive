#!/usr/bin/env node
// Local preview: serves public/ like Vercel (clean URLs, rewrites from vercel.json) and runs api/*.js as functions.
//   node scripts/dev.mjs            → http://localhost:3000
// Reads .env.local if present. With no Redis configured it switches on an in-memory review store (FFH_MEMORY_STORE=1)
// so the review flow can be tried end to end; that store never runs on Vercel.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import querystring from 'node:querystring';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PUB = path.join(ROOT, 'public');
const PORT = +process.env.PORT || 3000;

const envFile = path.join(ROOT, '.env.local');
if (fs.existsSync(envFile)) for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*"?(.*?)"?\s*$/); if (m && !(m[1] in process.env)) process.env[m[1]] = m[2];
}
if (!process.env.UPSTASH_REDIS_REST_URL && !process.env.KV_REST_API_URL && process.env.FFH_MEMORY_STORE === undefined) process.env.FFH_MEMORY_STORE = '1';
if (!process.env.REVIEW_SECRET) process.env.REVIEW_SECRET = 'local-dev-secret-not-for-production';

const vercel = JSON.parse(fs.readFileSync(path.join(ROOT, 'vercel.json'), 'utf8'));
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp4': 'video/mp4', '.json': 'application/json', '.xml': 'application/xml', '.txt': 'text/plain' };

function shim(res) {
  res.status = c => { res.statusCode = c; return res; };
  res.json = o => { if (!res.getHeader('content-type')) res.setHeader('content-type', 'application/json; charset=utf-8'); res.end(JSON.stringify(o)); return res; };
  res.send = b => { if (!res.getHeader('content-type')) res.setHeader('content-type', typeof b === 'string' ? 'text/html; charset=utf-8' : 'application/octet-stream'); res.end(b); return res; };
  return res;
}

async function runFunction(name, req, res, url) {
  const file = path.join(ROOT, 'api', name + '.js');
  if (!/^[a-z0-9-]+$/.test(name) || !fs.existsSync(file)) { res.statusCode = 404; return res.end('No such function'); }
  const chunks = []; for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString();
  const ct = String(req.headers['content-type'] || '');
  req.body = ct.includes('application/json') ? (raw ? JSON.parse(raw) : {}) : ct.includes('application/x-www-form-urlencoded') ? querystring.parse(raw) : raw;
  req.query = Object.fromEntries(url.searchParams);
  const mod = await import(pathToFileURL(file).href);
  await mod.default(req, shim(res));
}

function serveFile(file, req, res, status = 200) {
  const stat = fs.statSync(file); const type = TYPES[path.extname(file)] || 'application/octet-stream';
  const range = req.headers.range && /bytes=(\d*)-(\d*)/.exec(req.headers.range);
  if (range) {
    const start = range[1] ? +range[1] : 0, end = range[2] ? +range[2] : stat.size - 1;
    res.writeHead(206, { 'content-type': type, 'content-range': `bytes ${start}-${end}/${stat.size}`, 'accept-ranges': 'bytes', 'content-length': end - start + 1 });
    return fs.createReadStream(file, { start, end }).pipe(res);
  }
  res.writeHead(status, { 'content-type': type, 'content-length': stat.size, 'accept-ranges': 'bytes' });
  fs.createReadStream(file).pipe(res);
}

http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    let p = decodeURIComponent(url.pathname);
    for (const r of vercel.rewrites || []) if (p === r.source) p = r.destination;
    if (p.startsWith('/api/')) return await runFunction(p.slice(5).replace(/\/$/, ''), req, res, url);
    const candidates = p === '/' ? ['index.html'] : [p.slice(1), p.slice(1) + '.html'];
    for (const c of candidates) {
      const f = path.join(PUB, c);
      if (f.startsWith(PUB) && fs.existsSync(f) && fs.statSync(f).isFile()) return serveFile(f, req, res);
    }
    serveFile(path.join(PUB, '404.html'), req, res, 404);
  } catch (err) {
    console.error(err); res.statusCode = 500; res.end('dev server error');
  }
}).listen(PORT, () => console.log(`fitzferalhunters dev → http://localhost:${PORT}  (store: ${process.env.FFH_MEMORY_STORE === '1' ? 'memory' : 'redis'}, mail: ${process.env.RESEND_API_KEY ? 'resend' : 'off'})`));
