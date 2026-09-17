(() => {
  'use strict';
  const data = window.SNOW_DATA;
  const root = document.getElementById('app');
  const escape = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let lang = 'en';
  const pathLang = location.pathname.match(/^\/(en|ko)(?:\/|$)/)?.[1];
  const queryLang = new URLSearchParams(location.search).get('lang');
  let preference;
  try { preference = localStorage.getItem('snow-language'); } catch {}
  if (['en','ko'].includes(queryLang)) lang = queryLang;
  else if (pathLang) lang = pathLang;
  else if (['en','ko'].includes(preference)) lang = preference;
  const t = (en,ko) => lang === 'ko' ? ko : en;
  const tr = value => typeof value === 'string' ? value : value[lang];
  const iconArrow = '<span class="arrow" aria-hidden="true">↗</span>';
  const iconDown = '<span class="arrow" aria-hidden="true">↓</span>';
  const star = '<svg viewBox="0 0 36 36" fill="none" aria-hidden="true"><g stroke="currentColor" stroke-width="1.65"><path d="M18 1v34M3.28 9.5l29.44 17M3.28 26.5l29.44-17"/><path d="m12 5 6 6 6-6M12 31l6-6 6 6M3.7 16l8.2-2.2L9.7 5.6m22.6 14.4-8.2 2.2 2.2 8.2M9.7 30.4l2.2-8.2L3.7 20m28.6-4-8.2-2.2 2.2-8.2"/></g></svg>';
  const fileIcon = '<svg class="doc-icon" viewBox="0 0 32 40" fill="none" aria-hidden="true"><path d="M5 2h15l7 7v29H5V2Z" stroke="currentColor"/><path d="M20 2v8h7M10 19h12M10 24h12M10 29h8" stroke="currentColor"/></svg>';
  const lock = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="4" y="9" width="12" height="9" rx="2" stroke="currentColor"/><path d="M6 9V6a4 4 0 0 1 8 0v3" stroke="currentColor"/></svg>';
  const ext = (url,label,cls='textlink') => `<a class="${cls}" href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(label)} ${iconArrow}</a>`;
  const mail = (subject) => `mailto:${data.profile.email}?subject=${encodeURIComponent(subject)}`;

  function networkGraph(mode='discrete') {
    const layers = [[45,80,115,150].map(y=>[48,y+35]),[35,70,105,140,175].map(y=>[190,y+35]),[65,105,145].map(y=>[330,y+35])];
    let content = '<defs><pattern id="dots" width="17" height="17" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".65" fill="#668669" opacity=".26"/></pattern></defs><rect width="380" height="265" fill="url(#dots)"/>';
    layers.slice(0,-1).forEach((layer,l)=>layer.forEach(([x,y],i)=>layers[l+1].forEach(([nx,ny],j)=>{
      const active = (i*2+j+l)%3 === 0;
      content += `<path class="network-line ${active?'active':''}" d="M${x+15} ${y} C${x+64} ${y},${nx-65} ${ny},${nx-15} ${ny}"/>`;
    })));
    let n=0;
    layers.forEach((layer,l)=>layer.forEach(([x,y],i)=>{
      const value=[1,0,-1,1,0,-1,1,0,1,-1,1,0][n++];
      const label=mode==='discrete' ? (value===1?'+1':String(value)) : ['.73','.18','−.42','.61','.09','−.27','.88','.34','.56','−.31','.92','.14'][n-1];
      content += `<circle class="network-node ${value===1?'positive':value===-1?'negative':''}" cx="${x}" cy="${y}" r="${mode==='discrete'?16:19}"/><text class="network-val ${value===1?'dark':''}" x="${x}" y="${y+1}" style="font-size:${mode==='discrete'?12:10}px">${label}</text>`;
    }));
    content += `<text class="network-label" x="48" y="252" text-anchor="middle">INPUT</text><text class="network-label" x="190" y="252" text-anchor="middle">CONNECTIONS</text><text class="network-label" x="330" y="252" text-anchor="middle">OUTPUT</text>`;
    return content;
  }

  function documents() {
    return data.documents.map(doc=>`<article class="document-card"><div class="doc-top">${fileIcon}<span class="doc-label">${doc.language} / PDF</span></div><h3>${escape(tr(doc.title))}</h3><p>${escape(tr(doc.subtitle))}</p><a class="download" data-download="${escape(doc.filename)}" href="${window.SNOW_OFFLINE?'#documents':'/downloads/'+escape(doc.filename)}" download="${escape(doc.filename)}"><span>${t('Download draft PDF','초안 PDF 다운로드')}</span>${iconDown}</a></article>`).join('');
  }
  function research() {
    return data.research.map(r=>`<details class="research-card" id="research-${r.id}"><summary><span class="year">${r.year}</span><div><div class="research-topline">${escape(tr(r.category))}</div><h3>${escape(tr(r.title))}</h3><p class="research-summary">${escape(tr(r.summary))}</p><div class="tag-list">${r.tags.map(tag=>`<span class="tag">${escape(tag)}</span>`).join('')}</div></div><span class="research-more" aria-hidden="true">+</span></summary><div class="research-body"><div class="research-detail-grid"><div><h4>${t('The question','연구 질문')}</h4><p>${escape(tr(r.problem))}</p></div><div><h4>${t('The approach','접근 방법')}</h4><p>${escape(tr(r.approach))}</p></div></div><div class="evidence"><h4>${t('Research & materials','연구 자료')}</h4><p>${escape(tr(r.evidence))}</p></div><div class="research-links">${ext(r.github,t('Explore on GitHub','GitHub에서 보기'))}${r.paper?ext(r.paper,t('Read paper','논문 보기')):''}</div></div></details>`).join('');
  }

  function render() {
    document.documentElement.lang=lang;
    document.title = t('Soon Ho Choi · AI Research & Teaching','최순호 · AI 연구와 강의');
    root.innerHTML=`
      <a class="skip" href="#main">${t('Skip to content','본문으로 건너뛰기')}</a>
      <div class="draftbar">${t('PORTFOLIO PREVIEW · CONTENT & DOCUMENTS AWAITING REVIEW','포트폴리오 미리보기 · 소개 내용과 문서는 검토 중인 초안입니다')}</div>
      <header class="header"><div class="wrap header-inner"><a class="brand" href="#main" aria-label="${t('Snow home','Snow 홈')}">${star}<span>snow.</span></a><nav class="nav" id="nav" aria-label="${t('Main navigation','주요 메뉴')}"><a href="#research">${t('Research','연구')}</a><a href="#teaching">${t('Teaching','강의')}</a><a href="#notes">${t('Notes','노트')}</a><a href="#contact">${t('Contact','연락')}</a></nav><div class="header-actions"><div class="language" aria-label="${t('Language','언어')}"><button type="button" data-lang="en" aria-pressed="${lang==='en'}" lang="en">EN</button><button type="button" data-lang="ko" aria-pressed="${lang==='ko'}" lang="ko">KO</button></div><button type="button" class="header-cv" data-open="downloads-dialog">${t('Get CV','이력서')} ↗</button><button type="button" class="menu-toggle" aria-controls="nav" aria-expanded="false">${t('Menu','메뉴')} +</button></div></div></header>
      <main id="main">
        <section class="wrap hero" aria-labelledby="hero-title"><div class="hero-copy"><div class="hero-top eyebrow"><span class="status-dot"></span>${escape(tr(data.profile.title))}</div><h1 id="hero-title">${t('Intelligence,<br>in <em>discrete</em><br>form.','지능을,<br><em>이산적인</em><br>형태로.')}</h1><p class="hero-intro"><strong>${t('I’m Soon Ho Choi.','AI 연구자이자 강사, 최순호입니다.')}</strong> ${escape(tr(data.profile.bio))}</p><div class="hero-actions"><a href="#research" class="button">${t('Explore research','연구 살펴보기')}<span class="arrow" aria-hidden="true">↘</span></a><a href="#teaching" class="textlink">${t('Teaching & workshops','강의 · 워크숍')} ${iconArrow}</a></div><div class="hero-foot"><span>${t('BASED IN SOUTH KOREA','대한민국에서 연구하고 가르칩니다')}</span><span>RESEARCH × EDUCATION</span></div></div><div class="network-panel"><div class="network-head"><span>DISCRETE REPRESENTATIONS</span><span class="subtle">FIG. 01</span></div><svg class="network" viewBox="0 0 380 265" role="img" aria-label="${t('Illustrative neural network with binary and ternary states','이진·삼진 상태로 표현한 신경망 개념도')}">${networkGraph()}</svg><div class="network-bottom"><div class="network-mode" role="group" aria-label="${t('Illustration mode','개념도 표현 방식')}"><button type="button" data-mode="continuous" aria-pressed="false">${t('Continuous','연속')}</button><button type="button" data-mode="discrete" aria-pressed="true">${t('Discrete','이산')}</button></div><span class="network-caption">${t('An illustration, not an experiment.','실험 결과가 아닌 개념도입니다.')}</span></div></div></section>
        <div class="wrap"><div class="intro-strip"><span class="eyebrow muted">${t('THE QUESTION BEHIND MY WORK','연구의 출발점')}</span><p>${t('What can we learn when we change<br>the way a neural network represents the world?','신경망이 세상을 표현하는 방식을 바꾸면,<br>어떤 새로운 학습이 가능할까요?')}</p></div></div>
        <section class="wrap section" id="research"><div class="section-head"><div><p class="eyebrow">01 / ${t('SELECTED RESEARCH','연구')}</p><h2>${t('Fewer states.<br>New possibilities.','더 적은 상태,<br>새로운 가능성.')}</h2></div><p class="section-intro">${t('Logic gates, quantized representations, and the path toward integer neural networks. Open a project to read the question, approach, and available materials.','논리 게이트, 양자화 표현, 그리고 정수 신경망을 향한 탐구. 각 연구를 펼치면 질문과 접근 방법, 공개 자료를 볼 수 있습니다.')}</p></div><div class="research-list">${research()}</div><div class="research-footer">${ext(data.profile.scholar,'Google Scholar')}${ext(data.profile.github,'GitHub')}</div></section>
        <section class="teaching" id="teaching"><div class="wrap section"><div class="teaching-grid"><div><p class="eyebrow">02 / ${t('TEACHING & WORKSHOPS','강의 · 워크숍')}</p><h2>${t('Understand it.<br>Build with it.','이해하고,<br>직접 만듭니다.')}</h2><p class="teaching-copy">${t('From the first line of code to a working project. I connect computer science foundations with practical AI, one achievable step at a time.','첫 코드 한 줄부터 작동하는 프로젝트까지. 컴퓨터과학의 기초와 실용적인 AI 활용을, 하나씩 달성할 수 있는 단계로 연결합니다.')}</p><a class="button" href="${mail(t('Teaching / workshop inquiry','출강 / 워크숍 문의'))}">${t('Discuss a workshop','출강 문의하기')} ${iconArrow}</a><p class="muted" style="font-size:11px;margin-top:21px">${t('Python · C++ · Algorithms · Practical AI','Python · C++ · 알고리즘 · AI 활용')}</p></div><div>${data.teaching.map((course,i)=>`<article class="course"><span class="course-index">0${i+1}</span><div><h3>${escape(tr(course.title))}</h3><p>${escape(tr(course.description))}</p><div class="course-tags">${escape(tr(course.tags))}</div></div></article>`).join('')}</div></div><div class="about-row"><div><p class="eyebrow">${t('ACADEMIC BACKGROUND','학력')}</p><h3 style="margin-top:13px">${t('A foundation<br>in computer science.','컴퓨터과학에서<br>인공지능으로.')}</h3></div><div class="education-list">${data.education.map(edu=>`<div class="education-item"><span class="eyebrow">${escape(edu.period)}</span><h4>${escape(tr(edu.institution))}</h4><p>${escape(tr(edu.degree))}</p></div>`).join('')}</div></div></div></section>
        <section class="wrap section documents" id="documents"><div class="section-head"><div><p class="eyebrow">03 / ${t('CV & PROFILES','이력서 · 소개서')}</p><h2>${t('The details, in a document.','필요한 이력을, 문서로.')}</h2></div><p class="section-intro">${t('Research, experience, and teaching.<br>Choose the document that fits your purpose.','연구, 경력, 강의 분야를 정리했습니다.<br>목적에 맞는 문서를 선택하세요.')}</p></div><div class="document-grid">${documents()}</div><p class="documents-note">${t('Review copies · September 2026. Please verify the details before submitting.','2026년 9월 검토용 초안입니다. 외부 제출 전 세부 이력을 확인해 주세요.')}</p></section>
        <section class="wrap section notes-section" id="notes"><div class="notes-grid"><div><p class="eyebrow muted">04 / ${t('FIELD NOTES','배움의 기록')}</p><h2>${t('Questions worth keeping.','남겨두고 싶은 질문들.')}</h2><p class="notes-copy">${t('A place for ideas, reading, and lessons from making things. Selected notes will be shared here.','공부하며 만난 아이디어, 읽은 것들, 직접 만들며 배운 것들을 기록합니다. 정리한 노트를 이곳에 공유할 예정입니다.')}</p></div><div class="notes-empty"><div class="notes-mark">${star}</div><div><h3>${t('A notebook, just beginning.','새로운 노트의 첫 페이지.')}</h3><p>${t('No public notes yet. Research materials are available in the projects above.','아직 공개한 노트가 없습니다. 연구 자료는 위의 각 프로젝트에서 확인할 수 있습니다.')}</p><a class="textlink" href="#research">${t('Start with the research','연구부터 살펴보기')} ${iconArrow}</a></div></div></div></section>
        <section class="contact-section" id="contact"><div class="wrap contact-grid"><div><p class="eyebrow">${t('LET’S TALK','함께 이야기해요')}</p><h2>${t('A question?<br>A collaboration?','연구 이야기부터<br>새로운 수업까지.')}</h2></div><div class="contact-links"><p class="contact-desc">${t('For research conversations, collaborations, and teaching inquiries, email is the best place to start.','연구에 관한 대화, 협업 제안, 출강 문의를 환영합니다. 이메일로 편하게 연락해 주세요.')}</p><a class="email-link" href="mailto:${escape(data.profile.email)}">${escape(data.profile.email)} ${iconArrow}</a><div class="socials">${ext(data.profile.github,'GitHub','')}${ext(data.profile.linkedin,'LinkedIn','')}${ext(data.profile.scholar,'Google Scholar','')}</div><button class="copy-email" type="button">${t('Copy email address','이메일 주소 복사')}</button></div></div></section>
      </main><footer class="footer"><div class="wrap"><div class="footer-inner"><p><span class="footer-name">© 2026 ${escape(data.profile.name)}</span> · ${t('Research. Teaching. Learning.','연구하고, 가르치고, 배웁니다.')}</p><button type="button" class="footer-private" data-open="workspace-dialog">${lock}${t('Private workspace','개인 작업 공간')}</button></div></div></footer>
      <dialog class="dialog" id="downloads-dialog" aria-labelledby="downloads-title"><div class="dialog-inner"><div class="dialog-header"><div><p class="eyebrow muted" style="margin-bottom:12px">CV & PROFILES</p><h2 id="downloads-title">${t('Choose your document.','필요한 문서를 선택하세요.')}</h2></div><button type="button" class="dialog-close" data-close aria-label="${t('Close','닫기')}">×</button></div><div class="document-grid">${documents()}</div><p style="margin-top:20px">${t('All three PDFs are review copies awaiting approval.','세 문서 모두 승인 전 검토용 초안입니다.')}</p></div></dialog>
      <dialog class="dialog" id="workspace-dialog" aria-labelledby="workspace-title"><div class="dialog-inner"><div class="dialog-header"><div><p class="eyebrow muted" style="margin-bottom:12px">PRIVATE WORKSPACE</p><h2 id="workspace-title">${t('A space of your own.','나만의 기록 공간.')}</h2></div><button type="button" class="dialog-close" data-close aria-label="${t('Close','닫기')}">×</button></div><p>${t('Study notes, journals, and unpublished drafts belong in a separate space protected by your account.','공부 노트, 일기, 미공개 초안은 본인 계정으로 보호하는 별도 공간에서 관리합니다.')}</p><div class="workspace-detail"><strong>${t('Account connection required','계정 인증 연결 대기')}</strong><p>${t('The private editor is not active in this preview. No private notes are included or stored in this page.','이번 미리보기에서는 비공개 편집기가 활성화되지 않았습니다. 이 페이지에 비공개 기록을 포함하거나 저장하지 않습니다.')}</p></div>${ext('https://github.com/Snow0821/Snow0821.github.io',t('Open private repository','비공개 저장소 열기'))}</div></dialog><div class="toast" role="status" aria-live="polite"></div>`;
    attach();
  }

  function attach() {
    document.querySelectorAll('[data-lang]').forEach(button=>button.addEventListener('click',()=>{
      const y=window.scrollY;
      lang=button.dataset.lang;
      try { localStorage.setItem('snow-language',lang); } catch {}
      if(location.protocol !== 'file:') {
        document.cookie=`snow_lang=${lang}; Max-Age=31536000; Path=/; SameSite=Lax${location.protocol==='https:'?'; Secure':''}`;
        const url=new URL(location.href);
        if(/^\/(en|ko)\//.test(url.pathname)) url.pathname=url.pathname.replace(/^\/(en|ko)\//,`/${lang}/`);
        url.searchParams.set('lang',lang);
        history.replaceState(null,'',url);
      }
      render();window.scrollTo(0,y);
      document.querySelector(`[data-lang="${lang}"]`).focus({preventScroll:true});
    }));
    document.querySelector('.menu-toggle').addEventListener('click',event=>{
      const open=event.currentTarget.getAttribute('aria-expanded')!=='true';
      event.currentTarget.setAttribute('aria-expanded',String(open));
      document.querySelector('.nav').classList.toggle('open',open);
    });
    document.querySelectorAll('.nav a').forEach(a=>a.addEventListener('click',()=>{
      document.querySelector('.nav').classList.remove('open');
      document.querySelector('.menu-toggle').setAttribute('aria-expanded','false');
    }));
    document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
      document.querySelector('.network').innerHTML=networkGraph(button.dataset.mode);
      document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    }));
    document.querySelectorAll('[data-open]').forEach(button=>button.addEventListener('click',()=>document.getElementById(button.dataset.open).showModal()));
    document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>button.closest('dialog').close()));
    document.querySelectorAll('dialog').forEach(dialog=>dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();}));
    document.querySelectorAll('[data-download]').forEach(a=>a.addEventListener('click',event=>{
      const encoded=window.SNOW_DOWNLOADS?.[a.dataset.download];
      if(!encoded)return;
      event.preventDefault();
      const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));
      const url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));
      const link=document.createElement('a');link.href=url;link.download=a.dataset.download;
      document.body.appendChild(link);link.click();link.remove();
      setTimeout(()=>URL.revokeObjectURL(url),30000);
    }));
    document.querySelector('.copy-email').addEventListener('click',async()=>{
      try {
        if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(data.profile.email);
        notify(t('Email address copied.','이메일 주소를 복사했습니다.'));
      } catch {
        notify(t('Email: '+data.profile.email,'이메일: '+data.profile.email));
      }
    });
  }
  let toastTimer;
  function notify(message){const toast=document.querySelector('.toast');toast.textContent=message;toast.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('visible'),3500);}
  render();
})();
