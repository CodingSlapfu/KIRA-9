import assert from 'node:assert/strict';import fs from 'node:fs';import {productOf,logicalImage,checkUfw,ufwEntries} from '../platform/web/fm1pkg.js';
const raw=new Uint8Array(fs.readFileSync('app/build/kira-9-0.2.1-dev.fwsc'));assert.equal(productOf(raw),'FM-1_74000201');const image=logicalImage(raw);checkUfw(image);const parts=ufwEntries(image);assert.deepEqual(Object.keys(parts).sort(),['0','100']);assert.deepEqual(image.slice(parts[100].off,parts[100].off+parts[100].len),new Uint8Array(fs.readFileSync('app/build/loader/ota.bin')));
for(const pos of [0,0x40,parts[0].off+0x4000,parts[100].off+100]){const bad=image.slice();bad[pos]^=1;assert.throws(()=>checkUfw(bad));}
for(const len of [0,63,image.length-1])assert.throws(()=>checkUfw(image.slice(0,len)));
console.log('PASS actual KIRA-9 FWSC identity/integrity, byte-identical loader, corruption and truncation rejected before install');
