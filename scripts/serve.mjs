import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve('dist');
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.pdf':'application/pdf','.woff':'font/woff','.txt':'text/plain; charset=utf-8'};
http.createServer(async(req,res)=>{
  const url=new URL(req.url,'http://localhost');
  let pathname;
  try{pathname=decodeURIComponent(url.pathname);}catch{res.writeHead(400);res.end();return;}
  let file=path.resolve(root,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
  if(!file.startsWith(root+path.sep)){res.writeHead(404);res.end();return;}
  try{const bytes=await readFile(file);res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});res.end(bytes);}catch{res.writeHead(404);res.end('Not found');}
}).listen(4173,'127.0.0.1',()=>console.log('Preview ready at http://127.0.0.1:4173'));
