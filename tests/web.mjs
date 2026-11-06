// SPDX-License-Identifier: MIT
import assert from 'node:assert/strict';import fs from 'node:fs';
import {compile,encode,generate,validateProject,words} from '../studio/model.mjs';import {pack7,unpack7,frame,request,reply} from '../studio/transfer.mjs';
const dictionary=JSON.parse(fs.readFileSync('studio/dictionary.json'));
const m=new WebAssembly.Instance(new WebAssembly.Module(fs.readFileSync('studio/kira.wasm')),{}).exports;m._initialize();m.web_init();
const lyrics='[Verse]\n  My heart is a light.\n[Chorus]\nWe rise again!';const project={format:'KIRA9-PROJECT-1',lyrics,bpm:120,align:[],overrides:{}};const before=JSON.stringify(project);const song=compile(project,dictionary),bytes=encode(song);assert.equal(JSON.stringify(project),before);assert.equal(words(lyrics).length,8);new Uint8Array(m.memory.buffer,m.web_input(),bytes.length).set(bytes);assert.equal(m.web_load(bytes.length),1);let energy=0;for(let i=0;i<100;i++){const ptr=m.web_render(256),pcm=new Float32Array(m.memory.buffer,ptr,512);for(const v of pcm){assert(Number.isFinite(v));assert(Math.abs(v)<=.951);energy+=v*v;}}assert(energy>1);m.web_stop();for(let i=0;i<100;i++)m.web_render(256);assert(!m.web_playing());
const invalid=bytes.slice();invalid[30]^=1;new Uint8Array(m.memory.buffer,m.web_input(),invalid.length).set(invalid);assert.equal(m.web_load(invalid.length),0);
assert.throws(()=>compile({...project,lyrics:'qzxwvv'},dictionary),/Pronunciation needed/);assert.throws(()=>compile({...project,align:[{note:140}]},dictionary),/timing\/note/);assert.throws(()=>validateProject({lyrics}),/supported/);
assert(generate('a silver river','quiet').lyrics.includes('a silver river'));
const text=Array.from({length:1000},(_,i)=>i&255);assert.deepEqual(unpack7(pack7(text)),text);const original=generate('A <script> signal','quiet');assert.equal(original.title,'A <script> signal');assert(compile(original,dictionary).events.length>100);
for(let i=0;i<8;i++){m.web_demo(i);assert(m.web_playing());const factory=JSON.parse(fs.readFileSync('factory/songs.json'))[i];const frames=Math.ceil(factory.ticks*60/factory.bpm/96*44100)+2048;for(let f=0;f<frames;f+=1024)m.web_render(1024);assert(!m.web_playing());}
const data=reply({flag:0,address:12},[1,2]);assert.equal(data[0],240);assert.equal(data.at(-1),247);assert.equal(request(frame(48,[0,12,0,0,0,2,0,0])).address,12);assert.equal(request([1,2]),null);
console.log('PASS web lyric preservation, headings, pronunciations, bounds, shared-WASM song decode/render/stop, all eight factory demos, MIDI 7-bit framing');
