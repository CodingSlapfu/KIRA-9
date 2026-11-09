import assert from 'node:assert/strict';
import {compile,encode,decode,encodeEditable,PHONES,sectionProject} from '../studio/model.mjs';
const base={format:'KIRA9-PROJECT-1',lyrics:'[Verse]\nhello\n[Bridge]\noriginal words',bpm:120};
for(const mode of ['Vocalise','Scat','Hum','Vocables']){const p={...base,vocalMode:mode};const song=compile(p,{});assert(song.events.length);assert.deepEqual(decode(encode(song)).events,song.events);const saved=decode(encodeEditable(song,p));assert.equal(saved.project.vocalMode,mode);if(mode==='Hum')assert(song.events.every(e=>e.phone===PHONES.indexOf('M')));}
const mixed={...base,sectionModes:{1:'Hum'}};const s=compile(mixed,{hello:['HH','EH','L','OW']});assert.equal(s.events.at(-1).phone,PHONES.indexOf('M'));assert.equal(mixed.lyrics,base.lyrics);assert.equal(sectionProject(mixed,1).vocalMode,'Hum');
assert.throws(()=>compile({...base,vocalMode:'Scat',swing:17},{}));assert.throws(()=>compile({...base,vocalMode:'Scat',syllables:'bad'},{}));
const a=compile({...base,vocalMode:'Scat',swing:12},{});assert.equal(a.events[0].tick,0);assert.equal(a.events[2].tick,60);assert.deepEqual(a,compile({...base,vocalMode:'Scat',swing:12},{}));console.log('PASS wordless modes, deterministic swing, mixed sections, editable roundtrip and bounds');
