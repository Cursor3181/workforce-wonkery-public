(function(global){
'use strict';
const STORAGE_KEY='ww_workforce_lens_v1';
const EVENT_NAME='workforcewonkery:lenschange';
const VERSION=1;
const EMPTY={version:VERSION,country_code:'US',state_code:null,area_id:null,role_id:null};

function normalize(value){
  const next=Object.assign({},EMPTY,value||{});
  next.version=VERSION;
  next.country_code='US';
  next.state_code=next.state_code?String(next.state_code).toUpperCase():null;
  next.area_id=next.area_id?String(next.area_id):null;
  next.role_id=next.role_id?String(next.role_id):null;
  if(!next.state_code)next.area_id=null;
  return next;
}
function read(){
  try{return normalize(JSON.parse(global.localStorage.getItem(STORAGE_KEY)||'null'))}
  catch(_){return normalize(null)}
}
function emit(value){
  global.dispatchEvent(new CustomEvent(EVENT_NAME,{detail:{lens:value}}));
}
function write(patch){
  const value=normalize(Object.assign({},read(),patch||{}));
  try{global.localStorage.setItem(STORAGE_KEY,JSON.stringify(value))}catch(_){}
  emit(value);
  return value;
}
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
global.WorkforceWonkeryLens=Object.freeze({
  storageKey:STORAGE_KEY,
  eventName:EVENT_NAME,
  get:read,
  set:write,
  clear:clear,
  subscribe:subscribe
});
})(window);
