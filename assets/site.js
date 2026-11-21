/* Links, language navigation and the full career record work without JavaScript. */
(() => {
  const legacy = {
    '#publications': 'portfolio/', '#snow-panel-publications': 'portfolio/',
    '#teaching': 'career/', '#snow-panel-teaching': 'career/'
  };
  if (document.body.dataset.page === 'home' && legacy[location.hash]) {
    const english = document.documentElement.lang === 'en';
    location.replace((english ? '/en/' : '/') + legacy[location.hash]);
    return;
  }

  // Keep a reader at the same work or career category when switching languages.
  const language = document.querySelector('.language-link');
  function languageAnchor() {
    if (!language) return;
    const next = new URL(language.href);
    next.hash = document.getElementById(location.hash.slice(1)) ? location.hash : '';
    language.href = next.href;
  }
  languageAnchor();
  window.addEventListener('hashchange', languageAnchor);

  async function copy(button) {
    const target = document.getElementById(button.dataset.copy);
    const text = target.content.textContent.trim();
    const actions = button.closest('.paper-actions');
    const status = actions.querySelector('[data-copy-status]');
    const oldField = actions.querySelector('.copy-field');
    if (oldField) oldField.remove();
    status.textContent = '';
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const field = document.createElement('textarea');
      field.className = 'copy-field';
      field.value = text;
      field.readOnly = true;
      field.setAttribute('aria-label', actions.dataset.failure);
      actions.append(field);
      field.focus();
      field.select();
      let copied = false;
      try { copied = document.execCommand('copy'); } catch { /* Manual selection remains available. */ }
      if (!copied) {
        status.textContent = actions.dataset.failure;
        return;
      }
      field.remove();
      button.focus();
    }
    status.textContent = actions.dataset.success;
  }
  for (const button of document.querySelectorAll('button[data-copy]')) {
    button.addEventListener('click', () => copy(button));
  }
})();

for (const index of document.querySelectorAll('[data-work-index]')) {
  const cards = [...index.querySelectorAll('.work-entries > li')];
  const links = [...index.querySelectorAll('[data-filter]')];
  const more = index.querySelector('[data-expand]');
  const status = index.querySelector('[data-result-count]');
  const switcher = document.querySelector('.language-link');
  const validKinds = new Set(links.map(link => link.dataset.filter));
  let expanded = false;
  const featuredLimit = 5;
  const directory = document.querySelector('.work-directory');
  const detailSections = {research: document.getElementById('papers'), development: document.getElementById('projects')};

  function renderIndex() {
    const url = new URL(window.location.href);
    const requested = url.searchParams.get('type');
    let kind = validKinds.has(requested) ? requested : 'all';
    const target = document.getElementById(url.hash.slice(1));
    for (const [group, section] of Object.entries(detailSections)) {
      if (kind !== 'all' && kind !== group && section.contains(target)) {
        kind = group;
        url.searchParams.set('type', group);
        history.replaceState(null, '', url);
      }
    }
    directory.hidden = kind === 'education';
    for (const [group, section] of Object.entries(detailSections)) {
      section.hidden = kind !== 'all' && kind !== group;
      directory.querySelector('a[href="#' + section.id + '"]').hidden = section.hidden;
    }
    const matches = cards.filter(card => kind === 'all' || card.dataset.kind === kind);
    const visible = new Set(kind === 'all' && !expanded ? matches.slice(0, featuredLimit) : matches);
    for (const card of cards) card.hidden = !visible.has(card);
    for (const link of links) {
      if (link.dataset.filter === kind) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
    more.hidden = kind !== 'all' || matches.length <= featuredLimit;
    more.textContent = expanded ? index.dataset.less : index.dataset.more.replace('{count}', matches.length - visible.size);
    more.setAttribute('aria-expanded', String(expanded));
    status.textContent = index.dataset.count.replace('{shown}', visible.size).replace('{total}', matches.length);
    if (switcher) {
      const target = new URL(switcher.href);
      if (kind === 'all') target.searchParams.delete('type');
      else target.searchParams.set('type', kind);
      switcher.href = target.href;
    }
  }

  index.querySelector('[data-filters]').hidden = false;
  for (const link of links) {
    link.addEventListener('click', event => {
      if (event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const url = new URL(window.location.href);
      url.hash = '';
      if (link.dataset.filter === 'all') url.searchParams.delete('type');
      else url.searchParams.set('type', link.dataset.filter);
      if (url.href !== window.location.href) history.pushState(null, '', url);
      const language = document.querySelector('.language-link');
      if (language) { const target = new URL(language.href); target.hash = ''; language.href = target.href; }
      expanded = false;
      renderIndex();
    });
  }
  more.addEventListener('click', () => {
    expanded = !expanded;
    renderIndex();
    if (expanded) cards[featuredLimit].querySelector('a').focus();
  });
  window.addEventListener('popstate', () => { expanded = false; renderIndex(); });
  window.addEventListener('hashchange', renderIndex);
  renderIndex();
}
