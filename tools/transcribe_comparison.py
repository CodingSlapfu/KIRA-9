#!/usr/bin/env python3
"""Optional host assessment: pip install faster-whisper==1.2.1; never firmware input."""
import pathlib,json,subprocess,wave
import numpy as np
from faster_whisper import WhisperModel
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/vocal-comparison'
m=WhisperModel('tiny.en',device='cpu',compute_type='int8',cpu_threads=4,download_root=str(root/'build/whisper'));results=[]
for i in range(3):
 for v in ['before','after']:
  f=out/f'{i}-{v}.wav';target=out/f'{i}-{v}-16k.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-ar','16000','-ac','1',str(target)],check=True)
  with wave.open(str(target)) as w:audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
  segments,_=m.transcribe(audio,beam_size=5,language='en',condition_on_previous_text=False,vad_filter=False)
  text=' '.join(s.text for s in segments);results.append({'phrase':i,'version':v,'transcript':text});print(i,v,text,flush=True)
(out/'transcription.json').write_text(json.dumps({'model':'Systran faster-whisper tiny.en','note':'Diagnostic only: recognition of synthetic singing is not reliable enough for release acceptance. No expected-text prompt supplied.','results':results},indent=2)+'\n')
