#!/usr/bin/env python3
import json,pathlib,argparse
p=argparse.ArgumentParser();p.add_argument('responses');p.add_argument('--key',default='build/english6/listening/answers.json');a=p.parse_args();key=json.loads(pathlib.Path(a.key).read_text())['answers'];responses=json.loads(pathlib.Path(a.responses).read_text())['responses'];seen=set();result={}
for r in responses:
 if r['id'] in seen:raise SystemExit('Duplicate response')
 seen.add(r['id']);k=key[r['id']];name=k['engine']+'-'+str(k['note'])+'-'+k['group'];s=result.setdefault(name,{'correct':0,'total':0});s['total']+=1;s['correct']+=r['response']==k['word']
print(json.dumps(result,indent=2))
