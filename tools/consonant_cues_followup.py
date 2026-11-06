#!/usr/bin/env python3
"""Reproduce only the new failure-control, PCM-cue and kernel-size diagnostics."""
import pathlib,subprocess,json,ctypes,wave
import numpy as np
out=pathlib.Path('build/consonant-cues');old=pathlib.Path('build/english6');orig=str(pathlib.Path('core/kira.h').resolve())
src=(old/'baseline-instrumented.c').read_text().replace('#include "kira.h"','#include "'+orig+'"');(out/'control.c').write_text(src)
b=(old/'bridge.c').read_text();b=b[:b.index('__attribute__((visibility("default"))) float *web_diagnostics')]
b+='\n__attribute__((visibility("default"))) void cue_note(unsigned p,unsigned n,unsigned vel,unsigned frames){k9_note(&web_engine,p,n,vel);web_engine.phone_frames=frames;}\n'
b=b.replace('#include "kira.h"','#include "'+orig+'"');(out/'control-bridge.c').write_text(b)
subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Icore',str(out/'control.c'),'core/codec.c','core/library.c','core/tables.c','core/face.c',str(out/'control-bridge.c'),'-o',str(out/'control.so')],check=True)
lib=ctypes.CDLL(str((out/'control.so').resolve()));lib.web_render.restype=ctypes.POINTER(ctypes.c_float);lib.baseline_peak.restype=ctypes.c_float
r=json.loads((out/'evaluation.json').read_text());rows=[]
names='SIL AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH IY JH K L M N NG OW OY P R S SH T TH UH UW V W Y Z ZH'.split()
for x in [x for x in r['safety_cases'] if x['raw_peak']>=.9]:
 lib.web_init();lib.web_voice(x['voice'],0);lib.baseline_reset()
 for phone in ['P','IY','B','IY','S','SH','IY','SH','S','B','P','IY']:
  n=8820 if phone=='IY' else x['consonant_frames'];lib.cue_note(names.index(phone),x['note'],127,n)
  for pos in range(0,n,256):lib.web_render(min(256,n-pos))
 rows.append(dict(**x,baseline_raw_peak=lib.baseline_peak(),baseline_clamp_hits=lib.baseline_clips()))
(out/'failure-control.json').write_text(json.dumps({'scope':'Only NEW failing cells, preserved baseline with include paths adapted; no existing acceptance rerun','cases':rows},indent=2)+'\n')
tc=pathlib.Path('build/deps/jieli-linux-toolchains-20260730.1');flags=['-target','pi32v2','-mcpu=r3','-mfprev1','-O2','-ffp-contract=off','-Ibuild/consonant-cues','-Iexperiments/consonant_cues','-Icore']
subprocess.run([str(tc/'pi32v2/bin/clang'),*flags,'-c','experiments/consonant_cues/cues.c','-o',str(out/'cues-r3.o')],check=True)
size=subprocess.check_output(['size',str(out/'cues-r3.o')],text=True);undefined=subprocess.check_output(['nm','-u',str(out/'cues-r3.o')],text=True)
(out/'native.json').write_text(json.dumps({'kernel_size':size,'undefined_symbols':undefined,'state_bytes':28,'heap':False,'device_cpu':'UNVERIFIED; kernel object only, not firmware build or timing evidence'},indent=2)+'\n')
corpus=json.loads((old/'corpus.json').read_text());rows=[];vowels=[]
for c in corpus:
 if c['group']=='vowels':
  a=old/(c['id']+'-baseline.wav');b=out/(c['id']+'-candidate.wav');vowels.append({'note':c['note'],'byte_identical':a.read_bytes()==b.read_bytes()});continue
 seg=c['segments'][2];start=round(seg['start']*44100/192)
 for engine,p in [('baseline',old/(c['id']+'-baseline.wav')),('candidate',out/(c['id']+'-candidate.wav'))]:
  with wave.open(str(p)) as w:x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).mean(axis=1)/32768
  x=x[start:start+8820];lag=44100/(440*2**((c['note']-69)/12));curve=[]
  for ms in range(20,151,5):
   y=x[round((ms-15)*44.1):round((ms+15)*44.1)];y=y-y.mean();corr=[]
   for k in range(round(lag*.85),round(lag*1.15)+1):
    a=y[:-k];b=y[k:];corr.append(float(np.dot(a,b)/max(np.sqrt(np.dot(a,a)*np.dot(b,b)),1e-12)))
   curve.append({'center_ms':ms,'periodicity':max(corr),'rms':float(np.sqrt(np.mean(y*y)))})
  stable=next((curve[i]['center_ms'] for i in range(len(curve)-2) if all(x['periodicity']>.5 and x['rms']>.001 for x in curve[i:i+3])),None)
  rows.append({'note':c['note'],'engine':engine,'first_3_windows_periodicity_above_0_5_ms':stable,'curve':curve})
(out/'pcm-cues.json').write_text(json.dumps({'method':'30ms zero-mean normalized lag correlation; max at .85..1.15 nominal period; 5ms hop; first 3 windows >.5 and RMS>.001. Overlapping windows are diagnostic, not a phonetic VOT gold standard. Clock relative to scheduled P start; programmed release24ms.','p_rows':rows,'vowel_controls':vowels},indent=2)+'\n')
print('Saved new failure-control, PCM-cue and R3 kernel diagnostics; no ASR or acceptance replay.')
