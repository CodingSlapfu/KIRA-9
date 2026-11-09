"""Package verified v0.2.2 outputs, without building, flashing or publishing."""
from pathlib import Path
import argparse,json,hashlib,zipfile,shutil,sys,tempfile,re,subprocess
r=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,default=r.parent/'output/KIRA-9-0.2.1-dev-testing.zip');args=parser.parse_args();temp=tempfile.TemporaryDirectory(prefix='kira022-baseline-');baseline=Path(temp.name)
with zipfile.ZipFile(args.baseline) as z:
 for line in z.read('SHA256SUMS').decode().splitlines():
  h,n=line.split('  ',1);assert hashlib.sha256(z.read(n)).hexdigest()==h,n
 z.extractall(baseline)
sha=lambda b:hashlib.sha256(b).hexdigest();v='0.2.2-dev';identity='FM-1_74000202';out=r/'build'/f'KIRA-9-{v}-testing';out.mkdir(exist_ok=True);fw=out/'firmware';fw.mkdir(exist_ok=True)
sys.path.insert(0,str(r/'platform/tools'));import make_site as S,fm1_install as I
for n in [f'kira-9-{v}.fwsc','kira-9.bin','kira-9.elf','kira-9.dis','firmware.json']:shutil.copy2(r/'app/build'/n,fw/n)
shutil.copy2(r/'app/build/loader/ota.bin',fw/'ota.bin');assert I.product_of((fw/f'kira-9-{v}.fwsc').read_bytes())==identity
for src,dst,id in [('kira-9-0.2.1-dev.fwsc','rollback-0.2.1-dev.fwsc','FM-1_74000201'),('rollback-0.2.0-dev.fwsc','rollback-0.2.0-dev.fwsc','FM-1_74000200'),('rollback-FM-1_7400.fwsc','rollback-FM-1_7400.fwsc','FM-1_7400')]:
 data=(baseline/'firmware'/src).read_bytes();assert I.product_of(data)==id;(fw/dst).write_bytes(data)
site=out/'testing';site.mkdir(exist_ok=True);(site/'firmware').mkdir(exist_ok=True)
for p in fw.glob('*.fwsc'):shutil.copy2(p,site/'firmware'/p.name)
boot=r/'platform/web/m-bootloader'/f'fm1-uboot-{S.MBOOT_VERSION}.fwsc';bootname=f'm-bootloader-{S.MBOOT_VERSION}.fwsc';shutil.copy2(boot,site/'firmware'/bootname);shutil.copy2(boot.parent/'LICENSE',site/'firmware/m-bootloader-LICENSE.txt')
for p in (r/'platform/LICENSES').glob('*.txt'):shutil.copy2(p,site/'firmware'/p.name)
lib='\n'.join(S.strip_module((r/'platform/web'/n).read_text()) for n in ['fm1ports.js','fm1pkg.js','fm1ota.js']);template=(r/'platform/web/installer.html').read_text()
for k,val in [('RES',"KIRA-9 data"),('RES_JA','KIRA-9 data'),('NAME','KIRA-9'),('REPO','https://github.com/CodingSlapfu/KIRA-9'),('REPO_SHORT','github.com/CodingSlapfu/KIRA-9'),('LICENSE','MIT; platform MPL-2.0'),('CREDITS','')]:template=template.replace('{{'+k+'}}',val)
for folder,version,product,pkg in [('install',v,identity,f'kira-9-{v}.fwsc'),('rollback','0.2.1-dev rollback','FM-1_74000201','rollback-0.2.1-dev.fwsc'),('rollback-020','0.2.0-dev rollback','FM-1_74000200','rollback-0.2.0-dev.fwsc'),('legacy-rollback','legacy rollback','FM-1_7400','rollback-FM-1_7400.fwsc')]:
 meta={'version':version,'product':product,'pkg':'../firmware/'+pkg,'sha256':sha((fw/pkg).read_bytes()),'backup':True,'res':None,'boot':{'pkg':'../firmware/'+bootname,'version':S.MBOOT_VERSION,'sha256':sha(boot.read_bytes())}}
 page=template.replace('const pkg = new Uint8Array(await r.arrayBuffer());','const pkg = new Uint8Array(await r.arrayBuffer());\n    if (await sha256hex(pkg) !== meta.sha256) throw new Error("Testing firmware SHA-256 mismatch");').replace('/*LIB*/',lib).replace('/*META*/',json.dumps(meta)).replace('/*APP*/','null').replace('<main>','<main><p><strong>TESTING ONLY — KIRA-9 '+version+'. Back up before flashing. Human/hardware acceptance remains open.</strong></p>',1)
 (site/folder).mkdir(exist_ok=True);(site/folder/'index.html').write_text(page)
