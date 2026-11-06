#!/usr/bin/env python3
"""Narrow, identical-score baseline/late-nucleus study. No download or acceptance replay."""
import argparse,pathlib,ctypes,json,wave,hashlib,subprocess,os,re
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--recognize',action='store_true');p.add_argument('--variant',choices=['late','smooth'],default='late');args=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/nucleus-study';items=json.loads((out/'corpus.json').read_text());results=[]
def error(expected,actual):
 a=re.findall('[a-z]+',expected.lower());b=re.findall('[a-z]+',actual.lower());row=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  nextrow=[i]
  for j,y in enumerate(b,1):nextrow.append(min(nextrow[-1]+1,row[j]+1,row[j-1]+(x!=y)))
  row=nextrow
 return row[-1]/len(a)
model=None
if args.recognize:
 os.environ['HF_HUB_OFFLINE']='1'
 from faster_whisper import WhisperModel
 cache=list((root/'build/whisper').glob('models--Systran--faster-whisper-tiny.en/snapshots/*'));assert cache,'Same cached model required; do not download.'
 model=WhisperModel(str(cache[0]),device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
for variant in (['baseline','late'] if args.variant=='late' else ['smooth']):
 lib=ctypes.CDLL(str(out/f'{variant}.so'));lib.web_input.restype=ctypes.c_void_p;lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
 for item in items:
  name=item['id'];raw=(out/f'{name}.k9s').read_bytes();lib.web_init();ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));lib.web_voice(0,0);chunks=[];blocks=0
  while lib.web_playing() and blocks<44100*30//256:
   chunks.append(np.ctypeslib.as_array(lib.web_render(256),shape=(512,)).copy());blocks+=1
  for _ in range(30):chunks.append(np.ctypeslib.as_array(lib.web_render(256),shape=(512,)).copy())
  data=np.concatenate(chunks);path=out/f'{name}-{variant}.wav';pcm=np.rint(np.clip(data,-1,1)*32767).astype('<i2')
  with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(pcm.tobytes())
  result={'id':name,'group':item['group'],'note':item['note'],'variant':variant,'expected':item['lyrics'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'peak':float(np.max(abs(data))),'rms':float(np.sqrt(np.mean(data*data)))}
  if model:
   audio=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar','16000','-ac','1','pipe:1']);audio=np.frombuffer(audio,dtype='<f4')
   segments,_=model.transcribe(audio,beam_size=5,language='en',condition_on_previous_text=False,vad_filter=False)
   segments=list(segments);text=' '.join(s.text for s in segments);result.update(text=text,wer=error(item['lyrics'],text),no_speech=[s.no_speech_prob for s in segments]);print(name,variant,repr(text),'WER',round(result['wer'],3),flush=True)
  results.append(result);(out/('recognition.json' if args.variant=='late' else 'recognition-smooth.json')).write_text(json.dumps({'baseline':'3a407ec','change':('Diphthong tract progress only: linear whole event versus initial 60% nucleus + final 40% linear glide' if args.variant=='late' else 'Band weights moved from instantaneous resonator output to existing smoothed input-gain targets; original glide unchanged'),'model':'same cached tiny.en; offline, no lyric prompts','results':results},indent=2)+'\n')
for item in (items if args.variant=='late' else []):
 if item['group'] in ['vowels','transitions']:
  pair=[r for r in results if r['id']==item['id']];assert pair[0]['sha256']==pair[1]['sha256'],'Non-diphthong control changed'
with wave.open(str(out/('comparison.wav' if args.variant=='late' else 'comparison-smooth.wav')),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100)
 for item in items:
  for variant in ['baseline',args.variant]:
   with wave.open(str(out/f"{item['id']}-{variant}.wav")) as r:w.writeframes(r.readframes(r.getnframes()))
   w.writeframes(bytes(44100*4))
print('Study complete; fixed scores preserved. Late variant has byte-identical non-diphthong controls.',flush=True)
