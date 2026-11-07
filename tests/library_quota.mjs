import assert from 'node:assert/strict';
import {setupLibrary} from '../studio/library.mjs';
const nodes=new Map();function element(){return {value:'',files:[],children:[],replaceChildren(){this.children=[];},append(x){this.children.push(x);},setAttribute(){}};}
globalThis.document={getElementById(id){if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);},createElement:element};
let fail=false,saved=null;globalThis.localStorage={getItem(){return saved;},setItem(k,v){if(fail)throw Error('quota');saved=v;}};
let status='',pron;const draft={format:'KIRA9-PROJECT-1',title:'Preserved draft',lyrics:'hello',bpm:120,align:[],overrides:{}};
const lib=setupLibrary({setPronunciations(p){pron=p;},project:()=>draft,status:s=>status=s,applyPreset(){},openProject(){}});
fail=true;nodes.get('saveProject').onclick();assert.match(status,/could not be saved/i);assert.equal(lib.get().projects.length,0);assert.equal(saved,null);
fail=false;nodes.get('saveProject').onclick();assert.equal(lib.get().projects.length,1);const before=saved;
fail=true;nodes.get('pronunciations').value='kira = K IH R AH';nodes.get('savePronunciations').onclick();assert.match(status,/could not be saved/i);assert.deepEqual(pron,{});assert.equal(saved,before);
const input=nodes.get('presetRows').children[0].children[1].children[0];input.value='3';input.onchange();assert.match(status,/could not be saved/i);assert.equal(saved,before);assert.notEqual(lib.get().presets[0].voice,3);
console.log('PASS browser quota: failed project/preset/pronunciation saves roll back and never report success; draft preserved');
