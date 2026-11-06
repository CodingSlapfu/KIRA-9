#!/usr/bin/env python3
"""Grade frozen human exports without spelling inference or click-event claims."""
import pathlib,json,sys,re,collections,hashlib
r=pathlib.Path(__file__).resolve().parents[1]
keypath=r/'validation/residual-pilot-2026-11-06/listening-answers.json';key=json.loads(keypath.read_bytes());raw=pathlib.Path(sys.argv[1]).read_bytes();p=json.loads(raw)
if p.get('protocol')!=key['protocol'] or not p.get('listener','').strip():raise SystemExit('Wrong protocol or missing listener')
seen=set();groups=collections.defaultdict(lambda:dict(exact=0,homophone_inclusive=0,total=0,naturalness=[],artifact_complaints_yes=0,artifact_complaints_unsure=0));rows=[]
for x in p['responses']:
 i=x['id']
 if i in seen or i not in key['answers']:raise SystemExit('Duplicate or unknown trial '+i)
 seen.add(i);a=key['answers'][i]
 if not isinstance(x.get('response'),str) or not x['response'].strip():raise SystemExit('Missing response')
 if type(x.get('naturalness')) is not int or not 1<=x['naturalness']<=5 or x.get('clicks') not in ['yes','no','unsure']:raise SystemExit('Invalid rating')
 word=x['response'].strip().casefold();exact=word==a['word'];hom=exact or (word=='pee' and a['word']=='pea');ambiguous=word=='heead'
 rows.append({'id':i,'target':a['word'],'response_verbatim':x['response'],'note':a['note'],'group':a['group'],'exact':exact,'homophone_inclusive':hom,'ambiguous_unresolved':ambiguous,'exported_click_field':x['clicks'],'interpretation':'artifact complaint, not confirmed click event'})
 for g in ['overall',str(a['note']),a['group']]:
  row=groups[g];row['total']+=1;row['exact']+=exact;row['homophone_inclusive']+=hom;row['naturalness'].append(x['naturalness']);row['artifact_complaints_yes']+=x['clicks']=='yes';row['artifact_complaints_unsure']+=x['clicks']=='unsure'
print(json.dumps({'protocol':p['protocol'],'listener':p['listener'],'responses_sha256':hashlib.sha256(raw).hexdigest(),'frozen_key_sha256':hashlib.sha256(keypath.read_bytes()).hexdigest(),'completed':len(seen),'expected':len(key['answers']),'complete':len(seen)==len(key['answers']),'scoring':'Case/outer whitespace only for exact; pee→pea only additional homophone credit. Heead unresolved, not credited. No autocorrection.','click_clarification':'Owner heard human quality mixed with artificial/synthetic sound, not really distinct clicks/pops. Raw exported ratings preserved; interpreted as artifact complaints only.','groups':groups,'rows':rows,'acceptance':'One listener, diagnostic only; no promotion. Historical baseline is not a randomized paired control.'},indent=2))
