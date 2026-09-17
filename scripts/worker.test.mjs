import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import worker,{localeFor} from '../src/worker.js';
test('explicit language and saved preference override country; missing country uses English',()=>{
  const request=(url,country,cookie)=>{const r=new Request(url,{headers:cookie?{Cookie:cookie}:undefined});r.cf={country};return r;};
  assert.equal(localeFor(request('https://snow.test/','KR')),'ko');
  assert.equal(localeFor(request('https://snow.test/',undefined)),'en');
  assert.equal(localeFor(request('https://snow.test/','KR','snow_lang=en')),'en');
  assert.equal(localeFor(request('https://snow.test/?lang=ko','US','snow_lang=en')),'ko');
  assert.equal(localeFor(request('https://snow.test/?lang=invalid','US','snow_lang=invalid')),'en');
});
test('private routes fail closed without reading an asset binding',async()=>{
  for(const path of ['/private','/workspace','/workspace/notes','/api/notes','/%70rivate/notes']){
    const response=await worker.fetch(new Request('https://snow.test'+path),{ASSETS:{fetch(){throw Error('must not read asset');}}});
    assert.equal(response.status,503,path);
    assert.equal(response.headers.get('Cache-Control'),'no-store');
  }
});
test('source paths and unrecognized assets cannot be fetched through the worker',async()=>{
  for(const path of ['/content/profile.json','/docs/sources.md','/history/','/.project-memory/','/src/worker.js','/secret.json']){
    const response=await worker.fetch(new Request('https://snow.test'+path),{ASSETS:{fetch(){throw Error('must not read asset');}}});
    assert.equal(response.status,404,path);
  }
});
test('country redirects are not cacheable and do not override manual choice',async()=>{
  const request=new Request('https://snow.test/',{headers:{Cookie:'snow_lang=en'}});request.cf={country:'KR'};
  const response=await worker.fetch(request,{});
  assert.equal(response.status,302);
  assert.equal(response.headers.get('Location'),'https://snow.test/en/');
  assert.match(response.headers.get('Cache-Control'),/no-store/);
});
test('built site includes no private data directory and all PDF links have real PDFs',async()=>{
  const entries=await readdir(new URL('../dist/',import.meta.url));
  for(const forbidden of ['content','private','workspace','history','.project-memory','src','docs'])assert(!entries.includes(forbidden));
  const data=JSON.parse(await readFile(new URL('../content/profile.json',import.meta.url)));
  for(const doc of data.documents){const pdf=await readFile(new URL('../dist/downloads/'+doc.filename,import.meta.url));assert.equal(pdf.subarray(0,5).toString(),'%PDF-');}
});
