"""Emit one authenticated, compile-only CI job from this recovered source.
No releases, recordings, deployment, old acoustic experiments or credential handling.
"""
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1]
paths=[]
for folder in ['app','core','factory','studio']:
 for p in (r/folder).rglob('*'):
  n=p.relative_to(r).as_posix()
  if p.is_file() and '/build/' not in n and p.suffix in {'.c','.h','.toml','.mjs','.js','.html','.css','.tsv'}:paths.append(p)
for n in ['tools/setup_native.py','tools/build_web.sh','tools/verify_development022.py','tools/wordless_parity.py','tests/wordless_parity.mjs','tests/test_performance022.c','tests/worklet_profiles.mjs','tests/performance_timeline.mjs','tests/test_section_profiles.c']:paths.append(r/n)
files={p.relative_to(r).as_posix():{'content':p.read_text(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths}
payload=json.dumps(files,ensure_ascii=True,separators=(',',':')).replace('$','\\u0024')
steps=[{'uses':'actions/checkout@v4','with':{'ref':'54f9d9ad1d74dad67a59973507145b32d1b96044','submodules':'recursive'}},{'uses':'actions/setup-python@v5','with':{'python-version':'3.12'}},{'uses':'actions/setup-node@v4','with':{'node-version':'22'}},{'uses':'mymindstorm/setup-emsdk@v14','with':{'version':'4.0.19'}}]
for i,start in enumerate(range(0,len(payload),17000)):
 steps.append({'name':f'Restore verified source {i+1}','run':f"cat > /tmp/kira-recovery-{i:03d} <<'KIRA_SOURCE_EOF'\n{payload[start:start+17000]}\nKIRA_SOURCE_EOF\n"})
apply="""python3 - <<'PYCODE'
from pathlib import Path
import json,hashlib
files=json.loads(''.join(p.read_text().removesuffix('\\n') for p in sorted(Path('/tmp').glob('kira-recovery-*'))))
for name,entry in files.items():
 p=Path(name);assert not p.is_absolute() and '..' not in p.parts
 data=entry['content'].encode();assert hashlib.sha256(data).hexdigest()==entry['sha256']
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
Path('build').mkdir(exist_ok=True)
Path('build/compiled-input.json').write_text(json.dumps({name:entry['sha256'] for name,entry in files.items()},indent=2)+'\\n')
PYCODE
python3 -m pip install pillow
python3 tools/setup_native.py > build/native-env.json
python3 - <<'PYCODE'
import json,os
with open(os.environ['GITHUB_ENV'],'a') as f:
 for key,value in json.load(open('build/native-env.json')).items():f.write(key+'='+value+'\\n')
PYCODE
"""
steps.append({'name':'Verify input and prepare pinned native compiler','run':apply})
steps.append({'name':'Compile native and WASM without publication','run':'''set -euo pipefail
python3 platform/tools/build.py app --release 0.2.2-dev > build/native-build-022.txt 2>&1
sh tools/build_web.sh > build/wasm-build-022.txt 2>&1
python3 platform/tools/build.py app --web --release 0.2.2-dev > build/emulator-build-022.txt 2>&1
cc -shared -fPIC -Wl,--no-undefined -O2 -ffp-contract=off -Icore core/engine.c core/codec.c core/library.c core/tables.c core/face.c studio/bridge.c -o build/libkira.so
mkdir -p validation/development-022
python3 tools/wordless_parity.py > validation/development-022/parity.txt
node tests/wordless_parity.mjs >> validation/development-022/parity.txt
node tests/worklet_profiles.mjs > validation/development-022/worklet.txt
python3 tools/verify_development022.py > validation/development-022/package-safety.txt
'''})
steps.append({'uses':'actions/upload-artifact@v4','if':'always()','with':{'name':'KIRA-9-0.2.2-dev-compiled','path':'app/build/kira-9*\napp/build/firmware.json\napp/build/loader/ota.bin\napp/build/emu\nstudio/kira.wasm\nbuild/compiled-input.json\nbuild/*build-022.txt\nvalidation/development-022','retention-days':90,'if-no-files-found':'error'}})
workflow={'name':'KIRA-9 0.2.2 compile recovered verified source','on':{'push':{'paths':['.github/workflows/recovered-022.yml']},'workflow_dispatch':{}},'permissions':{'contents':'read'},'concurrency':{'group':'kira-9-development-checkpoint','cancel-in-progress':False},'jobs':{'compile':{'runs-on':'ubuntu-latest','timeout-minutes':25,'steps':steps}}}
p=r/'build/recovered-022.yml';p.write_text(json.dumps(workflow,indent=2)+'\n');(r/'build/compiled-input-expected.json').write_text(json.dumps({n:e['sha256'] for n,e in files.items()},indent=2)+'\n');print(json.dumps({'workflow':str(p),'bytes':p.stat().st_size,'restored_files':len(files)}))
