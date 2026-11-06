// SPDX-License-Identifier: MIT; reproducible English before/after inputs.
import fs from 'node:fs';import {compile,encode} from '../studio/model.mjs';import {compile as before} from '../build/model-before.mjs';
const lex=JSON.parse(fs.readFileSync('studio/dictionary.json')),oldlex=Object.fromEntries(Object.entries(lex).map(([k,v])=>[k,v.map(p=>p.replace(/[012]$/,''))]));
const phrases=['my heart is a light we rise again','the night is soft the stars are near','we carry dreams into the night'];
fs.mkdirSync('build/vocal-comparison',{recursive:true});
for(let i=0;i<phrases.length;i++){const p={format:'KIRA9-PROJECT-1',bpm:120,key:0,lyrics:phrases[i],align:[],overrides:{}};for(const [name,fn,d]of [['before',before,oldlex],['after',compile,lex]])fs.writeFileSync(`build/vocal-comparison/${i}-${name}.k9s`,encode(fn(p,d)));}
console.log('Created three English phrase A/B scores with original and stress-preserving compilers.');
