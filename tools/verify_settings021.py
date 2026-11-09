"""Actual app boots with prior version settings and corrupted new selectors."""
from pathlib import Path
import struct,zlib,subprocess,json
r=Path(__file__).resolve().parents[1];out=r/'validation/development-021/migration';out.mkdir(parents=True,exist_ok=True)
# k9_settings legacy layout: 56 bytes. Newly appended selectors start at 56.
p=bytearray(56);struct.pack_into('<I',p,0,0x4b395032);p[5]=3;p[6]=1;p[10]=1;p[38]=6;p[39]=20;p[40]=50;p[41]=110;p[46:54]=bytes(range(8));p[54]=1
cases=[('legacy020',p,3,0),('invalid-new-selector',p+bytes([255,255,0,0]),0,0)]
results=[]
for name,data,voice,mode in cases:
 image=bytearray(b'\xff'*0x100000);s=0xfc000;head=bytearray(b'\xff'*32);struct.pack_into('<IHHIII',head,0,0x30583058,0,0,1,len(data),zlib.crc32(data));struct.pack_into('<I',head,28,zlib.crc32(head[:28]));image[s:s+32]=head;image[s+256:s+256+len(data)]=data
 (out/(name+'.flash')).write_bytes(image);script=out/(name+'.txt');script.write_text(f'flash_load out:{name}.flash\nreboot\nexpect voice {voice}\nexpect vocal_mode {mode}\nexpect vocal_family 0\ntap SAVE\nwait 200\nreboot\nexpect voice {voice}\nexpect vocal_mode 0\nexpect vocal_family 0\n')
 result=subprocess.run([str(r/'app/build/host/kira-9_host'),str(script),str(out)],capture_output=True,text=True);(out/(name+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr;results.append({'case':name,'passed':True})
(out.parent/'settings-migration.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS previous 56-byte settings retain voice/live mode; absent selectors default Lyrics; invalid new settings rejected; SAVE/reboot migration')
