// SPDX-License-Identifier: MIT; fixed-pitch controls for nucleus/glide investigation.
import fs from 'node:fs';import {compile,encode,words} from '../studio/model.mjs';
const reuse=process.argv.includes('--from-corpus');
const lex=reuse?{}:JSON.parse(fs.readFileSync('studio/dictionary.json'));
const groups=[['vowels','beat bit bet bat boot bought'],['glides','bait bet bite bat boat bought'],['transitions','pea tea key see she me'],['contexts','my high light night right']];
const out='build/nucleus-study';fs.mkdirSync(out,{recursive:true});const items=reuse?JSON.parse(fs.readFileSync('validation/nucleus-2026-11-06/corpus.json')):[];
if(reuse)for(const item of items)fs.writeFileSync(`${out}/${item.id}.k9s`,encode(item.score));
if(!reuse)for(const note of [48,60,72])for(const [group,lyrics] of groups){const id=`${group}-${note}`,project={bpm:120,key:0,lyrics,align:words(lyrics).map(()=>({note,duration:96,stress:1})),overrides:{},wordGap:24};const score=compile(project,lex);fs.writeFileSync(`${out}/${id}.k9s`,encode(score));items.push({id,group,note,lyrics,score});}
fs.writeFileSync(`${out}/corpus.json`,JSON.stringify(items,null,2));console.log('Created fixed-pitch controls at MIDI 48/60/72; scores shared unchanged by both DSP variants.');
