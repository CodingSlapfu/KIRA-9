// SPDX-License-Identifier: MIT; identical timed inputs isolate DSP changes.
import fs from 'node:fs';import {compile,encode,words} from '../studio/model.mjs';
const lex=JSON.parse(fs.readFileSync('studio/dictionary.json'));
const phrases=['my heart is a light we rise again','the night is soft the stars are near','we carry dreams into the night','see she sue shoe','light night right','we sing a new song'];
fs.mkdirSync('build/acoustic-ab',{recursive:true});
for(let i=0;i<phrases.length;i++){const p={bpm:120,key:0,lyrics:phrases[i],align:[],overrides:{}};if(i>=3)p.align=words(p.lyrics).map(()=>({note:60}));fs.writeFileSync(`build/acoustic-ab/phrase-${i}.k9s`,encode(compile(p,lex)));}
fs.writeFileSync('build/acoustic-ab/phrases.json',JSON.stringify(phrases));
