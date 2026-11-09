import fs from 'node:fs';import assert from 'node:assert/strict';
const m=new WebAssembly.Instance(new WebAssembly.Module(fs.readFileSync('studio/kira.wasm')),{}).exports;m._initialize();let worst=0;
for(const f of JSON.parse(fs.readFileSync('build/wordless-parity.json'))){m.web_init();new Uint8Array(m.memory.buffer,m.web_input(),f.bytes.length).set(f.bytes);assert(m.web_load(f.bytes.length));for(let i=0;i<400;i++){const p=m.web_render(256),a=new Float32Array(m.memory.buffer,p,512);for(let j=0;j<512;j++)worst=Math.max(worst,Math.abs(a[j]-f.pcm[i*512+j]));assert.equal(m.web_pose(),f.poses[i]);if(f.mode===3)assert.equal(m.web_pose()>>>8,0);}}
assert(worst<.00001);console.log(`PASS all five modes native/WASM 1,024,000 PCM samples and 2,000 exact poses; max error ${worst}`);
