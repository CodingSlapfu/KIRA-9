// SPDX-License-Identifier: MIT
import assert from 'node:assert/strict';import {compile,PHONES} from '../studio/model.mjs';
const lex={again:['AH0','G','EH1','N'],light:['L','AY1','T']};
const p={bpm:120,key:0,lyrics:'again light',align:[],overrides:{}};
let score=compile(p,lex);assert.deepEqual(score.events.filter(e=>[PHONES.indexOf('AH'),PHONES.indexOf('EH')].includes(e.phone)).map(e=>e.stress),[0,1]);
assert.equal(score.events.at(-1).phone,PHONES.indexOf('T'));
const elapsed=[];for(const bpm of [60,120,180]){const s=compile({...p,bpm,lyrics:'light'},lex);const l=s.events[0];elapsed.push(l.duration*60000/(bpm*96));assert(s.events[1].duration>l.duration);}
assert(Math.max(...elapsed)-Math.min(...elapsed)<11);
score=compile({...p,align:[{stress:2}]},lex);assert(score.events.filter(e=>[PHONES.indexOf('AH'),PHONES.indexOf('EH')].includes(e.phone)).every(e=>e.stress===2));
assert.throws(()=>compile({...p,overrides:{again:['BAD']}},lex),/Pronunciation/);
console.log('PASS lexical syllable stress, explicit override, vowel sustain and bounded consonant timing at 60/120/180 BPM');
