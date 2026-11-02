// Key-value + sorted-set storage for reviews. Upstash Redis (Vercel Marketplace) in production;
// an in-memory store only for local development and tests, and only when FFH_MEMORY_STORE=1 off Vercel.
import { redis, redisConfigured } from './services.js';

const mem = globalThis.__ffhMem || (globalThis.__ffhMem = { kv: new Map(), z: new Map() });

export function kind() {
  if (redisConfigured()) return 'redis';
  if (!process.env.VERCEL && process.env.FFH_MEMORY_STORE === '1') return 'memory';
  return null;
}

export async function get(key) {
  if (kind() === 'redis') return redis('GET', key);
  return mem.kv.get(key) ?? null;
}
export async function mget(keys) {
  if (!keys.length) return [];
  if (kind() === 'redis') return redis('MGET', ...keys);
  return keys.map(k => mem.kv.get(k) ?? null);
}
export async function set(key, value) {
  if (kind() === 'redis') return redis('SET', key, value);
  mem.kv.set(key, value); return 'OK';
}
export async function zadd(key, score, member) {
  if (kind() === 'redis') return redis('ZADD', key, score, member);
  const z = mem.z.get(key) || new Map(); z.set(member, score); mem.z.set(key, z); return 1;
}
export async function zrem(key, member) {
  if (kind() === 'redis') return redis('ZREM', key, member);
  const z = mem.z.get(key); return z && z.delete(member) ? 1 : 0;
}
export async function zrevrange(key, start, stop) {
  if (kind() === 'redis') return redis('ZREVRANGE', key, start, stop);
  const z = mem.z.get(key); if (!z) return [];
  return [...z.entries()].sort((a, b) => b[1] - a[1]).slice(start, stop + 1).map(([m]) => m);
}
export function _resetMemory() { mem.kv.clear(); mem.z.clear(); }
