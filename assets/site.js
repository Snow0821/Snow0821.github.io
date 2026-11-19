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
