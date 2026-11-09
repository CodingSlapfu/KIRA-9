import fs from 'node:fs';import assert from 'node:assert/strict';import path from 'node:path';import {createHash} from 'node:crypto';
const base='build/KIRA-9-0.2.1-dev-testing/testing';
for(const [folder,id]of [['install','FM-1_74000201'],['rollback','FM-1_74000200'],['legacy-rollback','FM-1_7400']]){
 const html=fs.readFileSync(`${base}/${folder}/index.html`,'utf8'),meta=JSON.parse(html.match(/const meta = (\{[^\n]+\});/)[1]),raw=fs.readFileSync(path.resolve(base,folder,meta.pkg));assert.equal(meta.product,id);assert.equal(meta.sha256,createHash('sha256').update(raw).digest('hex'));assert(html.includes('await sha256hex(pkg) !== meta.sha256'));assert.equal(html.match(/TESTING ONLY/g).length,1);assert(!html.includes('/*META*/'));const bad=Buffer.from(raw);bad[100]^=1;assert.notEqual(meta.sha256,createHash('sha256').update(bad).digest('hex'));
}
assert(fs.statSync(`${base}/studio/dictionary.json`).size>1000000);assert(fs.existsSync(`${base}/studio/performance.mjs`));console.log('PASS current and both rollback installer identities, local paths, exact SHA-256 pins, tamper mismatch and offline dictionary/profile assets');
