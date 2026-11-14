/* SP-07 · shop mockup behaviour. Sample products and prices; nothing leaves the page. The cart is kept in this browser only. */
(function(){
  'use strict';
  var C={ink:{n:'Ink',c:'#1b2622'},olive:{n:'Olive',c:'#4a5236'},sand:{n:'Sand',c:'#cdbf9e',light:1},bone:{n:'Bone',c:'#e9e3d6',light:1},charcoal:{n:'Charcoal',c:'#34383a'},blaze:{n:'Blaze orange',c:'#c8551f',light:1}};
  var SIZES=['S','M','L','XL','2XL','3XL'];
  var GUIDE={tee:[['Chest',96,104,112,120,128,136],['Length',71,74,76,79,81,83]],hoodie:[['Chest',104,112,120,128,136,144],['Length',68,70,72,74,76,78]]};
  var P=[
    {h:'logo-tee',name:'Logo tee',cat:'Apparel',price:45,colours:['ink','olive','bone'],sizes:SIZES,guide:'tee',out:{bone:['3XL']},
     blurb:'Heavyweight cotton with the lockup on the chest and the rifle mark across the back.',
     specs:[['Fabric','220 gsm combed cotton'],['Print','Lockup on the chest, rifle mark across the back'],['Fit','Regular. Size up for more room'],['Care','Cold wash inside out, line dry']]},
    {h:'trucker-cap',name:'Trucker cap',cat:'Headwear',price:40,colours:['ink','olive','sand'],
     blurb:'Embroidered front, mesh back and a snap closure. Shade for long days in the paddock.',
     specs:[['Front','Embroidered Fitz Feral Hunters lockup'],['Back','Mesh with an adjustable snap'],['Fit','One size, about 56 to 61 cm'],['Care','Spot clean']]},
    {h:'field-hoodie',name:'Field hoodie',cat:'Apparel',price:89,colours:['ink','charcoal'],sizes:SIZES,guide:'hoodie',out:{charcoal:['S']},
     blurb:'Brushed fleece with an embroidered chest logo and a big front pocket for cold mornings.',
     specs:[['Fabric','380 gsm cotton and polyester fleece, brushed inside'],['Logo','Embroidered on the chest'],['Fit','Relaxed'],['Care','Cold wash, line dry']]},
    {h:'beanie',name:'Beanie',cat:'Headwear',price:35,colours:['ink','blaze'],
     blurb:'Rib-knit beanie with a woven Fitz Feral Hunters label, in ink or blaze orange.',
     specs:[['Knit','Acrylic and wool blend, double layer'],['Label','Woven, on the cuff'],['Fit','One size']]},
    {h:'stubby-holder',name:'Stubby holder',cat:'Accessories',price:15,colours:['ink'],
     blurb:'Neoprene with the lockup printed all the way round. Fits 375 ml cans and stubbies.',
     specs:[['Material','5 mm neoprene, stitched base'],['Fits','375 ml cans and stubbies'],['Care','Hand wash']]},
    {h:'sticker-pack',name:'Sticker pack',cat:'Accessories',price:10,colours:['ink'],noColour:1,
     blurb:'Three weatherproof vinyl stickers: the lockup, the rifle mark and a contour-map badge.',
     specs:[['In the pack','3 stickers, 80 to 120 mm wide'],['Material','UV-resistant vinyl'],['Goes on','Cars, toolboxes, eskies']]}
  ];
  var byH={}; P.forEach(function(p){ byH[p.h]=p; });
  var PARCEL=10.95, EXPRESS=16.95, FREE_OVER=100, MAX=10, CODES={WELCOME10:0.10};
  var KEY='ffh-shop-mock-cart';

  var cart=load(), filter='all', disc=null, sel=null, orders=0, lastOrder=null, first=true;
  var drawer=$('cart-drawer');

  /* ---------- helpers */
  function $(id){ return document.getElementById(id); }
  function esc(s){ return String(s).replace(/[&<>"']/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function money(n){ return '$'+(Math.round(n*100)/100).toFixed(2); }
  function r2(n){ return Math.round(n*100)/100; }
  function icon(n){ return '<svg class="i" aria-hidden="true"><use href="#i-'+n+'"/></svg>'; }
  var CORNERS='<i class="corner tl" aria-hidden="true"></i><i class="corner tr" aria-hidden="true"></i><i class="corner bl" aria-hidden="true"></i><i class="corner br" aria-hidden="true"></i>';
  function artEl(k){ return C[k] && C[k].light ? '<i class="art patch art-plate" aria-hidden="true"></i>' : '<i class="art art-logo" aria-hidden="true"></i>'; }
  function slot(k,label,tag){ return '<div class="slot pimg" style="--pc:'+C[k].c+'"'+(label?' role="img" aria-label="'+esc(label)+'"':' aria-hidden="true"')+'>'+artEl(k)+CORNERS+(tag?'<span class="ptag">Sample image</span>':'')+'</div>'; }
  function load(){ try{ var v=JSON.parse(localStorage.getItem(KEY)||'[]'); return Array.isArray(v)?v.filter(function(it){ return it && byH[it.h] && C[it.c] && it.q>0; }):[]; }catch(e){ return []; } }
  function save(){ try{ localStorage.setItem(KEY,JSON.stringify(cart)); }catch(e){} }
  function keyOf(it){ return it.h+'|'+it.c+'|'+(it.s||''); }
  function find(k){ for(var i=0;i<cart.length;i++){ if(keyOf(cart[i])===k) return i; } return -1; }
  function variant(it){ var p=byH[it.h], v=[]; if(p.colours.length>1) v.push(C[it.c].n); if(it.s) v.push('Size '+it.s); return v.join(' · '); }
  function count(){ return cart.reduce(function(a,it){ return a+it.q; },0); }
  function subtotal(){ return r2(cart.reduce(function(a,it){ return a+byH[it.h].price*it.q; },0)); }
  function totals(post){
    var sub=subtotal(), d=disc?r2(sub*CODES[disc]):0, after=r2(sub-d), free=after>=FREE_OVER;
    var ship=post==='pickup'?0:(post==='express'?EXPRESS:(free?0:PARCEL));
    var total=r2(after+ship);
    return {sub:sub,d:d,after:after,free:free,ship:ship,total:total,gst:r2(total/11)};
  }
  var toastEl=document.querySelector('.toast'), toastT=null;
  function toast(msg){ if(!toastEl) return; toastEl.textContent=msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT=setTimeout(function(){ toastEl.classList.remove('on'); },3200); }
  function say(msg){ var l=$('cart-live'); l.textContent=''; setTimeout(function(){ l.textContent=msg; },30); }

  /* ---------- cart */
  function add(h,c,s,q){
    var it={h:h,c:c,s:s||null,q:q}, k=keyOf(it), i=find(k);
    if(i>-1) cart[i].q=Math.min(MAX,cart[i].q+q); else cart.push(it);
    save(); renderCount();
    var p=byH[h], v=variant(it);
    say('Added '+p.name+(v?', '+v:'')+'. Your cart has '+count()+(count()===1?' item.':' items.'));
  }
  function setQty(k,q){
    var i=find(k); if(i<0) return;
    q=Math.max(0,Math.min(MAX,parseInt(q,10)||0));
    if(q===0){ var p=byH[cart[i].h]; cart.splice(i,1); say('Removed '+p.name+'.'); } else cart[i].q=q;
    if(!cart.length) disc=null;
    save(); renderCount();
  }
  function renderCount(){
    var n=count(), b=$('cart-count'), a=$('cart-btn');
    b.textContent=n; b.toggleAttribute('data-zero',n===0);
    a.setAttribute('aria-label','Cart, '+n+(n===1?' item':' items'));
  }

  /* ---------- shop grid */
  function dots(p){
    if(p.colours.length<2) return '';
    return '<span class="dots" role="img" aria-label="'+p.colours.length+' colours: '+p.colours.map(function(k){ return C[k].n; }).join(', ')+'">'+p.colours.map(function(k){ return '<i style="--sw:'+C[k].c+'"></i>'; }).join('')+'</span>';
  }
  function card(p){
    var btn=p.sizes?'<a class="btn btn-secondary" href="#item-'+p.h+'">Choose size</a>'
      :(p.colours.length>1?'<a class="btn btn-secondary" href="#item-'+p.h+'">Choose colour</a>'
      :'<button type="button" class="btn btn-secondary" data-add="'+p.h+'">Add to cart</button>');
    return '<li class="pcard" data-cat="'+p.cat+'"><a class="pc-link" href="#item-'+p.h+'">'+slot(p.colours[0])+'<h3>'+esc(p.name)+'</h3></a>'
      +'<div class="pc-row"><span class="price">'+money(p.price)+'</span>'+dots(p)+'</div>'+btn+'</li>';
  }
  function renderGrid(){
    $('grid').innerHTML=P.filter(function(p){ return filter==='all'||p.cat===filter; }).map(card).join('');
    [].forEach.call(document.querySelectorAll('[data-filter]'),function(b){ b.setAttribute('aria-pressed',String(b.getAttribute('data-filter')===filter)); });
  }

  /* ---------- product page */
  function renderItem(h){
    var p=byH[h]; sel={h:h,c:p.colours[0],s:null,q:1};
    var crumbs='<ol class="crumbs" aria-label="Breadcrumb"><li><a href="#shop" data-filter-go="all">Shop</a></li><li><a href="#shop" data-filter-go="'+p.cat+'">'+p.cat+'</a></li><li aria-current="page">'+esc(p.name)+'</li></ol>';
    var thumbs=p.colours.length>1?'<div class="thumbs" role="group" aria-label="Pictures by colour">'+p.colours.map(function(k,i){ return '<button type="button" data-thumb="'+k+'" aria-pressed="'+(i===0)+'" aria-label="Show '+C[k].n+'" style="--pc:'+C[k].c+'">'+artEl(k)+'</button>'; }).join('')+'</div>':'';
    var colour=p.noColour?'':(p.colours.length>1
      ?'<fieldset class="opt" id="opt-colour"><legend>Colour: <span id="colour-name">'+C[p.colours[0]].n+'</span></legend><div class="swatches">'+p.colours.map(function(k,i){ return '<input class="vh" type="radio" name="colour" id="col-'+k+'" value="'+k+'"'+(i===0?' checked':'')+'><label for="col-'+k+'" style="--sw:'+C[k].c+'" title="'+C[k].n+'"><i></i><span class="sr">'+C[k].n+'</span></label>'; }).join('')+'</div></fieldset>'
      :'<p class="small" style="margin:0;color:var(--ink-2)">Colour: '+C[p.colours[0]].n+'</p>');
    var guide=p.guide?'<details class="guide"><summary>Size guide</summary><div class="table-wrap"><table><thead><tr><th scope="col">Centimetres</th>'+p.sizes.map(function(s){ return '<th scope="col">'+s+'</th>'; }).join('')+'</tr></thead><tbody>'+GUIDE[p.guide].map(function(r){ return '<tr><th scope="row">'+r[0]+'</th>'+r.slice(1).map(function(v){ return '<td>'+v+'</td>'; }).join('')+'</tr>'; }).join('')+'</tbody></table></div><p class="small" style="margin:0 0 14px;color:var(--ink-2)">Measured flat across the chest and doubled. Length is from the top of the shoulder.</p></details>':'';
    var sizes=p.sizes?'<fieldset class="opt" id="opt-size"><legend>Size: <span id="size-name">choose one</span></legend><div class="sizes">'+p.sizes.map(function(s){ return '<input class="vh" type="radio" name="size" id="sz-'+s+'" value="'+s+'" aria-describedby="e-size"><label for="sz-'+s+'">'+s+'<span class="sr" data-out-sr hidden>, sold out</span></label>'; }).join('')+'</div><span class="err" id="e-size">Choose a size.</span></fieldset>'+guide:'';
    var related=P.filter(function(o){ return o.h!==p.h; }).sort(function(a,b){ return (b.cat===p.cat)-(a.cat===p.cat); }).slice(0,3);
    $('item-body').innerHTML=crumbs
      +'<div class="pdp"><div class="gallery"><div id="pdp-art">'+slot(sel.c,'Sample image: '+p.name+(p.noColour?'':' in '+C[sel.c].n),true)+'</div>'+thumbs+'</div>'
      +'<div class="pinfo stack" style="--gap:22px"><div class="stack" style="--gap:12px"><p class="eyebrow" style="margin:0">'+p.cat+'</p><h1 id="h-item" tabindex="-1">'+esc(p.name)+'</h1>'
      +'<p class="price-row"><span class="price-big">'+money(p.price)+'</span><span class="gst">AUD, GST included</span></p></div><p style="margin-top:14px">'+esc(p.blurb)+'</p>'
      +'<form id="add-form" class="stack" style="--gap:22px" novalidate>'+colour+sizes
      +'<div class="add-row"><div class="qty" role="group" aria-label="Quantity"><button type="button" data-step="-1" aria-label="One fewer">'+icon('minus')+'</button><input type="number" id="item-qty" min="1" max="'+MAX+'" value="1" inputmode="numeric" aria-label="Quantity"><button type="button" data-step="1" aria-label="One more">'+icon('plus')+'</button></div>'
      +'<button type="submit" class="btn btn-primary" id="add-btn">'+icon('bag')+'<span>Add to cart · <span class="num" id="add-total">'+money(p.price)+'</span></span></button></div></form>'
      +'<p class="posted">'+icon('truck')+'<span>Posted from Warragul within two business days. Free postage on orders over '+money(FREE_OVER).replace('.00','')+'.</span></p>'
      +'<dl class="specs">'+p.specs.map(function(s){ return '<dt>'+esc(s[0])+'</dt><dd>'+esc(s[1])+'</dd>'; }).join('')+'</dl>'
      +'<details class="more"><summary>Postage, pick-up and swaps</summary><div class="stack" style="--gap:8px"><p style="margin:0">Australia Post Parcel Post is '+money(PARCEL)+', or free over '+money(FREE_OVER).replace('.00','')+'. Express Post is '+money(EXPRESS)+'.</p><p style="margin:0">Pick-up in Warragul is free. Fitz texts you when it\'s ready.</p><p style="margin:0">Wrong size? Swap it within 30 days if it\'s unworn, with the tags on.</p></div></details>'
      +'</div></div>'
      +'<section class="related" aria-labelledby="h-rel"><h2 id="h-rel" style="font-size:var(--fs-h3)">More from the shop</h2><ul class="pgrid">'+related.map(card).join('')+'</ul></section>';
    updateSizes();
    document.title=p.name+' · Shop · Fitz Feral Hunters';
  }
  function setColour(k){
    var p=byH[sel.h]; sel.c=k;
    $('pdp-art').innerHTML=slot(k,'Sample image: '+p.name+' in '+C[k].n,true);
    var n=$('colour-name'); if(n) n.textContent=C[k].n;
    var r=$('col-'+k); if(r) r.checked=true;
    [].forEach.call(document.querySelectorAll('[data-thumb]'),function(b){ b.setAttribute('aria-pressed',String(b.getAttribute('data-thumb')===k)); });
    updateSizes();
  }
  function updateSizes(){
    var p=byH[sel.h]; if(!p.sizes) return;
    var out=(p.out&&p.out[sel.c])||[];
    p.sizes.forEach(function(s){
      var inp=$('sz-'+s), gone=out.indexOf(s)>-1; inp.disabled=gone;
      inp.nextElementSibling.querySelector('[data-out-sr]').hidden=!gone;
      if(gone&&inp.checked){ inp.checked=false; sel.s=null; $('size-name').textContent='choose one'; }
    });
  }
  function itemQty(){ var i=$('item-qty'), q=Math.max(1,Math.min(MAX,parseInt(i.value,10)||1)); i.value=q; sel.q=q; $('add-total').textContent=money(byH[sel.h].price*q); return q; }

  /* ---------- line items */
  function line(it,edit){
    var p=byH[it.h], k=esc(keyOf(it)), v=variant(it);
    var ctl=edit
      ?'<div class="ln-ctl"><div class="qty sm" role="group" aria-label="Quantity of '+esc(p.name+(v?', '+v:''))+'"><button type="button" data-dec="'+k+'" aria-label="One fewer">'+icon('minus')+'</button><input type="number" min="0" max="'+MAX+'" value="'+it.q+'" inputmode="numeric" data-q="'+k+'" aria-label="Quantity"><button type="button" data-inc="'+k+'" aria-label="One more">'+icon('plus')+'</button></div><button type="button" class="btn btn-quiet" data-rm="'+k+'">Remove<span class="sr"> '+esc(p.name)+'</span></button></div>'
      :'<span class="sr">Quantity '+it.q+'</span>';
    return '<li class="line"><a class="thumb" href="#item-'+p.h+'" style="--pc:'+C[it.c].c+'" tabindex="-1" aria-hidden="true">'+artEl(it.c)+(edit?'':'<span class="qbadge">'+it.q+'</span>')+'</a>'
      +'<div class="ln-main">'+(edit?'<a class="ln-name" href="#item-'+p.h+'">'+esc(p.name)+'</a>':'<span class="ln-name">'+esc(p.name)+'</span>')+(v?'<span class="ln-var">'+esc(v)+'</span>':'')+ctl+'</div>'
      +'<span class="ln-price num">'+money(p.price*it.q)+'</span></li>';
  }
  function freeNote(after){
    if(after>=FREE_OVER) return '<p class="free done">'+icon('check')+' Free postage on this order</p>';
    var pct=Math.round(after/FREE_OVER*100);
    return '<div class="free"><p style="margin:0">Spend <b class="num">'+money(FREE_OVER-after)+'</b> more for free postage.</p><div class="meter" role="progressbar" aria-label="Towards free postage" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+pct+'"><i style="width:'+pct+'%"></i></div></div>';
  }
  function emptyHTML(){
    return '<div class="empty"><p><b>Your cart is empty.</b> Pick something from the shop.</p><a class="btn btn-primary" href="#shop">Back to the shop</a><p class="helper"><span>Mockup helper</span><button type="button" class="btn btn-quiet" data-sample>Add two sample items</button></p></div>';
  }

  /* ---------- drawer */
  function renderDrawer(){
    var t=totals('parcel');
    $('cd-lines').innerHTML=cart.length?cart.map(function(it){ return line(it,true); }).join(''):'<li class="line" style="grid-template-columns:1fr"><p style="margin:0">Your cart is empty.</p></li>';
    $('cd-sub').textContent=money(t.after);
    $('cd-free').textContent=!cart.length?'':(t.free?'Free postage on this order.':'Spend '+money(FREE_OVER-t.after)+' more for free postage.');
  }
  function openDrawer(){
    $('cd-title').textContent='Added to your cart';
    renderDrawer();
    if(drawer.showModal){ if(!drawer.open) drawer.showModal(); } else drawer.setAttribute('open','');
    $('cd-title').focus();
  }
  function closeDrawer(){ if(drawer.open){ if(drawer.close) drawer.close(); else drawer.removeAttribute('open'); } }

  /* ---------- cart page */
  function renderCart(){
    var el=$('cart-body');
    if(!cart.length){ el.innerHTML=emptyHTML(); return; }
    var t=totals('parcel');
    el.innerHTML='<div class="cart-layout"><div style="min-width:0"><ul class="lines big">'+cart.map(function(it){ return line(it,true); }).join('')+'</ul><p style="margin:16px 0 0"><a class="btn btn-quiet" href="#shop">Keep shopping</a></p></div>'
      +'<aside class="sumbox" aria-labelledby="sum-h"><h2 id="sum-h">Summary</h2>'+freeNote(t.after)
      +'<dl class="totals">'+(t.d?'<dt>Items</dt><dd class="num">'+money(t.sub)+'</dd><dt>Discount '+disc+'</dt><dd class="num">−'+money(t.d)+'</dd>':'')+'<dt class="grand">Subtotal</dt><dd class="grand num"><small>AUD</small>'+money(t.after)+'</dd></dl>'
      +'<p class="small" style="margin:0;color:var(--ink-2)">GST included. Postage is worked out at checkout: '+money(PARCEL)+' by Parcel Post, free over '+money(FREE_OVER).replace('.00','')+', or pick up free in Warragul.</p>'
      +'<a class="btn btn-primary" href="#checkout">'+icon('lock')+'Checkout</a></aside></div>';
  }

  /* ---------- checkout */
  function val(name){ var r=document.querySelector('#co-form input[name="'+name+'"]:checked'); return r?r.value:''; }
  function coState(){ var m=val('method'); return {method:m,post:m==='pickup'?'pickup':val('post'),pay:val('pay'),bill:m==='pickup'?'other':val('bill')}; }
  function discHTML(id){
    if(disc) return '<p style="margin:0"><span class="disc-chip">'+disc+' · 10% off<button type="button" class="icon-btn" data-undisc aria-label="Remove discount code '+disc+'">'+icon('x')+'</button></span></p>';
    return '<form class="disc" data-disc novalidate><label class="sr" for="disc-'+id+'">Discount code</label><input id="disc-'+id+'" type="text" placeholder="Discount code" autocomplete="off" autocapitalize="characters" spellcheck="false" aria-describedby="disc-msg-'+id+'"><button type="submit" class="btn btn-secondary">Apply</button></form><p class="disc-msg" id="disc-msg-'+id+'">Mockup: try WELCOME10.</p>';
  }
  function summaryHTML(id){
    var s=coState(), t=totals(s.post), shipName=s.post==='pickup'?'Pick-up, Warragul':(s.post==='express'?'Express Post':'Parcel Post');
    return (id==='d'?'<h2 id="co-sum-h">Order summary</h2>':'')
      +'<ul class="lines">'+cart.map(function(it){ return line(it,false); }).join('')+'</ul>'+discHTML(id)
      +'<dl class="totals"><dt>Subtotal</dt><dd class="num">'+money(t.sub)+'</dd>'+(t.d?'<dt>Discount '+disc+'</dt><dd class="num">−'+money(t.d)+'</dd>':'')
      +'<dt>'+shipName+'</dt><dd class="num">'+(t.ship?money(t.ship):'Free')+'</dd><dt class="grand">Total</dt><dd class="grand num"><small>AUD</small>'+money(t.total)+'</dd></dl>'
      +'<p class="gst-line" style="margin:-8px 0 0;font-size:var(--fs-caption);color:var(--ink-2);text-align:right">Including '+money(t.gst)+' in GST</p>';
  }
  function renderSummary(){
    var s=coState(), t=totals(s.post);
    $('co-sum-d').innerHTML=summaryHTML('d'); $('co-sum-m').innerHTML=summaryHTML('m');
    $('co-mob-total').textContent=money(t.total);
    $('amt-parcel').textContent=t.free?'Free':money(PARCEL);
    $('afterpay-note').textContent='Four payments of '+money(t.total/4)+', every two weeks. Afterpay opens to finish the payment.';
    $('co-pay').querySelector('.lbl').textContent='Pay now · '+money(t.total);
  }
  function updateForm(){
    var s=coState(), pick=s.method==='pickup';
    $('ship-fields').hidden=pick; $('pickup-fields').hidden=!pick; $('sec-postage').hidden=pick;
    $('bill-same-row').hidden=pick; if(pick) $('b-other').checked=true;
    $('bill-fields').hidden=!(pick||val('bill')==='other');
    ['card','paypal','afterpay'].forEach(function(k){ $('sub-'+k).hidden=(s.pay!==k); });
    renderSummary();
  }
  function renderCheckout(){
    var has=cart.length>0;
    $('co').hidden=!has; $('co-empty').hidden=has;
    if(!has){ $('co-empty').innerHTML=emptyHTML(); return; }
    updateForm();
  }
  function req(v){ return v.length>0; }
  function isEmail(v){ return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }
  function isPc(v){ return /^\d{4}$/.test(v); }
  function isPhone(v){ return (v.replace(/\D/g,'').length)>=8; }
  function validate(){
    var s=coState(), checks=[['c-email',isEmail,'Email']];
    if(s.method==='ship') checks.push(['d-first',req,'First name'],['d-last',req,'Last name'],['d-addr',req,'Street address'],['d-sub',req,'Suburb or town'],['d-state',req,'State'],['d-pc',isPc,'Postcode']);
    else checks.push(['p-first',req,'First name'],['p-last',req,'Last name'],['p-phone',isPhone,'Mobile']);
    if(s.bill==='other') checks.push(['b-first',req,'Billing first name'],['b-last',req,'Billing last name'],['b-addr',req,'Billing street address'],['b-sub',req,'Billing suburb or town'],['b-state',req,'Billing state'],['b-pc',isPc,'Billing postcode']);
    [].forEach.call(document.querySelectorAll('#co-form .field.has-err'),function(f){ f.classList.remove('has-err'); });
    [].forEach.call(document.querySelectorAll('#co-form [aria-invalid]'),function(el){ el.removeAttribute('aria-invalid'); el.removeAttribute('aria-describedby'); });
    var bad=[];
    checks.forEach(function(c){
      var el=$(c[0]), ok=c[1](el.value.trim());
      if(!ok){ el.closest('.field').classList.add('has-err'); el.setAttribute('aria-invalid','true'); el.setAttribute('aria-describedby','e-'+c[0]); bad.push(c); }
    });
    var box=$('co-err');
    if(bad.length){
      $('co-err-list').innerHTML=bad.map(function(c){ return '<li><a href="#'+c[0]+'" data-focus-field="'+c[0]+'">'+c[2]+': '+esc($('e-'+c[0]).textContent)+'</a></li>'; }).join('');
      box.hidden=false; box.focus();
    } else box.hidden=true;
    return !bad.length;
  }
  function placeOrder(){
    var s=coState(), t=totals(s.post), pick=s.method==='pickup';
    lastOrder={no:'FFH-'+(1001+orders++),items:cart.slice(),t:t,s:s,disc:disc,email:$('c-email').value.trim(),
      first:(pick?$('p-first'):$('d-first')).value.trim(),phone:$('p-phone').value.trim(),
      addr:pick?null:[$('d-first').value+' '+$('d-last').value,$('d-addr').value+($('d-apt').value?', '+$('d-apt').value:''),$('d-sub').value+' '+$('d-state').value+' '+$('d-pc').value].map(function(x){ return x.trim(); })};
    cart=[]; disc=null; save(); renderCount();
    location.hash='done';
  }
  function fillSample(){
    var v={'c-email':'sam.taylor@example.com','d-first':'Sam','d-last':'Taylor','d-addr':'12 Queen Street','d-sub':'Warragul','d-state':'VIC','d-pc':'3820','d-phone':'0412 345 678','p-first':'Sam','p-last':'Taylor','p-phone':'0412 345 678','b-first':'Sam','b-last':'Taylor','b-addr':'12 Queen Street','b-sub':'Warragul','b-state':'VIC','b-pc':'3820'};
    Object.keys(v).forEach(function(id){ $(id).value=v[id]; });
    [].forEach.call(document.querySelectorAll('#co-form .field.has-err'),function(f){ f.classList.remove('has-err'); });
    $('co-err').hidden=true;
  }

  /* ---------- confirmation */
  function renderDone(){
    var o=lastOrder, el=$('done-body');
    if(!o){ el.innerHTML='<div class="done"><div class="sec-head" style="margin:0"><p class="eyebrow">Shop</p><h1 id="h-done" tabindex="-1">No order yet</h1><p class="measure">Place an order at the checkout to see this page.</p></div><p><a class="btn btn-primary" href="#shop">Back to the shop</a></p></div>'; return; }
    var pick=o.s.method==='pickup', pay={card:'Card',paypal:'PayPal',afterpay:'Afterpay'}[o.s.pay];
    el.innerHTML='<div class="done"><div class="sec-head" style="margin:0"><p class="meta"><b>Sheet</b><span>Shop · Order</span><span class="lead" aria-hidden="true"></span><span class="num">'+o.no+'</span></p><p class="eyebrow">Order confirmed · <span class="num">'+o.no+'</span></p><h1 id="h-done" tabindex="-1">Thanks, '+esc(o.first||'mate')+'</h1>'
      +'<p class="measure">'+(pick?'Fitz will text '+esc(o.phone)+' when your order is ready to pick up in Warragul.':'Your order goes in the post from Warragul within two business days. The tracking number goes to '+esc(o.email)+'.')+'</p></div>'
      +'<div class="confirm" role="status"><b>This was a mockup</b><p style="margin:0">Nothing was charged and no order was sent. On the live shop, Shopify emails the receipt and the order shows up in Fitz\'s Shopify admin.</p></div>'
      +'<div class="cols"><div><b>Contact</b><p>'+esc(o.email)+'</p></div><div><b>'+(pick?'Pick-up':'Delivery')+'</b><p>'+(pick?'Warragul, by arrangement':o.addr.map(esc).join('<br>'))+'</p></div><div><b>Payment</b><p>'+pay+' · <span class="num">'+money(o.t.total)+'</span> AUD</p></div></div>'
      +'<ul class="lines">'+o.items.map(function(it){ return line(it,false); }).join('')+'</ul>'
      +'<dl class="totals"><dt>Subtotal</dt><dd class="num">'+money(o.t.sub)+'</dd>'+(o.t.d?'<dt>Discount '+o.disc+'</dt><dd class="num">−'+money(o.t.d)+'</dd>':'')+'<dt>'+(pick?'Pick-up, Warragul':(o.s.post==='express'?'Express Post':'Parcel Post'))+'</dt><dd class="num">'+(o.t.ship?money(o.t.ship):'Free')+'</dd><dt class="grand">Total</dt><dd class="grand num"><small>AUD</small>'+money(o.t.total)+'</dd></dl>'
      +'<p class="gst-line" style="margin:-16px 0 0;font-size:var(--fs-caption);color:var(--ink-2);text-align:right">Including '+money(o.t.gst)+' in GST</p>'
      +'<p><a class="btn btn-primary" href="#shop">Back to the shop</a></p></div>';
  }

  /* ---------- views */
  var TITLES={shop:'Shop · Fitz Feral Hunters',cart:'Cart · Shop · Fitz Feral Hunters',checkout:'Checkout · Shop · Fitz Feral Hunters',done:'Order confirmed · Shop · Fitz Feral Hunters'};
  function route(){
    var h=(location.hash||'').slice(1), view='shop', arg=null;
    if(h.indexOf('item-')===0&&byH[h.slice(5)]){ view='item'; arg=h.slice(5); }
    else if(h==='cart'||h==='checkout'||h==='done') view=h;
    else if(h&&h!=='shop'&&document.getElementById(h)) return; /* in-page anchors such as the skip link */
    closeDrawer();
    ['shop','item','cart','checkout','done'].forEach(function(v){ $('v-'+v).hidden=(v!==view); });
    if(view==='shop') renderGrid();
    if(view==='item') renderItem(arg);
    if(view==='cart') renderCart();
    if(view==='checkout') renderCheckout();
    if(view==='done') renderDone();
    if(TITLES[view]) document.title=TITLES[view];
    var cb=$('cart-btn'); if(view==='cart') cb.setAttribute('aria-current','page'); else cb.removeAttribute('aria-current');
    if(!first){ window.scrollTo(0,0); var h1=$('h-'+view); if(h1) h1.focus({preventScroll:true}); }
    first=false;
  }
  function refresh(focus){
    renderDrawer();
    if(!$('v-cart').hidden) renderCart();
    if(!$('v-checkout').hidden) renderCheckout();
    if(focus){
      var scope=drawer.open?drawer:document, el=scope.querySelector('['+focus[0]+'="'+(window.CSS&&CSS.escape?CSS.escape(focus[1]):focus[1])+'"]');
      if(el) el.focus(); else if(drawer.open) $('cd-title').focus(); else { var h=$('h-cart'); if(h&&!$('v-cart').hidden) h.focus(); }
    }
  }

  /* ---------- events */
  document.addEventListener('click',function(e){
    var t=e.target.closest('button, a'); if(!t) return;
    var a;
    if((a=t.getAttribute('data-add'))){ add(a,byH[a].colours[0],null,1); openDrawer(); return; }
    if((a=t.getAttribute('data-filter'))){ filter=a; renderGrid(); return; }
    if((a=t.getAttribute('data-filter-go'))){ filter=a; if(location.hash==='#shop'){ e.preventDefault(); route(); } return; }
    if((a=t.getAttribute('data-thumb'))){ setColour(a); return; }
    if((a=t.getAttribute('data-step'))){ var i=$('item-qty'); i.value=(parseInt(i.value,10)||1)+parseInt(a,10); itemQty(); return; }
    if((a=t.getAttribute('data-inc'))){ var j=find(a); if(j>-1) setQty(a,cart[j].q+1); refresh(['data-inc',a]); return; }
    if((a=t.getAttribute('data-dec'))){ var k=find(a); if(k>-1) setQty(a,cart[k].q-1); refresh(['data-dec',a]); return; }
    if((a=t.getAttribute('data-rm'))){ setQty(a,0); refresh(['data-rm','__none']); return; }
    if(t.hasAttribute('data-sample')){ add('logo-tee','olive','L',1); add('trucker-cap','ink',null,1); route(); return; }
    if(t.hasAttribute('data-undisc')){ disc=null; refresh(); return; }
    if(t.hasAttribute('data-close')){ closeDrawer(); return; }
    if((a=t.getAttribute('data-focus-field'))){ e.preventDefault(); var f=$(a); f.focus(); f.scrollIntoView({block:'center'}); return; }
    if((a=t.getAttribute('data-xp'))){ toast('Mockup: on the live shop, '+a+' opens here to pay in one step.'); return; }
    if(t.id==='cd-close'){ closeDrawer(); return; }
    if(t.id==='co-fill'){ fillSample(); return; }
  });
  drawer.addEventListener('click',function(e){ if(e.target===drawer) closeDrawer(); });
  document.addEventListener('change',function(e){
    var t=e.target;
    if(t.name==='colour'&&t.closest('#add-form')){ setColour(t.value); return; }
    if(t.name==='size'&&t.closest('#add-form')){ sel.s=t.value; $('size-name').textContent=t.value; $('opt-size').classList.remove('has-err'); return; }
    if(t.id==='item-qty'){ itemQty(); return; }
    if(t.hasAttribute('data-q')){ var k=t.getAttribute('data-q'); setQty(k,t.value); refresh(['data-q',k]); return; }
    if(t.closest('#co-form')&&t.type==='radio'){ updateForm(); return; }
  });
  document.addEventListener('submit',function(e){
    var f=e.target; e.preventDefault();
    if(f.id==='add-form'){
      var p=byH[sel.h];
      if(p.sizes&&!sel.s){ $('opt-size').classList.add('has-err'); var first=f.querySelector('input[name="size"]:not(:disabled)'); if(first) first.focus(); return; }
      add(p.h,sel.c,sel.s,itemQty()); openDrawer(); return;
    }
    if(f.hasAttribute('data-disc')){
      var inp=f.querySelector('input'), code=inp.value.trim().toUpperCase(), msg=f.nextElementSibling;
      if(CODES[code]){ disc=code; refresh(); }
      else { msg.textContent=code?'That code isn\'t valid. Check it and try again.':'Enter a discount code first.'; msg.classList.add('bad'); inp.focus(); }
      return;
    }
    if(f.id==='co-form'){
      if(!validate()) return;
      var b=$('co-pay'); b.classList.add('is-busy'); b.setAttribute('aria-disabled','true');
      setTimeout(function(){ b.classList.remove('is-busy'); b.removeAttribute('aria-disabled'); placeOrder(); },900);
    }
  });
  window.addEventListener('hashchange',route);

  renderCount(); route();
})();
