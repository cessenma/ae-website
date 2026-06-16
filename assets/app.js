/* ===========================================================
   American English 埃森美語 — shared site script
   Injects header / drawer / footer / LINE button on every page
   and powers all interactions. Edit once, applies site-wide.
   =========================================================== */
(function(){
  "use strict";

  var LINE = "https://lin.ee/W9J8TuQ";
  var PHONE = "+886928067772";
  var PHONE_TXT = "0928-067-772";
  var ADDRESS = "新北市板橋區中正路89巷4號1樓";
  var LOGO = "/assets/img/american-english-banqiao-logo.jpg";

  // Primary navigation (label, path)
  var NAV = [
    {t:"首頁", h:"/"},
    {t:"課程", h:"/courses/"},
    {t:"師資", h:"/certified-american-teacher-banqiao/"},
    {t:"家長見證", h:"/banqiao-parent-testimonials/"},
    {t:"部落格", h:"/blog/"}
  ];

  var ROCKET = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5c2.8 2.4 4 6 3.7 9.3l-3.7 2.7-3.7-2.7C8 8.5 9.2 4.9 12 2.5Z"/><circle cx="12" cy="9" r="1.7"/><path d="M8.3 12.2 5 15.4l3.2-.9M15.7 12.2 19 15.4l-3.2-.9M10 16.5l2 3 2-3"/></svg>';
  var LINE_SVG = '<svg viewBox="0 0 24 24"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></svg>';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // current page key — works for /courses/, /courses, /courses.html, courses.html, and "/"
  function pageKey(p){ p=p.split('?')[0].split('#')[0].replace(/\/+$/,''); p=(p.split('/').pop()||'').replace(/\.html$/,''); return p===''?'index':p; }
  var page = pageKey(location.pathname);

  /* ---------- Build chrome ---------- */
  function navLinks(isDrawer){
    return NAV.map(function(n){
      var active = (pageKey(n.h) === page) ? ' class="active"' : '';
      return '<a href="'+n.h+'"'+active+'>'+n.t+'</a>';
    }).join('') + '<a href="'+LINE+'" target="_blank" rel="noopener" class="btn btn-primary '+(isDrawer?'':'nav-cta')+'">LINE 預約試聽</a>';
  }

  function injectChrome(){
    // favicon (from logo) if the page doesn't already declare one
    if(!document.querySelector('link[rel="icon"]')){
      var fav=document.createElement('link'); fav.rel='icon'; fav.href=LOGO; document.head.appendChild(fav);
    }
    // progress bar (skip if baked into static HTML)
    var prog = document.getElementById('progress');
    if(!prog){
      prog = document.createElement('div'); prog.className='progress'; prog.id='progress';
      document.body.insertBefore(prog, document.body.firstChild);
    }

    // header (skip if baked into static HTML — better for crawlers/AI)
    var header = document.getElementById('siteHeader');
    if(!header){
      header = document.createElement('header');
      header.className = 'site-header'; header.id = 'siteHeader';
      header.innerHTML =
        '<div class="wrap nav">'+
          '<a href="/" class="brand"><img class="brand-logo" src="'+LOGO+'" alt="American English 埃森美語 logo" width="38" height="38">埃森<b>美語</b></a>'+
          '<nav class="nav-links" aria-label="主選單">'+navLinks(false)+'</nav>'+
          '<button class="hamburger" id="hamburger" aria-label="開啟選單" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button>'+
        '</div>';
      document.body.insertBefore(header, prog.nextSibling);
    }

    // drawer (skip if baked into static HTML)
    if(!document.getElementById('drawer')){
      var drawer = document.createElement('div');
      drawer.className='drawer'; drawer.id='drawer';
      drawer.innerHTML = navLinks(true);
      document.body.insertBefore(drawer, header.nextSibling);
    }

    // footer — skip if the page already has a static footer (static HTML is better for crawlers)
    if(!document.querySelector('footer.site-footer')){
    var footer = document.createElement('footer');
    footer.className='site-footer';
    footer.innerHTML =
      '<div class="wrap">'+
        '<div class="foot-grid">'+
          '<div><div class="foot-logo"><img class="foot-logo-img" src="'+LOGO+'" alt="American English 埃森美語 logo" width="34" height="34">American English 埃森美語</div>'+
          '<p class="foot-tag">板橋中正路在地深耕的美籍外師英文補習班。100% 美籍持證教師、每班 12 人小班制。</p></div>'+
          '<div class="foot-links">'+
            '<div class="foot-col"><h4>課程</h4><a href="/courses/">課程階段</a><a href="/courses/#path">學習旅程</a><a href="'+LINE+'" target="_blank" rel="noopener">LINE 預約試聽</a></div>'+
            '<div class="foot-col"><h4>關於</h4><a href="/certified-american-teacher-banqiao/">師資介紹</a><a href="/banqiao-parent-testimonials/">家長見證</a><a href="/blog/">部落格</a></div>'+
            '<div class="foot-col"><h4>聯絡</h4><a href="tel:'+PHONE+'">☎ '+PHONE_TXT+'</a><a href="'+LINE+'" target="_blank" rel="noopener">LINE 線上預約</a></div>'+
          '</div>'+
        '</div>'+
        '<div class="foot-bottom"><span>© 2026 American English 埃森美語</span><span>'+ADDRESS+'</span></div>'+
      '</div>';
    document.body.appendChild(footer);
    }

    // floating LINE button
    var fab = document.createElement('a');
    fab.className='line-fab'; fab.href=LINE; fab.target='_blank'; fab.rel='noopener';
    fab.setAttribute('aria-label','加 LINE 預約試聽');
    fab.innerHTML = LINE_SVG;
    document.body.appendChild(fab);

    // fill rocket icons
    document.querySelectorAll('[data-rocket]').forEach(function(el){ el.innerHTML = ROCKET; });
    // fill any LINE icon placeholders in page content
    document.querySelectorAll('[data-line-icon]').forEach(function(el){ el.innerHTML = LINE_SVG; });
  }

  /* ---------- Interactions ---------- */
  function wire(){
    var header = document.getElementById('siteHeader');
    var progress = document.getElementById('progress');
    function onScroll(){ header.classList.toggle('scrolled', window.scrollY>8); var h=document.documentElement; progress.style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+'%'; }
    window.addEventListener('scroll', onScroll, {passive:true}); onScroll();

    var burger=document.getElementById('hamburger'), drawer=document.getElementById('drawer');
    function setMenu(open){ document.body.classList.toggle('menu-open',open); burger.setAttribute('aria-expanded',open); burger.setAttribute('aria-label',open?'關閉選單':'開啟選單'); }
    burger.addEventListener('click',function(){ setMenu(!document.body.classList.contains('menu-open')); });
    drawer.querySelectorAll('a').forEach(function(a){ a.addEventListener('click',function(){ setMenu(false); }); });

    // twinkling stars + hero parallax
    var deco=document.querySelector('.bg-deco');
    if(deco && !reduce){
      var cols=['var(--yellow)','var(--blue)','var(--purple)','var(--green)'];
      for(var i=0;i<18;i++){ var s=document.createElement('span'); s.className='star'; var size=6+(i%4)*4; s.style.cssText='width:'+size+'px;height:'+size+'px;border-radius:50%;background:'+cols[i%4]+';left:'+((i*53)%100)+'%;top:'+((i*37)%100)+'%;animation-delay:'+(i*0.2)+'s'; deco.appendChild(s); }
      var scene=document.getElementById('scene'), heroEl=document.querySelector('.hero');
      if(scene && heroEl){ heroEl.addEventListener('mousemove',function(e){ var x=(e.clientX/window.innerWidth-.5), y=(e.clientY/window.innerHeight-.5); scene.style.transform='translate('+(x*18)+'px,'+(y*18)+'px)'; deco.style.transform='translate('+(x*-12)+'px,'+(y*-12)+'px)'; }); }
    }

    // IntersectionObserver support? (covers very old browsers — show everything if not)
    var hasIO = ('IntersectionObserver' in window);

    // reveal
    var revs=document.querySelectorAll('.reveal');
    if(reduce || !hasIO){ revs.forEach(function(r){ r.classList.add('in'); }); }
    else{
      var ro=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); ro.unobserve(e.target); } }); },{threshold:0,rootMargin:'0px 0px -5% 0px'});
      revs.forEach(function(r){ ro.observe(r); });
      // failsafe: never leave content hidden if the observer never fires (some in-app/embedded browsers)
      setTimeout(function(){ revs.forEach(function(r){ r.classList.add('in'); }); }, 3500);
    }

    // reversible swing-in for feature illustrations: the observer adds .in on enter (plays
    // the swingIn keyframes) and .out on leave (plays swingOut = same path, reversed), so
    // each illustration swings in on scroll-down and swings back out on scroll-up.
    var swings=document.querySelectorAll('.illus.swing');
    if(reduce || !hasIO){ swings.forEach(function(s){ s.style.opacity='1'; }); }
    else{
      var ioFired=false;
      // threshold:0 fires on both entry and full exit; the negative bottom margin holds
      // the trigger until the block is ~12% up from the viewport bottom.
      var so=new IntersectionObserver(function(es){ ioFired=true; es.forEach(function(e){
        var el=e.target;
        if(e.isIntersecting){ el.classList.add('in'); el.classList.remove('out'); }
        else if(el.classList.contains('in')){ el.classList.remove('in'); el.classList.add('out'); }
      }); },{threshold:0, rootMargin:'0px 0px -12% 0px'});
      swings.forEach(function(s){ so.observe(s); });
      // failsafe: if a broken observer never fires at all, just settle them visible
      setTimeout(function(){ if(!ioFired){ swings.forEach(function(s){ s.classList.add('in'); }); } }, 3500);
    }

    // staggered cascade — children animate in one-by-one when the group enters view
    document.querySelectorAll('[data-cascade]').forEach(function(group){
      var items=group.querySelectorAll('.cascade');
      if(reduce || !hasIO){ items.forEach(function(it){ it.classList.add('in'); }); return; }
      var co=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ items.forEach(function(it,i){ it.style.transitionDelay=(i*0.1)+'s'; it.classList.add('in'); }); co.disconnect(); } }); },{threshold:.15});
      co.observe(group);
    });

    // learning path stagger (per-path: index resets each container so each rail staggers on its own)
    document.querySelectorAll('.path').forEach(function(path){
      var nodes=path.querySelectorAll('.node');
      if(reduce || !hasIO){ nodes.forEach(function(n){ n.classList.add('in'); }); return; }
      var poFired=false;
      var po=new IntersectionObserver(function(es){ poFired=true; es.forEach(function(e){ if(e.isIntersecting){ var idx=[].indexOf.call(nodes,e.target); e.target.style.animationDelay=(idx*0.14)+'s'; e.target.classList.add('in'); po.unobserve(e.target); } }); },{threshold:.35});
      nodes.forEach(function(n){ po.observe(n); });
      // failsafe: if the observer never fires at all (broken IO), force the nodes fully
      // visible (clear any half-started animation) so they can never get stuck hidden
      setTimeout(function(){ if(!poFired){ nodes.forEach(function(n){ n.style.animation='none'; n.style.opacity='1'; n.style.transform='none'; }); } }, 3500);
    });

    // tabs (supports multiple tab groups by aria-controls)
    var tabs=document.querySelectorAll('.tab');
    tabs.forEach(function(tab){ tab.addEventListener('click',function(){
      var group=tab.closest('[role="tablist"]');
      group.querySelectorAll('.tab').forEach(function(t){ var sel=t===tab; t.setAttribute('aria-selected',sel); var p=document.getElementById(t.getAttribute('aria-controls')); if(p) p.hidden=!sel; });
    }); });

    // stat counters
    var statBlock=document.querySelector('[data-stats]');
    if(statBlock){
      var runCounts=function(){ statBlock.querySelectorAll('.stat-num').forEach(function(el){ var to=+el.dataset.to, suf=el.dataset.suffix||''; if(reduce){ el.textContent=to+suf; return; } var start=null; function step(ts){ if(!start)start=ts; var p=Math.min((ts-start)/1500,1); el.textContent=Math.round(to*(1-Math.pow(1-p,3)))+suf; if(p<1)requestAnimationFrame(step); } requestAnimationFrame(step); }); };
      if(!hasIO){ runCounts(); }
      else{ var counted=false; new IntersectionObserver(function(es){ if(es[0].isIntersecting&&!counted){ counted=true; runCounts(); } },{threshold:.3}).observe(statBlock); }
    }

    // testimonial carousel
    var track=document.getElementById('track');
    if(track){
      var slides=track.children.length, idx=0, timer=null, dots=document.getElementById('dots');
      if(dots){ for(var j=0;j<slides;j++){ (function(n){ var b=document.createElement('button'); b.setAttribute('role','tab'); b.setAttribute('aria-label','第 '+(n+1)+' 則'); b.addEventListener('click',function(){ go(n); reset(); }); dots.appendChild(b); })(j); } }
      function go(n){ idx=(n+slides)%slides; track.style.transform='translateX('+(-idx*100)+'%)'; if(dots) dots.querySelectorAll('button').forEach(function(d,di){ d.setAttribute('aria-current',di===idx); }); }
      var nx=document.getElementById('next'), pv=document.getElementById('prev');
      if(nx) nx.addEventListener('click',function(){ go(idx+1); reset(); });
      if(pv) pv.addEventListener('click',function(){ go(idx-1); reset(); });
      function start(){ if(reduce)return; timer=setInterval(function(){ go(idx+1); },6000); }
      function reset(){ clearInterval(timer); start(); }
      var carousel=document.getElementById('carousel');
      if(carousel){ carousel.addEventListener('mouseenter',function(){ clearInterval(timer); }); carousel.addEventListener('mouseleave',start); }
      go(0); start();
    }

    // faq accordion
    document.querySelectorAll('.faq-q').forEach(function(q){ q.addEventListener('click',function(){ var item=q.parentElement, open=item.classList.toggle('open'); q.setAttribute('aria-expanded',open); var a=item.querySelector('.faq-a'); a.style.maxHeight=open?a.scrollHeight+'px':0; }); });
  }

  /* ---------- SEO: structured data (JSON-LD) ---------- */
  function injectSEO(){
    function addLD(obj){ var s=document.createElement('script'); s.type='application/ld+json'; s.textContent=JSON.stringify(obj); document.head.appendChild(s); }
    // skip a JSON-LD type if it's already baked into the page statically (seo_build.py)
    function hasLD(type){ return [].some.call(document.querySelectorAll('script[type="application/ld+json"]'), function(s){ return s.textContent.indexOf('"'+type+'"')!==-1; }); }

    // Sitewide Organization/LocalBusiness + founder Person schema are STATIC JSON-LD
    // in each page <head>. breadcrumb + FAQ + hreflang are also baked in by seo_build.py;
    // the guards below only inject them as a fallback for any unbuilt page.

    // hreflang — self-reference (zh-Hant-TW) + x-default. Add `en` entries here once English pages exist.
    var canon=document.querySelector('link[rel="canonical"]');
    if(canon && !document.querySelector('link[rel="alternate"][hreflang]')){
      [["zh-Hant-TW",canon.href],["x-default",canon.href]].forEach(function(p){
        var a=document.createElement('link'); a.rel='alternate'; a.hreflang=p[0]; a.href=p[1]; document.head.appendChild(a);
      });
    }

    // BreadcrumbList from the page breadcrumb (if present and not already static)
    var crumb=document.querySelector('.breadcrumb');
    if(crumb && !hasLD('BreadcrumbList')){
      var parts=[], i=1;
      crumb.querySelectorAll('a').forEach(function(a){ parts.push({"@type":"ListItem","position":i++,"name":a.textContent.trim(),"item":new URL(a.getAttribute('href'),location.href).href}); });
      parts.push({"@type":"ListItem","position":i,"name":(document.querySelector('h1')||{}).textContent ? document.querySelector('h1').textContent.replace(/\s+/g,' ').trim() : document.title});
      addLD({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":parts});
    }

    // FAQPage from any FAQ accordion on the page (if not already static)
    var qs=document.querySelectorAll('.faq-item');
    if(qs.length && !hasLD('FAQPage')){
      var faqs=[];
      qs.forEach(function(item){
        var q=item.querySelector('.faq-q'), a=item.querySelector('.faq-a');
        if(q&&a){ var qt=q.cloneNode(true); var pm=qt.querySelector('.pm'); if(pm)pm.remove();
          faqs.push({"@type":"Question","name":qt.textContent.trim(),"acceptedAnswer":{"@type":"Answer","text":a.textContent.trim()}}); }
      });
      if(faqs.length) addLD({"@context":"https://schema.org","@type":"FAQPage","mainEntity":faqs});
    }
  }

  function init(){ injectChrome(); wire(); injectSEO(); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
