#!/usr/bin/env python3
"""New candidate-only recognition; preserved baseline scores are referenced."""
import os,pathlib,json,re,subprocess
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
import numpy as np
from faster_whisper import WhisperModel
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/residual-pilot';g=json.loads((out/'evaluation.json').read_text());native=json.loads((out/'native.json').read_text());assert g['headroom_pass'] and g['pitch_pass'] and g['host_budget_pass'] and g['data_bytes']<=65536 and g['state_bytes_host']<=8192
assert '27924' in native['object_size'];source=json.loads((out/'extraction.json').read_text());assert min(x['snr_db'] for x in source['units'][:12])>=20
modelpath=next((root/'build/whisper').glob('models--Systran--faster-whisper-tiny.en/snapshots/*'));model=WhisperModel(str(modelpath),device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
def wer(a,b):
 row=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  n=[i]
  for j,y in enumerate(b,1):n.append(min(n[-1]+1,row[j]+1,row[j-1]+(x!=y)))
  row=n
 return row[-1]/len(a)
rows=[];previous=json.loads((root/'build/english6/evaluation.json').read_text())
for f in g['files']:
 if f['note']==84:continue
 pcm=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(out/f['file']),'-f','f32le','-ar','16000','-ac','1','pipe:1']),dtype='<f4');segs,_=model.transcribe(pcm,beam_size=5,language='en',condition_on_previous_text=False,vad_filter=False);text=' '.join(s.text for s in segs);expected=[x['word'] for x in f['segments']];words=re.findall("[a-z]+(?:'[a-z]+)?",text.lower());old=next(x for x in previous['results'] if x['engine']=='baseline' and x['note']==f['note'] and x['group']==f['group']);rows.append({'file':f['file'],'note':f['note'],'group':f['group'],'expected':' '.join(expected),'text':text,'wer':wer(expected,words),'preserved_baseline_text':old['text'],'preserved_baseline_wer':old['wer']});print(rows[-1],flush=True)
 (out/'recognition.json').write_text(json.dumps({'model':'Existing cached tiny.en, offline int8, beam5; no vocabulary/text prompt or installs','comparison':'Original frozen baseline ASR scores reused; candidate only newly transcribed. Candidate natural-time units differ in duration from baseline, so diagnostic comparison is not a controlled equal-duration speech study.','human_acceptance':False,'results':rows},indent=2)+'\n')
