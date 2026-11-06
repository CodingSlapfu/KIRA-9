#!/usr/bin/env python3
"""Obtain a bounded original-source CMU SLT subset; no external DSP code."""
import pathlib,urllib.request,hashlib,json,re,concurrent.futures
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/residual-pilot';out.mkdir(exist_ok=True)
base='http://www.festvox.org/cmu_arctic/cmu_arctic/cmu_us_slt_arctic/'
def get(path):
 p=out/'source'/path;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  with urllib.request.urlopen(base+path,timeout=25) as r:raw=r.read()
  p.write_bytes(raw)
 return p.read_bytes()
license=get('COPYING');readme=get('README')
assert b'This voice is free for use for any purpose (commercial or otherwise)' in license
assert b'CMU ARCTIC SLT 0.95' in readme
# License checked before downloading any waveform. Preserve verbatim notices.
texts=get('etc/txt.done.data').decode();sentences=re.findall(r'\(\s*(arctic_\w+)\s+"([^"]+)"\s*\)',texts)
groups=[r'\bhe\b',r'\bhim\b|\bhis\b',r'\bhead\b|\bhelp\b',r'\bhad\b',r'\bneed\b|\blead\b',r'\bdid\b',r'\bsaid\b|\bdead\b',r'\bsee\b|\bseem\b|\bsea\b',r'\bshe\b',r'\bpeople\b|\bpeace\b|\bpiece\b',r'\bbe\b|\bbeing\b']
ids=[]
for pat in groups:
 ids.extend(i for i,t in [(i,t) for i,t in sentences if re.search(pat,t,re.I)][:6])
ids=sorted(set(ids));print('Candidate utterance labels',len(ids),flush=True)
def lab(ident):
 raw=get('lab/'+ident+'.lab').decode();items=[];last=0
 for line in raw.splitlines():
  bits=line.split()
  if len(bits)==3:
   end=float(bits[0]);items.append({'phone':bits[2],'start':last,'end':end});last=end
 return ident,items
with concurrent.futures.ThreadPoolExecutor(8) as pool:labels=dict(pool.map(lab,ids))
pairs=[('hh',v) for v in ['iy','ih','eh','ae']]+[(v,'d') for v in ['iy','ih','eh','ae']]+[(p,'iy') for p in ['s','sh','p','b']]
chosen=[]
for a,b in pairs:
 candidates=[]
 for ident,phones in labels.items():
  for j,(x,y) in enumerate(zip(phones,phones[1:])):
   if (x['phone'],y['phone'])==(a,b) and x['end']-x['start']>=.025 and y['end']-y['start']>=.05:
    candidates.append((ident,j,x,y))
 if not candidates:raise SystemExit('Missing source transition: '+a+'-'+b)
 ident,j,x,y=sorted(candidates,key=lambda x:(x[0],x[1]))[0]
 chosen.append({'pair':[a,b],'utterance':ident,'phone_index':j,'first':x,'second':y,'text':dict(sentences)[ident]})
for ident in sorted(set(x['utterance'] for x in chosen)):get('wav/'+ident+'.wav')
manifest={str(p.relative_to(out/'source')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/'source').rglob('*') if p.is_file()}
(out/'sources.json').write_text(json.dumps({'source_base':base,'version':'CMU ARCTIC SLT 0.95','license':'Exact bank COPYING verified before waveform download; all original copyright/conditions retained; derivative modifications must be marked.','alignment':'Original automatic phone labels, NOT manually verified; boundaries may be wrong.','selection':'First lexical filename/index satisfying prespecified pair and min phone durations; no synthesis-output tuning.','chosen':chosen,'source_sha256':manifest},indent=2)+'\n')
print('Selected',len(chosen),'transitions from',len(set(x['utterance'] for x in chosen)),'utterances',flush=True)
