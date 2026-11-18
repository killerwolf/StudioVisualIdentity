#!/usr/bin/env node
// Imprime window.STORYBOARD (poses caméra et lignes calculées par scene.html) en JSON.
// usage (racine du dépôt) : SVI_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" node out/report/notes/lyrics-chemin/proto/dump.mjs
import { createRequire } from 'node:module';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright-core');
const ROOT = process.cwd();
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': p.endsWith('.html') ? 'text/html' : p.endsWith('.js') ? 'text/javascript' : 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
await new Promise(ok => srv.listen(0, '127.0.0.1', ok));
const b = await chromium.launch({ executablePath: process.env.SVI_CHROME }); const pg = await b.newPage();
pg.on('pageerror', e => console.error('PAGE', e.message));
await pg.goto(`http://127.0.0.1:${srv.address().port}/out/report/notes/lyrics-chemin/proto/scene.html`);
await pg.evaluate(() => window.ready);
console.log(JSON.stringify(await pg.evaluate(() => window.STORYBOARD), null, 1));
await b.close(); srv.close();
