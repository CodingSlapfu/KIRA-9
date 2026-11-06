#!/usr/bin/env python3
"""Independent development backup, explicitly not a release certification."""
import pathlib,subprocess,zipfile,hashlib,json,datetime
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/checkpoint';out.mkdir(parents=True,exist_ok=True)
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
paths=[]
for line in subprocess.check_output(['git','ls-files','--recurse-submodules'],cwd=root,text=True).splitlines():
 p=root/line
 if p.is_file():paths.append((p,'source/'+line))
for folder in [root/'app/build',root/'build/panel',root/'build/vocal-comparison']:
 for p in folder.rglob('*'):
  if p.is_file() and p.suffix in {'.fwsc','.bin','.elf','.dis','.wasm','.png','.wav','.json','.js','.html','.css'}:paths.append((p,'artifacts/'+str(p.relative_to(root))))
for p in [root/'studio/kira.wasm',root/'studio/dictionary.json',root/'build/golden.f32']:
 if p.exists():paths.append((p,'artifacts/'+str(p.relative_to(root))))
for p in (root/'studio').rglob('*'):
 if p.is_file() and p.suffix not in {'.c'} and 'emulator' not in p.relative_to(root/'studio').parts:paths.append((p,'website/'+str(p.relative_to(root/'studio'))))
for p in (root/'app/build/emu').rglob('*'):
 if p.is_file():paths.append((p,'website/emulator/'+str(p.relative_to(root/'app/build/emu'))))
manifest={name:hashlib.sha256(p.read_bytes()).hexdigest() for p,name in paths}
archive=out/'KIRA-9-development-checkpoint.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p,name in sorted(paths,key=lambda item:item[1]):
  info=zipfile.ZipInfo(name,date_time=(2026,11,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(p.stat().st_mode&0xffff)<<16;z.writestr(info,p.read_bytes())
 info=zipfile.ZipInfo('CHECKPOINT.json',date_time=(2026,11,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(info,json.dumps({'source_commit':sha,'release_accepted':False,'identity':'FM-1_7400','files':manifest},indent=2))
digest=hashlib.sha256(archive.read_bytes()).hexdigest();(out/'SHA256SUMS').write_text(digest+'  '+archive.name+'\n')
print('Development backup',sha,digest,archive)
