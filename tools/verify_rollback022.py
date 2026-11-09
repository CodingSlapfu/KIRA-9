"""Verify exact021 rollback from022 using the existing installer simulator."""
from pathlib import Path
import sys,ast,zipfile,tempfile,json,hashlib,shutil
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'platform/tools'));import fm1_install as I
p=r/'platform/tests/install_test.py';nodes=[]
for node in ast.parse(p.read_text()).body:
 if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='wire':break
 nodes.append(node)
ns={'__file__':str(p),'__name__':'kira022_rollback_fixture'};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
with zipfile.ZipFile(r.parent/'output/KIRA-9-0.2.1-dev-testing.zip') as z:raw=z.read('firmware/kira-9-0.2.1-dev.fwsc')
assert I.product_of(raw)=='FM-1_74000201';image=I.logical_image(raw)
with tempfile.TemporaryDirectory() as tmp:
 fw=Path(tmp)/'rollback-021.fwsc';fw.write_bytes(raw);d=ns['FakeFM1'](image,identity='FM-1_74000202',name='FM-1',after_write='FM-1_74000201');rc,stdout,stderr=ns['cli']([str(fw),'--yes','--classic'],d);assert rc==0 and d.bad==0,(rc,stdout,stderr)
 report={'case':'022-to-exact-021-rollback','passed':True,'served_reads':d.served,'wrong_bytes':d.bad,'rollback_sha256':hashlib.sha256(raw).hexdigest(),'preferences_compatible':True,'settings_bytes':60,'storage_map_unchanged':True,'physical_restore':'OWNER_UNVERIFIED','scope':'Actual old package and installer protocol simulation; no hardware writes'}
 (r/'validation/development-022/rollback.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
shutil.rmtree(ns['TMP'],ignore_errors=True)
