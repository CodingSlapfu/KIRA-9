#!/usr/bin/env python3
"""DSP-only A/B against d8bff4d; requires NumPy, no transcription model."""
import subprocess,pathlib,json,ctypes,time,statistics,wave,hashlib
import numpy as np
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/acoustic-ab';out.mkdir(parents=True,exist_ok=True)
baseline='d8bff4dcb34c043c128c43bc76b5688c9adcacb7'
def run(args,**kw):return subprocess.run(args,cwd=root,check=True,**kw)
run(['git','fetch','origin',baseline,'--depth=1'],stdout=subprocess.PIPE)
(out/'engine-baseline.c').write_bytes(subprocess.check_output(['git','show',baseline+':core/engine.c'],cwd=root))
run(['node','tools/acoustic_scores.mjs']);metrics={};timings={};files={}
for v,source in [('baseline','build/acoustic-ab/engine-baseline.c'),('final','core/engine.c')]:
 common=[source,'core/codec.c','core/library.c','core/tables.c']
 run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Icore',*common,'core/face.c','studio/bridge.c','-o',str(out/f'{v}.so')])
 run(['cc','-O2','-ffp-contract=off','-Icore','tests/acoustic_probe.c',*common,'-o',str(out/f'probe-{v}')])
 p=run([str(out/f'probe-{v}')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 data=np.frombuffer(p.stdout,dtype='<f4').reshape(7,39,4,2048,2);assert np.isfinite(data).all()
 assert 'clips=0' in p.stderr.decode(),p.stderr.decode()
 metrics[v]={'grid':p.stderr.decode().strip(),'phones':{}}
 for phone,name in [(18,'IY'),(17,'IH'),(29,'S'),(30,'SH'),(38,'Z'),(22,'M')]:
  samples=data[0,phone-1,1,:,0];q=abs(np.fft.rfft(samples*np.hanning(len(samples))))**2;f=np.fft.rfftfreq(len(samples),1/44100);power=float(q.sum());rms=float(np.sqrt(np.mean(samples*samples)))
  metrics[v]['phones'][name]={'centroid_hz':float((q*f).sum()/power),'f2_fraction':float(q[(f>1500)&(f<3500)].sum()/power),'low_fraction':float(q[f<1000].sum()/power),'rms':rms}
 lib=ctypes.CDLL(str(out/f'{v}.so'));lib.web_render.restype=ctypes.POINTER(ctypes.c_float);lib.web_init();lib.web_demo(0);times=[]
 for i in range(300):
  start=time.perf_counter_ns();lib.web_render(256);times.append((time.perf_counter_ns()-start)/1000)
 times.sort();timings[v]={'p50_us':statistics.median(times),'p95_us':times[284],'p99_us':times[296],'max_us':max(times)}
 for i in range(6):
  target=out/f'{i}-{v}.wav';run(['python3','tools/render_phrase.py',str(out/f'phrase-{i}.k9s'),str(target),'--library',str(out/f'{v}.so')],stdout=subprocess.PIPE);
  with wave.open(str(target)) as rendered:assert rendered.getnframes()>0,target
  files[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
b=metrics['baseline']['phones'];a=metrics['final']['phones'];assert a['IY']['f2_fraction']>b['IY']['f2_fraction']*10;assert a['IH']['f2_fraction']>b['IH']['f2_fraction']*10
assert a['S']['centroid_hz']>a['SH']['centroid_hz']+500
assert .15<a['Z']['low_fraction']<.85,a['Z'];assert a['M']['low_fraction']>.8
with wave.open(str(out/'comparison.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100)
 for i in range(6):
  for v in ['baseline','final']:
   with wave.open(str(out/f'{i}-{v}.wav')) as r:w.writeframes(r.readframes(r.getnframes()))
   w.writeframes(bytes(44100*4))
files['comparison.wav']=hashlib.sha256((out/'comparison.wav').read_bytes()).hexdigest()
(out/'analysis.json').write_text(json.dumps({'baseline':baseline,'note':'Identical timed inputs; spectral corrections are not a word intelligibility pass. Host timings are not FM-1 timings.','order':'Each phrase: baseline, silence, final, silence. First three are prior fixtures; last three are held-out contrasts.','phrases':json.loads((out/'phrases.json').read_text()),'spectra':metrics,'host_callback':timings,'wav_sha256':files},indent=2)+'\n')
print('PASS upper-formant recovery, sibilant separation, retained voiced-fricative bar and nasal energy, seven-voice/four-pitch no-clipping grid; six identical-score audio A/B pairs')
