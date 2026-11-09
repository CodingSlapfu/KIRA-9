"""Package already verified 0.2.1-dev artifacts. Does not build/install/publish."""
from pathlib import Path
import sys,json,hashlib,zipfile,shutil,subprocess,re,argparse,tempfile
r=Path(__file__).resolve().parents[1];v='0.2.1-dev';identity='FM-1_74000201';out=r/'build'/f'KIRA-9-{v}-testing';out.mkdir(exist_ok=True)
sys.path.insert(0,str(r/'platform/tools'));import make_site as S,fm1_install as I
sha=lambda b:hashlib.sha256(b).hexdigest()
fw=out/'firmware';fw.mkdir(exist_ok=True)
for name in [f'kira-9-{v}.fwsc','kira-9.bin','kira-9.elf','kira-9.dis','firmware.json']:shutil.copy2(r/'app/build'/name,fw/name)
shutil.copy2(r/'app/build/loader/ota.bin',fw/'ota.bin');assert I.product_of((fw/f'kira-9-{v}.fwsc').read_bytes())==identity
# Exact prior attached candidate and pre-existing legacy rollback; never regenerate them.
parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,default=r/'build/KIRA-9-0.2.0-dev-testing.zip');args=parser.parse_args();baseline=args.baseline
if baseline.is_file():
 baseline_temp=tempfile.TemporaryDirectory(prefix='kira021-baseline-');
 with zipfile.ZipFile(baseline) as z:z.extractall(baseline_temp.name)
 baseline=Path(baseline_temp.name)
rollback=baseline/'firmware/kira-9-0.2.0-dev.fwsc';assert I.product_of(rollback.read_bytes())=='FM-1_74000200'
shutil.copy2(rollback,fw/'rollback-0.2.0-dev.fwsc');shutil.copy2(baseline/'firmware/rollback-FM-1_7400.fwsc',fw/'rollback-FM-1_7400.fwsc')
site=out/'testing';site.mkdir(exist_ok=True);(site/'firmware').mkdir(exist_ok=True)
for p in fw.glob('*.fwsc'):shutil.copy2(p,site/'firmware'/p.name)
boot=r/'platform/web/m-bootloader'/f'fm1-uboot-{S.MBOOT_VERSION}.fwsc';bootname=f'm-bootloader-{S.MBOOT_VERSION}.fwsc';shutil.copy2(boot,site/'firmware'/bootname);shutil.copy2(boot.parent/'LICENSE',site/'firmware/m-bootloader-LICENSE.txt')
for p in (r/'platform/LICENSES').glob('*.txt'):shutil.copy2(p,site/'firmware'/p.name)
lib='\n'.join(S.strip_module((r/'platform/web'/p).read_text()) for p in ['fm1ports.js','fm1pkg.js','fm1ota.js'])
template=(r/'platform/web/installer.html').read_text()
for key,value in [('RES',"KIRA-9's data"),('RES_JA','KIRA-9 data'),('NAME','KIRA-9'),('REPO','https://github.com/CodingSlapfu/KIRA-9'),('REPO_SHORT','github.com/CodingSlapfu/KIRA-9'),('LICENSE','MIT; platform MPL-2.0'),('CREDITS','')]:template=template.replace('{{'+key+'}}',value)
for folder,version,product,pkg in [('install',v,identity,f'kira-9-{v}.fwsc'),('rollback','0.2.0-dev rollback','FM-1_74000200','rollback-0.2.0-dev.fwsc'),('legacy-rollback','legacy rollback','FM-1_7400','rollback-FM-1_7400.fwsc')]:
 meta={'version':version,'product':product,'pkg':'../firmware/'+pkg,'sha256':sha((site/'firmware'/pkg).read_bytes()),'backup':True,'res':None,'boot':{'pkg':'../firmware/'+bootname,'version':S.MBOOT_VERSION,'sha256':sha(boot.read_bytes())}}
 page=template.replace('const pkg = new Uint8Array(await r.arrayBuffer());', 'const pkg = new Uint8Array(await r.arrayBuffer());\n    if (await sha256hex(pkg) !== meta.sha256) throw new Error("Testing firmware SHA-256 mismatch");').replace('/*LIB*/',lib).replace('/*META*/',json.dumps(meta)).replace('/*APP*/','null');page=page.replace('<main>','<main><p><strong>TESTING ONLY — KIRA-9 '+version+'. Back up the device first. Human and hardware acceptance remain open.</strong></p>',1)
 (site/folder).mkdir(exist_ok=True);(site/folder/'index.html').write_text(page)
