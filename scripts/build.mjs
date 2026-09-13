import { readFile, writeFile, mkdir, cp, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(await readFile(path.join(root,'content/profile.json'),'utf8'));
const css=await readFile(path.join(root,'src/style.css'),'utf8');
const app=await readFile(path.join(root,'src/app.js'),'utf8');
// Explicitly select public fields. Source ledgers and private content never enter the build.
const clean=JSON.parse(JSON.stringify(data,(key,value)=>key==='source'?undefined:value));
const json=JSON.stringify(clean).replace(/</g,'\\u003c');
const js=`window.SNOW_DATA=${json};\n${app}`;
const shell=(style,script,language='en')=>`<!DOCTYPE html>\n<html lang="${language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><meta name="color-scheme" content="light"><meta name="theme-color" content="#183d32"><meta name="description" content="Soon Ho Choi — research in discrete neural networks and teaching in AI and programming."><title>Soon Ho Choi · AI Research & Teaching</title>${style}</head><body><div id="app"></div><noscript><div class="noscript"><h1>Soon Ho Choi</h1><p>AI researcher and instructor. Please enable JavaScript to use this portfolio preview.</p><a href="mailto:sosaror@gmail.com">sosaror@gmail.com</a></div></noscript>${script}</body></html>`;
await rm(path.join(root,'dist'),{recursive:true,force:true});
await mkdir(path.join(root,'dist'),{recursive:true});
await cp(path.join(root,'public'),path.join(root,'dist'),{recursive:true});
await writeFile(path.join(root,'dist/style.css'),css);
await writeFile(path.join(root,'dist/app.js'),js);
for(const language of ['en','ko']){
  await mkdir(path.join(root,'dist',language),{recursive:true});
  await writeFile(path.join(root,'dist',language,'index.html'),shell('<link rel="stylesheet" href="/style.css">','<script src="/app.js" defer></script>',language));
}
await writeFile(path.join(root,'dist/index.html'),shell('<link rel="stylesheet" href="/style.css">','<script src="/app.js" defer></script>'));
await writeFile(path.join(root,'dist/404.html'),'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><title>Page not found · Snow</title><body style="padding:8%;background:#f7f6f0;color:#183d32;font:18px Georgia"><h1>Page not found.</h1><p><a href="/">Return to the portfolio</a></p></body></html>');
await writeFile(path.join(root,'dist/robots.txt'),'User-agent: *\nDisallow: /\n');
const embedded={};
for(const doc of data.documents){embedded[doc.filename]=(await readFile(path.join(root,'public/downloads',doc.filename))).toString('base64');}
let portableCSS=css;
try {const font=await readFile(path.join(root,'public/fonts/snow-kr.woff'));portableCSS=css.replace("url('./fonts/snow-kr.woff')",`url('data:font/woff;base64,${font.toString('base64')}')`);}catch{throw new Error('Missing Korean web font');}
await mkdir(path.join(root,'preview'),{recursive:true});
await writeFile(path.join(root,'preview/Snow-Portfolio-Preview.html'),shell(`<style>${portableCSS}</style>`,`<script>window.SNOW_OFFLINE=true;window.SNOW_DOWNLOADS=${JSON.stringify(embedded)};${js.replace(/<\/script/gi,'<\\/script')}</script>`));
console.log('Built public site and self-contained preview with three PDF downloads.');
