import assert from 'node:assert/strict';import fs from 'node:fs';import {encode,PHONES} from '../studio/model.mjs';
const m=new WebAssembly.Instance(new WebAssembly.Module(fs.readFileSync('studio/kira.wasm')),{}).exports;m._initialize();m.web_init();
const bytes=encode({bpm:120,ticks:144,events:[{tick:0,duration:12,phone:PHONES.indexOf('F'),note:60,velocity:100,stress:0},{tick:120,duration:24,phone:PHONES.indexOf('AA'),note:64,velocity:100,stress:1}]});new Uint8Array(m.memory.buffer,m.web_input(),bytes.length).set(bytes);assert(m.web_load(bytes.length));let sawGap=false,sawVowel=false;
for(let i=0;i<150;i++){m.web_render(256);const t=m.web_tick(),pose=m.web_pose();if(t>=48&&t<100){assert.equal(pose,0,'Silent labiodental gap must close');sawGap=true;}if(t>=124&&m.web_playing()){assert(pose>>>8>0);sawVowel=true;}}
assert(sawGap&&sawVowel);m.web_stop();assert.equal(m.web_pose(),0);
let hashes=new Set();for(let emotion=0;emotion<4;emotion++)for(let mouth=0;mouth<6;mouth++){const p=m.web_face_pose(mouth|(24<<8),17100,emotion,1);const pixels=new Uint16Array(m.memory.buffer,p,240*240);assert(pixels.some(x=>x));hashes.add(pixels.reduce((a,b)=>(Math.imul(a,31)+b)>>>0,0));}assert(hashes.size>=12);
console.log('PASS new WASM silent-F gap, resumed-vowel pose, Stop closure, distinct expression/mouth render combinations');