for name,data in S.tool_pages(r/'app').items():p=site/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
for a,b in [(r/'app/build/emu',site/'emu'),(r/'app/web/words',site/'words'),(r/'studio',site/'studio')]:shutil.copytree(a,b,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.c','emulator'))
assert len(json.loads((site/'studio/dictionary.json').read_text()))==126051
shutil.copy2(r/'platform/tools/fm1_install.py',site/'fm1_install.py')
proof=out/'validation';shutil.copytree(r/'validation/development-021',proof,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.flash','midi_out.txt'))
for kind in ['native','host','wasm','emulator']:shutil.copy2(r/'build'/f'{kind}-build-021.txt',proof/f'{kind}-build.txt')
# Archive complete current source, including pinned nested repositories and generated offline assets.
source_files={}
for repo,prefix in [(r,''),(r/'platform','platform/'),(r/'platform/bsp','platform/bsp/')]:
 paths=subprocess.check_output(['git','ls-files','--stage'],cwd=repo,text=True).splitlines()
 for line in paths:
  info,name=line.split('\t',1)
  if info.startswith('160000') or name.startswith('build/') or name.startswith('app/build/'):continue
  p=repo/name
  if p.is_file():source_files[prefix+name]=p.read_bytes()
for name in ['studio/dictionary.json','studio/kira.wasm']:source_files[name]=(r/name).read_bytes()
source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
source_meta={'source_commit':source_commit,'preserved_checkpoint':'1d1e37b','platform_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r/'platform',text=True).strip(),'bsp_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r/'platform/bsp',text=True).strip(),'files':{n:sha(data) for n,data in source_files.items()},'remote_backup':'Not independently verified for this turn; last prior verified54f9d9a.'}
with zipfile.ZipFile(out/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,data in sorted(source_files.items()):z.writestr(n,data)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(source_meta,indent=2)+'\n')
with zipfile.ZipFile(out/'source.zip') as z:
 for n,h in source_meta['files'].items():assert sha(z.read(n))==h
(out/'README.txt').write_text('''KIRA-9 0.2.1-dev — TESTING ONLY
Identity FM-1_74000201 / native build 7D1F43B7

Extract this ZIP completely. In this folder run:
  python -m http.server 8000 --bind 127.0.0.1
Windows may use: py -3 -m http.server 8000 --bind 127.0.0.1
Use Chrome or Edge. Keep the server running while using these pages.

1. BEFORE FLASHING: http://localhost:8000/testing/backup/
   Export the complete device backup and retain it outside this folder.
2. Testing installer: http://localhost:8000/testing/install/
   Choose the actual FM-1 USB MIDI ports. Do not interrupt a flash write.
3. Studio: http://localhost:8000/testing/studio/
   Emulator: http://localhost:8000/testing/emu/
4. Exact previous 0.2.0-dev rollback: http://localhost:8000/testing/rollback/
   Earlier FM-1_7400 rollback: http://localhost:8000/testing/legacy-rollback/
   OLD FIRMWARE RESETS THE ENLARGED SETTINGS OBJECT. Restore the corresponding
   pre-update device backup after rollback. Song/phrase/word storage maps are unchanged.
5. Firmware/, source.zip, validation/, MANIFEST.json and SHA256SUMS are included.

VOICE page: ALGO selects Lyrics / Vocalise / Scat / Hum / Vocables;
K3 selects the displayed vowel/family (Lyrics: twitch). SAVE stores the live
selection. The EXPRESSION page retains breath/vibrato/glide/morph controls.
Use SONG page LIVE mode for keys. Physical control acceptance remains open.

Studio: select Full song or one named section. Voice/delivery, emotion,
expression, breath/vibrato/glide/morph/harmony, mode, syllable pattern, melody
MIDI notes, note length, density, swing and variation apply to that scope.
Apply technique defaults is explicit and preserves lyrics. Transfer full
arrangement stores separate section presets in device song banks. Select one
section for a single device-score export. Back up banks before replacing them.
The pronunciation dictionary is included for offline use. USB is used by
browser installation/transfer; BLE musical performance remains supported.

Outstanding work: natural singing quality and English intelligibility,
owner vowel judgments, full portrait/control/editor workflow acceptance,
physical BLE pairing/reconnection/jitter, real CPU/audio timing and actual
interrupted-flash/rollback/restore. All 23 release requirements remain partial.
Production source-filter singer retained; frozen five-grain experiment NOT
promoted. See validation/STATUS.md and validation/release-gate.txt.
No official release, public installer deployment, or AQUORA changes.
Current source/artifacts have not been independently backed up to GitHub in
this turn. The complete downloadable source is in source.zip.
''')
manifest={'version':v,'identity':identity,'native_build_id':'7D1F43B7','testing_only':True,'official_release':False,'source_commit':source_commit,'source_manifest':'source.zip/SOURCE_MANIFEST.json','source_members_verified':len(source_files),'rollback':{'identity':'FM-1_74000200','sha256':sha(rollback.read_bytes()),'source':'Exact firmware from user attached verified0.2.0-dev ZIP'},'software_evidence':'validation/STATUS.md','physical_acceptance':'OWNER_UNVERIFIED','official_gate':'BLOCKED: all23 requirements remain partial; see validation/release-gate.txt','files':{}}
manifest['files']={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file() and p.name not in {'MANIFEST.json','SHA256SUMS'}}
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');hashes={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'};(out/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()))
path=out.parent/(out.name+'.zip')
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(out)))
with zipfile.ZipFile(path) as z:
 assert z.testzip() is None
 for n,h in hashes.items():assert sha(z.read(n))==h,n
report={'package':str(path),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'members_verified':len(hashes),'source_members_verified':len(source_files),'identity':identity,'build':'7D1F43B7','source_commit':source_commit,'rollback_sha256':sha(rollback.read_bytes())}
(r/'build/testing-package-021.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
