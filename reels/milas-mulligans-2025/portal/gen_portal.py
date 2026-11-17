"""Build Mila's Mulligans portal approvals pages (R0BATO portal dark design) from the review-page data.
Usage: python gen_portal.py <review-page dir> <review video dir> <out dir> <slug>
Writes <out>/clients/<slug>/approvals/index.html (calendar + project cards) and
<out>/clients/<slug>/approvals/throwback-reels/index.html (three reels, captions, review form) plus media/."""
import html, json, os, shutil, sys

RP, VID, OUT, SLUG = sys.argv[1:5]
R = json.load(open(os.path.join(RP, 'data.json')))
S = json.load(open(os.path.join(RP, 'schedule.json')))
FILES = {'hot-dog': 'HotDogSandwich_v19_review.mp4', 'mayo-or-sand': 'MayoOrSand_v4_review.mp4',
         'guess-the-50-50': 'Guess5050_v3_review.mp4'}
base = os.path.join(OUT, 'clients', SLUG, 'approvals')
proj = os.path.join(base, 'throwback-reels')
os.makedirs(os.path.join(proj, 'media'), exist_ok=True)
for r in R:
    shutil.copyfile(os.path.join(VID, FILES[r['id']]), os.path.join(proj, 'media', r['file']))

e = html.escape
j = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#0d1b2f">
<title>{title}</title>
<link rel="stylesheet" href="/assets/portal-shell.css">
<script defer src="/assets/portal-shell.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap">
<style>
:root{{--navy:#0d1b2f;--gold:#d4a23f;--red:#c62f36;--red-lt:#ef777c;--muted:#a9b5c7;--line:rgba(255,255,255,.12);--card:#13243d;--card-h:#182d4a;--ink:#f3f5f9;--ok:#5fd394;--warn:#f0b35c}}
*{{box-sizing:border-box}}
[hidden]{{display:none!important}}
body{{margin:0;color:var(--ink);font:16px/1.55 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:radial-gradient(circle at 80% 8%,rgba(198,47,54,.22),transparent 30%),#0d1b2f;min-height:100vh}}
.wrap{{max-width:1000px;margin:0 auto;padding:40px max(16px,env(safe-area-inset-left,0px)) 56px}}
.brand{{color:var(--gold);text-transform:uppercase;letter-spacing:.3em;font-weight:800;font-size:13px;text-align:center}}
.prep{{color:var(--muted);text-transform:uppercase;letter-spacing:.14em;font-size:13px;text-align:center;margin-top:14px}}
.emoji{{font-size:44px;text-align:center;margin-top:10px}}
h1{{font-family:Georgia,"Times New Roman",serif;font-weight:400;color:var(--gold);font-size:clamp(38px,7vw,58px);line-height:1.05;text-align:center;margin:4px 0 10px}}
h1 span{{color:var(--red-lt)}}
.lede{{max-width:62ch;margin:0 auto;text-align:center;color:#e3e8f1}}
a{{color:var(--gold)}}
button{{font:inherit}}
:focus-visible{{outline:3px solid var(--gold);outline-offset:2px}}
footer{{text-align:center;color:var(--muted);font-size:12px;letter-spacing:.2em;margin-top:48px}}
{extra}
</style>
</head>
<body>
<div class="wrap">
"""
FOOT = """<footer>R0BATO MEDIA · CREATOR-LED · BUILT IN PA</footer>
</div>
{script}
</body>
</html>
"""

# ---------- approvals landing: calendar + project cards ----------
CAL_CSS = """
.cal{background:var(--card);border:1px solid var(--line);border-radius:6px;margin:36px auto 0;max-width:860px}
.cal-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px 16px;padding:18px 20px 6px}
.cal-head h2{margin:0;color:var(--gold);font-size:13px;letter-spacing:.2em;text-transform:uppercase}
.cal-month{display:flex;align-items:center;gap:10px}
.cal-month strong{font-family:Georgia,serif;font-weight:400;font-size:26px;min-width:7.5em;text-align:center}
.cal-month button{background:none;border:1px solid var(--line);color:var(--ink);border-radius:4px;padding:2px 10px;cursor:pointer}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;padding:4px 20px 14px;font-size:14px;color:#dfe5ee;align-items:center}
.legend span{display:inline-flex;gap:6px;align-items:center}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;flex:none}
.t-reel{background:#f0484f}.t-carousel{background:#5aa9ff}
.grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));border-top:1px solid var(--line)}
.dow{text-align:center;color:var(--muted);font-size:12px;letter-spacing:.12em;text-transform:uppercase;padding:10px 0;border-bottom:1px solid var(--line)}
.day{min-height:68px;padding:8px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);display:grid;align-content:start;gap:8px;font-size:14px;font-variant-numeric:tabular-nums;background:none;border-top:0;border-left:0;color:var(--ink);text-align:left;font-weight:600}
.day:nth-child(7n){border-right:0}
.day.past{color:var(--muted);font-weight:400}
.day.out{color:transparent}
.day.has{cursor:pointer}.day.has:hover{background:var(--card-h)}
.day.sel{box-shadow:inset 0 0 0 2px var(--gold)}
.day .n{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%}
.day.today .n{background:var(--gold);color:var(--navy);font-weight:800}
.dots{display:flex;gap:4px}
@media (max-width:560px){.day{min-height:50px;padding:5px}}
.cal-detail{padding:12px 20px;border-bottom:1px solid var(--line);display:grid;gap:8px}
.cal-item{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;font-size:15px}
.cal-item a{color:var(--ink);font-weight:700}
.cal-item .when{color:var(--muted);font-size:14px}
.cal-foot{padding:14px 20px 18px;color:#dfe5ee;font-size:14px;display:grid;gap:8px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:4px;padding:26px 30px;margin:36px auto 0;max-width:1000px;text-decoration:none;color:var(--ink);transition:transform .15s,background .15s}
.card:hover{background:var(--card-h);transform:translateX(3px)}
.card-top{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 22px}
.card .num{font-family:Georgia,serif;color:var(--gold);font-size:34px}
.card h2{font-family:Georgia,serif;font-weight:400;font-size:30px;margin:0;flex:1}
.card .count{color:var(--gold);font-weight:700}
.card .row{display:flex;gap:30px;border-top:1px solid var(--line);margin-top:16px;padding-top:14px}
.card .row b{color:var(--gold);min-width:8em}
.card .wait{color:#dfe5ee;margin:14px 0 18px}
.card .go{display:block;text-align:center;background:var(--gold);color:var(--navy);font-weight:800;padding:16px;border-radius:2px;font-size:18px}
@media (prefers-reduced-motion:reduce){.card{transition:none}.card:hover{transform:none}}
"""
CAL_JS = r"""<script>
(function(){
  var S=__S__, R=__R__;
  function el(t,a,k){var n=document.createElement(t);for(var x in a||{}){if(x==='text')n.textContent=a[x];else n.setAttribute(x,a[x]);}(k||[]).forEach(function(c){if(c)n.appendChild(c)});return n}
  var M=['January','February','March','April','May','June','July','August','September','October','November','December'];
  var dated=S.items.filter(function(x){return x.date}), grid=document.getElementById('cal-grid'), title=document.getElementById('cal-title');
  var detail=document.getElementById('cal-detail'), foot=document.getElementById('cal-foot');
  var f=dated.length?dated[0].date.split('-').map(Number):[new Date().getFullYear(),new Date().getMonth()+1], view={y:f[0],m:f[1]-1}, sel=null;
  var now=new Date(), pad=function(v){return ('0'+v).slice(-2)}, today=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate());
  var key=function(y,m,d){return y+'-'+pad(m+1)+'-'+pad(d)};
  function row(x){return el('div',{class:'cal-item'},[el('i',{class:'dot t-'+x.type}),el('a',{href:'throwback-reels/#'+x.reel,text:x.title}),el('span',{class:'when',text:x.when})])}
  function show(k){sel=k;detail.textContent='';var l=dated.filter(function(x){return x.date===k});detail.hidden=!l.length;l.forEach(function(x){detail.appendChild(row(x))});draw()}
  function draw(){
    title.textContent=M[view.m]+' '+view.y; grid.textContent='';
    ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(function(d){grid.appendChild(el('div',{class:'dow',text:d}))});
    var st=new Date(view.y,view.m,1).getDay(), days=new Date(view.y,view.m+1,0).getDate(), cells=Math.ceil((st+days)/7)*7;
    for(var i=0;i<cells;i++){var d=i-st+1;
      if(d<1||d>days){grid.appendChild(el('div',{class:'day out','aria-hidden':'true'}));continue}
      var k=key(view.y,view.m,d), l=dated.filter(function(x){return x.date===k});
      var c=el(l.length?'button':'div',{class:'day'+(k===today?' today':'')+(k<today?' past':'')+(l.length?' has':'')+(k===sel?' sel':'')},[el('span',{class:'n',text:String(d)}),el('span',{class:'dots'},l.map(function(x){return el('i',{class:'dot t-'+x.type})}))]);
      if(l.length){c.type='button';c.setAttribute('aria-label',M[view.m]+' '+d+': '+l.map(function(x){return x.title}).join(', '));c.addEventListener('click',(function(kk){return function(){show(kk===sel?null:kk)}})(k))}
      grid.appendChild(c)}
  }
  document.getElementById('cal-prev').onclick=function(){view.m--;if(view.m<0){view.m=11;view.y--}draw()};
  document.getElementById('cal-next').onclick=function(){view.m++;if(view.m>11){view.m=0;view.y++}draw()};
  foot.appendChild(el('p',{style:'margin:0',text:S.note}));
  S.items.filter(function(x){return !x.date}).forEach(function(x){foot.appendChild(row(x))});
  draw();
})();
</script>"""
landing = HEAD.format(title="Mila's Mulligans · Approvals", extra=CAL_CSS) + f"""<div class="brand">R0BATO Media</div>
<div class="prep">Prepared for Mila's Mulligans · Bath, PA</div>
<div class="emoji" aria-hidden="true">⛳</div>
<h1>Approvals</h1>
<p class="lede">Pick a project. Look through each post, read where and when it goes, then approve it or tell us what to change. Nothing goes out until you approve it.</p>
<section class="cal" aria-label="What's posting">
  <div class="cal-head"><h2>What's posting</h2>
    <div class="cal-month"><button type="button" id="cal-prev" aria-label="Previous month">&#8592;</button><strong id="cal-title"></strong><button type="button" id="cal-next" aria-label="Next month">&#8594;</button></div></div>
  <div class="legend"><span><i class="dot t-reel"></i>Reel</span><span><i class="dot t-carousel"></i>Carousel</span><span>Tap a date to see what goes out</span></div>
  <div class="grid" id="cal-grid"></div>
  <div class="cal-detail" id="cal-detail" hidden></div>
  <div class="cal-foot" id="cal-foot"></div>
</section>
<a class="card" href="throwback-reels/">
  <div class="card-top"><span class="num">01</span><h2>Throwback reels · Mila's Mulligans 2025</h2><span class="count">{len(R)} to review</span></div>
  <div class="row"><b>On Instagram</b><span>{' · '.join(e(r['title']) for r in R)}</span></div>
  <p class="wait">Waiting for you.</p>
  <span class="go">Open this project &#8594;</span>
</a>
""" + FOOT.format(script=CAL_JS.replace('__S__', j(S)).replace('__R__', j([{'id': r['id'], 'title': r['title']} for r in R])))
open(os.path.join(base, 'index.html'), 'w').write(landing)

# ---------- project page: three reels, captions, review form (Netlify Forms) ----------
P_CSS = """
.back{display:inline-block;margin-bottom:6px;color:var(--muted);text-decoration:none;font-size:14px}
.reel{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--red);border-radius:4px;padding:22px;margin-top:32px;display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:26px;scroll-margin-top:16px}
@media (max-width:760px){.reel{grid-template-columns:minmax(0,1fr)}.player{max-width:320px;margin:0 auto;width:100%}}
.player{display:grid;gap:10px;align-content:start}
.player video{width:100%;aspect-ratio:9/16;background:#000;border-radius:6px;display:block}
.facts{display:flex;flex-wrap:wrap;gap:6px;font-size:12px;color:var(--muted)}
.facts span{border:1px solid var(--line);border-radius:4px;padding:2px 8px}
.side{display:grid;gap:16px;min-width:0;align-content:start}
.side .num{font-family:Georgia,serif;color:var(--red-lt);font-size:28px}
.side h2{font-family:Georgia,serif;font-weight:400;font-size:30px;line-height:1.1;margin:0}
.sub{color:#dfe5ee;margin:2px 0 0}
h3{margin:0;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.copy{border:1px solid var(--line);border-radius:4px}
.copy-h{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid var(--line)}
.copy pre{margin:0;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.55 Inter,system-ui,sans-serif;color:#e8edf5}
.btn{background:none;border:1px solid var(--line);color:var(--ink);border-radius:4px;padding:6px 12px;font-weight:700;font-size:13px;cursor:pointer}
.btn:hover{border-color:var(--gold)}
.note{color:var(--muted);font-size:14px;margin:0}
.rv{border-top:1px solid var(--line);padding-top:16px;display:grid;gap:10px}
label{display:grid;gap:4px;font-size:14px;font-weight:600}
input[type=text],textarea{font:inherit;font-size:15px;color:var(--ink);background:#0f1f36;border:1px solid var(--line);border-radius:4px;padding:9px 11px;width:100%}
textarea{min-height:90px;resize:vertical}
fieldset{border:0;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
legend{font-size:14px;font-weight:600;margin-bottom:6px;padding:0}
.choice{position:relative}
.choice input{position:absolute;opacity:0}
.choice span{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:7px 14px;font-size:14px;font-weight:600;cursor:pointer}
.choice input:focus-visible+span{outline:3px solid var(--gold)}
.choice input[value=Approved]:checked+span{background:rgba(95,211,148,.16);border-color:var(--ok);color:var(--ok)}
.choice input[value="Approved with small changes"]:checked+span{background:rgba(240,179,92,.16);border-color:var(--warn);color:var(--warn)}
.choice input[value="Needs changes"]:checked+span{background:rgba(239,119,124,.16);border-color:var(--red-lt);color:var(--red-lt)}
.nh{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.send{background:var(--gold);color:var(--navy);border:0;border-radius:2px;padding:12px 18px;font-weight:800;cursor:pointer;justify-self:start}
.status{font-size:14px;margin:0;min-height:1.2em}
.status.err{color:var(--red-lt)}.status.ok{color:var(--ok)}
.hp{position:absolute;left:-9999px}
"""
cards = []
for i, r in enumerate(R, 1):
    rid = r['id']
    copy = ''.join(f"""<div class="copy"><div class="copy-h"><h3>{t}</h3><button type="button" class="btn" data-copy>Copy</button></div><pre>{e(r[k])}</pre></div>"""
                   for t, k in (('Instagram caption', 'instagram'), ('Pinned comment', 'pinned'), ('Facebook', 'facebook')))
    note = f'<p class="note">{e(r["note"])}</p>' if r.get('note') else ''
    cards.append(f"""<article class="reel" id="{rid}">
  <div class="player"><video controls playsinline preload="metadata" src="media/{e(r['file'])}" aria-label="{e(r['title'])} reel"></video>
    <div class="facts">{''.join(f'<span>{e(x)}</span>' for x in r['facts'])}</div>
    <a class="btn" href="media/{e(r['file'])}" download>Download video</a></div>
  <div class="side">
    <div><span class="num">0{i}</span><h2>{e(r['title'])}</h2><p class="sub">{e(r['sub'])}</p></div>
    {copy}{note}
    <form class="rv" name="mila-reel-review" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="./?sent=1#{rid}">
      <input type="hidden" name="form-name" value="mila-reel-review">
      <input type="hidden" name="reel" value="{e(r['title'])} ({e(r['facts'][1])})">
      <p class="hp"><label>Leave this empty <input name="bot-field"></label></p>
      <h3>Your call on this one</h3>
      <label>Your name<input type="text" name="name" autocomplete="name" required data-name></label>
      <fieldset><legend>Decision</legend>
        <label class="choice"><input type="radio" name="decision" value="Approved" required><span>Approved</span></label>
        <label class="choice"><input type="radio" name="decision" value="Approved with small changes"><span>Approved with small changes</span></label>
        <label class="choice"><input type="radio" name="decision" value="Needs changes"><span>Needs changes</span></label>
      </fieldset>
      <div class="nh"><label for="n-{rid}" style="display:block">Notes</label><button type="button" class="btn" data-stamp>Add time 0:00</button></div>
      <textarea id="n-{rid}" name="notes" placeholder="Pause the video and tap the time button to mark the moment."></textarea>
      <button class="send" type="submit">Send my review</button>
      <p class="status" role="status"></p>
    </form>
  </div>
</article>""")
P_JS = r"""<script>
(function(){
  var mmss=function(t){t=Math.max(0,Math.floor(t||0));return Math.floor(t/60)+':'+('0'+t%60).slice(-2)};
  document.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){var pre=b.closest('.copy').querySelector('pre');
    var ok=function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1600)};
    var sel=function(){var r=document.createRange();r.selectNodeContents(pre);var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected'};
    try{navigator.clipboard.writeText(pre.textContent).then(ok,sel)}catch(e){sel()}})});
  var saved=''; try{saved=localStorage.getItem('mila-reviewer')||''}catch(e){}
  document.querySelectorAll('.reel').forEach(function(card){
    var v=card.querySelector('video'), stamp=card.querySelector('[data-stamp]'), ta=card.querySelector('textarea'), f=card.querySelector('form'), st=card.querySelector('.status'), nm=card.querySelector('[data-name]');
    if(saved)nm.value=saved;
    v.addEventListener('timeupdate',function(){stamp.textContent='Add time '+mmss(v.currentTime)});
    stamp.addEventListener('click',function(){var a=ta.selectionStart!=null?ta.selectionStart:ta.value.length,pre=ta.value.slice(0,a),post=ta.value.slice(a);
      var ins=(pre&&!/\s$/.test(pre)?'\n':'')+mmss(v.currentTime)+' ';ta.value=pre+ins+post;ta.focus();ta.selectionStart=ta.selectionEnd=(pre+ins).length});
    f.addEventListener('submit',function(ev){
      if(!window.fetch)return; ev.preventDefault();
      if(!nm.value.trim()){st.className='status err';st.textContent='Add your name so we know who signed off.';nm.focus();return}
      if(!f.querySelector('input[name=decision]:checked')){st.className='status err';st.textContent='Pick Approved, Approved with small changes, or Needs changes.';return}
      try{localStorage.setItem('mila-reviewer',nm.value.trim())}catch(e){}
      var btn=f.querySelector('.send');btn.disabled=true;btn.textContent='Sending';
      fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(f)).toString()})
        .then(function(r){if(!r.ok)throw 0;st.className='status ok';st.textContent='Sent. Thank you, Rob has your review.'},function(){st.className='status err';st.textContent='That did not send. Check your connection and try again.'})
        .then(function(){btn.disabled=false;btn.textContent='Send my review'});
    });
  });
})();
</script>"""
page = HEAD.format(title="Mila's Mulligans · Throwback reels", extra=P_CSS) + """<a class="back" href="../">&#8592; All approvals</a>
<div class="brand">R0BATO Media</div>
<div class="prep">Prepared for Mila's Mulligans · Bath, PA</div>
<h1>Throwback <span>reels</span></h1>
<p class="lede">Three reels from the 2025 tournament. Watch each one, read the caption that goes with it, then approve it or tell us what to change. Nothing posts until you approve it.</p>
""" + '\n'.join(cards) + FOOT.format(script=P_JS)
open(os.path.join(proj, 'index.html'), 'w').write(page)
print(base)
