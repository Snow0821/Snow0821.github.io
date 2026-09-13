// Only /dist is an asset binding. No repository root, notes, or source files are served.
export function localeFor(request){
  const url=new URL(request.url);
  const query=url.searchParams.get('lang');
  if(query==='en'||query==='ko')return query;
  const cookie=request.headers.get('Cookie')?.match(/(?:^|;\s*)snow_lang=(en|ko)(?:;|$)/)?.[1];
  return cookie||(request.cf?.country==='KR'?'ko':'en');
}
const security={
  'X-Content-Type-Options':'nosniff',
  'Referrer-Policy':'strict-origin-when-cross-origin',
  'X-Robots-Tag':'noindex, nofollow, noarchive',
  'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
  'Permissions-Policy':'camera=(), microphone=(), geolocation=()'
};
export default {
  async fetch(request,env){
    const url=new URL(request.url);
    let decoded;
    try{decoded=decodeURIComponent(url.pathname);}catch{return new Response('Bad request',{status:400,headers:security});}
    // A preview is not an authentication system. Private routes fail closed until implemented.
    if(/^\/(?:workspace|private|api)(?:\/|$)/i.test(decoded))return new Response('Private workspace is not configured. No private records are served.',{status:503,headers:{...security,'Cache-Control':'no-store','Content-Type':'text/plain; charset=utf-8'}});
    const allowed=/^\/(?:$|(?:en|ko)\/?(?:index\.html)?$|index\.html$|app\.js$|style\.css$|robots\.txt$|fonts\/snow-kr\.woff$|downloads\/Soon-Ho-Choi-(?:Research-CV|Resume-KO|Instructor-Profile)\.pdf$)/;
    if(!allowed.test(decoded))return new Response('Not found',{status:404,headers:security});
    if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405,headers:{...security,Allow:'GET, HEAD'}});
    if(url.pathname==='/'||url.pathname==='/index.html'){
      url.pathname=`/${localeFor(request)}/`;
      return new Response(null,{status:302,headers:{...security,Location:url.href,'Cache-Control':'private, no-store',Vary:'Cookie'}});
    }
    const response=await env.ASSETS.fetch(request);
    const headers=new Headers(response.headers);
    for(const [k,v]of Object.entries(security))headers.set(k,v);
    if(decoded.startsWith('/downloads/'))headers.set('Content-Disposition',`attachment; filename="${decoded.split('/').pop()}"`);
    return new Response(response.body,{status:response.status,headers});
  }
};
