/* The three routes and the language switch are ordinary, bookmarkable links. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/site.js'), 'utf8');
const origin = 'https://example.test';

function route(lang, tab) {
  return (lang === 'en' ? '/en/' : '/') + (tab ? tab + '/' : '');
}

function attribute(markup, name) {
  const key = markup.match(new RegExp('\\s'+name+'="([^"]*)"'));
  return key ? key[1] : null;
}

for (const lang of ['ko', 'en']) {
  for (const tab of ['', 'portfolio', 'career']) {
    const url = origin + route(lang, tab);
    const html = fs.readFileSync(path.join(root, route(lang, tab), 'index.html'), 'utf8');
    const menu = html.match(/<nav\b[^>]*\bsite-nav\b[^>]*>([\s\S]*?)<\/nav>/)[1];
    const links = [...menu.matchAll(/<a\b[^>]*>/g)].map(item => item[0]);
    assert.deepEqual(links.map(link => new URL(attribute(link, 'href'), url).pathname),
      ['', 'portfolio', 'career'].map(name => route(lang, name)));
    const selected = links.filter(link => attribute(link, 'aria-current') === 'page');
    assert.equal(selected.length, 1);
    assert.equal(new URL(attribute(selected[0], 'href'), url).pathname, route(lang, tab));
    const switcher = [...html.matchAll(/<a\b[^>]+>/g)].map(item => item[0]).find(link => attribute(link, 'class')?.includes('language-link'));
    const other = lang === 'ko' ? 'en' : 'ko';
    assert.equal(attribute(switcher, 'hreflang'), other);
    assert.equal(new URL(attribute(switcher, 'href'), url).pathname, route(other, tab));
    assert.doesNotMatch(html, /role="tab(?:list|panel)?"/);
  }
}

// Run the full, shipped script to verify links kept from the single-page version.
function visit(lang, page, hash) {
  const redirects = [];
  const listeners = {};
  const language = {href: origin + route(lang === 'ko' ? 'en' : 'ko', page === 'home' ? '' : 'career')};
  const location = {hash, replace(value) { redirects.push(value); }};
  const document = {
    documentElement: {lang}, body: {dataset: {page}},
    querySelector: () => language, querySelectorAll: () => [],
    getElementById: id => ['teaching', 'credentials'].includes(id) ? {} : null,
  };
  vm.runInNewContext(source, {document, location, URL,
    window: {addEventListener(name, fn) { listeners[name] = fn; }}});
  return {location, language, listeners, redirects};
}
for (const lang of ['ko','en']) {
  for (const [hash, tab] of [['#publications','portfolio'],['#snow-panel-publications','portfolio'],
                             ['#teaching','career'],['#snow-panel-teaching','career']]) {
    assert.deepEqual(visit(lang,'home',hash).redirects, [route(lang,tab)]);
  }
  const live = visit(lang,'career','#credentials');
  assert.deepEqual(live.redirects, []);
  assert.equal(new URL(live.language.href).hash, '#credentials');
  live.location.hash = '#unknown';
  live.listeners.hashchange();
  assert.equal(new URL(live.language.href).hash, '');
  assert.deepEqual(visit(lang, 'home', '').redirects, []);
}
console.log('Static bilingual routes, bookmark redirects and language section links passed.');
