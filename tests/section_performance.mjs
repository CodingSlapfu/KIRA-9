import assert from 'node:assert/strict';
import {compile,encodeEditable,decode,sectionProject,setPerformance,modeDefaults} from '../studio/model.mjs';
const p={format:'KIRA9-PROJECT-1',lyrics:'[Verse]\nhello\n[Bridge]\noriginal words',bpm:120,voice:0,expression:110};
for(const [k,v]of Object.entries(modeDefaults('Hum')))setPerformance(p,'1',k,v);
setPerformance(p,'1','voice',3);setPerformance(p,'1','emotion',2);setPerformance(p,'1','expression',75);
const verse=sectionProject(p,0),bridge=sectionProject(p,1);
assert.equal(verse.voice,0);assert.equal(verse.expression,110);assert.equal(bridge.voice,3);assert.equal(bridge.vocalMode,'Hum');assert.equal(bridge.emotion,2);
const restored=decode(encodeEditable(compile(bridge,{}),bridge)).project;
for(const key of ['voice','emotion','expression','vocalMode','breath','glide'])assert.equal(restored[key],bridge[key]);
const song=compile(p,{hello:['HH','EH','L','OW']});assert(song.events.length>8);assert.equal(p.lyrics,'[Verse]\nhello\n[Bridge]\noriginal words');
assert.throws(()=>setPerformance(p,'7','voice',2));assert.throws(()=>setPerformance(p,'all','bad',2));
const legacy={...p,sectionSettings:undefined,sectionModes:{1:'Scat'}};assert.equal(sectionProject(legacy,1).vocalMode,'Scat');
console.log('PASS independent section identity/expression/defaults, legacy modes, editable roundtrip, mixed compile and preserved lyrics');

const bop=compile({...p,sectionSettings:undefined,vocalMode:'Scat',syllables:'bop',density:1},{}).events;assert(bop[1].duration>bop[2].duration);assert.equal(bop[2].duration,8);
const held=compile({...p,sectionSettings:undefined,vocalMode:'Vocalise',syllables:'ee uh',density:2,noteTicks:384,wordlessNotes:[62,65]},{});assert.equal(held.ticks,768);assert.equal(held.events[0].phone,18);assert.throws(()=>compile({...p,vocalMode:'Scat',noteTicks:24},{}));
console.log('PASS vowel sustain before final scat consonants, editable long notes/vowels and duration bounds');