for name,data in S.tool_pages(r/'app').items():p=site/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
for a,b in [(r/'app/build/emu',site/'emu'),(r/'app/web/words',site/'words'),(r/'studio',site/'studio')]:shutil.copytree(a,b,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.c','emulator'))
assert len(json.loads((site/'studio/dictionary.json').read_text()))==126051
shutil.copy2(r/'platform/tools/fm1_install.py',site/'fm1_install.py')
proof=out/'validation';shutil.copytree(r/'validation/development-022',proof,dirs_exist_ok=True)
for kind in ['native','host','wasm','emulator']:shutil.copy2(r/'build'/f'{kind}-build-022.txt',proof/f'{kind}-build.txt')
build_id=re.search(r'build\s+([A-F0-9]{8})', (r/'build/native-build-022.txt').read_text()).group(1)
# Full snapshot, including pinned platform/BSP, offline dictionary, workflows and fresh tests.
files={}
for p in r.rglob('*'):
 if not p.is_file():continue
 n=p.relative_to(r).as_posix()
 if any(x in p.relative_to(r).parts for x in ['.git','__pycache__']) or n.startswith(('build/','app/build/','studio/emulator/')) or n=='SOURCE_MANIFEST.json' or n.endswith(('.pyc','.flash','.wav','.flac','.ogg','.mp3')):continue
 files[n]=p.read_bytes()
files['RECOVERED_021_SOURCE_MANIFEST.json']=(r/'SOURCE_MANIFEST.json').read_bytes()
inputs=json.loads((r/'build/compiled-input.json').read_text())
for n,h in inputs.items():assert sha((r/n).read_bytes())==h,('CI/local source mismatch',n)
manifest_source={'restored_from':'verified v0.2.1-dev ZIP/source.zip','local_checkpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'ci_workflow_commit':'0f36eb06e4560a6425cadf55dd352296b249a2a8','ci_run':42635509598,'verified_source_backup':json.loads((r/'validation/development-022/github-source-backup.json').read_text()),'native_build_id':build_id,'platform_commit':'698e2cba46b33bf14d9bf756675036053535638e','bsp_commit':'f878800967e66e721dfbc9a4f5fe1835772ae8fc','files':{n:sha(data) for n,data in sorted(files.items())},'note':'Historical audio recordings omitted; original baseline ZIP remains unchanged. Frozen experiment source/data retained, not promoted.'}
with zipfile.ZipFile(out/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,data in sorted(files.items()):z.writestr(n,data)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest_source,indent=2)+'\n')
(out/'README.txt').write_text(f'''KIRA-9 {v} — TESTING ONLY
Identity {identity}; native build {build_id}

Extract all files. In this folder run:
  python -m http.server 8000 --bind 127.0.0.1
Windows: py -3 -m http.server 8000 --bind 127.0.0.1
Use Chrome or Edge, and leave this server running.

FIRST export a full device backup: http://localhost:8000/testing/backup/
Testing installer: http://localhost:8000/testing/install/
Studio: http://localhost:8000/testing/studio/
Device emulator: http://localhost:8000/testing/emu/
Exact v0.2.1-dev rollback: http://localhost:8000/testing/rollback/
v0.2.0-dev rollback: http://localhost:8000/testing/rollback-020/
Earlier rollback: http://localhost:8000/testing/legacy-rollback/
Each installer verifies the exact firmware SHA-256 and package integrity.
Never interrupt actual flash writes. Physical installation is owner-unverified.

New: first-note pitch starts in tune; connected vowels/humming retain vibrato
onset and avoid repeated tail gates; diphthongs hold their nucleus before a
bounded off-glide, with synchronized lip shapes; envelope-driven brows and
emotional eyelids; source-owned MIDI sustain with safe release/panic; duplicate,
future and stale clock rejection; prompt studio STOP and live expression.
No new sample voice was promoted. Naturalness/intelligibility need your feedback.

Existing VOICE ALGO selects Lyrics/Vocalise/Scat/Hum/Vocables. K3 chooses the
family; SAVE retains it. On SONG, select LIVE for keys. Studio section settings
and Transfer full arrangement preserve independent voices and expression.
The offline pronunciation dictionary is included. No network is needed to sing.

Rollback to 0.2.1 keeps the same 60-byte preferences and storage layout.
0.2.0/earlier resets newer preferences; restore its corresponding pre-update
backup. Song/phrase/word storage offsets and CRC wire formats are unchanged.
Source.zip contains complete source, platform/BSP, tests and manifests.
Validation/ contains build/resource/installer/test receipts and owner checklist.
All 23 requirements remain tracked. No subjective or physical acceptance claims,
no official release/public website deployment, no AQUORA changes.
''')
manifest={'version':v,'identity':identity,'native_build_id':build_id,'testing_only':True,'official_release':False,'ci_run':'https://github.com/CodingSlapfu/KIRA-9/actions/runs/42635509598','physical_acceptance':'OWNER_UNVERIFIED','source_members':len(files),'rollback_021_sha256':sha((fw/'rollback-0.2.1-dev.fwsc').read_bytes()),'files':{}}
manifest['files']={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file() and p.name not in {'MANIFEST.json','SHA256SUMS'}};(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
hashes={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'};(out/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()))
archive=out.parent/(out.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(out)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for n,h in hashes.items():assert sha(z.read(n))==h,n
 with zipfile.ZipFile(__import__('io').BytesIO(z.read('source.zip'))) as s:
  for n,h in manifest_source['files'].items():assert sha(s.read(n))==h,n
report={'package':str(archive),'sha256':sha(archive.read_bytes()),'bytes':archive.stat().st_size,'package_members_verified':len(hashes),'source_members_verified':len(files),'identity':identity,'native_build_id':build_id};(r/'build/testing-package-022.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
