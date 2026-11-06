// SPDX-License-Identifier: MIT
import assert from 'node:assert/strict';import {spawn} from 'node:child_process';import readline from 'node:readline';
import {parseFrame,frame,upload,download} from '../studio/transfer.mjs';import {compile,encodeEditable,decode,encodePronunciations,decodePronunciations,defaultPresets,encodePresets,decodePresets,encodeArrangement,decodeArrangement} from '../studio/model.mjs';
const child=spawn('build/transfer-device',[],{stdio:['pipe','pipe','inherit']}),lines=readline.createInterface({input:child.stdout});const input=new EventTarget();input.open=async()=>{};let waiting=[],drop=0,dropOp=0,damage=false,duplicated=false,controlResolve;lines.on('line',line=>{if(line.startsWith('!')){controlResolve?.(line.slice(1));return;}const r=new Uint8Array(line.match(/../g)?.map(n=>parseInt(n,16))||[]);if(drop){drop--;return;}if(dropOp&&r[2]===dropOp){dropOp=0;return;}if(damage){damage=false;r[0]^=1;}const event=new Event('midimessage');event.data=frame(0x67,[...r]);input.dispatchEvent(event);if(duplicated){duplicated=false;const repeat=new Event('midimessage');repeat.data=frame(0x67,[...r]);input.dispatchEvent(repeat);}});
const output={open:async()=>{},send(bytes){const p=parseFrame(bytes);if(!p)throw Error('Bad outgoing protocol frame');child.stdin.write(p.op.toString(16)+' '+[...p.body].map(n=>n.toString(16)).join(' ')+'\n');}};
const control=s=>new Promise(resolve=>{controlResolve=resolve;child.stdin.write(s+'\n');});
const project={format:'KIRA9-PROJECT-1',title:'Roundtrip',lyrics:'my heart is a light',bpm:120,voice:2,style:4,key:0,align:[],overrides:{}},lex={my:['M','AY'],heart:['HH','AA','R','T'],is:['IH','Z'],a:['AH'],light:['L','AY','T']};const bytes=encodeEditable(compile(project,lex),project),options={timeout:25,retries:3};
try{
 drop=1;await upload(input,output,bytes,0,()=>{},0,options);assert.equal(Number(await control('stats')),1);
 drop=1;const received=await download(input,output,0,0,()=>{},options);assert.deepEqual(received,bytes);for(const [key,value] of Object.entries(project))assert.deepEqual(decode(received).project[key],value);assert.equal(decode(received).project.breath,6);
 dropOp=0x64;duplicated=true;await upload(input,output,bytes,1,()=>{},1,options);assert.equal(Number(await control('stats')),2);
 const corrupt=bytes.slice();corrupt[32]^=1;await assert.rejects(upload(input,output,corrupt,0,()=>{},0,options),/Checksum/);assert.equal(Number(await control('stats')),2);assert.deepEqual(await download(input,output,0,0,()=>{},options),bytes);
 await control('busy 1');await assert.rejects(upload(input,output,bytes,0,()=>{},0,options),/Stop device/);await control('busy 0');
 await control('fail 1');await assert.rejects(upload(input,output,bytes,0,()=>{},0,options),/Flash save/);await control('fail 0');assert.deepEqual(await download(input,output,0,0,()=>{},options),bytes);
 const pronunciation=encodePronunciations({kira:['K','IH','R','AH']});await upload(input,output,pronunciation,0,()=>{},3,options);assert.deepEqual(decodePronunciations(await download(input,output,0,3,()=>{},options)),{kira:['K','IH','R','AH']});
 const presets=defaultPresets();presets[2].name='Soft copper';presets[2].harmony=7;const voices=encodePresets(presets);await upload(input,output,voices,0,()=>{},4,options);assert.deepEqual(decodePresets(await download(input,output,0,4,()=>{},options)),presets);
 const arrangement=encodeArrangement(3,113,true,[2,0,1,3,4,5,6,7]);await upload(input,output,arrangement,0,()=>{},5,options);assert.deepEqual(decodeArrangement(await download(input,output,0,5,()=>{},options)),{count:3,tempo:113,loop:true,active:true,slots:[2,0,1,3,4,5,6,7]});
 await assert.rejects(download(input,output,7,0,()=>{},options),/Empty slot/);
 damage=true;assert.deepEqual(await download(input,output,0,0,()=>{},options),bytes);
 console.log('PASS browser↔actual C device protocol: editable project and score, pronunciation and eight voice presets roundtrip; loss/retry/duplicate/corruption/busy/save-failure preserve committed state');
}finally{child.stdin.end();lines.close();child.kill();}
