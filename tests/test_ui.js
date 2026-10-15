/* Exercise career disclosure state, independent buttons, and translated labels. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/site.js'), 'utf8');
const messages = {
  ko: {expand_career: '{title} 세부 이력 펼치기', collapse_career: '{title} 세부 이력 접기'},
  en: {expand_career: 'Expand details for {title}', collapse_career: 'Collapse details for {title}'},
};
const panels = {};
const languageListeners = [];
const buttons = ['education', 'development'].map(id => {
  const attrs = {'aria-expanded': 'false', 'aria-controls': id};
  const listeners = {};
  const sign = {textContent: '+'};
  panels[id] = {hidden: true};
  return {
    attrs, listeners, sign,
    closest: () => ({querySelector: selector => ({textContent: selector.includes('"ko"') ? '과정' : 'Course'})}),
    getAttribute: key => attrs[key],
    setAttribute: (key, value) => { attrs[key] = value; },
    querySelector: () => sign,
    addEventListener: (type, callback) => {listeners[type] = callback;},
  };
});
const root = {lang: 'ko', querySelectorAll: () => buttons,
  addEventListener: (type, callback) => {assert.equal(type, 'languagechange'); languageListeners.push(callback);}};
const message = (key, values) => messages[root.lang][key].replace('{title}', values.title);
const start = source.indexOf('  function initCareerDetails()');
const end = source.indexOf('  function initPublications()', start);
assert.ok(start >= 0 && end > start);
vm.runInNewContext(source.slice(start, end) + '\ninitCareerDetails();', {root, message, document: {getElementById: id => panels[id]}});
languageListeners.forEach(callback => callback());
assert.equal(buttons[0].attrs['aria-label'], '과정 세부 이력 펼치기');
buttons[0].listeners.click();
assert.equal(buttons[0].attrs['aria-expanded'], 'true');
assert.equal(buttons[0].sign.textContent, '−');
assert.equal(panels.education.hidden, false);
assert.equal(panels.development.hidden, true);
root.lang = 'en'; languageListeners.forEach(callback => callback());
assert.equal(buttons[0].attrs['aria-label'], 'Collapse details for Course');
assert.equal(buttons[1].attrs['aria-label'], 'Expand details for Course');
buttons[0].listeners.click();
assert.equal(buttons[0].attrs['aria-expanded'], 'false');
assert.equal(buttons[0].sign.textContent, '+');
assert.equal(panels.education.hidden, true);
for (let index = 0; index < 6; index++) buttons[1].listeners.click();
assert.equal(buttons[1].attrs['aria-expanded'], 'false');
assert.equal(panels.development.hidden, true);
buttons[0].attrs['data-title-en'] = 'Program · Course';
languageListeners.forEach(callback => callback());
assert.equal(buttons[0].attrs['aria-label'], 'Expand details for Program · Course');
console.log('Career disclosure tests passed: open, close, repeated clicks, independent state, KO/EN labels.');
