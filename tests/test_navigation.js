/* Pure UI logic regression: no browser rendering is implied by these checks. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/site.js'), 'utf8');
const page = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
function moduleBody(name, next) { const a=source.indexOf(`  function ${name}()`); const b=source.indexOf(`  function ${next}()`,a); assert.ok(a>=0 && b>a); return source.slice(a,b)+`\n${name}();`; }
function control(attrs={}) { return {attrs,listeners:{},dataset:{},setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k];},addEventListener(k,f){this.listeners[k]=f;},focus(){this.focused=true;}}; }
// Native tablist keyboard navigation and repeat/back transitions.
{
 const tabs=['home','publications','teaching'].map(id=>control({'aria-controls':id}));
 const panels=tabs.map(t=>({id:t.attrs['aria-controls'],hidden:false}));
 const root={querySelectorAll:s=>s==='[data-tab]'?tabs:panels};
 vm.runInNewContext(moduleBody('initTabs','initDisclosures'),{root});
 const key=(tab,key)=>tab.listeners.keydown({key,preventDefault(){}});
 tabs[0].listeners.click();
 key(tabs[0],'ArrowRight');assert.equal(tabs[1].attrs['aria-selected'],'true');assert.equal(panels[1].hidden,false);
 key(tabs[1],'End');assert.equal(tabs[2].attrs['aria-selected'],'true');
 key(tabs[2],'ArrowRight');assert.equal(tabs[0].attrs['aria-selected'],'true');
 key(tabs[0],'ArrowLeft');assert.equal(tabs[2].attrs['aria-selected'],'true');
 key(tabs[2],'Home');assert.equal(tabs[0].attrs['aria-selected'],'true');
 for(let i=0;i<5;i++)tabs[1].listeners.click();
 assert.equal(tabs[1].tabIndex,0);assert.equal(panels.filter(p=>!p.hidden).length,1);
}
// Narrow-layout accordion logic retains independent page groups.
{
 const sections=Array.from({length:3},()=>{const b=control();b.sign={textContent:'+'};b.querySelector=()=>b.sign;return {dataset:{expanded:'false'},button:b,querySelector:()=>b};});
 const root={querySelectorAll:()=>[{querySelectorAll:()=>sections}]};
 vm.runInNewContext(moduleBody('initDisclosures','initCareerDetails'),{root});
 sections[0].button.listeners.click();assert.equal(sections[0].dataset.expanded,'true');
 sections[1].button.listeners.click();assert.equal(sections[0].dataset.expanded,'false');assert.equal(sections[1].dataset.expanded,'true');
 sections[1].button.listeners.click();assert.equal(sections[1].dataset.expanded,'false');
 assert.equal(sections[1].button.sign.textContent,'+');
}
// Both language states update download, accessibility, hidden translations and document language.
{
 const config=JSON.parse(page.match(/<script type="application\/json" id="snow-config">([\s\S]+?)<\/script>/)[1]);
 const nodes=['ko','en','ko','en'].map(l=>Object.assign(control(),{dataset:{l}}));
 const button=control(),download=control(),email=control(),tablist=control(),live={textContent:''};
 const root={lang:'ko',dataset:{},querySelectorAll:()=>nodes,querySelector:s=>s==='.contact-email'?email:tablist,dispatchEvent(e){this.event=e;}};
 const document={documentElement:{lang:'ko'},getElementById:id=>({'snow-language':button,'snow-cv-download':download,'snow-live':live})[id]};
 const message=(key,values={},language=root.lang)=>config.messages[language][key].replace(/\{(\w+)\}/g,(_,k)=>values[k]);
 const a=source.indexOf('  function initLanguage()');const b=source.indexOf('\n  initTabs();',a);
 vm.runInNewContext(source.slice(a,b)+'\ninitLanguage();',{root,config,message,document,CustomEvent:class{constructor(type,detail){this.type=type;this.detail=detail;}}});
 assert.equal(download.href,'assets/Choi-Soon-Ho-CV-KO.pdf');
 button.listeners.click();assert.equal(root.lang,'en');assert.equal(document.documentElement.lang,'en');assert.equal(download.href,'assets/Choi-Soon-Ho-CV-EN.pdf');assert.equal(nodes[0].hidden,true);assert.equal(nodes[1].hidden,false);
 button.listeners.click();assert.equal(root.lang,'ko');assert.equal(download.download,'Choi-Soon-Ho-CV-KO.pdf');assert.equal(nodes[0].hidden,false);assert.equal(nodes[1].hidden,true);assert.ok(download.attrs['aria-label']);
}
console.log('Navigation logic passed: Arrow/Home/End tabs, repeated switching, accordion, KO/EN and PDF download states.');
