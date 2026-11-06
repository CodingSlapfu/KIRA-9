#!/usr/bin/env python3
"""Only new output-weight candidate; reuse three preserved baseline WAVs, no recognition."""
import ctypes,pathlib,json,wave,hashlib,subprocess,gzip,re
import numpy as np
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/output-weight-study'
base=ctypes.CDLL(str(out/'baseline.so'));candidate=ctypes.CDLL(str(out/'output.so'))
for lib in [base,candidate]:
 lib.web_render.restype=ctypes.POINTER(ctypes.c_float);lib.web_input.restype=ctypes.c_void_p;lib.web_feedback_hash.restype=ctypes.c_uint;lib.web_init()
# Novel state-invariance probe, not a rerun of old recordings.
checks=0
for note in [48,60,72]:
 for phone in [22,18,29,18,27,18,20,1]:
  for lib in [base,candidate]:lib.web_probe_phone(phone,note)
  for block in range(12):
   for lib in [base,candidate]:lib.web_render(256)
   assert base.web_feedback_hash()==candidate.web_feedback_hash(),'Feedback state diverged'
   checks+=1
corpus=[x for x in json.loads((root/'validation/nucleus-2026-11-06/corpus.json').read_text()) if x['group']=='transitions'];records=json.loads((root/'validation/nucleus-2026-11-06/recognition.json').read_text())['results']
(out/'corpus.json').write_text(json.dumps(corpus,indent=2)+'\n')
js="import fs from 'node:fs';import {encode} from './studio/model.mjs';for(const x of JSON.parse(fs.readFileSync('build/output-weight-study/corpus.json')))fs.writeFileSync('build/output-weight-study/'+x.id+'.k9s',encode(x.score));"
subprocess.run(['node','--input-type=module','-e',js],cwd=root,check=True)
guard=(out/'guard.txt').read_text();match=re.search(r'(\d+) samples, (\d+) limiter hits, peak ([0-9.]+)',guard);assert match;sample_count,hits,peak=int(match[1]),int(match[2]),float(match[3]);assert hits>0,'Reassess recognition eligibility instead of using this failed-guard report.'
rows=[];files={};clips=[]
for item in corpus:
 name=item['id'];baseline=root/f'build/nucleus-study/{name}-baseline.wav';expected=next(r['sha256'] for r in records if r['id']==name and r['variant']=='baseline');assert hashlib.sha256(baseline.read_bytes()).hexdigest()==expected
 with wave.open(str(baseline)) as w:old=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).mean(axis=1)/32768
 raw=(out/f'{name}.k9s').read_bytes();candidate.web_init();ctypes.memmove(candidate.web_input(),raw,len(raw));assert candidate.web_load(len(raw));candidate.web_voice(0,0);chunks=[]
 while candidate.web_playing():chunks.append(np.ctypeslib.as_array(candidate.web_render(256),shape=(512,)).copy())
 for _ in range(30):chunks.append(np.ctypeslib.as_array(candidate.web_render(256),shape=(512,)).copy())
 data=np.concatenate(chunks);pcm=np.rint(np.clip(data,-1,1)*32767).astype('<i2');target=out/f'{name}-output.wav'
 with wave.open(str(target),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(pcm.tobytes())
 with gzip.open(str(target)+'.gz','wb',compresslevel=9) as f:f.write(target.read_bytes())
 files[target.name]={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'baseline_sha256':expected};clips.append({'id':name,'peak':float(max(abs(data))),'sample_frames':len(data)//2})
 new=pcm.reshape(-1,2).mean(axis=1)/32768;assert len(new)==len(old)
 for j,e in enumerate(item['score']['events']):
  if e['phone']!=18 or not j:continue
  start=round(e['tick']*44100*60/120/96);names={27:'P',31:'T',20:'K',29:'S',30:'SH',22:'M'};before=names[item['score']['events'][j-1]['phone']]
  def steps(a,n):return float(max(abs(np.diff(a[start-n:start+n+1]))))
  rows.append({'note':item['note'],'transition':before+'→IY','baseline_exact_edge':steps(old,4),'candidate_exact_edge':steps(new,4),'baseline_3ms_max':steps(old,132),'candidate_3ms_max':steps(new,132)})
result={'baseline':'d40d558 / production DSP 1641726b','candidate':'output weights smoothed at existing .003 rate, 3 additional floats; no other DSP changes','production_changed':False,'feedback_checks':checks,'feedback_hashes_identical':True,'baseline_recordings_regenerated':False,'recognition_run':False,'recognition_skip_reason':f'Full-velocity headroom guard failed: {hits} limiter hits in {sample_count} samples; recorded baseline 746.','guard':{'samples':sample_count,'limiter_hits':hits,'baseline_recorded_hits':746,'peak':peak,'stop_tails':'pass'},'clips':clips,'transitions':rows,'files':files}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',checks,'raw feedback-state comparisons; only 3 new candidate transition recordings rendered. Recognition skipped; guard failed.')
for r in rows:
 if r['note']==72:print(r)
