#!/usr/bin/env python3
"""Extract additional neighboring grains from existing licensed recordings only."""
import pathlib,json,re,wave,hashlib,fcntl,shutil
import numpy as np
from scipy.signal import lfilter
r=pathlib.Path(__file__).resolve().parents[1];e=r/'experiments/multigrain_sustain';b=r/'build/residual-pilot';v=r/'validation/multigrain-sustain-2026-11-06';lock=open(r/'build/verify.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
s=json.loads((b/'sources.json').read_text());ex=json.loads((b/'extraction.json').read_text());h=(r/'experiments/residual_pilot/data/units.h').read_text();records=[];text='/* MODIFIED CMU ARCTIC SLT0.95 recorded residuals; extra neighboring grains only. Original authors/notices retained in experiments/residual_pilot/data/COPYING-SLT. */\n';tables=[];extra=0
for j,vowel in enumerate(['iy','ih','eh','ae']):
 u=ex['units'][12+j];period=u['source_period'];center=u['center_sample'];p=b/'source/wav'/(u['utterance']+'.wav');rawbytes=p.read_bytes()
 with wave.open(str(p)) as w:assert w.getframerate()==16000;raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 k=np.fromstring(re.search(r'rp_k'+str(12+j)+r'\[\]=\{([^}]+)',h)[1],sep=',')/32768;a=np.zeros(12)
 for m,x in enumerate(k):a[:m]=a[:m]+x*a[:m][::-1];a[m]=x
 residual=lfilter(np.r_[1,a],[1],raw);phone=s['chosen'][j]['second'];lo=round(phone['start']*16000);hi=round(phone['end']*16000);sign=1 if residual[center]>=0 else -1;refs=[];scales=[];centers=[]
 for g,offset in enumerate([-2,-1,0,1,2]):
  if offset==0:
   refs.append('rp_res'+str(12+j));scale=float(re.search(r'\{rp_res'+str(12+j)+r',rp_k'+str(12+j)+r',\d+,\d+,([^f]+)f',h)[1]);centers.append(center);scales.append(scale);continue
  predicted=center+offset*period;left=max(lo+period,predicted-period//4);right=min(hi-period,predicted+period//4+1);assert left<right
  mark=left+int(np.argmax(residual[left:right]*sign));assert lo<=mark-period and mark+period<=hi;grain=residual[mark-period:mark+period]*np.hanning(2*period);scale=max(max(abs(grain))/127,1e-8);q=np.rint(grain/scale).astype(np.int8);name=f'mg_{j}_{g}';text+='static const int8_t '+name+'[]={'+','.join(map(str,q))+'};\n';refs.append(name);scales.append(float(scale));centers.append(mark);extra+=q.nbytes
 assert centers==sorted(centers) and len(set(centers))==5
 tables.append((refs,scales));records.append(dict(vowel=vowel,utterance=u['utterance'],source_wav_sha256=hashlib.sha256(rawbytes).hexdigest(),centers_sample=centers,source_phone_samples=[lo,hi],period_samples=period,grains=5,frozen_center_reused=True))
text+='static const int8_t *const mg_res[4][5]={'+','.join('{'+','.join(t[0])+'}' for t in tables)+'};\n';text+='static const float mg_scale[4][5]={'+','.join('{'+','.join(f'{x:.10g}f' for x in t[1])+'}' for t in tables)+'};\n';extra+=4*5*8+9*4;text+=f'#define MG_EXTRA_BYTES {extra}u\n';(e/'grains.h').write_text(text)
# Isolated source copy: original pilot itself is never edited.
c=(r/'experiments/residual_pilot/residual.c').read_text();c=c.replace('#include "units.h"','#include "units.h"\n#include "grains.h"')
a=c.index('   for(unsigned i=0;i<u->samples;i++){');z=c.index('   s->phase+=s->period;',a)
c=c[:a]+'''   static const unsigned path[9]={2,3,4,3,2,1,0,1,2};
   unsigned slot=(s->grain_tick/8u)%8u;
   unsigned g0=path[slot],g1=path[slot+1u];
   float blend=(float)(s->grain_tick%8u)*.125f;
   unsigned vowel=s->unit-12u;
   const int8_t *q0=mg_res[vowel][g0],*q1=mg_res[vowel][g1];
   float scale0=mg_scale[vowel][g0],scale1=mg_scale[vowel][g1];
   for(unsigned i=0;i<u->samples;i++){
    float a0=(float)q0[i],b0=i+1<u->samples?(float)q0[i+1]:0;
    float a1=(float)q1[i],b1=i+1<u->samples?(float)q1[i+1]:0;
    float x0=(a0+(b0-a0)*fraction)*scale0;
    float x1=(a1+(b1-a1)*fraction)*scale1;
    s->ring[(s->head+i)&511u]+=x0+(x1-x0)*blend;
   }
   s->grain_tick=(s->grain_tick+1u)%64u;
'''+c[z:];c=c.replace('s->holding=hold;','s->holding=hold && unit>=12;');c=c.replace('return RP_DATA_BYTES;','return RP_DATA_BYTES+MG_EXTRA_BYTES;');(e/'residual.c').write_text(c);hdr=(r/'experiments/residual_pilot/residual.h').read_text().replace('unsigned unit,pos,frame,head,holding,running;','unsigned unit,pos,frame,head,holding,running,grain_tick;');(e/'residual.h').write_text(hdr)
(v/'extraction.json').write_text(json.dumps({'change':'Five neighboring recorded residual grains, original center unchanged','records':records,'extra_data_budget':extra,'consonant_header_sha256':hashlib.sha256(h.encode()).hexdigest(),'total_data_budget':29175+extra,'source_notice':'CMU ARCTIC SLT0.95; modified data, original COPYING retained'},indent=2)+'\n');print('Prepared multigrain data, extra bytes',extra,'total',29175+extra)
