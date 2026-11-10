"""Package existing verified outputs; never rebuild or flash."""
from pathlib import Path
import json,zipfile,hashlib,shutil,re,io
r=Path(__file__).resolve().parents[1];site=r.parent/'kira-site/.sites-checkout/dist';o=r/'build/KIRA-9-0.2.3-dev-testing';o.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
# Verify inherited package hashes and exact 022 rollback before copying.
with zipfile.ZipFile(site/'downloads/KIRA-9-0.2.2-dev-testing.zip') as z:
 for line in z.read('SHA256SUMS').decode().splitlines():
  h,n=line.split('  ',1);assert sha(z.read(n))==h,n
 assert z.read('firmware/kira-9-0.2.2-dev.fwsc')==(site/'firmware/kira-9-0.2.2-dev.fwsc').read_bytes()
 # Keep the offline dictionary, rather than regenerating an already tested one.
 (r/'studio/dictionary.json').write_bytes(z.read('testing/studio/dictionary.json'))
fw=o/'firmware';fw.mkdir(exist_ok=True)
for p in (site/'firmware').glob('*'):shutil.copy2(p,fw/p.name)
for n in ['kira-9.bin','kira-9.elf','kira-9.dis','firmware.json']:shutil.copy2(r/'app/build'/n,fw/n)
shutil.copy2(r/'app/build/loader/ota.bin',fw/'ota.bin')
t=o/'testing';t.mkdir(exist_ok=True)
for name in ['assets','backup','emu','firmware','install','install-022','rollback','rollback-020','rollback-021','legacy-rollback','manual','previews','studio','words']:
 shutil.copytree(site/name,t/name,dirs_exist_ok=True)
shutil.copy2(site/'index.html',t/'index.html')
# Inherited source backup plus current complete platform/BSP and artwork masters.
files={}
for p in sorted(r.rglob('*')):
 if not p.is_file():continue
 parts=p.relative_to(r).parts;n=p.relative_to(r).as_posix()
 if any(x in parts for x in ['.git','build','__pycache__']) or n.startswith('studio/emulator/') or p.suffix in ['.wav','.flac','.ogg','.mp3','.pyc']:continue
 files[n]=p.read_bytes()
with zipfile.ZipFile(o/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,b in files.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps({'source_branch':'kira-0.2.3-development','source_checkpoint':'feecf11e35d924c13a2b6c465b1496b590e1ef68','platform':'698e2cba46b33bf14d9bf756675036053535638e','bsp':'f878800967e66e721dfbc9a4f5fe1835772ae8fc','files':{n:sha(b) for n,b in files.items()}},indent=2))
shutil.copytree(r/'validation/development-023',o/'validation',dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.wav'))
for kind in ['native','wasm','emulator']:shutil.copy2(r/f'build/{kind}-build-023.txt',o/f'validation/{kind}-build.txt')
(o/'README.txt').write_text('''KIRA-9 v0.2.3-dev — DEVELOPMENT TESTING ONLY
Identity FM-1_74000203; build DA116E4F. Exact hashes: MANIFEST.json / SHA256SUMS.

Extract ALL files, then serve this folder:
 Windows: py -3 -m http.server 8000 --bind 127.0.0.1 --directory testing
 macOS/Linux: python3 -m http.server 8000 --bind 127.0.0.1 --directory testing
Use Chrome/Edge. Export backup FIRST: http://localhost:8000/backup/
Installer: http://localhost:8000/install/
Studio/audio: http://localhost:8000/studio/
Emulator: http://localhost:8000/emu/
Before/after: http://localhost:8000/previews/
Exact 0.2.2 rollback: http://localhost:8000/rollback/
Older rollback: rollback-021/, rollback-020/, legacy-rollback/ beneath the server root.
The --directory testing option serves the complete included website at /,
so home navigation, studio, installer and rollback links work locally.

New original cel character is shared by native, WASM and emulator. Original
expressive contours preserve the working formant engine and frozen experiment.
Five modes, saved assets and wireless MIDI infrastructure remain intact.
No production release. Physical appearance, vocal quality, BLE pairing/jitter,
FM-1 CPU/audio and flash/recovery/rollback require owner evaluation.
Read validation/OWNER_TESTS.md. Do not interrupt a flash write. Save matching
pre-update backups; older 0.2.0/legacy firmware resets newer preferences.
Source.zip includes full source/platform/BSP/artwork and per-file hashes.
AQUORA was not modified.
''')
manifest={'version':'0.2.3-dev','identity':'FM-1_74000203','native_build_id':'DA116E4F','development_testing':True,'official_release':False,'owner_acceptance':'OPEN','source_checkpoint':'feecf11e35d924c13a2b6c465b1496b590e1ef68','firmware_sha256':sha((fw/'kira-9-0.2.3-dev.fwsc').read_bytes()),'rollback_022_sha256':sha((fw/'kira-9-0.2.2-dev.fwsc').read_bytes()),'source_files':len(files)}
(o/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
hashes={p.relative_to(o).as_posix():sha(p.read_bytes()) for p in sorted(o.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'}
(o/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()))
archive=o.parent/(o.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(o.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(o).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for n,h in hashes.items():assert sha(z.read(n))==h,n
report={**manifest,'package':str(archive),'package_sha256':sha(archive.read_bytes()),'bytes':archive.stat().st_size,'verified_members':len(hashes)}
(r/'validation/development-023/package-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
