"""Original synthetic comparisons through actual before/after C engines."""
from pathlib import Path
import subprocess,json,ctypes,wave,struct,time
r=Path(__file__).resolve().parents[1];o=r/'validation/development-023';o.mkdir(exist_ok=True)
subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Icore','core/engine.c','core/codec.c','core/library.c','core/tables.c','core/face.c','studio/bridge.c','-o','build/libkira.so'],cwd=r,check=True)
js="import{compile,encode}from './studio/model.mjs';console.log(JSON.stringify(['Lyrics','Vocalise','Scat','Hum','Vocables'].map(vocalMode=>Array.from(encode(compile({bpm:100,lyrics:'we rise again',vocalMode,density:3},{we:['W','IY'],rise:['R','AY','Z'],again:['AH','G','EH','N']}))))));"
scores=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=r,text=True));metrics={}
for label,library in [('before','build/before023.so'),('after','build/libkira.so')]:
 lib=ctypes.CDLL(str(r/library));lib.web_input.restype=ctypes.c_void_p;lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
 combined=[];segments=[]
 for style in range(6):
  raw=bytes(scores[0]);lib.web_init();ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));lib.web_voice(0,style);samples=[];start=time.perf_counter()
  for j in range(600):
   p=lib.web_render(256);samples.extend(p[i] for i in range(512))
  metrics[f'{label}-style{style}']={'render_seconds':time.perf_counter()-start,'frames':153600,'peak':max(map(abs,samples)),'rms':(sum(x*x for x in samples)/len(samples))**.5,'clipped_samples':sum(abs(x)>=.93999 for x in samples)}
  segments.append({'style':['Pop','House','IDM','Trip-hop','Ethereal','Soul'][style],'start_seconds':len(combined)/88200});combined+=samples+[0.0]*22050
 def save(name,samples):
  with wave.open(str(o/(name+'.wav')),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(struct.pack('<'+'h'*len(samples),*[round(max(-1,min(1,x))*32767) for x in samples]))
 save(label+'-styles',combined)
 if label=='after':
  for mode,raw in enumerate(scores):
   raw=bytes(raw);lib.web_init();ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));lib.web_voice(0,mode);samples=[]
   for j in range(600):p=lib.web_render(256);samples.extend(p[i] for i in range(512))
   save('mode-'+['lyrics','vocalise','scat','hum','vocables'][mode],samples)
(o/'audio-metrics.json').write_text(json.dumps({'metrics':metrics,'style_segments':segments,'original_lyric':'we rise again','limits':'Host render time is not physical CPU; no subjective acceptance inferred. Identical phrase/voice/style inputs in before and after.'},indent=2)+'\n')
