"""Package existing 0.2.0-dev outputs; never builds or publishes."""
from pathlib import Path
import json,subprocess,zipfile,hashlib,shutil,sys
r=Path(__file__).resolve().parents[1];out=r/'build/KIRA-9-0.2.0-dev-testing';out.mkdir(exist_ok=True)
sys.path.insert(0,str(r/'platform/tools'));import make_site,fm1_install
source='54f9d9ad1d74dad67a59973507145b32d1b96044';tree='e76fd6c437ea43a772fa99f0f2c7a9c8dab582da'
assert subprocess.check_output(['git','rev-parse',source+'^{tree}'],cwd=r,text=True).strip()==tree
# Complete the existing generated installer without a public landing page.
site=r/'build/testing-site';site.mkdir(exist_ok=True)
for name,data in make_site.tool_pages(r/'app').items():
 p=site/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
for a,b in [(r/'app/build/emu',site/'emu'),(r/'app/web/words',site/'words'),(r/'studio',site/'studio')]:
 shutil.copytree(a,b,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.c','emulator'))
installer=site/'install/index.html';s=installer.read_text();s=s.replace('<main>','<main><p><strong>TESTING ONLY — KIRA-9 0.2.0-dev. Human vocal and hardware acceptance are open. Export your existing backup before installation.</strong></p>');installer.write_text(s)
fw=out/'firmware';fw.mkdir(exist_ok=True)
for name in ['kira-9-0.2.0-dev.fwsc','kira-9.bin','kira-9.elf','kira-9.dis','firmware.json']:
 shutil.copy2(r/'app/build'/name,fw/name)
shutil.copy2(r/'app/build/loader/ota.bin',fw/'ota.bin');shutil.copytree(site,out/'testing',dirs_exist_ok=True)
# Preserve one exact prior production-DSP development image for rollback.
with zipfile.ZipFile(r/'build/rollback-source.zip') as z:
 m=json.loads(z.read('CHECKPOINT.json'));name='artifacts/app/build/kira-9.fwsc';raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==m['files'][name]
 assert fm1_install.product_of(raw)=='FM-1_7400'
 (fw/'rollback-FM-1_7400.fwsc').write_bytes(raw)
rollback={'source_commit':m['source_commit'],'sha256':hashlib.sha256(raw).hexdigest(),'identity':'FM-1_7400','compatibility':'Existing app store map unchanged; physical restore remains unverified.'}
# Exact source including pinned platform and BSP; no historical experiment/audio archive copies.
archive=out/'source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for repo,prefix,ref in [(r,'',source),(r/'platform','platform/','HEAD'),(r/'platform/bsp','platform/bsp/','HEAD')]:
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',ref],cwd=repo,text=True).splitlines()
  for p in paths:
   info=subprocess.check_output(['git','ls-tree',ref,'--',p],cwd=repo,text=True)
   if info.startswith('160000'):continue
   data=subprocess.check_output(['git','show',ref+':'+p],cwd=repo);z.writestr(prefix+p,data)
proof=out/'validation';proof.mkdir(exist_ok=True)
for p in (r/'validation/development-020').glob('*'):shutil.copy2(p,proof/p.name)
for name in ['native-build.txt','host-build.txt','wasm-build.txt','emulator-build.txt','package-safety.txt']:
 shutil.copy2(r/'build'/name,proof/name)
manifest={'version':'0.2.0-dev','identity':'FM-1_74000200','testing_only':True,'official_release':False,'native_build_source_commit':subprocess.check_output(['git','rev-parse','9c625e2'],cwd=r,text=True).strip(),'verified_equivalent_remote_source_commit':source,'source_tree':tree,'build_id':'433FCA0B','platform':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r/'platform',text=True).strip(),'bsp':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r/'platform/bsp',text=True).strip(),'rollback':rollback,'software_evidence':'validation/','physical_acceptance':'UNVERIFIED','five_grain_promoted':False,'known_incomplete':['English intelligibility and natural recorded-human processing','Issue #3 full acceptance: mode defaults/section-specific expression and presets; live selector persistence; listening and device CPU','Physical BLE pairing/clock/transport; controls; restore and interrupted flash'],'files':{}}
for p in sorted(out.rglob('*')):
 if p.is_file():manifest['files'][str(p.relative_to(out))]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'README.txt').write_text('KIRA-9 0.2.0-dev — TESTING ONLY\n\n1. Back up the device first. Keep the backup outside this folder.\n2. From this folder run: python -m http.server 8000\n3. In Chrome/Edge open http://localhost:8000/testing/backup/ to export the device backup.\n4. Open http://localhost:8000/testing/install/ and select KIRA-9 USB MIDI. Installer verifies package integrity/identity before writing.\n5. Studio: http://localhost:8000/testing/studio/ ; emulator: /testing/emu/\n6. On device VOICE page: ALGO = Lyrics/Vocalise/Scat/Hum/Vocables for live keys/MIDI. K3 selects the vowel/family in wordless modes. Existing breath/vibrato/glide/expression controls remain on EXPRESSION.\n7. Studio: choose mode for full song or selected section, syllable pattern, note count and swing; transfer compiled sections as usual. Lyrics remain unchanged.\n8. Rollback: firmware/rollback-FM-1_7400.fwsc via testing/install/ file picker (if offered), or python testing/fm1_install.py firmware/rollback-FM-1_7400.fwsc . Requires pip install mido python-rtmidi. Use supported update/recovery instructions, never disconnect during writes.\n\nKnown limits: source-filter production singer retained, five-grain experiment NOT promoted. Naturalness/intelligibility unresolved; all 23 requirements are not complete. Live mode selection is temporary; compiled wordless songs persist normally. Hardware pairing, audio timing, screen quality and real rollback remain owner-unverified. No public deployment.\n')
shutil.copy2(r/'platform/tools/fm1_install.py',out/'testing/fm1_install.py')
rollback_page=out/'testing/rollback/index.html';rollback_page.parent.mkdir(exist_ok=True)
rollback_page.write_text(installer.read_text().replace('FM-1_74000200','FM-1_7400').replace('0.2.0-dev','rollback').replace('../firmware/kira-9-rollback.fwsc','../firmware/rollback-FM-1_7400.fwsc'))
shutil.copy2(fw/'rollback-FM-1_7400.fwsc',out/'testing/firmware/rollback-FM-1_7400.fwsc')
p=out/'README.txt';p.write_text(p.read_text().replace('firmware/rollback-FM-1_7400.fwsc via testing/install/ file picker (if offered), or','http://localhost:8000/testing/rollback/ or'))
manifest['files']={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name not in {'MANIFEST.json','SHA256SUMS'}}
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'};(out/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in files.items()))
zip_path=out.parent/(out.name+'.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(out)))
with zipfile.ZipFile(zip_path) as z:
 for n,h in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
print(json.dumps({'package':str(zip_path),'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'size':zip_path.stat().st_size,'members_verified':len(files),'rollback':rollback},indent=2))
