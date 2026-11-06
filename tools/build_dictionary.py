#!/usr/bin/env python3
"""Build the local pronunciation asset from a pinned, credited CMU dictionary."""
import json,pathlib,re,subprocess,shutil
root=pathlib.Path(__file__).resolve().parents[1];dep=root/'build/cmudict';pin='74790861f652b15e4ac49015a90074ad62a27690'
if not (dep/'.git').exists():subprocess.run(['git','clone','https://github.com/cmusphinx/cmudict.git',str(dep)],check=True)
subprocess.run(['git','-C',str(dep),'checkout','--detach',pin],check=True)
lex={}
for line in (dep/'cmudict.dict').read_text().splitlines():
 if not line or line.startswith(';;;'):continue
 word,*phones=line.split(' #')[0].split();word=re.sub(r'\(\d+\)$','',word)
 if word not in lex:lex[word]=[re.sub('[012]$','',p) for p in phones]
(root/'studio/dictionary.json').write_text(json.dumps(lex,separators=(',',':')))
shutil.copyfile(dep/'LICENSE',root/'studio/CMUDICT-LICENSE.txt')
print('Built dictionary from verified CMU revision',pin)
