#!/usr/bin/env python3
"""Candidate-only targeted acoustic evidence; frozen baseline PCM reused."""
import pathlib,ctypes,json,wave,time,hashlib
import numpy as np
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/consonant-cues';old=root/'build/english6'
lib=ctypes.CDLL(str(out/'candidate.so'));lib.web_input.restype=ctypes.c_void_p;lib.web_render.restype=ctypes.POINTER(ctypes.c_float);lib.cue_peak.restype=ctypes.c_float
names='SIL AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH IY JH K L M N NG OW OY P R S SH T TH UH UW V W Y Z ZH'.split()
def render(n):return np.ctypeslib.as_array(lib.web_render(n),shape=(2*n,)).copy().reshape(-1,2)
def readwav(p):
 with wave.open(str(p)) as w:return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).mean(axis=1)/32768
def centroid(x):
 s=abs(np.fft.rfft(x*np.hanning(len(x))))**2;f=np.fft.rfftfreq(len(x),1/44100);return float(np.sum(s*f)/max(np.sum(s),1e-20))
corpus=json.loads((old/'corpus.json').read_text());contrasts=[];files=[]
for item in corpus:
 raw=(old/(item['id']+'.k9s')).read_bytes();lib.web_init();lib.cue_reset();ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));lib.web_voice(0,0);data=[]
 for _ in range(1800):
  data.append(render(256))
  if not lib.web_playing():break
 data.extend(render(256) for _ in range(30));pcm=np.concatenate(data);assert np.isfinite(pcm).all();p=out/(item['id']+'-candidate.wav')
 with wave.open(str(p),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.rint(np.clip(pcm,-1,1)*32767).astype('<i2').tobytes())
 files.append({'file':p.name,'raw_peak':lib.cue_peak(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 if item['group']=='consonants':
  for engine,audio in [('baseline',readwav(old/(item['id']+'-baseline.wav'))),('candidate',pcm.mean(axis=1))]:
   cs=[]
   for seg in item['segments'][:2]:
    start=round(seg['start']*44100/192);cs.append(centroid(audio[start+441:start+2205]))
   contrasts.append({'note':item['note'],'engine':engine,'s_centroid_hz':cs[0],'sh_centroid_hz':cs[1],'difference_hz':cs[0]-cs[1]})
# Changed-phoneme transitions, full velocity, seven timbres, four registers,
# short and ordinary consonant events; no unrelated acceptance replay.
frames=bad=clips=stopfail=0;peak=0;cases=[]
for v in range(7):
 for n in [48,60,72,84]:
  for duration in [353,2117,5292]:
   lib.web_init();lib.web_voice(v,0);lib.cue_reset()
   for phone in ['P','IY','B','IY','S','SH','IY','SH','S','B','P','IY']:
    count=8820 if phone=='IY' else duration;lib.cue_note(names.index(phone),n,127,count)
    for pos in range(0,count,256):
     a=render(min(256,count-pos));bad+=int(np.sum(~np.isfinite(a)));frames+=len(a)
   lib.web_stop()
   for _ in range(100):a=render(256)
   stopfail+=bool(np.max(abs(a))>1e-5);clips+=lib.cue_clips();peak=max(peak,lib.cue_peak());cases.append({'voice':v,'note':n,'consonant_frames':duration,'raw_peak':lib.cue_peak()})
# Interleaved callback microbenchmark, same existing baseline shared object.
base=ctypes.CDLL(str(old/'baseline.so'));base.web_render.restype=ctypes.POINTER(ctypes.c_float)
times={x:[] for x in ['baseline','candidate']}
for x,l in [('baseline',base),('candidate',lib)]:l.web_init();l.web_demo(0)
for i in range(1200):
 for x,l in ([('baseline',base),('candidate',lib)] if i%2 else [('candidate',lib),('baseline',base)]):
  t=time.thread_time_ns();l.web_render(256);dt=(time.thread_time_ns()-t)/1000
  if i>=200:times[x].append(dt)
stats={x:{'median_us':float(np.median(t)),'p95_us':float(np.percentile(t,95))} for x,t in times.items()};ratio=stats['candidate']['median_us']/stats['baseline']['median_us']
result={'human_participants_new':0,'decision':'NOT PROMOTED; acoustic evidence only','safety':{'frames':frames,'raw_peak':peak,'nonfinite':bad,'clamp_hits':clips,'stop_failures':int(stopfail),'pass':peak<.9 and not (bad or clips or stopfail)},'fricative_contrasts':contrasts,'centroid_gate_pass':all(x['difference_hz']>=1500 for x in contrasts if x['engine']=='candidate'),'callback_host':stats,'host_ratio':ratio,'host_budget_pass':ratio<=1.25,'device_timing':'UNVERIFIED','state_bytes':lib.cue_state_size(),'files':files,'safety_cases':cases}
(out/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['safety_cases','files']},indent=2))
