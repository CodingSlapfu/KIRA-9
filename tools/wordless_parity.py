import ctypes,json,pathlib,struct,subprocess
r=pathlib.Path(__file__).resolve().parents[1]
lib=ctypes.CDLL(str(r/'build/libkira.so'));lib.web_input.restype=ctypes.c_void_p;lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
script="import {compile,encode} from './studio/model.mjs'; console.log(JSON.stringify(['Lyrics','Vocalise','Scat','Hum','Vocables'].map(vocalMode=>Array.from(encode(compile({bpm:120,lyrics:'hello',vocalMode},{hello:['HH','EH','L','OW']}))))));"
fixtures=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],cwd=r,text=True));out=[]
for n,data in enumerate(fixtures):
 raw=bytes(data);lib.web_init();ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));pcm=[];poses=[]
 for i in range(400):
  p=lib.web_render(256);pcm.extend(p[j] for j in range(512));poses.append(lib.web_pose())
 assert max(abs(x) for x in pcm)<1
 out.append({'mode':n,'bytes':data,'pcm':pcm,'poses':poses})
(r/'build/wordless-parity.json').write_text(json.dumps(out));print('Native five-mode PCM and pose fixture ready (temporary)')
