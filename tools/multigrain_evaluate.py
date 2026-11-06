#!/usr/bin/env python3
"""New multigrain-only technical gates and controlled frozen-pilot comparisons."""
import pathlib,fcntl,json,ctypes,subprocess,hashlib,time,wave,ast
import numpy as np
r=pathlib.Path(__file__).resolve().parents[1];out=r/'build/multigrain-sustain';out.mkdir(exist_ok=True);v=r/'validation/multigrain-sustain-2026-11-06';lock=open(r/'build/verify.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
# New diagnostic wrapper permits exact source pitch; native object omits it.
(out/'wrapper.c').write_text('#include "../../experiments/multigrain_sustain/residual.c"\nvoid mg_native(rp_state *s,unsigned v){rp_start(s,12+v,60,1);s->period=rp_units[12+v].period;}\n')
subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Iexperiments/residual_pilot/data',str(out/'wrapper.c'),'-o',str(out/'multi.so')],cwd=r,check=True)
tc=r/'build/deps/jieli-linux-toolchains-20260730.1';flags=['-target','pi32v2','-mcpu=r3','-mfprev1','-O2','-ffp-contract=off','-Iexperiments/residual_pilot/data']
subprocess.run([str(tc/'pi32v2/bin/clang'),*flags,'-c','experiments/multigrain_sustain/residual.c','-o',str(out/'multi-r3.o')],cwd=r,check=True)
(out/'sizes.c').write_text('#include "../../experiments/multigrain_sustain/residual.h"\nchar multigrain_state[sizeof(rp_state)];\n');subprocess.run([str(tc/'pi32v2/bin/clang'),*flags,'-c',str(out/'sizes.c'),'-o',str(out/'sizes-r3.o')],cwd=r,check=True)
native={'size_sections':subprocess.check_output(['size','-A',str(out/'multi-r3.o')],text=True),'size_total':subprocess.check_output(['size',str(out/'multi-r3.o')],text=True),'undefined':subprocess.check_output(['nm','-u',str(out/'multi-r3.o')],text=True),'state':subprocess.check_output(['nm','-S',str(out/'sizes-r3.o')],text=True),'device_cpu':'UNVERIFIED; new isolated object, not full firmware','whole_firmware_map':'NOT INTEGRATED/UNVERIFIED'};(v/'native.json').write_text(json.dumps(native,indent=2)+'\n')
new=ctypes.CDLL(str(out/'multi.so'));old=ctypes.CDLL(str(r/'build/residual-pilot/residual.so'))
for lib in [new,old]:
 lib.rp_size.restype=ctypes.c_uint;lib.rp_start.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint];lib.rp_render.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_uint];lib.rp_stop.argtypes=[ctypes.c_void_p]
new.mg_native.argtypes=[ctypes.c_void_p,ctypes.c_uint];states={lib:ctypes.create_string_buffer(lib.rp_size()) for lib in [new,old]};buf=(ctypes.c_float*256)()
def render(lib,n):
 pieces=[]
 for t in range(0,n,256):
  count=min(256,n-t);lib.rp_render(states[lib],buf,count);pieces.append(np.ctypeslib.as_array(buf)[:count].copy())
 return np.concatenate(pieces)
def unit(lib,i,note,n,hold=0):lib.rp_start(states[lib],i,note,hold);return render(lib,n)
# Reuse pitch estimator definition, not the old experiment's top-level gates.
a=ast.parse((r/'tools/residual_evaluate.py').read_text());fn=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='pitch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'preserved-pitch-definition','exec'))
rows=[];peak=0.;bad=0;stopfails=0;transitions=[]
for note in [48,60,72,84]:
 for j in range(4):
  x=unit(new,12+j,note,44100*2,1);p=float(max(abs(x)));peak=max(peak,p);bad+=int(np.sum(~np.isfinite(x)));freq,c=pitch(x);target=440*2**((note-69)/12);cents=float(1200*np.log2(freq/target)) if freq else None;rows.append({'vowel':['iy','ih','eh','ae'][j],'note':note,'raw_peak':p,'f0_hz':freq,'cents':cents,'periodicity':c,'pitch_pass':bool(cents is not None and abs(cents)<=35 and c>=.6)});new.rp_stop(states[new]);stopfails+=int(max(abs(render(new,1024)))>1e-8)
 # New regression: prove new code leaves all12 source transitions byte exact.
 for j in range(12):
  a=unit(old,j,note,8820);b=unit(new,j,note,8820);transitions.append({'unit':j,'note':note,'byte_identical':a.tobytes()==b.tobytes()})
# Only new candidate source-pitch PCM; old source-pitch E WAVs are reused.
source=[];ex=json.loads((r/'validation/residual-pilot-2026-11-06/extraction.json').read_text())
for j,vowel in enumerate(['iy','ih','eh','ae']):
 new.mg_native(states[new],j);x=render(new,44100);new.rp_stop(states[new]);n=ex['units'][12+j]['source_period'];y=__import__('scipy.signal',fromlist=['resample_poly']).resample_poly(x,160,441)[1600:-100];delta=float(np.sqrt(np.mean((y[n:]-y[:-n])**2))/np.sqrt(np.mean(y*y)));source.append({'vowel':vowel,'native_period':n,'cycle_delta_ratio':delta})
 path=out/(vowel+'-multigrain-source.wav')
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);assert max(abs(x))<1;w.writeframes(np.rint(x*32767).astype('<i2').tobytes())
 source[-1]['file']=path.name;source[-1]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
# New kernel median against frozen pilot with identical unit/note/block workload.
times={'frozen':[],'multi':[]};old.rp_start(states[old],12,60,1);new.rp_start(states[new],12,60,1)
for i in range(1400):
 for name,lib in ([('frozen',old),('multi',new)] if i%2 else [('multi',new),('frozen',old)]):
  start=time.thread_time_ns();lib.rp_render(states[lib],buf,256);elapsed=(time.thread_time_ns()-start)/1000
  if i>=200:times[name].append(elapsed)
timing={k:{'median_us':float(np.median(x)),'p95_us':float(np.percentile(x,95))} for k,x in times.items()};ratio=timing['multi']['median_us']/timing['frozen']['median_us']
# Unit switching forward/reverse: new behavior only, no limiter.
for indices in [list(range(16)),list(reversed(range(16)))]:
 for note in [48,60,72,84]:
  for j in indices:
   x=unit(new,j,note,4410,j>=12);peak=max(peak,float(max(abs(x))));bad+=int(np.sum(~np.isfinite(x)))
report={'scope':'New isolated correction only. Frozen source/units/product unchanged. All velocity-equivalent tests use unchanged fixed gain.35, no limiter/clamp/effects.','headroom_peak':peak,'nonfinite':bad,'stop_failures':stopfails,'headroom_pass':peak<.9 and bad==0 and stopfails==0,'pitch_pass':all(x['pitch_pass'] for x in rows),'state_bytes':new.rp_size(),'data_budget_bytes':new.rp_data_size(),'host_timing':timing,'host_ratio_vs_frozen_pilot':ratio,'host_budget_pass':ratio<=1.25,'all48_transition_outputs_byte_identical':all(x['byte_identical'] for x in transitions),'rows':rows,'source_pitch_variation':source,'human_acceptance':'NOT PERFORMED; variation does not establish human naturalness or word intelligibility.','device_cpu':'UNVERIFIED','promotion':False}
(v/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n');(out/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:x for k,x in report.items() if k not in ['rows','source_pitch_variation']},indent=2));print('pitch rows',[(x['vowel'],x['note'],round(x['cents'],2),x['pitch_pass']) for x in rows]);print('variation',source)
