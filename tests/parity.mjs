// SPDX-License-Identifier: MIT
import fs from 'node:fs';import assert from 'node:assert/strict';
const e=new WebAssembly.Instance(new WebAssembly.Module(fs.readFileSync('studio/kira.wasm')),{}).exports;e._initialize();e.web_init();e.web_demo(0);e.web_voice(0,0);const bytes=fs.readFileSync('build/golden.f32'),gold=new Float32Array(bytes.buffer,bytes.byteOffset,bytes.length/4);let max=0;
for(let i=0;i<100;i++){const p=e.web_render(256),pcm=new Float32Array(e.memory.buffer,p,512);for(let j=0;j<512;j++)max=Math.max(max,Math.abs(pcm[j]-gold[i*512+j]));}
assert(max<.00001);console.log('PASS native/WASM PCM parity: 51200 samples, max absolute error '+max);
