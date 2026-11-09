#!/usr/bin/env python3
"""Verify actual KIRA-9 development package; never installs on hardware/deploys."""
import pathlib,sys,json,hashlib,struct,subprocess,ast,fcntl,shutil
r=pathlib.Path(__file__).resolve().parents[1];out=r/'validation/development-021';out.mkdir(exist_ok=True);sys.path.insert(0,str(r/'platform/tools'));import fm1_install as I, fm1pkg_make as P
raw=(r/'app/build/kira-9-0.2.1-dev.fwsc').read_bytes();image=I.logical_image(raw);assert I.product_of(raw)=='FM-1_74000201';head=bytearray(image[:64]);P.enc(head,0,64);assert P.crc16(head[2:])==struct.unpack_from('<H',head)[0];n=struct.unpack_from('<H',head,8)[0];assert P.crc16(image[64:64+n*80])==struct.unpack_from('<H',head,2)[0];parts={}
for j in range(n):
 e=bytearray(image[64+j*80:64+(j+1)*80]);P.enc(e,0,80);typ,_,crc,_,off,size,_=struct.unpack_from('<HHHHIII',e);data=image[off:off+size];assert len(data)==size and P.crc16(data)==crc;parts[typ]=data
assert parts[100]==(r/'app/build/loader/ota.bin').read_bytes();region=bytearray(parts[0][0x4000:]);P.sfc(region,0,len(region),0,P.KEY);app=(r/'app/build/kira-9.bin').read_bytes();assert region[0x120:0x120+len(app)]==app;assert set(region[0x120+len(app):0x120+P.APP_SLOT])<={255}
# Cross-check package write span against ALL30 A/B storage pairs; no old power-cut replay.
import re
h=(r/'app/app.h').read_text();m=h[h.index('#define APP_STORE_MAP'):h.index('#define APP_BACKUP_OBJS')];slots=[int(x,16) for x in re.findall(r'0x([0-9a-f]+)u',m)];assert len(slots)==30 and min(slots)>=len(parts[0]);assert all(a+8192<=b or b+8192<=a for i,a in enumerate(slots) for b in slots[i+1:])
nm=subprocess.check_output(['nm','--defined-only',str(r/'app/build/kira-9.elf')],text=True);symbols={x[2]:int(x[0],16) for line in nm.splitlines() if len(x:=line.split())==3};assert not any(name.startswith(('rp_','mg_')) for name in symbols)
ram=symbols['_bss_end']-symbols['_data_start'];pool=symbols['_pool_end']-symbols['_pool_start'];rt=symbols['_rt_end']-symbols['_rt_start'];assert ram<=98304 and pool<=344064 and len(app)<=P.APP_SLOT
budgets={'app_bytes':len(app),'app_slot_bytes':P.APP_SLOT,'app_spare':P.APP_SLOT-len(app),'data_bss_bytes':ram,'data_bss_spare':98304-ram,'pool_bytes':pool,'pool_spare':344064-pool,'ram_code_bytes':rt,'ram_code_spare':32768-rt,'conservative_future_voice_reserve_flash':73728,'conservative_future_voice_reserve_ram':8192,'flash_after_reserve':P.APP_SLOT-len(app)-73728,'data_bss_after_reserve':98304-ram-8192,'experimental_voice_linked':False,'physical_cpu':'UNVERIFIED; no host measurement claimed as FM-1 timing'}
assert budgets['flash_after_reserve']>0 and budgets['data_bss_after_reserve']>0
# Reuse simulator definitions, not its already-completed generic tests.
p=r/'platform/tests/install_test.py';tree=ast.parse(p.read_text());nodes=[]
for node in tree.body:
 if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='wire':break
 nodes.append(node)
ns={'__file__':str(p),'__name__':'kira_specific_install_fixture'};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns);Fake=ns['FakeFM1'];cli=ns['cli'];results=[]
for label,identity,name,unplug,target in [('direct-development-update','FM-1_74000200','FM-1',None,'FM-1_74000201'),('loader-recovery','ota-FM-1_74000201','Felucca Update',None,'FM-1_74000201'),('connection-loss','FM-1_74000201','FM-1',2,'FM-1_74000201'),('wrong-final-identity','FM-1_74000201','FM-1',None,'FM-1_999')]:
 d=Fake(image,identity=identity,name=name,unplug_after=unplug,after_write=target);rc,stdout,stderr=cli([str(r/'app/build/kira-9-0.2.1-dev.fwsc'),'--yes','--classic'],d);expected=4 if unplug else 6 if target!='FM-1_74000201' else 0;assert rc==expected,(label,rc,stdout,stderr);assert d.bad==0;results.append({'case':label,'exit_code':rc,'expected':expected,'served_reads':d.served,'wrong_bytes':d.bad,'scope':'Host installer protocol simulation with actual package; not real flash writes/power loss.'})
shutil.rmtree(ns['TMP'],ignore_errors=True)
files={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ['app/build/kira-9.bin','app/build/kira-9.elf','app/build/kira-9-0.2.1-dev.fwsc','app/build/loader/ota.bin','studio/kira.wasm']}
report={'identity':'FM-1_74000201','release_accepted':False,'published':False,'checks':'Python and JS actual-package validation; decrypted app bytes and loader exact;30store pairs outside package flash; experimental voice absent; classic direct/recovery/loss/final-ID fixtures','memory':budgets,'installer_cases':results,'artifacts_sha256':files,'limitations':'Fast real-loader interrupted flash/rollback physical acceptance remains unverified; existing generic fixtures retained, not replayed. Same development identity cannot identify source revision on a physical unit: use matching manifest/build ID; release identity/version gated.'};(out/'package-and-budgets.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
