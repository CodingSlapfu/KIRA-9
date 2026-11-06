#!/usr/bin/env python3
"""Package NEW candidate-only free-text trials; never rerender baseline or grade invented listeners."""
import pathlib,json,wave,random,hashlib,base64,io,fcntl
import numpy as np
r=pathlib.Path(__file__).resolve().parents[1]
lock=open(r/'build/verify.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
b=r/'build/residual-pilot';out=b/'listening';out.mkdir(exist_ok=True)
e=json.loads((b/'evaluation.json').read_text());items=[]
for f in e['files']:
 if f['note']==84:continue
 raw=(b/f['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256']
 with wave.open(io.BytesIO(raw)) as w:x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 for s in f['segments']:items.append((f,s,x[s['start_sample']:s['end_sample']].copy()))
random.Random(906244).shuffle(items);cases=[];answers={}
for i,(f,s,x) in enumerate(items):
 gain=min(.08/max(float(np.sqrt(np.mean(x*x))),1e-9),.7/max(float(max(abs(x))),1e-9));x*=gain
 # Edge ramps only. Internal joins are unchanged and can be rated honestly.
 n=min(100,len(x)//4);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
 buf=io.BytesIO()
 with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.rint(x*32767).astype('<i2').tobytes())
 raw=buf.getvalue();ident=f'r{i:02d}';cases.append({'id':ident,'audio':'data:audio/wav;base64,'+base64.b64encode(raw).decode()});answers[ident]={'word':s['word'],'note':f['note'],'group':f['group'],'engine':'residual','gain_listening_only':gain,'sha256':hashlib.sha256(raw).hexdigest()}
key={'protocol':'kira-residual-free-v1','answers':answers};(out/'answers.json').write_text(json.dumps(key,indent=2)+'\n')
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>KIRA-9 new voice listening</title><style>body{font:18px system-ui;max-width:720px;margin:32px auto;padding:20px;background:#111725;color:#f2f4ff}button,input,select{font:inherit;padding:10px;margin:8px 0;width:100%;box-sizing:border-box}audio{width:100%}small{color:#bfc8df}</style><h1>KIRA-9: new recorded-voice test</h1><p>24 new clips, about 5–8 minutes. Use headphones at a comfortable volume. Type what you hear, or “unclear”. No answer choices or target words are shown. These are isolated research sounds, not an accepted singing engine.</p><label>Your listener code (use the same code if you tested previously)<input id="who" placeholder="Choose a nickname"></label><p id="status"></p><audio id="audio" controls></audio><label>Word heard<input id="heard" autocomplete="off" spellcheck="false"></label><label>Naturalness<select id="natural"><option value="">Choose</option><option value="1">1 — entirely artificial</option><option value="2">2 — mostly artificial</option><option value="3">3 — mixed</option><option value="4">4 — mostly human</option><option value="5">5 — naturally human</option></select></label><label>Clicks or abrupt joins<select id="clicks"><option value="">Choose</option><option value="no">No</option><option value="yes">Yes</option><option value="unsure">Unsure</option></select></label><button id="next">Save answer and next</button><button id="export">Download answers</button><p><small>Answers stay in this browser. Download the JSON and return it to the conversation. No network requests. This test does not repeat the earlier 48 trials; prior baseline results are historical context, not a controlled paired comparison.</small></p><script>
const cases=CASES,storage='kira-residual-free-v1';const $=x=>document.getElementById(x);let responses=[],position=0;
try{const saved=JSON.parse(localStorage.getItem(storage)||'null');if(saved){responses=saved.responses||[];position=responses.length;$('who').value=saved.listener||''}}catch(e){}
function save(){try{localStorage.setItem(storage,JSON.stringify({listener:$('who').value,responses}))}catch(e){}}
function show(){const done=position>=cases.length;$('status').textContent=done?'Complete — download your answers.':`Clip ${position+1} of ${cases.length}`;$('audio').src=done?'':cases[position].audio;$('next').disabled=done;for(const x of ['heard','natural','clicks'])$(x).value=''}
$('next').onclick=()=>{if(!$('who').value.trim()||!$('heard').value.trim()||!$('natural').value||!$('clicks').value){alert('Enter a listener code, word (or unclear), and both ratings.');return}responses.push({id:cases[position].id,response:$('heard').value.trim(),naturalness:Number($('natural').value),clicks:$('clicks').value});position++;save();show()};
$('export').onclick=()=>{save();const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify({protocol:storage,listener:$('who').value.trim(),responses},null,2)],{type:'application/json'}));a.href=u;a.download='KIRA9-new-voice-responses.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};show();</script></html>'''.replace('CASES',json.dumps(cases))
(out/'KIRA9-new-voice-listening.html').write_text(html)
print('Prepared',len(cases),'new candidate trials; human results NOT PERFORMED;',len(html),'HTML bytes')
