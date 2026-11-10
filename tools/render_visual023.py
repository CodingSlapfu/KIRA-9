"""Render actual C-engine/portrait animation; discard PCM, create no audio files."""
from pathlib import Path
import ctypes,json,subprocess,hashlib
from PIL import Image
r=Path(__file__).resolve().parents[1];out=r/'validation/development-023';out.mkdir(exist_ok=True)
lib=r/'build/libkira023.so';subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Icore','core/engine.c','core/codec.c','core/library.c','core/tables.c','core/face.c','studio/bridge.c','-o',str(lib)],cwd=r,check=True)
e=ctypes.CDLL(str(lib));e.web_input.restype=ctypes.c_void_p;e.web_face.restype=ctypes.POINTER(ctypes.c_uint16)
script="import {compile,encode} from './studio/model.mjs';console.log(JSON.stringify(['Lyrics','Vocalise','Scat','Hum','Vocables'].map(vocalMode=>Array.from(encode(compile({bpm:120,lyrics:'hello',vocalMode,density:3,syllables:vocalMode==='Scat'?'ba doo sha':undefined},{hello:['HH','AY']}))))));"
fixtures=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],cwd=r,text=True));frames=[];hum=0;pose_sets=[]
for mode,fixture in enumerate(fixtures):
 raw=bytes(fixture);e.web_init();ctypes.memmove(e.web_input(),raw,len(raw));assert e.web_load(len(raw));e.web_voice(mode%7,mode%8);e.web_parameters(0,6,35,50,0,110,mode%4);poses=set()
 for i in range(28):
  left=2205
  while left:n=min(left,1024);e.web_render(n);left-=n
  pose=e.web_pose();poses.add(pose)
  if mode==3 and e.web_playing():assert pose>>8==0;hum+=1
  pixels=e.web_face((len(frames)+1)*50,mode%4,1);rgb=bytearray()
  for j in range(240*240):
   p=pixels[j];rgb.extend((((p>>11)&31)*255//31,((p>>5)&63)*255//63,(p&31)*255//31))
  frames.append(Image.frombytes('RGB',(240,240),bytes(rgb)))
 pose_sets.append(len(poses))
assert hum>0 and max(pose_sets)>1
frames[0].save(out/'engine-face-023.gif',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=False)
contact=Image.new('RGB',(240*5,240))
for mode in range(5):contact.paste(frames[mode*28+6],(mode*240,0))
contact.save(out/'engine-face-023-contact.png')
report={'frames':len(frames),'size':[240,240],'fps':20,'closed_hum_frames':hum,'distinct_poses_per_mode':pose_sets,'real_C_audio_and_face_engine':True,'PCM_discarded':True,'audio_files_created':False,'gif_sha256':hashlib.sha256((out/'engine-face-023.gif').read_bytes()).hexdigest(),'limitation':'Technical sequence, not owner visual acceptance; browser compact pose carries mouth/open and emotion, native envelope-driven brow emphasis is not separately encoded.'}
(out/'visual-sequence.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
