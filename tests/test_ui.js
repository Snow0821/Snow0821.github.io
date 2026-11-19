/* Exercise the delivered clipboard handler, including both failure paths. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/site.js'), 'utf8');

function fixture(writeText, execCommand) {
  const markup = {
    ref: 'Choi and Kim. Learning to Wire. IJCNN 2026.',
    bib: '@inproceedings{choi2026,\n  title={Learning to Wire}\n}',
  };
  const status = {textContent: ''};
  const fields = [];
  const actions = {
    dataset: {success: 'Copied', failure: 'Select the text to copy.'},
    querySelector: key => key === '[data-copy-status]' ? status : fields.at(-1),
    append: field => fields.push(field),
  };
  const buttons = Object.keys(markup).map(key => ({
    dataset: {copy:key}, closest: selector => selector === '.paper-actions' ? actions : null,
    addEventListener(name, fn) { if (name === 'click') this.click = fn; },
    focus() { this.focused = true; },
  }));
  const document = {
    body: {dataset: {page: 'work'}}, documentElement: {lang: 'en'},
    querySelector: () => null,
    querySelectorAll: selector => selector === 'button[data-copy]' ? buttons : [],
    getElementById: id => markup[id] ? {content: {textContent: ' ' + markup[id] + ' '}} : null,
    execCommand,
    createElement(tag) {
      assert.equal(tag,'textarea');
      const field = {attrs:{},
        setAttribute(key, value) { this.attrs[key] = value; },
        focus() { this.focused = true; }, select() { this.selected = true; },
        remove() { fields.splice(fields.indexOf(this), 1); },
      };
      return field;
    },
  };
  vm.runInNewContext(source, {document, location:{hash:''}, URL, navigator:{clipboard:writeText ? {writeText} : undefined},
    window:{addEventListener(){}}});
  return {buttons, markup, status, fields};
}

(async () => {
  const writes = [];
  const modern = fixture(async text => { writes.push(text); }, () => assert.fail('unexpected fallback'));
  await modern.buttons[0].click();
  await modern.buttons[1].click();
  assert.deepEqual(writes, [modern.markup.ref, modern.markup.bib]);
  assert.equal(modern.status.textContent, 'Copied');
  assert.equal(modern.fields.length, 0);

  const fallback = fixture(undefined, command => { assert.equal(command, 'copy'); return true; });
  await fallback.buttons[0].click();
  assert.equal(fallback.status.textContent, 'Copied');
  assert.equal(fallback.fields.length, 0);
  assert.equal(fallback.buttons[0].focused, true);

  const denied = fixture(async () => { throw new Error('Denied'); }, () => false);
  await denied.buttons[0].click();
  await denied.buttons[1].click();
  assert.equal(denied.fields.length, 1);
  const field = denied.fields[0];
  assert.equal(field.value, denied.markup.bib);
  assert.ok(field.readOnly && field.focused && field.selected);
  assert.ok(field.attrs['aria-label']);
  assert.equal(denied.status.textContent, 'Select the text to copy.');
  console.log('Clipboard, fallback and accessible manual selection passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
