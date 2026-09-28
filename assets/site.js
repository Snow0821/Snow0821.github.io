
    (() => {
      const root = document.getElementById('snow-cv-portfolio');
      const download = root.querySelector('#snow-cv-download');
      const cvPDFs = { ko: download.getAttribute('href'), en: download.dataset.pdfEn };
      const tabs = Array.from(root.querySelectorAll('[data-tab]'));
      const panels = Array.from(root.querySelectorAll('[role="tabpanel"]'));
      const languageButton = root.querySelector('#snow-language');
      const live = root.querySelector('#snow-live');
      function activateTab(button) {
        for (const tab of tabs) { tab.setAttribute('aria-selected', String(tab === button)); tab.tabIndex = tab === button ? 0 : -1; }
        for (const panel of panels) panel.hidden = panel.id !== button.getAttribute('aria-controls');
      }
      for (const button of tabs) {
        button.addEventListener('click', () => activateTab(button));
        button.addEventListener('keydown', event => {
          const current = tabs.indexOf(button);
          const next = event.key === 'ArrowRight' ? (current + 1) % tabs.length
            : event.key === 'ArrowLeft' ? (current + tabs.length - 1) % tabs.length
            : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
          if (next === null) return;
          event.preventDefault();
          activateTab(tabs[next]);
          tabs[next].focus();
        });
      }
      function applyLanguage(language) {
        root.dataset.language = language;
        root.lang = language;
        document.documentElement.lang = language;
        const pdfLabel = language === 'ko' ? '국문 CV 다운로드 (PDF)' : 'Download English CV (PDF)';
        download.setAttribute('href', cvPDFs[language]);
        download.setAttribute('download', 'Choi-Soon-Ho-CV-' + language.toUpperCase() + '.pdf');
        download.setAttribute('aria-label', pdfLabel);
        download.setAttribute('title', pdfLabel);
        for (const node of root.querySelectorAll('[data-l]')) {
          node.setAttribute('aria-hidden', String(node.dataset.l !== language));
          if (!node.hasAttribute('lang')) node.lang = node.dataset.l;
        }
        languageButton.setAttribute('aria-label', language === 'ko' ? '현재 언어: 한국어. Switch to English' : 'Current language: English. 한국어로 전환');
        languageButton.setAttribute('title', language === 'ko' ? '한국어 · Switch to English' : 'English · 한국어로 전환');
        root.querySelector('[role="tablist"]').setAttribute('aria-label', language === 'ko' ? '포트폴리오' : 'Portfolio');
        for (const paper of root.querySelectorAll('.paper')) {
          const title = paper.querySelector('.paper-name').textContent;
          paper.querySelector('.paper-expand').setAttribute('aria-label', title + (language === 'ko' ? ' 상세 보기' : ' details'));
        }
      }
      languageButton.addEventListener('click', () => {
        applyLanguage(root.lang === 'ko' ? 'en' : 'ko');
        live.textContent = root.lang === 'ko' ? '한국어로 전환했습니다.' : 'Switched to English.';
      });
      for (const button of root.querySelectorAll('.fold-toggle')) {
        button.addEventListener('click', () => {
          const section = button.closest('.fold-section');
          const expand = section.dataset.expanded !== 'true';
          const panel = section.closest('[role="tabpanel"]');
          for (const sibling of panel.querySelectorAll('.fold-section')) {
            const selected = sibling === section && expand;
            sibling.dataset.expanded = String(selected);
            const control = sibling.querySelector('.fold-toggle');
            control.setAttribute('aria-expanded', String(selected));
            control.querySelector('.fold-sign').textContent = selected ? '−' : '+';
          }
          });
      }
      function closeCitations() {
        for (const toggle of root.querySelectorAll('.cite-toggle')) toggle.setAttribute('aria-expanded', 'false');
        for (const citation of root.querySelectorAll('.citation')) citation.hidden = true;
      }
      for (const paper of root.querySelectorAll('.paper')) {
        paper.querySelector('.paper-expand').addEventListener('click', () => {
          const expand = paper.dataset.open !== 'true';
          for (const item of root.querySelectorAll('.paper')) {
            const open = item === paper && expand;
            item.dataset.open = String(open);
            item.querySelector('.paper-expand').setAttribute('aria-expanded', String(open));
            item.querySelector('.expand-sign').textContent = open ? '−' : '+';
          }
          closeCitations();
          });
        paper.querySelector('.cite-toggle').addEventListener('click', event => {
          const toggle = event.currentTarget;
          const expand = toggle.getAttribute('aria-expanded') !== 'true';
          closeCitations();
          toggle.setAttribute('aria-expanded', String(expand));
          paper.querySelector('.citation').hidden = !expand;
          });
      }
      for (const citation of root.querySelectorAll('.citation')) {
        const format = citation.querySelector('.cite-format');
        const output = citation.querySelector('.cite-text');
        const status = citation.querySelector('.copy-status');
        function renderCitation() {
          const prefix = format.value === 'bibtex' ? 'snow-bib-' : 'snow-ref-';
          const source = root.querySelector('#' + prefix + citation.dataset.paper);
          output.textContent = source.content.textContent.trim();
          output.dataset.format = format.value;
          status.textContent = '';
        }
        format.addEventListener('change', renderCitation);
        renderCitation();
        citation.querySelector('.copy').addEventListener('click', async () => {
          let copied = false;
          try {
            if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
            await navigator.clipboard.writeText(output.textContent.trim());
            copied = true;
          } catch {
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(output);
            if (selection) { selection.removeAllRanges(); selection.addRange(range); }
            try { copied = document.execCommand('copy'); } catch { copied = false; }
          }
          const messages = copied
            ? { ko: '복사했습니다.', en: 'Copied.' }
            : { ko: '텍스트를 선택했습니다. 복사 메뉴 또는 Ctrl/Cmd+C를 사용하세요.', en: 'Text selected. Use the copy menu or Ctrl/Cmd+C.' };
          const pair = document.createElement('span');
          pair.className = 'pair';
          for (const language of ['ko', 'en']) {
            const text = document.createElement('span');
            text.dataset.l = language;
            text.lang = language;
            text.setAttribute('aria-hidden', String(root.lang !== language));
            text.textContent = messages[language];
            pair.append(text);
          }
          status.replaceChildren(pair);
        });
      }
      applyLanguage('ko');
    })();
