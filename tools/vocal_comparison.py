#!/usr/bin/env python3
"""Reproduce Issue #2 A/B recordings; external code/tables are never imported."""
import subprocess,pathlib,json,ctypes,time,statistics,wave,array,hashlib
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/vocal-comparison';out.mkdir(parents=True,exist_ok=True)
baseline='13aca33db7491a67df6de3fbc912c48da3462c92'
def run(args):return subprocess.run(args,cwd=root,check=True,stdout=subprocess.PIPE).stdout
run(['git','fetch','origin',baseline,'--depth=1'])
for source,dest in [('core/engine.c','build/engine-before.c'),('studio/model.mjs','build/model-before.mjs')]:
 (root/dest).write_bytes(run(['git','show',baseline+':'+source]))
for v,source in [('before','build/engine-before.c'),('after','core/engine.c')]:
 run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Icore',source,'core/codec.c','core/library.c','core/tables.c','core/face.c','studio/bridge.c','-o',f'build/libkira-{v}.so'])
run(['node','tools/vocal_scores.mjs']);metrics=[]
for v in ['before','after']:
 lib=ctypes.CDLL(str(root/f'build/libkira-{v}.so'));lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
 lib.web_init();lib.web_demo(0);times=[]
 for i in range(300):
  start=time.perf_counter_ns();lib.web_render(256);times.append((time.perf_counter_ns()-start)/1000)
 ordered=sorted(times);performance={'p50_us':statistics.median(times),'p95_us':ordered[284],'p99_us':ordered[296],'max_us':max(times)}
 for i in range(3):
  filename=out/f'{i}-{v}.wav';run(['python3','tools/render_phrase.py',str(out/f'{i}-{v}.k9s'),str(filename),'--library',f'build/libkira-{v}.so'])
  with wave.open(str(filename)) as w:pcm=array.array('h',w.readframes(w.getnframes()))
  metrics.append({'phrase':i,'version':v,'file':filename.name,'sha256':hashlib.sha256(filename.read_bytes()).hexdigest(),'peak':max(abs(x) for x in pcm)/32768,'rms':(sum(x*x for x in pcm)/len(pcm))**.5/32768,'max_adjacent_step':max(abs(pcm[j]-pcm[j-2]) for j in range(2,len(pcm)))/32768,'host_callback':performance})
with wave.open(str(out/'comparison.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100)
 for i in range(3):
  for v in ['before','after']:
   with wave.open(str(out/f'{i}-{v}.wav')) as r:w.writeframes(r.readframes(r.getnframes()))
   w.writeframes(bytes(44100*4))
(out/'metrics.json').write_text(json.dumps({'baseline':baseline,'order':'For each phrase: before, one second silence, after, one second silence.','phrases':['my heart is a light we rise again','the night is soft the stars are near','we carry dreams into the night'],'note':'Host callback times are not FM-1 timings. Metrics alone do not establish intelligibility.','metrics':metrics},indent=2)+'\n')
print('PASS reproducible English A/B audio and host performance metrics; listening/transcription acceptance remains separate')
