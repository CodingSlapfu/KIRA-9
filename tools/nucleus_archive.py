#!/usr/bin/env python3
"""Package the new experiment only; previous firmware/acceptance archives untouched."""
import pathlib,subprocess,json,zipfile,hashlib
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/checkpoint';out.mkdir(parents=True,exist_ok=True);sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();paths={}
for name in subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines():
 p=root/name
 if p.is_file():paths['source/'+name]=p
for p in (root/'build/nucleus-study').glob('*'):
 if p.suffix in ['.json','.flac']:paths['evidence/'+p.name]=p
manifest={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in paths.items()}
with zipfile.ZipFile(out/'nucleus-evidence.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,p in sorted(paths.items()):z.write(p,name)
 z.writestr('EXPERIMENT.json',json.dumps({'source_commit':sha,'firmware_baseline':'3a407ec870481833f7b13fbdf98b3122f7fc4bc2','release_accepted':False,'firmware_changed':False,'files':manifest},indent=2))
a=out/'nucleus-evidence.zip';(out/'SHA256SUMS').write_text(hashlib.sha256(a.read_bytes()).hexdigest()+'  nucleus-evidence.zip\n');print('Packaged new experiment evidence',sha,len(manifest),'members')
