#!/usr/bin/env python3
"""Original LPC analysis/quantization of license-verified source subset."""
import pathlib,json,wave,math
import numpy as np
from scipy.signal import lfilter
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/residual-pilot';src=json.loads((out/'sources.json').read_text());units=[];records=[]
def audio(name):
 with wave.open(str(out/'source/wav'/name)) as w:
  assert w.getframerate()==16000 and w.getnchannels()==1 and w.getsampwidth()==2
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
def coeff(x):
 x=x*np.hanning(len(x));r=np.correlate(x,x,'full')[len(x)-1:len(x)+12];r[0]*=1.001
 a=np.zeros(12);ks=[];error=max(r[0],1e-10)
 for m in range(12):
  k=np.clip(-(r[m+1]+np.dot(a[:m],r[m:0:-1]))/error,-.98,.98);old=a.copy();a[:m]=old[:m]+k*old[:m][::-1];a[m]=k;ks.append(k);error*=1-k*k
 q=np.rint(np.array(ks)*32768).astype(np.int16);a=stepup(q/32768)
 return q,a
def stepup(k):
 a=np.zeros(12)
 for m,r in enumerate(k):a[:m]=a[:m]+r*a[:m][::-1];a[m]=r
 return a
def analyze(x,context):
 qs=[];res=np.zeros(len(x));recon=np.zeros(len(x));history=np.zeros(12)
 for start in range(0,len(x),160):
  mid=start+80;frame=np.pad(x,(256,256))[mid:mid+512];q,a=coeff(frame);qs.append(q)
  for i in range(start,min(start+160,len(x))):
   past=np.array([x[i-j-1] if i>j else 0 for j in range(12)]);res[i]=x[i]+np.dot(a,past)
 scale=max(float(max(abs(res)))/127,1e-8);quant=np.rint(res/scale).astype(np.int8)
 # Reconstruct with quantized reflection/residual through the SAME original
 # analysis definition; no subjective score or recognition target used.
 for i,e in enumerate(quant.astype(float)*scale):
  a=stepup(qs[i//160]/32768);y=e-np.dot(a,history);history[1:]=history[:-1];history[0]=y;recon[i]=y
 error=float(np.sqrt(np.mean((recon-x)**2)));snr=float(10*np.log10(max(np.sum(x*x),1e-20)/max(np.sum((recon-x)**2),1e-20)))
 return quant,np.array(qs),scale,{'rms_error':error,'snr_db':snr,'original_peak':float(max(abs(x))),'reconstructed_peak':float(max(abs(recon)))}
for c in src['chosen']:
 raw=audio(c['utterance']+'.wav');a,b=c['pair'];x,y=c['first'],c['second']
 if a in ['iy','ih','eh','ae']:
  start=max(x['start'],x['end']-.035);end=y['end']
 else:start=x['start'];end=min(y['end'],y['start']+.035)
 # Prespecified bounded unit length; very long consonants retain final125ms.
 if end-start>.16:start=end-.16
 clip=raw[round(start*16000):round(end*16000)];q,k,scale,metrics=analyze(clip,None);units.append((q,k,scale,0));records.append(dict(pair=c['pair'],utterance=c['utterance'],start=start,end=end,**metrics))
for vowel in ['iy','ih','eh','ae']:
 c=next(c for c in src['chosen'] if c['pair']==['hh',vowel]);raw=audio(c['utterance']+'.wav');v=c['second'];mid=round((v['start']+v['end'])*8000);x=raw[mid-320:mid+320];q,a=coeff(x)
 # Select period using native voiced source autocorrelation in80..400Hz.
 z=x-x.mean();scores=[np.dot(z[:-lag],z[lag:])/max(np.sqrt(np.dot(z[:-lag],z[:-lag])*np.dot(z[lag:],z[lag:])),1e-15) for lag in range(40,201)];period=40+int(np.argmax(scores));res=lfilter(np.r_[1,a],[1],raw)
 center=mid+int(np.argmax(abs(res[mid-period//2:mid+period//2])))-period//2;grain=res[center-period:center+period]*np.hanning(2*period)
 scale=max(float(max(abs(grain)))/127,1e-8);quant=np.rint(grain/scale).astype(np.int8);units.append((quant,q[None,:],scale,period));records.append({'sustain':vowel,'utterance':c['utterance'],'center_sample':center,'source_period':period,'source_f0':16000/period})
notice=(out/'source/COPYING').read_text();text='/* MODIFIED DATA: CMU ARCTIC SLT0.95, original12th-order LPC analysis, extraction and quantization for KIRA-9 research; not a complete or accepted voice. Original notices in COPYING-SLT. */\n'
bytes_used=len(notice.encode())+16*28+128*4
for i,(q,k,scale,period) in enumerate(units):
 text+=f'static const int8_t rp_res{i}[]={{'+','.join(map(str,q))+'};\n';text+=f'static const int16_t rp_k{i}[]={{'+','.join(map(str,k.ravel()))+'};\n';bytes_used+=q.nbytes+k.nbytes
text+='static const rp_unit rp_units[16]={\n'+''.join(f'{{rp_res{i},rp_k{i},{len(q)},{len(k)},{scale:.10g}f,{period}.0f}},\n' for i,(q,k,scale,period) in enumerate(units))+'};\n'
text+='static const float rp_period[128]={'+','.join(f'{16000/(440*2**((n-69)/12)):.9g}f' for n in range(128))+'};\n';text+=f'#define RP_DATA_BYTES {bytes_used}u\n';(out/'units.h').write_text(text);(out/'COPYING-SLT').write_text(notice)
(out/'extraction.json').write_text(json.dumps({'units':records,'data_bytes_including_notice_index_pitch_table':bytes_used,'unit_count':len(units),'modifications':'Original LPC12 analysis,8bit residual quantization,16bit reflection quantization; sustained two-period Hann-windowed grains. Original code; not Festival coefficients/runtime.','limits':'Automatic boundaries unverified; duration truncation may remove cues; no human quality evidence.'},indent=2)+'\n');assert bytes_used<=65536;print('Extracted16 units, bytes',bytes_used)
