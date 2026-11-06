#!/usr/bin/env python3
"""Package frozen stimuli without synthesis, normalization or answer-key exposure."""
import base64,hashlib,json,pathlib,re,argparse
p=argparse.ArgumentParser();p.add_argument('--frozen',default='build/english6/listening');p.add_argument('--output',default='build/english6/KIRA-9-listening.html');a=p.parse_args()
src=pathlib.Path(a.frozen);html=(src/'index.html').read_text();cases=json.loads(re.search(r'const cases=(.*?);let trials=',html).group(1));key=json.loads((src/'answers.json').read_text())['answers']
assert len(cases)==48 and len({c['id'] for c in cases})==48
for c in cases:
 data=(src/c['audio']).read_bytes()
 assert hashlib.sha256(data).hexdigest()==key[c['id']]['sha256']
 html=html.replace('"audio": "'+c['audio']+'"','"audio": "data:audio/wav;base64,'+base64.b64encode(data).decode()+'"')
html=html.replace('<option>60</option>','<option>All 48</option><option>60</option>')
html=html.replace('let trials=[],position=0,responses=[];',"let trials=[],position=0,responses=JSON.parse(localStorage.getItem('kira9-english6-responses')||'[]');")
html=html.replace("responses.push({id:c.id,response:label});position++;show()", "responses=responses.filter(r=>r.id!==c.id);responses.push({id:c.id,response:label});localStorage.setItem('kira9-english6-responses',JSON.stringify(responses));position++;show()")
html=html.replace("trials=cases.filter(c=>c.note===Number($('register').value));position=0;responses=[];show()", "trials=cases.filter(c=>($('register').value==='All 48'||c.note===Number($('register').value))&&!responses.some(r=>r.id===c.id));position=0;show()")
html=html.replace('16 trials per register.', '48 trials total, or 16 per register. Answers are saved in this browser; completed trials are skipped. Export includes every completed register.')
html=html.replace('Export before starting another register.', 'Export the JSON and return it to this conversation for grading. Keep a copy before clearing browser data.')
html=html.replace('Do not open answers.json before judging.', 'Choose what you hear; choose Unclear if you cannot identify it. Start quietly and use a comfortable headphone volume.')
html=html.replace('Block complete. Export responses.', 'Block complete. Export responses, or select another register and Start register.')
assert 'answers.json' not in html and '"engine"' not in html
out=pathlib.Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html)
print(json.dumps({'output':str(out),'trials':48,'all_audio_hashes_match_frozen_key':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
