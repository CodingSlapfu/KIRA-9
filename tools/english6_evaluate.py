#!/usr/bin/env python3
"""New small English control set; no previous acceptance/failed experiment replay."""
import pathlib,ctypes,json,time,wave,hashlib,subprocess,re,os
import numpy as np
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/english6';corpus=json.loads((out/'corpus.json').read_text());results=[];timings={}
def edit(a,b):
 row=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  n=[i]
  for j,y in enumerate(b,1):n.append(min(n[-1]+1,row[j]+1,row[j-1]+(x!=y)))
  row=n
 return row[-1]/len(a)
for engine in ['baseline','prototype']:
 lib=ctypes.CDLL(str(out/f'{engine}.so'));lib.web_input.restype=ctypes.c_void_p;lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
 if engine=='baseline':lib.baseline_peak.restype=ctypes.c_float
 else:lib.web_diagnostics.restype=ctypes.POINTER(ctypes.c_float)
 lib.web_init();lib.web_demo(0);cpu=[];wall=[]
 for _ in range(1000):
  a=time.thread_time_ns();b=time.perf_counter_ns();lib.web_render(256);wall.append((time.perf_counter_ns()-b)/1000);cpu.append((time.thread_time_ns()-a)/1000)
 def stats(a):a=sorted(a);return {'p50_us':a[len(a)//2],'p95_us':a[int(len(a)*.95)],'p99_us':a[int(len(a)*.99)],'max_us':max(a)}
 timings[engine]={'host_thread_cpu':stats(cpu),'host_wall':stats(wall)}
 for item in corpus:
  raw=(out/f"{item['id']}.k9s").read_bytes();lib.web_init()
  if engine=='baseline':lib.baseline_reset()
  ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));lib.web_voice(0,0);data=[];count=0
  while lib.web_playing() and count<44100*10//256:data.append(np.ctypeslib.as_array(lib.web_render(256),shape=(512,)).copy());count+=1
  for _ in range(30):data.append(np.ctypeslib.as_array(lib.web_render(256),shape=(512,)).copy())
  pcm=np.concatenate(data);assert np.isfinite(pcm).all();f=out/f"{item['id']}-{engine}.wav"
  with wave.open(str(f),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.rint(np.clip(pcm,-1,1)*32767).astype('<i2').tobytes())
  peak=float(lib.baseline_peak()) if engine=='baseline' else float(lib.web_diagnostics()[0]);over=int(lib.baseline_clips()) if engine=='baseline' else int(lib.web_diagnostics()[3]);assert engine!='prototype' or (peak<.9 and over==0)
  results.append({'id':item['id'],'engine':engine,'expected':item['text'],'note':item['note'],'group':item['group'],'unclamped_peak':peak,'over94':over,'rms':float(np.sqrt(np.mean(pcm*pcm))),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
# Same already-cached recognizer, no network/model installation, no text prompts.
os.environ['HF_HUB_OFFLINE']='1'
from faster_whisper import WhisperModel
models=list((root/'build/whisper').glob('models--Systran--faster-whisper-tiny.en/snapshots/*'));assert models
model=WhisperModel(str(models[0]),device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
lex=json.loads((root/'studio/dictionary.json').read_text());vowels=set('AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW'.split())
for row in results:
 f=out/f"{row['id']}-{row['engine']}.wav";audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-f','f32le','-ar','16000','-ac','1','pipe:1']),dtype='<f4')
 seg,_=model.transcribe(audio,beam_size=5,language='en',condition_on_previous_text=False,vad_filter=False);text=' '.join(s.text for s in seg);words=re.findall("[a-z]+(?:'[a-z]+)?",text.lower());row['text']=text;row['wer']=edit(row['expected'].split(),words)
 if row['group']=='vowels':
  extracted=[]
  for w in words:
   for p in lex.get(w,[]):
    p=re.sub('[012]$','',p)
    if p in vowels:extracted.append(p);break
  row['recognized_vowels']=extracted;row['vowel_sequence_error']=edit(['IY','IH','EH','AE'],extracted)
 print(row['id'],row['engine'],repr(text),'WER',round(row['wer'],3),flush=True)
 (out/'evaluation.json').write_text(json.dumps({'scope':'Dry monophonic research prototype, MIDI 48/60/72; no word/listening pass inferred from spectra. MIDI84 fails stricter .90 peak margin; not promoted.','model':'same cached tiny.en offline, beam5, no expected text prompt','cpu_note':'Host microseconds are NOT FM-1 CPU. One calling thread; physical 5.8ms deadline unverified.','host_callback':timings,'results':results},indent=2)+'\n')
