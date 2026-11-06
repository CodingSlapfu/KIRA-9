#!/usr/bin/env python3
"""New controlled stage ablations from frozen SLT data; no product changes."""
import pathlib,json,re,wave,hashlib,io,base64,fcntl
import numpy as np
from scipy.signal import lfilter,resample_poly
r=pathlib.Path(__file__).resolve().parents[1];b=r/'build/residual-pilot';v=r/'validation/residual-artifact-stages-2026-11-06';out=b/'artifact-stages'
lock=open(r/'build/verify.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
v.mkdir(exist_ok=True);out.mkdir(exist_ok=True)
source=json.loads((b/'sources.json').read_text());ex=json.loads((b/'extraction.json').read_text());ev=json.loads((b/'evaluation.json').read_text());header=(r/'experiments/residual_pilot/data/units.h').read_text()
units=[]
for i in range(16):
 q=np.fromstring(re.search(r'rp_res'+str(i)+r'\[\]=\{([^}]+)',header)[1],sep=',');k=np.fromstring(re.search(r'rp_k'+str(i)+r'\[\]=\{([^}]+)',header)[1],sep=',').reshape(-1,12)/32768
 meta=re.search(r'\{rp_res'+str(i)+r',rp_k'+str(i)+r',\d+,\d+,([^f]+)f,([^f]+)f\}',header)
 units.append((q,k,float(meta[1]),float(meta[2])))
def stepup(k):
 a=np.zeros(12)
 for m,x in enumerate(k):a[:m]=a[:m]+x*a[:m][::-1];a[m]=x
 return a
def audio(name):
 p=b/'source/wav'/name
 with wave.open(str(p)) as w:assert w.getframerate()==16000;return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768

def decode(e,ks):
 y=np.zeros(len(e));h=np.zeros(12)
 for i,x in enumerate(e):
  a=stepup(ks[min(i//160,len(ks)-1)]);s=x-np.dot(a,h);h[1:]=h[:-1];h[0]=s;y[i]=s
 return y

def sustain(grain,k,period,n):
 # Same fractional placement as frozen runtime, double precision diagnostic.
 ring=np.zeros(512);head=0;phase=0.;exc=[]
 for t in range(n):
  if phase<=0:
   frac=-phase
   for i,x in enumerate(grain):ring[(head+i)&511]+=(x+((grain[i+1] if i+1<len(grain) else 0)-x)*frac)
   phase+=period
  phase-=1;exc.append(ring[head]);ring[head]=0;head=(head+1)&511
 return lfilter([1],np.r_[1,stepup(k)],np.array(exc))
def snr(a,z):return float(10*np.log10(max(np.sum(a*a),1e-30)/max(np.sum((a-z)**2),1e-30)))
def envelope_error(a,z):
 # Coarse third-octave-like band power difference after unit-energy matching.
 def spec(x):
  x=x/np.sqrt(max(np.sum(x*x),1e-30));p=abs(np.fft.rfft(x*np.hanning(len(x)),4096))**2;f=np.fft.rfftfreq(4096,1/16000)
  return np.array([10*np.log10(max(np.sum(p[(f>=lo)&(f<hi)]),1e-12)) for lo,hi in [(100,300),(300,600),(600,1000),(1000,1600),(1600,2400),(2400,3500),(3500,6000)]])
 return float(np.sqrt(np.mean((spec(a)-spec(z))**2)))
rows=[];clips=[];metrics=[]
def clip(label,x,sr=16000):
 x=np.asarray(x);assert np.isfinite(x).all();rawpeak=float(max(abs(x)));rms=float(np.sqrt(np.mean(x*x)));gain=min(.08/max(rms,1e-12),.7/max(rawpeak,1e-12));y=x*gain
 # Only listening copies get common outer ramps/level adjustment; no masking.
 n=min(round(sr*.002),len(y)//4);y[:n]*=np.linspace(0,1,n);y[-n:]*=np.linspace(1,0,n)
 buf=io.BytesIO()
 with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.rint(y*32767).astype('<i2').tobytes())
 raw=buf.getvalue();name=f'stage{len(clips):02d}.wav';(out/name).write_bytes(raw);c=dict(label=label,file=name,rate=sr,duration_s=len(x)/sr,raw_peak=rawpeak,listening_gain=gain,listening_rms=float(np.sqrt(np.mean(y*y))),sha256=hashlib.sha256(raw).hexdigest());clips.append(c);return c
for j,vowel in enumerate(['iy','ih','eh','ae']):
 c=source['chosen'][j];raw=audio(c['utterance']+'.wav');m=ex['units'][j];x=raw[round(m['start']*16000):round(m['end']*16000)];q,ks,scale,_=units[j];assert len(q)==len(x)
 # Recompute unquantized residual against EXACT frozen quantized envelopes.
 residual=np.zeros(len(x))
 for i,s in enumerate(x):
  a=stepup(ks[min(i//160,len(ks)-1)]);residual[i]=s+sum(a[t]*x[i-t-1] for t in range(12) if i>t)
 d8=decode(q*scale,ks);df=decode(residual,ks);scale16=max(max(abs(residual))/32767,1e-12);d16=decode(np.rint(residual/scale16)*scale16,ks)
 grainq,gk,gs,period=units[j+12];sc=ex['units'][j+12];a=stepup(gk[0]);res=lfilter(np.r_[1,a],[1],raw);center=sc['center_sample'];gf=res[center-int(period):center+int(period)]*np.hanning(int(period)*2);g8=grainq*gs
 native=sustain(g8,gk[0],period,6400);unquant=sustain(gf,gk[0],period,6400);shift=sustain(g8,gk[0],16000/(440*2**((60-69)/12)),6400)
 # Additional ablation bypasses LPC, using the SAME center/period/window.
 rawgrain=raw[center-int(period):center+int(period)]*np.hanning(int(period)*2)
 direct_native=sustain(rawgrain,np.zeros(12),period,6400);direct_shift=sustain(rawgrain,np.zeros(12),16000/(440*2**((60-69)/12)),6400)
 # 40ms source control around the very same grain center, no looping/stretch.
 original=raw[center-320:center+320];native40=native[-640:];shift40=shift[-640:]
 poles=np.roots(np.r_[1,a]);formants=sorted(float(np.angle(z)*16000/(2*np.pi)) for z in poles if np.imag(z)>0 and 100<np.angle(z)*16000/(2*np.pi)<4000)
 metrics.append(dict(vowel=vowel,transition_float_snr_db=snr(x,df),transition_q8_snr_db=snr(x,d8),transition_q16_snr_db=snr(x,d16),sustain_q8_vs_float_snr_db=snr(unquant,native),source_f0_hz=16000/period,fixed_envelope_pole_hz=formants,native_grain_vs_source_band_error_db=envelope_error(original,native40),shifted_grain_vs_source_band_error_db=envelope_error(original,shift40)))
 family=[clip('A Original human transition',x),clip('B Same transition, frozen 8-bit LPC decode',d8),clip('C Same transition, 16-bit residual control',d16),clip('D Source vowel, 40ms — short unlooped control',original),clip('E Recorded grain at source pitch, 400ms',native),clip('F Same grain at source pitch, unquantized residual',unquant),clip('G Same 8-bit grain shifted to MIDI60, 400ms',shift)]
 f=next(f for f in ev['files'] if f['note']==60 and f['group']=='vowels');p=b/f['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
 with wave.open(str(p)) as w:word=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 s=f['segments'][j];family.append(clip('H Frozen assembled word, MIDI60',word[s['start_sample']:s['end_sample']],44100));family.extend([clip('I Direct human waveform grain, source pitch — LPC bypass',direct_native),clip('J Same direct waveform grain, MIDI60 — LPC bypass',direct_shift)]);rows.append(dict(vowel=vowel,stages=family))
report={'purpose':'Owner-reported artificial/synthetic sound; not confirmed click events. New isolated stage ablations, no product or frozen candidate changes.','metrics':metrics,'clips':clips,'limitations':'Matched listening RMS.08 with peak ceiling.7, outer2ms fades only, no effects. Durations differ for sustain and original short source; no human ratings inferred. Float diagnostics are not native timing/headroom acceptance. Pole estimates and band errors are diagnostic, not vowel recognition.','source_license':'Modified CMU ARCTIC SLT0.95. COPYING-SLT retained; original source URLs/hashes in residual-pilot sources.json.','human_results':'NOT PERFORMED'}
(v/'measurement.json').write_text(json.dumps(report,indent=2)+'\n');(out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n')
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>KIRA-9 voice stages</title><style>body{font:17px system-ui;max-width:1000px;margin:30px auto;padding:20px;background:#111725;color:#eef2ff}section{background:#1d2940;padding:18px;margin:18px 0;border-radius:12px}label{display:block;margin-top:15px}audio{display:block;width:100%}textarea{font:inherit;width:95%;min-height:60px}button{font:inherit;padding:12px}small{color:#c6d2ef}</style><h1>Where does the artificial sound enter?</h1><p>Compare each row in order. A–C isolate compression of the same human transition. D is a very short original vowel. E–F isolate quantization in sustained-grain playback at source pitch. E–G isolate the pitch change. H is the frozen assembled word you tested. I–J bypass LPC using the same recorded waveform center, grain window and pitch schedule; they are experimental controls, not an accepted replacement.</p><p>Listening copies use the same RMS target and peak ceiling. Durations intentionally differ for source versus sustain. No reverb, chorus or artifact masking. These are diagnostic stages, not new accepted voices. Your earlier answers remain preserved; you do not need to repeat the 24-word test.</p>ROWS<button id="export">Download stage observations</button><p><small>Modified CMU ARCTIC SLT0.95 recordings; copyright Carnegie Mellon University2003, authors retained. Source use/copy/modification permitted subject to original notice, conditions and warranty disclaimer. Full notice follows.</small></p><pre style="white-space:pre-wrap">NOTICE</pre><script>document.getElementById('export').onclick=()=>{const responses=[...document.querySelectorAll('textarea')].map(x=>({vowel:x.id,observations:x.value}));const u=URL.createObjectURL(new Blob([JSON.stringify({protocol:'kira-artifact-stages-v1',responses},null,2)],{type:'application/json'})),a=document.createElement('a');a.href=u;a.download='KIRA9-stage-observations.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};</script></html>'''
from html import escape
sections=[]
for row in rows:
 sections.append('<section><h2>'+row['vowel']+'</h2>'+''.join('<label>'+escape(c['label'])+f" ({c['duration_s']:.3f}s)"+'<audio controls preload="none" src="data:audio/wav;base64,'+base64.b64encode((out/c['file']).read_bytes()).decode()+'"></audio></label>' for c in row['stages'])+'<label>Which stage first adds the artificial sound? What changes?<textarea id="'+row['vowel']+'"></textarea></label></section>')
html=html.replace('ROWS',''.join(sections)).replace('NOTICE',escape((r/'experiments/residual_pilot/data/COPYING-SLT').read_text()));(out/'KIRA9-voice-stage-comparison.html').write_text(html)
print(json.dumps(metrics,indent=2));print('New stage clips',len(clips),'HTML bytes',len(html.encode()))
