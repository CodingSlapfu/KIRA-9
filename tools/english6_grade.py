#!/usr/bin/env python3
"""Grade genuine exported responses; partial blocks remain explicitly partial."""
import json,pathlib,argparse

def grade(doc,key):
 if doc.get('protocol')!='english6-blind-v1':raise ValueError('Unknown response protocol')
 responses=doc.get('responses')
 if not isinstance(responses,list) or not responses:raise ValueError('No responses supplied')
 seen=set();result={}
 for r in responses:
  ident=r.get('id');response=r.get('response')
  if ident in seen:raise ValueError('Duplicate response: '+str(ident))
  if ident not in key:raise ValueError('Unknown stimulus: '+str(ident))
  k=key[ident];choices=['heed','hid','head','had'] if k['group']=='vowels' else ['see','she','pea','bee']
  if response not in choices+['Unclear']:raise ValueError('Invalid response: '+str(response))
  seen.add(ident);name=k['engine']+'-'+str(k['note'])+'-'+k['group'];s=result.setdefault(name,{'correct':0,'total':0,'confusions':{}});s['total']+=1;s['correct']+=response==k['word'];row=s['confusions'].setdefault(k['word'],{});row[response]=row.get(response,0)+1
 for s in result.values():s['accuracy']=s['correct']/s['total']
 return {'status':'complete' if len(seen)==len(key) else 'partial','answered':len(seen),'expected':len(key),'missing_ids':sorted(set(key)-seen),'by_engine_register_group':result,'interpretation':'Single response file; descriptive forced-choice identification, not release acceptance or an independent participant count.'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('responses');p.add_argument('--key',default='build/english6/listening/answers.json');a=p.parse_args()
 try:print(json.dumps(grade(json.loads(pathlib.Path(a.responses).read_text()),json.loads(pathlib.Path(a.key).read_text())['answers']),indent=2))
 except (ValueError,KeyError,TypeError) as e:p.exit(2,str(e)+'\n')
