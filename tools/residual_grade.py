#!/usr/bin/env python3
"""Grade actual exported candidate responses; reject mismatches and duplicates."""
import pathlib,json,sys,re,collections
r=pathlib.Path(__file__).resolve().parents[1]
key=json.loads((r/'validation/residual-pilot-2026-11-06/listening-answers.json').read_text());p=json.loads(pathlib.Path(sys.argv[1]).read_text())
if p.get('protocol')!=key['protocol'] or not p.get('listener','').strip():raise SystemExit('Wrong protocol or missing listener')
seen=set();groups=collections.defaultdict(lambda:dict(correct=0,total=0,naturalness=[],clicks=0))
for x in p['responses']:
 i=x['id']
 if i in seen or i not in key['answers']:raise SystemExit('Duplicate or unknown trial '+i)
 seen.add(i);a=key['answers'][i]
 if not isinstance(x.get('response'),str) or not x['response'].strip():raise SystemExit('Missing response')
 if type(x.get('naturalness')) is not int or not 1<=x['naturalness']<=5 or x.get('clicks') not in ['yes','no','unsure']:raise SystemExit('Invalid rating')
 word=re.sub(r'[^a-z ]','',x['response'].strip().lower())
 for g in ['overall',str(a['note']),a['group']]:
  row=groups[g];row['total']+=1;row['correct']+=word==a['word'];row['naturalness'].append(x['naturalness']);row['clicks']+=x['clicks']=='yes'
print(json.dumps({'listener':p['listener'],'completed':len(seen),'expected':len(key['answers']),'complete':len(seen)==len(key['answers']),'groups':groups,'acceptance':'Diagnostic only; not promotion. Historical baseline is not a randomized paired control.'},indent=2))
