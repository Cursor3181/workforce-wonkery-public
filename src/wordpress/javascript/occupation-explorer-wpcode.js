/* Workforce Wonkery Occupation Explorer - WPCode fallback */
(function(){
  const p=window.location.pathname.replace(/\/+$/,'');
  if(p!=='/data/occupation-explorer')return;
  if(document.querySelector('#occ-results .result-card'))return;
  async function start(){
    try{


 const cfg=document.getElementById('occ-config'),state=document.getElementById('occ-data-state');if(!cfg)return;
 const toolCfg=JSON.parse(cfg.textContent||'{}');
 let d,tech={occupations:[]},msaLayer={},msaObs={};
 try{
  const runtimeNode=document.getElementById('occ-runtime-data'),contextNode=document.getElementById('occ-runtime-context');
  if(runtimeNode){
   const runtime=JSON.parse(runtimeNode.textContent||'{}'),ctx=contextNode?JSON.parse(contextNode.textContent||'{}'):{};
   if(!runtime||!runtime.markets||!runtime.occupations)throw new Error('Compact occupation runtime is invalid');
   const occupations=Object.entries(runtime.occupations).map(([soc,meta])=>({soc,title:meta?.title||soc,sector:null,skill_tier:null})).sort((a,b)=>a.soc.localeCompare(b.soc));
   msaLayer={crosswalk:ctx.msa_occupation_layer?.crosswalk||[],markets:ctx.msa_occupation_layer?.markets||{},observations:{}};
   d={meta:{release:runtime.release||'Workforce Wonkery occupation data'},occupations,sources:ctx.sources||[],geographies:ctx.geographies||[],labor_force_observations:ctx.labor_force_observations||[],market_observations:[],msa_occupation_layer:msaLayer};
   tech={occupations:ctx.technology||[]};
   const rowToObservation=(gid,label,row)=>{
    const soc=row?.[0],wage=row?.[1],openings=row?.[2],growth=row?.[3],employment=row?.[4],projected=row?.[5];
    return {geography_id:gid,soc,title:runtime.occupations?.[soc]?.title||soc,employment:employment??null,projected_employment:projected??null,growth_pct:growth??null,total_openings:openings??null,wage:wage==null?null:{value:wage,unit:'median hourly'},fit:gid==='california'?'direct':'exact',evidence_geography:label||gid,source_period:ctx.market_periods?.[gid]||'2023-2033 projections; wages 2025 Q1',source_id:null};
   };
   Object.entries(runtime.markets).forEach(([gid,market])=>{
    const rows=(market?.rows||[]).map(row=>rowToObservation(gid,market?.label||gid,row));
    if(gid==='california')d.market_observations=rows;else msaObs[gid]=rows;
   });
   msaLayer.observations=msaObs;
  }else{
   const config=JSON.parse(cfg.textContent),res=await fetch(config.public_url,{credentials:'same-origin'});if(!res.ok)throw new Error('HTTP '+res.status);
   const html=await res.text(),doc=new DOMParser().parseFromString(html,'text/html'),node=doc.querySelector('#ww-public-data'),exactNode=doc.querySelector('#ww-exact-local-occupation-projections'),techNode=doc.querySelector('#ww-technology-watch');if(!node)throw new Error('Public data block not found');
   d=JSON.parse(node.textContent);const exact=exactNode?JSON.parse(exactNode.textContent||'{}'):{geographies:[]};if(techNode)tech=JSON.parse(techNode.textContent||'{}');
   const localToCbsa={imperial:'20940',kings:'25260',merced:'32900',stanislaus:'33700',ventura:'37100',monterey:'41500','san-diego':'41740','san-luis-obispo':'42020','santa-cruz':'42100','santa-barbara':'42200',sonoma:'42220','san-joaquin':'44700',solano:'46700',tulare:'47300'};
   msaLayer=d.msa_occupation_layer||{};msaObs=Object.assign({},msaLayer.observations||{});
   const oldMeta=new Map((d.occupations||[]).map(o=>[o.soc,o])),cat=new Map((d.occupations||[]).map(o=>[o.soc,o.title]));
   (exact.geographies||[]).forEach(g=>{
    (g.rows||[]).forEach(r=>{if(!r[0])return;if(!r[1])return;if(cat.has(r[0]))return;cat.set(r[0],r[1]);});
    const cbsa=localToCbsa[g.geography_id];if(!cbsa)return;
    msaObs[cbsa]=(g.rows||[]).map(r=>{const hourly=Number(r[7]||0),annual=Number(r[8]||0),wageObj=hourly>0?{value:hourly,unit:'median hourly'}:annual>0?{value:annual,unit:'median annual'}:null;return {soc:r[0],title:r[1],employment:r[2]??null,projected_employment:r[3]??null,growth_pct:r[5]??null,total_openings:r[6]??null,wage:wageObj,fit:'exact',evidence_geography:g.source_geography_label||g.geography_label,source_period:'2023-2033 projections; wages 2025 Q1',source_id:'src-edd-exact-'+g.geography_id};});
   });
   d.occupations=[...cat.entries()].map(([soc,title])=>{const old=oldMeta.get(soc)||{};return {soc,title,sector:old.sector||null,skill_tier:old.skill_tier||null};}).sort((a,b)=>a.soc.localeCompare(b.soc));
  }
  if(!d||!d.meta)throw new Error('Occupation data is invalid');
  state.textContent=d.meta.release;
 }catch(err){state.textContent='Public data unavailable';document.getElementById('occ-note').innerHTML='<strong>Load error:</strong> '+String(err.message||err);return;}
 const msaObsByKey={};Object.entries(msaObs).forEach(([gid,rows])=>(rows||[]).forEach(r=>msaObsByKey[gid+'|'+r.soc]=r));
 document.getElementById('occ-data-summary').textContent='Curated occupation evidence · exact geographies only';
 const srcById=Object.fromEntries((d.sources||[]).map(s=>[s.id,s]));
 const occBySoc=Object.fromEntries((d.occupations||[]).map(o=>[o.soc,o]));
 const techBySoc=Object.fromEntries((tech.occupations||[]).map(o=>[o.soc,o]));
 const geoById=Object.fromEntries((d.geographies||[]).map(g=>[g.id,g]));
 const obsByKey=Object.fromEntries((d.market_observations||[]).map(x=>[x.geography_id+'|'+x.soc,x]));
 const laborByGeo=Object.fromEntries((d.labor_force_observations||[]).map(x=>[x.geography_id,x]));
 const search=document.getElementById('occ-search'),soc=document.getElementById('occ-soc'),geo=document.getElementById('occ-geo');
 const career=document.getElementById('occ-career'),payFilter=document.getElementById('occ-pay'),openingsFilter=document.getElementById('occ-openings-filter'),growthFilter=document.getElementById('occ-growth-filter'),techFilter=document.getElementById('occ-tech-filter'),researchFilter=document.getElementById('occ-research-filter'),sort=document.getElementById('occ-sort'),results=document.getElementById('occ-results'),resultsSummary=document.getElementById('occ-results-summary'),activeFilters=document.getElementById('occ-active-filters'),clearFilters=document.getElementById('occ-clear-filters');
 const esc=s=>String(s==null?'':s).replace(/[\u0026<>"']/g,m=>({'\u0026':'\u0026amp;','<':'\u0026lt;','>':'\u0026gt;','"':'\u0026quot;',"'":'\u0026#39;'}[m]));
 const fmt=n=>n==null?'—':Number(n).toLocaleString('en-US');
 const pct=n=>n==null?'—':(Number(n)>0?'+':'')+Number(n).toFixed(1)+'%';
 const wage=w=>{if(!w)return'—';const v=Number(w.value).toLocaleString('en-US',{maximumFractionDigits:2}),dollar=String.fromCharCode(36);return w.unit==='median annual'?dollar+v+' median annual':((w.unit||'').includes('hourly')?dollar+v+'/hr':dollar+v+(w.unit?' '+w.unit:''));};
 const fitLabel=f=>({direct:'Direct geography',component_aggregate:'Component aggregate',regional:'Regional RPU context',proxy:'Broader proxy',supplemental:'Supplemental local',missing:'Not loaded'}[f]||'Not loaded');
 const GEO_KEY='ww_data_wonk_geo_v1',OCC_KEY='ww_data_wonk_soc_v1';
 let storedGeo='',storedSoc='';try{storedGeo=localStorage.getItem(GEO_KEY)||'';storedSoc=localStorage.getItem(OCC_KEY)||''}catch(e){}
 const params=new URLSearchParams(window.location.search),requestedGeo=params.get('geo'),requestedSoc=params.get('soc');
 let preferredSoc=occBySoc[requestedSoc]?requestedSoc:(occBySoc[storedSoc]?storedSoc:'');
  const marketDefs={california:{label:'California',components:[{label:'California',geog_area:'0601000000'}]}};
 (msaLayer.crosswalk||[]).forEach(x=>marketDefs[String(x.cbsa)]={label:x.label,components:x.official_components||[],status:x.crosswalk_status||''});
 const strongMetric=m=>{if(!m)return false;if(!(m.fit==='exact'||m.fit==='direct'))return false;if(!(m.total_openings!=null||m.growth_pct!=null||m.employment!=null))return false;return !!m.wage;};
 Object.entries(toolCfg.context_markets||{}).forEach(([id,label])=>{
  if(!marketDefs[id])marketDefs[id]={label,components:[],status:'context-only',context_only:true};
  else if(!(msaObs[id]||[]).some(strongMetric)){marketDefs[id].context_only=true;marketDefs[id].status=marketDefs[id].status||'context-only';}
 });
 const sourceToMarket=Object.fromEntries(Object.entries(msaLayer.markets||{}).filter(([id,v])=>v?v.source:false).map(([id,v])=>[v.source,id]));
 const marketIds=Object.keys(marketDefs).filter(id=>id!=='california'?((msaObs[id]||[]).some(strongMetric)||marketDefs[id]?.context_only):false).sort((a,b)=>marketDefs[a].label.localeCompare(marketDefs[b].label));
 const californiaAvailable=(d.occupations||[]).some(o=>strongMetric(obsByKey['california|'+o.soc]));
 geo.innerHTML=(californiaAvailable?'<option value="california">California statewide</option>':'')+'<optgroup label="California labor market areas">'+marketIds.map(id=>'<option value="'+id+'">'+esc(marketDefs[id].label)+(marketDefs[id]?.context_only?' · context only':'')+'</option>').join('')+'</optgroup>';

 const selectable=[...(californiaAvailable?['california']:[]),...marketIds];
 const requestedMapped=selectable.includes(requestedGeo)?requestedGeo:(sourceToMarket[requestedGeo]||'');
 const storedMapped=selectable.includes(storedGeo)?storedGeo:(sourceToMarket[storedGeo]||'');
 const initialGeo=selectable.includes(requestedMapped)?requestedMapped:(selectable.includes(storedMapped)?storedMapped:(selectable[0]||''));geo.value=initialGeo;
 function sourceGeo(g){return g==='california'?'california':((msaLayer.markets||{})[g]?.source||g);}
 function marketFor(s,g){return g==='california'?(obsByKey['california|'+s]||null):(msaObsByKey[g+'|'+s]||null);}
 function publicationMarket(s,g){const m=marketFor(s,g);return strongMetric(m)?m:null;}
 function contextOnly(g){return !!marketDefs[g]?.context_only;}
 function publishedMetric(m){return m?(m.employment!=null||m.projected_employment!=null||m.growth_pct!=null||m.total_openings!=null||m.wage):false;}
 const careerMap={
  '11':['Management','management'],'13':['Business \u0026 Finance','business-finance'],'15':['Technology \u0026 Data','technology-data'],'17':['Engineering \u0026 Architecture','engineering-architecture'],'19':['Science \u0026 Research','science-research'],'21':['Community \u0026 Social Services','community-social'],'23':['Legal','legal'],'25':['Education','education'],'27':['Arts, Design \u0026 Media','arts-media'],'29':['Healthcare Practitioners','healthcare-practitioners'],'31':['Healthcare Support','healthcare-support'],'33':['Public Safety','public-safety'],'35':['Food Service','food-service'],'37':['Building \u0026 Grounds','building-grounds'],'39':['Personal Care \u0026 Services','personal-care'],'41':['Sales','sales'],'43':['Office \u0026 Administrative','office-admin'],'45':['Agriculture \u0026 Natural Resources','agriculture-natural'],'47':['Construction \u0026 Extraction','construction'],'49':['Installation, Maintenance \u0026 Repair','maintenance-repair'],'51':['Production \u0026 Manufacturing','production-manufacturing'],'53':['Transportation \u0026 Logistics','transportation-logistics'],'55':['Military','military']
 };
 function careerInfo(o){const mg=String(o.soc||'').slice(0,2),x=careerMap[mg]||['Other occupations','other'];return {label:x[0],value:x[1]};}
 function hourlyWage(m){if(!m?.wage)return null;const v=Number(m.wage.value);if(!Number.isFinite(v))return null;if((m.wage.unit||'').includes('hourly'))return v;if(m.wage.unit==='median annual')return v/2080;return null;}
 const deeperSocSet=new Set(['29-1141','47-2111','47-2152','31-9092','29-1292']);
 function researchAvailable(s,g){return deeperSocSet.has(s)?['41500','42100'].includes(g):false;}
 function sortRows(rows){
   const mode=contextOnly(geo.value)?'title':(sort?.value||'openings');
   return rows.sort((a,b)=>{
     const am=publicationMarket(a.soc,geo.value),bm=publicationMarket(b.soc,geo.value);
     if(mode==='title')return a.title.localeCompare(b.title);
     if(mode==='wage')return (hourlyWage(bm)??-1)-(hourlyWage(am)??-1)||a.title.localeCompare(b.title);
     if(mode==='growth')return (Number(bm?.growth_pct)??-999)-(Number(am?.growth_pct)??-999)||a.title.localeCompare(b.title);
     return (Number(bm?.total_openings)??-1)-(Number(am?.total_openings)??-1)||a.title.localeCompare(b.title);
   });
 }
 function filtered(){
  const q=(search.value||'').trim().toLowerCase(),minPay=Number(payFilter?.value||0),minOpen=Number(openingsFilter?.value||0),growthVal=growthFilter?.value??'',careerVal=career?.value||'',techVal=techFilter?.value||'',researchVal=researchFilter?.value||'';
  const rows=(d.occupations||[]).filter(o=>{
   const isContext=contextOnly(geo.value),m=publicationMarket(o.soc,geo.value);if(!m&&!isContext)return false;
   if(q){if(!(o.title+' '+o.soc).toLowerCase().includes(q))return false;}
   if(careerVal){if(careerInfo(o).value!==careerVal)return false;}
   if(!isContext&&minPay){if((hourlyWage(m)??-1)<minPay)return false;}
   if(!isContext){if(minOpen){if(Number(m.total_openings??-1)<minOpen)return false;}}
   if(!isContext){if(growthVal!==''){if(Number(m.growth_pct??-999)<Number(growthVal)+(growthVal==='0'?Number.EPSILON:0))return false;}}
   if(techVal==='__none'){if(techBySoc[o.soc])return false;}if(techVal){if(techVal!=='__none'){if((techBySoc[o.soc]?.effect||'')!==techVal)return false;}}
   if(researchVal==='yes'){if(!researchAvailable(o.soc,geo.value))return false;}
   return true;
  });
  return sortRows(rows);
 }
 function comparisonGeos(g){
  return g==='california'?['california']:[g,'california'];
 }
 function syncContextControls(){
  const isContext=contextOnly(geo.value);
  if(isContext){payFilter.value='0';openingsFilter.value='0';growthFilter.value='';if(sort)sort.value='title';}
  [payFilter,openingsFilter,growthFilter].forEach(el=>{if(el)el.disabled=isContext;});
  document.querySelectorAll('.quickview').forEach(btn=>{if(['wage','demand','growth'].includes(btn.dataset.view||'')){btn.disabled=isContext;if(isContext)btn.classList.remove('active');}});
 }
 function syncLinks(){
  const gg=marketDefs[geo.value],o=occBySoc[soc.value],cg=document.getElementById('occ-ctx-geo'),co=document.getElementById('occ-ctx-occ'),cs=document.getElementById('occ-ctx-status');
  if(cg)cg.textContent=gg?.label||geo.value;if(co)co.textContent=o?o.title:'No occupation selected';
  if(cs){const mm=publicationMarket(soc.value,geo.value);cs.textContent=geo.value==='california'?'Statewide reference':(mm?'Exact MSA evidence':'Occupation evidence unavailable');}
 }
 function writeSelectionUrl(push){
  const u=new URL(window.location.href);
  u.searchParams.set('geo',geo.value);
  if(soc.value)u.searchParams.set('soc',soc.value);else u.searchParams.delete('soc');
  history[push?'pushState':'replaceState']({geo:geo.value,soc:soc.value||''},'',u);
 }
 function syncGeo(push){try{localStorage.setItem(GEO_KEY,geo.value)}catch(e){}writeSelectionUrl(!!push);syncLinks();}
 function syncOcc(explicit,push){if(explicit){if(soc.value){preferredSoc=soc.value;try{localStorage.setItem(OCC_KEY,soc.value)}catch(e){}}}writeSelectionUrl(!!push);syncLinks();}
 function renderFilterChips(){
  const chips=[];
  if(search.value.trim())chips.push('Search: '+search.value.trim());
  if(career.value)chips.push(career.options[career.selectedIndex].text);
  if(Number(payFilter.value))chips.push(payFilter.options[payFilter.selectedIndex].text);
  if(Number(openingsFilter.value))chips.push(openingsFilter.options[openingsFilter.selectedIndex].text+' openings');
  if(growthFilter.value!=='')chips.push(growthFilter.options[growthFilter.selectedIndex].text+' growth');
  if(techFilter.value)chips.push(techFilter.options[techFilter.selectedIndex].text);
  if(researchFilter.value)chips.push('Deeper research available');
  activeFilters.innerHTML=chips.map(x=>'<span class="filter-chip">'+esc(x)+'</span>').join('');
 }
 function renderResults(rows){
  const isContext=contextOnly(geo.value),total=isContext?(d.occupations||[]).length:(d.occupations||[]).filter(o=>publicationMarket(o.soc,geo.value)).length;
  resultsSummary.textContent=isContext?(rows.length+' occupations available for context selection · local occupation metrics are not published for '+(marketDefs[geo.value]?.label||geo.value)):rows.length+' of '+total+' published occupations';
  if(!rows.length){results.innerHTML='<div class="no-results"><strong>No occupations match these filters.</strong><p style="margin-top:5px">Try clearing a search or non-metric filter.</p></div>';return;}
  results.innerHTML=rows.map(o=>{
    const m=publicationMarket(o.soc,geo.value),ci=careerInfo(o),selected=o.soc===soc.value?' selected':'';
    if(isContext)return '<button type="button" class="result-card'+selected+'" data-soc="'+esc(o.soc)+'" aria-pressed="'+(o.soc===soc.value?'true':'false')+'"><span class="result-main"><strong>'+esc(o.title)+'</strong><small>'+esc(ci.label)+' · '+esc(o.soc)+' · Context selection</small></span><span class="result-stat"><span>Local metrics</span><strong>Unavailable</strong></span><span class="result-stat"><span>Graph context</span><strong>Available</strong></span><span class="result-stat result-growth"><span>Evidence rule</span><strong>No proxy</strong></span><span class="result-go">'+(o.soc===soc.value?'Selected':'Connect →')+'</span></button>';
    return '<button type="button" class="result-card'+selected+'" data-soc="'+esc(o.soc)+'" aria-pressed="'+(o.soc===soc.value?'true':'false')+'"><span class="result-main"><strong>'+esc(o.title)+'</strong><small>'+esc(ci.label)+' · '+esc(o.soc)+'</small></span><span class="result-stat"><span>Pay</span><strong>'+esc(wage(m?.wage))+'</strong></span><span class="result-stat"><span>Openings</span><strong>'+esc(fmt(m?.total_openings))+'</strong></span><span class="result-stat result-growth"><span>Growth</span><strong>'+esc(pct(m?.growth_pct))+'</strong></span><span class="result-go">'+(o.soc===soc.value?'Selected':'Explore →')+'</span></button>';
  }).join('');
  results.querySelectorAll('[data-soc]').forEach(btn=>btn.addEventListener('click',()=>{
    const target=btn.getAttribute('data-soc');if(!target)return;
    const opts=[...soc.options],match=opts.find(o=>o.value===target);if(!match)return;
    soc.value=target;preferredSoc=target;syncOcc(true,true);render();renderResults(filtered());
    document.getElementById('occ-heading')?.scrollIntoView({behavior:'smooth',block:'start'});
  }));
 }
 function populate(){
  const rows=filtered(),prev=soc.value;soc.innerHTML=rows.map(o=>'<option value="'+esc(o.soc)+'">'+esc(o.title)+' · '+esc(o.soc)+'</option>').join('');
  if(rows.some(o=>o.soc===prev))soc.value=prev;else if(rows.some(o=>o.soc===preferredSoc))soc.value=preferredSoc;else if(rows.length)soc.value=rows[0].soc;else soc.value='';
  document.getElementById('occ-count').textContent=contextOnly(geo.value)?rows.length+' occupations available for context':rows.length+' occupations shown';renderFilterChips();syncOcc(false);renderResults(rows);if(rows.length)render();
 }
 function renderLabor(g){
  const row=laborByGeo[sourceGeo(g)],set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
  if(row?.labor_force!=null){
   set('occ-lf-rate',Number(row.unemployment_rate).toFixed(1)+'%');set('occ-lf-force',fmt(row.labor_force));set('occ-lf-employed',fmt(row.employment));set('occ-lf-unemployed',fmt(row.unemployment));set('occ-lf-fit',g==='california'?'Statewide':'Exact labor-market footprint');
   const note=document.getElementById('occ-lf-note');if(note)note.innerHTML='<strong>'+(g==='california'?'Statewide context.':'Exact MSA footprint.')+'</strong> Current labor-force conditions are kept separate from the occupation projection below.';
  }else{
   set('occ-lf-rate','—');set('occ-lf-force','—');set('occ-lf-employed','—');set('occ-lf-unemployed','—');set('occ-lf-fit','Unavailable');
   const note=document.getElementById('occ-lf-note');if(note)note.innerHTML='<strong>Labor-force evidence unavailable.</strong> No county, WDB, or workforce-region substitute is shown.';
  }
 }
 function eddLinks(s,g){
  const clean=String(s||'').replace('-',''),defs=marketDefs[g]||{},targets=g==='california'?[{label:'California',geog_area:'0601000000'}]:(defs.components||[]);
  return targets.filter(t=>t?t.geog_area:false).map(t=>({label:t.label||defs.label||g,url:'https://labormarketinfo.edd.ca.gov/cgi/databrowsing/occExplorerQSDetails.asp?geogArea='+encodeURIComponent(t.geog_area)+String.fromCharCode(38)+'menuchoice=localAreaPro'+String.fromCharCode(38)+'soccode='+encodeURIComponent(clean+'++++')}));
 }
 const deeperResearch={
  '29-1141':{url:'https://workforcewonkery.com/data/training-opportunities/north-central-coast/registered-nurses-decision-brief/',response:'Scale + Access'},
  '47-2111':{url:'https://workforcewonkery.com/data/training-opportunities/north-central-coast/electricians-decision-brief/',response:'Access + Apprenticeship'},
  '47-2152':{url:'https://workforcewonkery.com/data/training-opportunities/north-central-coast/plumbers-pipefitters-decision-brief/',response:'Access + Apprenticeship'},
  '31-9092':{url:'https://workforcewonkery.com/data/training-opportunities/north-central-coast/medical-assistants-decision-brief/',response:'Validate + Redesign'},
  '29-1292':{url:'https://workforcewonkery.com/data/training-opportunities/north-central-coast/dental-hygienists-decision-brief/',response:'Validate + Access'}
 };
 const deeperMarkets=new Set(['41500','42100']);
 function renderDeeper(s,g,gg,o,m){
  const cfg=deeperResearch[s],eligible=cfg?deeperMarkets.has(g):false,panel=document.getElementById('occ-deeper-research');
  if(!panel)return;
  if(!eligible){panel.hidden=true;return;}
  const u=new URL(cfg.url);u.searchParams.set('geo',g);u.searchParams.set('soc',s);
  panel.hidden=false;
  document.getElementById('occ-deeper-market').textContent=gg?.label||g;
  document.getElementById('occ-deeper-response').textContent=cfg.response;
  document.getElementById('occ-deeper-copy').textContent=(gg?.label||g)+' demand, growth, and wage evidence remain local to the selected MSA. The Decision Brief adds North Central Coast training supply, capacity, access, outcomes, and a regional response.';
  document.getElementById('occ-deeper-link').href=u.toString();
 }

 let toolRuntimePromise=null,toolRenderSeq=0;
 const intelNorm=value=>String(value||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
 async function toolHash(text){
  if(!window.crypto||!crypto.subtle)throw new Error('Secure hash support unavailable');
  const bytes=new TextEncoder().encode(text),digest=new Uint8Array(await crypto.subtle.digest('SHA-256',bytes));
  return Array.from(digest,b=>b.toString(16).padStart(2,'0')).join('');
 }
 async function loadToolIntelligence(){
  if(toolRuntimePromise)return toolRuntimePromise;
  toolRuntimePromise=(async()=>{
   const slug=toolCfg.tool_intelligence_slug,expected=toolCfg.tool_intelligence_sha256,pageId=Number(toolCfg.tool_intelligence_page_id||0);
   if((!slug&&!pageId)||!expected)throw new Error('Tool intelligence release is not configured');
   const url=pageId?('/wp-json/wp/v2/pages/'+pageId+'?_fields=id,modified,content'):('/wp-json/wp/v2/pages?slug='+encodeURIComponent(slug)+'&status=publish&per_page=1&_fields=id,modified,content');
   const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),12000);
   let res;try{res=await fetch(url,{credentials:'same-origin',signal:ctl.signal});}finally{clearTimeout(timer);}
   if(!res.ok)throw new Error('Connected intelligence HTTP '+res.status);
   const payload=await res.json(),page=Array.isArray(payload)?payload[0]:payload;if(!page)throw new Error('Connected intelligence release not found');
   const box=document.createElement('div');box.innerHTML=page.content?.rendered||'';
   const node=box.querySelector('#ww-tool-intelligence-runtime');if(!node)throw new Error('Connected intelligence payload missing');
   const raw=(node.textContent||'').trim();if(!raw)throw new Error('Connected intelligence payload empty');
   const actual=await toolHash(raw+'\n');if(actual!==expected)throw new Error('Connected intelligence fingerprint mismatch');
   return JSON.parse(raw);
  })().catch(err=>{toolRuntimePromise=null;throw err;});
  return toolRuntimePromise;
 }
 function intelLinks(rows){
  return (rows||[]).map(row=>'<a href="'+esc(row.url)+'">'+esc(row.title)+' →</a>').join('');
 }
 async function renderConnectedIntelligence(s,g,o){
  const status=document.getElementById('occ-intel-status'),grid=document.getElementById('occ-intel-grid'),boundary=document.getElementById('occ-intel-boundary');
  if(!status||!grid)return;
  const seq=++toolRenderSeq;
  if(g==='california'){
   status.textContent='Choose an MSA for local connections';grid.innerHTML='';
   if(boundary)boundary.textContent='Connected training, sector, and Access & Equity evidence is published at governed local-market geographies rather than inferred from the statewide selection.';
   return;
  }
  status.textContent='Connecting '+(marketDefs[g]?.label||g)+' + '+(o?.title||s)+'…';
  try{
   const runtime=await loadToolIntelligence();if(seq!==toolRenderSeq)return;
   const market=runtime.markets?.[g];if(!market)throw new Error('No governed tool context for this market');
   const training=market.training||null,exactCases=(training?.cases||[]).filter(row=>(row.occupation_socs||[]).includes(s));
   const major=String(s||'').split('-')[0],family=runtime.occupation_major_families?.[major]||{},terms=(family.sector_terms||[]).map(intelNorm);
   const aligned=(market.sector_partnerships||[]).filter(row=>{const hay=intelNorm([row.title,row.family,row.summary].join(' '));return terms.some(term=>term&&hay.includes(term));});
   const trainingCard=exactCases.length?(()=>{
    const row=exactCases[0],url=(training.url||'')+(row.anchor?'#'+encodeURIComponent(row.anchor):'');
    return '<article class="occ-intel-card" data-kind="training"><div class="occ-intel-card-top"><span class="occ-intel-label">Training opportunity</span><span class="occ-intel-match">Exact occupation match</span></div><h4>'+esc(row.title)+'</h4><p>'+esc(row.current_response||'A governed training case is linked to this occupation and market.')+'</p>'+(row.decision_trigger?'<p class="occ-intel-note"><strong>Decision trigger:</strong> '+esc(row.decision_trigger)+'</p>':'')+(url?'<div class="occ-intel-links"><a href="'+esc(url)+'">Open '+esc(training.title||'training brief')+' →</a></div>':'')+'</article>';
   })():training?'<article class="occ-intel-card" data-kind="training"><div class="occ-intel-card-top"><span class="occ-intel-label">Training opportunity</span><span class="occ-intel-match">Market context only</span></div><h4>No exact occupation case is mapped yet</h4><p>'+esc(training.title)+' covers this market, but its structured evidence does not currently connect '+esc(o?.title||s)+' to a specific training response.</p><div class="occ-intel-links"><a href="'+esc(training.url)+'">Open market training brief →</a></div></article>':'<article class="occ-intel-card" data-kind="training"><div class="occ-intel-card-top"><span class="occ-intel-label">Training opportunity</span><span class="occ-intel-match">No governed match</span></div><h4>No training case is currently mapped</h4><p>The graph does not infer a training need from occupation demand alone.</p></article>';
   let sectorCard='';
   if(aligned.length){
    sectorCard='<article class="occ-intel-card" data-kind="sector"><div class="occ-intel-card-top"><span class="occ-intel-label">Sector partnerships</span><span class="occ-intel-match">'+aligned.length+' aligned</span></div><h4>'+esc(family.label||'Related sector work')+'</h4><p>These published partnerships align with the selected occupation family in '+esc(market.label)+'.</p><div class="occ-intel-list">'+intelLinks(aligned.slice(0,3))+'</div></article>';
   }else{
    const all=market.sector_partnerships||[],portfolio=all[0]?.url||('https://workforcewonkery.com/data/sector-partnerships/#market-'+encodeURIComponent(g));
    sectorCard='<article class="occ-intel-card" data-kind="sector"><div class="occ-intel-card-top"><span class="occ-intel-label">Sector partnerships</span><span class="occ-intel-match">No aligned local match</span></div><h4>No '+esc((family.label||'occupation-family').toLowerCase())+' partnership is mapped here</h4><p>'+esc(market.label)+' has '+all.length+' published sector partnership'+(all.length===1?'':'s')+', but none matches this occupation family. Workforce Wonkery does not force an unrelated sector connection.</p>'+(all.length?'<div class="occ-intel-links"><a href="'+esc(portfolio)+'">View '+esc(market.label)+' sector portfolio →</a></div>':'')+'</article>';
   }
   const wae=market.access_equity||[],countyText=(market.component_counties||[]).join(' + ');
   const equityCard='<article class="occ-intel-card" data-kind="equity"><div class="occ-intel-card-top"><span class="occ-intel-label">Access &amp; Equity</span><span class="occ-intel-match">'+wae.length+' local profile'+(wae.length===1?'':'s')+'</span></div><h4>'+esc(market.label)+' access context</h4><p>'+(countyText?esc('This labor market spans '+countyText+'. Use the component workforce-area profiles to test who can reach training, services, and employers.'):'Review the published local Access & Equity context for barriers to participation and mobility.')+'</p>'+(wae.length?'<div class="occ-intel-list">'+intelLinks(wae)+'</div>':'<p class="occ-intel-note"><strong>No governed Access & Equity profile is mapped to this market yet.</strong></p>')+'</article>';
   const policies=exactCases.length?(runtime.system_policies||[]):[];
   const policyCard=policies.length?'<article class="occ-intel-card" data-kind="policy"><div class="occ-intel-card-top"><span class="occ-intel-label">Policy</span><span class="occ-intel-match">System policy lens</span></div><h4>Policy conditions around the training decision</h4><p>These policies shape the workforce or training environment. They are not occupation-specific requirements, and program applicability still has to be checked.</p><div class="occ-intel-list">'+intelLinks(policies)+'</div></article>':'<article class="occ-intel-card" data-kind="policy"><div class="occ-intel-card-top"><span class="occ-intel-label">Policy</span><span class="occ-intel-match">No mapped trigger</span></div><h4>No training-specific policy connection is asserted</h4><p>System policy lenses appear here when the selected market and occupation have a structured training case. The graph does not add generic policy simply to fill the card.</p></article>';
   grid.innerHTML=trainingCard+sectorCard+equityCard+policyCard;
   const connected=(exactCases.length?1:0)+(aligned.length?1:0)+(wae.length?1:0)+(policies.length?1:0);
   status.textContent=market.label+' · '+(o?.title||s)+' · '+connected+' evidence layer'+(connected===1?'':'s')+' connected';
   if(boundary)boundary.textContent='Connections are deterministic from governed evidence. A missing connection means the current graph has no supported match; it is not treated as proof that no program, partnership, barrier, or policy exists.';
  }catch(err){
   if(seq!==toolRenderSeq)return;
   status.textContent='Connected context unavailable';
   grid.innerHTML='<div class="no-results"><strong>Connected intelligence could not be loaded.</strong><p style="margin-top:5px">The occupation evidence above remains available. No connection is inferred while the governed context runtime is unavailable.</p></div>';
   if(boundary)boundary.textContent='Connected intelligence fails closed so a runtime problem cannot create unsupported recommendations.';
   console.warn('Workforce Wonkery tool intelligence unavailable',err);
  }
 }
 function render(){
  const s=soc.value,o=occBySoc[s];if(!o)return;const g=geo.value,gg=marketDefs[g],m=publicationMarket(s,g),contextMarket=contextOnly(g);if(!m&&!contextMarket)return;const source=m?.source_id?srcById[m.source_id]:null;
  document.getElementById('occ-heading').textContent=o.title+' · '+(gg?.label||g);renderLabor(g);
  const exactFit=m?.fit==='exact'||m?.fit==='direct',contextFit=contextMarket&&!m;
  const fitText=contextFit?'Context-only market':(g==='california'?'Statewide published evidence':'Exact MSA evidence');
  const fit=document.getElementById('occ-fit');fit.className='pill '+(exactFit?'direct':contextFit?'regional':'missing');fit.textContent=fitText;
  document.getElementById('occ-period').textContent=m?.source_period||m?.projection_period||(publishedMetric(m)?'Source period unavailable':'No embedded projection');
  document.getElementById('occ-employment').textContent=fmt(m?.employment);document.getElementById('occ-projected').textContent='Projected: '+fmt(m?.projected_employment);document.getElementById('occ-growth').textContent=pct(m?.growth_pct);document.getElementById('occ-openings').textContent=fmt(m?.total_openings);document.getElementById('occ-wage').textContent=wage(m?.wage);
  const note=contextFit?'Exact occupation demand and wage metrics are not published for this market. No county, WDB, regional, or statewide proxy is substituted. Connected intelligence below can still use governed market + occupation relationships.':'This combination is published because the underlying EDD geography matches the selected labor market and includes usable demand and wage evidence.';
  document.getElementById('occ-note').innerHTML='<strong>'+fitText+'.</strong> '+note;
  const setDecision=(id,value)=>{const el=document.getElementById(id);if(el)el.textContent=value;};
  const demandText=m?.total_openings!=null?fmt(m.total_openings)+' openings':(m?.growth_pct!=null?pct(m.growth_pct)+' growth':'Demand unavailable');
  setDecision('occ-decision-demand',demandText);
  setDecision('occ-decision-demand-note',(m?.source_period||m?.projection_period||'No embedded demand period')+(m?.total_openings!=null?(m?.growth_pct!=null?' · '+pct(m.growth_pct)+' growth':''):''));
  setDecision('occ-decision-wage',m?.wage?wage(m.wage):'Wage unavailable');
  setDecision('occ-decision-wage-note',m?.wage?'Source-specific wage evidence. No affordability threshold is inferred.':'No standardized wage measure is embedded for this market/occupation.');
  setDecision('occ-decision-fit',fitText);
  setDecision('occ-decision-fit-note',exactFit?'Projection geography matches the selected MSA.':contextFit?'No local occupation metric proxy is used; this selection is available only to connect governed contextual evidence.':'Use the official EDD profile for source detail.');
  const tw=techBySoc[s]||null;
  setDecision('occ-tech-status',tw?.review||'No governed signal');
  setDecision('occ-tech-status-note',tw?.family?tw.family:'No occupation-level technology baseline is published yet.');
  setDecision('occ-tech-effect',tw?.effect||'No governed signal');
  setDecision('occ-tech-effect-note',tw?.opportunity||'Technology effect has not been classified.');
  setDecision('occ-tech-training',tw?.modifier||'Use standard demand + training evidence');
  setDecision('occ-tech-training-note',tw?.program_map==='Mapped'?'A program/pathway translation exists in the governed model.':'Program implications are added only when technology could change a training decision.');
  const techNote=document.getElementById('occ-tech-note');
  if(techNote)techNote.innerHTML='<strong>Ask how the work changes before asking whether the job disappears.</strong> This is not a job-loss score. '+(tw?'This is an occupation-level starting screen. '+(tw.local_grounding==='Yes'?'Local grounding is required before the training response changes.':'Any local response change still requires local demand, adoption, supply, access, and employer evidence.'):'No governed technology signal is available for this occupation yet.')+' <a href="https://www.bls.gov/emp/publications/ai-exposure-categories.htm" target="_blank" rel="noopener noreferrer">BLS AI exposure method ↗</a><br><small>BLS exposure is a separate national method and is not yet a Workforce Wonkery local training signal.</small>';
  document.getElementById('occ-table').innerHTML=comparisonGeos(g).map(id=>{const x=publicationMarket(s,id),gx=marketDefs[id],xf=id==='california'?(x?'Statewide reference':'Unavailable'):(x?'Exact MSA evidence':'Unavailable');return'<tr><td><strong>'+esc(gx?.label||id)+'</strong>'+(id===g?'<br><small>Selected labor market</small>':'')+'</td><td>'+esc(xf)+'</td><td>'+esc(fmt(x?.employment))+' → '+esc(fmt(x?.projected_employment))+'</td><td>'+esc(pct(x?.growth_pct))+'</td><td>'+esc(fmt(x?.total_openings))+'</td><td>'+esc(wage(x?.wage))+'</td></tr>';}).join('');
  const lf=laborByGeo[sourceGeo(g)],sourceIds=[m?.source_id,lf?.source_id].filter(Boolean),uniq=[...new Set(sourceIds)].map(id=>srcById[id]).filter(Boolean),links=eddLinks(s,g),ledger=uniq.slice(0,12).map(x=>'<div class="source"><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer"><strong>'+esc(x.label)+' ↗</strong></a>'+(x.source_period?'<p>'+esc(x.source_period)+'</p>':'')+'</div>');
  links.forEach(x=>ledger.push('<div class="source"><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer"><strong>Open '+esc(x.label)+' EDD occupation profile ↗</strong></a><p>Official EDD profile for the selected SOC.</p></div>'));
  document.getElementById('occ-sources').innerHTML=ledger.length?ledger.join(''):'<p>No source record is available for the selected view.</p>';
  renderDeeper(s,g,gg,o,m);
  renderConnectedIntelligence(s,g,o);
  syncLinks();
 }
 const careerOptions=[...new Map((d.occupations||[]).map(o=>{const ci=careerInfo(o);return [ci.value,ci.label]})).entries()].sort((a,b)=>a[1].localeCompare(b[1]));
 career.innerHTML='<option value="">Any career area</option>'+careerOptions.map(([v,l])=>'<option value="'+esc(v)+'">'+esc(l)+'</option>').join('');
 function clearAll(){
   search.value='';career.value='';payFilter.value='0';openingsFilter.value='0';growthFilter.value='';techFilter.value='';researchFilter.value='';document.querySelectorAll('.quickview').forEach(b=>b.classList.remove('active'));populate();
 }
 function setQuick(view,btn){
   clearAll();
   if(view==='wage')payFilter.value='40';
   if(view==='demand')openingsFilter.value='100';
   if(view==='growth')growthFilter.value='5';
   if(view==='research')researchFilter.value='yes';
   btn.classList.add('active');populate();
 }
 search.addEventListener('input',()=>{document.querySelectorAll('.quickview').forEach(b=>b.classList.remove('active'));populate();});
 [career,payFilter,openingsFilter,growthFilter,techFilter,researchFilter].forEach(el=>el.addEventListener('change',()=>{document.querySelectorAll('.quickview').forEach(b=>b.classList.remove('active'));populate();}));
 sort.addEventListener('change',populate);
 clearFilters.addEventListener('click',clearAll);
 document.querySelectorAll('.quickview').forEach(btn=>btn.addEventListener('click',()=>setQuick(btn.dataset.view,btn)));
 soc.addEventListener('change',()=>{syncOcc(true,true);render();renderResults(filtered());});
 geo.addEventListener('change',()=>{
  preferredSoc='';
  const u=new URL(window.location.href);
  u.searchParams.set('geo',geo.value);
  u.searchParams.delete('soc');
  history.pushState({geo:geo.value,soc:''},'',u);
  applyGeoChange(false);
 });
 function applyGeoChange(push){
  const next=geo.value;
  if(!next||!selectable.includes(next))return;
  if(preferredSoc){if(!publicationMarket(preferredSoc,next)&&!contextOnly(next))preferredSoc='';}
  syncContextControls();
  populate();
  syncGeo(!!push);
  if(soc.value?(publicationMarket(soc.value,next)||contextOnly(next)):false)render();
  else renderLabor(next);
  syncLinks();
 }
 window.addEventListener('popstate',()=>{
  const p=new URLSearchParams(window.location.search),nextGeo=p.get('geo'),nextSoc=p.get('soc');
  if(nextGeo){if(selectable.includes(nextGeo))geo.value=nextGeo;}
  preferredSoc=nextSoc?(occBySoc[nextSoc]?nextSoc:''):'';
  applyGeoChange(false);
  if(nextSoc){
   if([...soc.options].some(o=>o.value===nextSoc)){
    soc.value=nextSoc;preferredSoc=nextSoc;render();renderResults(filtered());syncLinks();
   }
  }
 });
 syncGeo(false);syncContextControls();populate();

    }catch(err){
      console.error('Workforce Wonkery Occupation Explorer startup error',err);
      const msg=String(err?(err.message||err):'Unknown startup error');
      const state=document.getElementById('occ-data-state');
      const summary=document.getElementById('occ-results-summary');
      const note=document.getElementById('occ-note');
      if(state)state.textContent='Explorer startup error';
      if(summary)summary.textContent='The Occupation Explorer could not start.';
      if(note)note.innerHTML='<strong>Explorer error:</strong> '+msg;
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();