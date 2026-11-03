#!/usr/bin/env node
'use strict';

/**
 * Solis beeldserver
 * Opent het echte dashboard van Solis voor Homey in een onzichtbare browser en
 * levert elke pagina als afbeelding aan de Kodi-add-on. Zo ziet Kodi precies
 * hetzelfde als de Mac of de webversie.
 *
 * Gebruik:  node solis-beeld.js http://IP-VAN-JE-HOMEY:8765
 * Opties (omgevingsvariabelen):
 *   POORT=8780        poort van deze server
 *   VERS=8            hoeveel seconden een afbeelding vers blijft
 *   DONKER_VAN=18     vanaf dit uur donkere weergave (als het dashboard op "auto" staat)
 *   DONKER_TOT=7      tot dit uur
 */

const http = require('http');
const { chromium } = require('playwright');

const DASH = String(process.env.DASH || process.argv[2] || '').replace(/\/+$/, '');
const POORT = Number(process.env.POORT || 8780);
const VERS = Number(process.env.VERS || 8) * 1000;
const DONKER_VAN = Number(process.env.DONKER_VAN || 18);
const DONKER_TOT = Number(process.env.DONKER_TOT || 7);
const STANDAARD = ['zon', 'stroom', 'meer', 'inzicht', 'overzicht', 'dynamisch', 'verbruik', 'slim', 'instel'];

if (!DASH) {
  console.error('Geef het adres van het dashboard mee, bijvoorbeeld:\n  node solis-beeld.js http://192.168.178.20:8765');
  process.exit(1);
}

let browser = null;
let pages = STANDAARD.slice();
const cache = {}; // id -> { buf, at, busy, page }

function donker() {
  const h = new Date().getHours();
  return DONKER_VAN > DONKER_TOT ? (h >= DONKER_VAN || h < DONKER_TOT) : (h >= DONKER_VAN && h < DONKER_TOT);
}

async function haalPaginas() {
  try {
    const res = await fetch(DASH + '/config');
    const c = await res.json();
    if (Array.isArray(c.pages) && c.pages.length) pages = c.pages.filter((p) => STANDAARD.indexOf(p) >= 0);
  } catch (e) { /* standaardlijst */ }
}

async function zorgVoorBrowser() {
  if (browser && browser.isConnected()) return browser;
  for (const k of Object.keys(cache)) { cache[k].page = null; }
  console.log('Browser starten...');
  browser = await chromium.launch();
  browser.on('disconnected', () => { console.log('Browser is gestopt. Hij wordt bij het volgende verzoek opnieuw gestart.'); browser = null; });
  return browser;
}

async function openPagina(id) {
  await zorgVoorBrowser();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await ctx.addInitScript((thema) => { try { localStorage.setItem('solisThema', thema); } catch (e) { /* niets */ } }, id);
  const page = await ctx.newPage();
  await page.goto(DASH + '/', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(1500);
  return page;
}

async function render(id) {
  const c = cache[id] || (cache[id] = { buf: null, at: 0, busy: null, page: null });
  if (c.busy) return c.busy;
  c.busy = (async () => {
    try {
      await zorgVoorBrowser();
      if (!c.page) c.page = await openPagina(id);
      await c.page.emulateMedia({ colorScheme: donker() ? 'dark' : 'light' });
      await c.page.waitForTimeout(350);
      c.buf = await c.page.screenshot({ type: 'jpeg', quality: 92 });
      c.at = Date.now();
    } catch (e) {
      console.error('Beeld maken mislukt voor ' + id + ': ' + e.message);
      try { if (c.page) await c.page.context().close(); } catch (x) { /* niets */ }
      c.page = null;
      throw e;
    } finally { c.busy = null; }
    return c.buf;
  })();
  return c.busy;
}

async function beeld(id) {
  const c = cache[id];
  if (c && c.buf && Date.now() - c.at < VERS) return c.buf;
  try { return await render(id); } catch (e) { if (c && c.buf) return c.buf; throw e; }
}

const server = http.createServer(async (req, res) => {
  const url = req.url.split('?')[0];
  try {
    if (url === '/pages.json') {
      res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
      return res.end(JSON.stringify({ pages, donker: donker() }));
    }
    const m = /^\/page\/([a-z]+)\.jpg$/.exec(url);
    if (m && STANDAARD.indexOf(m[1]) >= 0) {
      const buf = await beeld(m[1]);
      res.writeHead(200, { 'Content-Type': 'image/jpeg', 'Cache-Control': 'no-store', 'Content-Length': buf.length });
      return res.end(buf);
    }
    res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('Solis beeldserver draait. Pagina\'s: ' + pages.join(', ') + '\nVoorbeeld: /page/' + pages[0] + '.jpg');
  } catch (e) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('Fout: ' + e.message);
  }
});

(async () => {
  await haalPaginas();
  await zorgVoorBrowser();
  server.on('error', (e) => {
    if (e.code === 'EADDRINUSE') console.error('Poort ' + POORT + ' is al in gebruik. De beeldserver draait waarschijnlijk al in een ander Terminal-venster.\nStop hem met:  kill $(lsof -ti :' + POORT + ')\nof gebruik een andere poort:  POORT=8790 node solis-beeld.js ' + DASH);
    else console.error('Serverfout: ' + e.message);
    process.exit(1);
  });
  server.listen(POORT, '0.0.0.0', () => {
    console.log('Solis beeldserver draait op poort ' + POORT + ' en leest ' + DASH);
    console.log('Pagina\'s: ' + pages.join(', '));
    console.log('Vul in Kodi dit adres in van deze computer, poort ' + POORT + '. Laat dit venster open.');
  });
  // alvast de eerste pagina warm maken
  beeld(pages[0]).catch(() => {});
  const stop = async () => { try { if (browser) await browser.close(); } catch (e) { /* niets */ } process.exit(0); };
  process.on('SIGINT', stop); process.on('SIGTERM', stop);
})().catch((e) => { console.error('Starten mislukt: ' + e.message); process.exit(1); });
