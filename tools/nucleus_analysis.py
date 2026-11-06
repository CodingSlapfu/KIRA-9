#!/usr/bin/env python3
"""Measure changed nuclei and unchanged consonant/vowel boundaries, not word quality."""
import pathlib,json,wave,numpy as np,argparse
p=argparse.ArgumentParser();p.add_argument("--variant",choices=["late","smooth"],default="late");variant=p.parse_args().variant
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/nucleus-study';corpus=json.loads((out/'corpus.json').read_text());names='SIL AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH IY JH K L M N NG OW OY P R S SH T TH UH UW V W Y Z ZH'.split()
def load(path):
 with wave.open(str(path)) as w:return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).mean(axis=1)/32768
rows=[]
for item in corpus:
 a=load(out/f"{item['id']}-baseline.wav");b=load(out/f"{item['id']}-{variant}.wav");rate=44100*60/120/96
 for j,e in enumerate(item['score']['events']):
  name=names[e['phone']];start=round(e['tick']*rate);n=round(e['duration']*rate)
  if name in ['AY','EY','OW','AW','OY']:
   for phase,l,r in [('nucleus',.2,.4),('glide',.75,.95)]:
    values={}
    for variant,data in [('baseline',a),(variant,b)]:
     seg=data[start+round(n*l):start+round(n*r)];q=abs(np.fft.rfft(seg*np.hanning(len(seg))))**2;f=np.fft.rfftfreq(len(seg),1/44100);values[variant]={'centroid_hz':float((q*f).sum()/max(q.sum(),1e-20)),'rms':float(np.sqrt(np.mean(seg*seg)))}
    rows.append({'id':item['id'],'phone':name,'event':j,'phase':phase,**values})
  if item['group']=='transitions' and name=='IY' and j:
   before=a[max(0,start-353):start];after=a[start:start+353];boundary=a[max(0,start-132):start+132];rows.append({'id':item['id'],'transition':names[item['score']['events'][j-1]['phone']]+'→IY','before_8ms_rms':float(np.sqrt(np.mean(before*before))),'after_8ms_rms':float(np.sqrt(np.mean(after*after))),'boundary_step':float(max(abs(np.diff(boundary)))),'exact_edge_step':float(max(abs(np.diff(a[max(0,start-4):start+5])))),'candidate_boundary_step':float(max(abs(np.diff(b[max(0,start-132):start+132])))),'candidate_exact_edge_step':float(max(abs(np.diff(b[max(0,start-4):start+5]))))})
recognition=json.loads((out/'recognition.json').read_text())['results'];summary=[]
if variant=='smooth':recognition+=json.loads((out/'recognition-smooth.json').read_text())['results']
for note in [48,60,72]:
 for entry in ['baseline',variant]:
  group=[r for r in recognition if r['note']==note and r['variant']==entry];summary.append({'note':note,'variant':entry,'mean_wer':float(np.mean([r['wer'] for r in group])),'empty_clips':sum(not r['text'].strip() for r in group),'clip_count':len(group)})
(out/('analysis.json' if variant=='late' else 'analysis-smooth.json')).write_text(json.dumps({'note':'No listening pass; centroid/transition measures cannot certify intelligibility. WER includes insertions and may exceed 1.','recognition_summary':summary,'measurements':rows},indent=2)+'\n')
print(json.dumps(summary,indent=2));print('Transition maximum adjacent step',max(r['boundary_step'] for r in rows if 'boundary_step' in r))
