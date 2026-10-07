(function(global){
'use strict';
const STORAGE_KEY='ww_workforce_lens_v1';
const LEGACY_ROLE_KEY='ww-reader-role';
const EVENT_NAME='workforcewonkery:lenschange';
const VERSION=1;
const EMPTY={version:VERSION,country_code:'US',jurisdiction_code:null,state_code:null,area_id:null,role_id:null};

function normalize(value){
  const next=Object.assign({},EMPTY,value||{});
  next.version=VERSION;
  next.country_code='US';
  const legacy=next.state_code?String(next.state_code).toUpperCase():null;
  const jurisdiction=next.jurisdiction_code?String(next.jurisdiction_code).toUpperCase():legacy;
  next.jurisdiction_code=jurisdiction||null;
  next.state_code=legacy||jurisdiction||null;
  next.area_id=next.area_id?String(next.area_id):null;
  next.role_id=next.role_id?String(next.role_id):null;
  if(!next.jurisdiction_code)next.area_id=null;
  return next;
}
function readLegacyRole(){
  try{return global.localStorage.getItem(LEGACY_ROLE_KEY)||null}catch(_){return null}
}
function read(){
  try{
    const stored=JSON.parse(global.localStorage.getItem(STORAGE_KEY)||'null');
    const value=normalize(stored);
    if(!value.role_id){
      const legacy=readLegacyRole();
      if(legacy)value.role_id=legacy;
    }
    return value;
  }catch(_){
    const value=normalize(null);
    const legacy=readLegacyRole();
    if(legacy)value.role_id=legacy;
    return value;
  }
}
function emit(value){
  global.dispatchEvent(new CustomEvent(EVENT_NAME,{detail:{lens:value}}));
}
function write(patch){
  const current=read();
  const nextPatch=Object.assign({},patch||{});
  if(Object.prototype.hasOwnProperty.call(nextPatch,'state_code')&&!Object.prototype.hasOwnProperty.call(nextPatch,'jurisdiction_code')){
    nextPatch.jurisdiction_code=nextPatch.state_code;
  }
  if(Object.prototype.hasOwnProperty.call(nextPatch,'jurisdiction_code')){
    const proposed=nextPatch.jurisdiction_code?String(nextPatch.jurisdiction_code).toUpperCase():null;
    if(proposed!==current.jurisdiction_code&&!Object.prototype.hasOwnProperty.call(nextPatch,'area_id'))nextPatch.area_id=null;
    nextPatch.state_code=proposed;
  }
  const value=normalize(Object.assign({},current,nextPatch));
  try{
    global.localStorage.setItem(STORAGE_KEY,JSON.stringify(value));
    if(value.role_id)global.localStorage.setItem(LEGACY_ROLE_KEY,value.role_id);
  }catch(_){}
  emit(value);
  return value;
}
function setJurisdiction(code){return write({jurisdiction_code:code||null,state_code:code||null,area_id:null})}
function setState(code){return setJurisdiction(code)}
function setArea(areaId){return write({area_id:areaId||null})}
function setRole(roleId){return write({role_id:roleId||null})}
function clear(){
  try{global.localStorage.removeItem(STORAGE_KEY)}catch(_){}
  const value=normalize(null);emit(value);return value;
}
function subscribe(handler){
  if(typeof handler!=='function')return function(){};
  const listener=function(event){handler(event.detail&&event.detail.lens?event.detail.lens:read())};
  global.addEventListener(EVENT_NAME,listener);
  return function(){global.removeEventListener(EVENT_NAME,listener)};
}
function context(runtime,value){
  const lens=normalize(value||read());
  const jurisdictions=((runtime||{}).jurisdictions||[]);
  const desks=((runtime||{}).jurisdiction_desks||[]);
  const areas=((runtime||{}).areas||[]);
  const roles=((runtime||{}).roles||[]);
  const jurisdiction=jurisdictions.find(function(x){return x.jurisdiction_code===lens.jurisdiction_code})||null;
  const desk=desks.find(function(x){return x.jurisdiction_code===lens.jurisdiction_code})||null;
  const area=areas.find(function(x){return x.area_id===lens.area_id&&(!lens.jurisdiction_code||x.jurisdiction_code===lens.jurisdiction_code)})||null;
  const role=roles.find(function(x){return x.id===lens.role_id})||null;
  return {
    lens:lens,
    jurisdiction:jurisdiction,
    state:jurisdiction,
    jurisdiction_desk:desk,
    state_desk:desk,
    area:area,
    role:role,
    national_fallback:!!(desk&&desk.national_fallback)
  };
}
global.WorkforceWonkeryLens=Object.freeze({
  storageKey:STORAGE_KEY,
  legacyRoleKey:LEGACY_ROLE_KEY,
  eventName:EVENT_NAME,
  get:read,
  set:write,
  setJurisdiction:setJurisdiction,
  setState:setState,
  setArea:setArea,
  setRole:setRole,
  clear:clear,
  subscribe:subscribe,
  context:context
});
})(window);
