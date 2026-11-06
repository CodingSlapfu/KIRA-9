#!/usr/bin/env python3
"""Optional diagnostic using the already installed/cached tiny.en model; no install/download."""
import pathlib,json,subprocess,wave,re
import numpy as np
from faster_whisper import WhisperModel
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/acoustic-ab';cache=root/'build/whisper';models=list(cache.glob('models--Systran--faster-whisper-tiny.en/snapshots/*'))
if not models:raise SystemExit('Existing tiny.en cache absent; do not install a model for this check.')
m=WhisperModel(str(models[0]),device='cpu',compute_type='int8',cpu_threads=4);phrases=json.loads((out/'phrases.json').read_text());results=json.loads((out/'recognition.json').read_text())['results'] if (out/'recognition.json').exists() else []
for i in [0,3,4,5]:
 for v in ['baseline','final']:
  if any(r['phrase']==i and r['version']==v for r in results):continue
  f=out/f'{i}-{v}.wav';target=out/f'{i}-{v}-16k.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-ar','16000','-ac','1',str(target)],check=True)
  with wave.open(str(target)) as w:audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
  segments,_=m.transcribe(audio,beam_size=5,language='en',condition_on_previous_text=False,vad_filter=False)
  text=' '.join(s.text for s in segments);results.append({'phrase':i,'expected':phrases[i],'version':v,'text':text});print(i,v,text,flush=True);(out/'recognition.json').write_text(json.dumps({'results':results},indent=2))
(out/'recognition.json').write_text(json.dumps({'note':'Cached same tiny.en model, default no-speech threshold, no expected-text prompt. Empty text is not a pass.','results':results},indent=2)+'\n')
