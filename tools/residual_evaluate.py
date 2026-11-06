#!/usr/bin/env python3
"""New residual-pilot gates only. No old experiment or acceptance replay."""
import pathlib,ctypes,json,time,wave,subprocess,hashlib
import numpy as np
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/residual-pilot';lib=ctypes.CDLL(str(out/'residual.so'))
lib.rp_size.restype=ctypes.c_uint;state=ctypes.create_string_buffer(lib.rp_size());buf=(ctypes.c_float*256)()
for name in ['rp_init','rp_stop']:getattr(lib,name).argtypes=[ctypes.c_void_p]
lib.rp_start.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint];lib.rp_render.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_uint]
def render(n):
 values=[]
 for pos in range(0,n,256):
  count=min(256,n-pos);lib.rp_render(state,buf,count);values.append(np.ctypeslib.as_array(buf)[:count].copy())
 return np.concatenate(values)
def unit(index,note,n,hold=False):lib.rp_start(state,index,note,int(hold));return render(n)
def pitch(x):
 x=x[-8820:].astype(float);x-=x.mean();spec=abs(np.fft.rfft(x,32768))**2;acf=np.fft.irfft(spec);acf/=max(acf[0],1e-30);lo=29;hi=551
 peaks=[j for j in range(lo,hi) if acf[j]>acf[j-1] and acf[j]>=acf[j+1]];best=max((acf[j] for j in peaks),default=0);lag=next((j for j in peaks if acf[j]>=best*.99),None)
 if lag is None:return None,best
 shift=.5*(acf[lag-1]-acf[lag+1])/(acf[lag-1]-2*acf[lag]+acf[lag+1]);return 44100/(lag+shift),float(acf[lag])
rows=[];peak=0;bad=0;total=0;stopfail=0
for note in [48,60,72,84]:
 for index in range(16):
  x=unit(index,note,44100 if index>=12 else 8820,index>=12);total+=len(x);bad+=int(np.sum(~np.isfinite(x)));p=float(max(abs(x)));peak=max(peak,p)
  row={'unit':index,'note':note,'raw_peak':p,'finite':bool(np.isfinite(x).all())}
  if index>=12:
   f,c=pitch(x);target=440*2**((note-69)/12);cents=1200*np.log2(f/target) if f else None;row.update(f0_hz=f,target_hz=target,cents=float(cents) if cents is not None else None,periodicity=c,pitch_pass=bool(c>.6 and cents is not None and abs(cents)<=35))
  rows.append(row);lib.rp_stop(state);stopfail+=bool(max(abs(render(1024)))>1e-8)
# New unit change sequence in both orders; native API intentionally resets
# between units. Join-step metrics expose rather than conceal discontinuity.
joins=[]
for note in [48,60,72,84]:
 for indices in [list(range(16)),list(reversed(range(16)))]:
  pieces=[unit(i,note,4410,i>=12) for i in indices];x=np.concatenate(pieces);total+=len(x);bad+=int(np.sum(~np.isfinite(x)));peak=max(peak,float(max(abs(x))));joins.append({'note':note,'max_adjacent_step':float(max(abs(np.diff(x))))})
# Twelve matched candidate clips: one per group/register48/60/72 plus84
# diagnostic. Existing baseline recordings are reused; no baseline resynthesis.
corpus=json.loads((root/'build/english6/corpus.json').read_text());ex=json.loads((out/'extraction.json').read_text());files=[]
for note in [48,60,72,84]:
 for group in ['vowels','consonants']:
  audio=[];segments=[];position=0
  for j in range(4):
   onset=j if group=='vowels' else 8+j;vowel=j if group=='vowels' else 0;begin=position
   n=round((ex['units'][onset]['end']-ex['units'][onset]['start'])*44100);a=unit(onset,note,n);b=unit(12+vowel,note,13781,True);word=np.r_[a,b]
   if group=='vowels':
    c=ex['units'][4+j];word=np.r_[word,unit(4+j,note,round((c['end']-c['start'])*44100))]
   audio.extend([word,np.zeros(5513,dtype=np.float32)]);position+=len(word);segments.append({'word':(['heed','hid','head','had'] if group=='vowels' else ['see','she','pea','bee'])[j],'start_sample':begin,'end_sample':position});position+=5513
  pcm=np.concatenate(audio);p=out/f'{group}-{note}-residual.wav'
  # Refuse to hide clipping in saved research audio.
  if np.max(abs(pcm))<1:
   with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.rint(pcm*32767).astype('<i2').tobytes())
   files.append({'file':p.name,'note':note,'group':group,'peak':float(max(abs(pcm))),'segments':segments,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
base=ctypes.CDLL(str(root/'build/english6/baseline.so'));base.web_init();base.web_demo(0);lib.rp_start(state,12,60,1);times={'baseline':[],'residual':[]}
for i in range(1200):
 for name in (['baseline','residual'] if i%2 else ['residual','baseline']):
  t=time.thread_time_ns()
  if name=='baseline':base.web_render(256)
  else:lib.rp_render(state,buf,256)
  if i>=200:times[name].append((time.thread_time_ns()-t)/1000)
timings={n:{'median_us':float(np.median(v)),'p95_us':float(np.percentile(v,95))} for n,v in times.items()};ratio=timings['residual']['median_us']/timings['baseline']['median_us']
report={'scope':'Single recorded SLT identity, fixed velocity127/gain.35. No seven-timbre/style/expressive compatibility accepted. New units only. No clamp/limiter anywhere. Hard-reset unit joins can click; measured below.','frames':total,'raw_peak':peak,'nonfinite':bad,'stop_failures':int(stopfail),'headroom_pass':peak<.9 and not (bad or stopfail),'pitch_pass':all(r.get('pitch_pass',True) for r in rows),'data_bytes':lib.rp_data_size(),'state_bytes_host':lib.rp_size(),'callback_host':timings,'host_ratio':ratio,'host_budget_pass':ratio<=1.25,'device_cpu':'UNVERIFIED','cases':rows,'joins':joins,'files':files,'human_results_new':'NOT PERFORMED','recognition':'GATED until headroom, pitch, reconstruction, native size and runtime budget assessed'}
(out/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['cases','files','joins']},indent=2));print('Pitch cents:',[(r['unit'],r['note'],round(r['cents'],2),r['pitch_pass']) for r in rows if 'cents' in r])
