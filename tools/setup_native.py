#!/usr/bin/env python3
"""Pinned, noninteractive native dependencies; never downloads into a source tree."""
import pathlib,urllib.request,hashlib,tarfile,os,json
root=pathlib.Path(__file__).resolve().parents[1];deps=root/'build/deps';deps.mkdir(parents=True,exist_ok=True)
url='https://jl-update.oss-cn-shenzhen.aliyuncs.com/jieli-linux-toolchains-20260730.1.tar.xz';sha='a1545cddbc451a06bac43eb5cd96d831470c42a97c5c0b1f98879a20fc7647bd';archive=deps/'toolchain.tar.xz'
def fetch(url,path,sha):
 if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
  temp=path.with_suffix('.part');urllib.request.urlretrieve(url,temp)
  if hashlib.sha256(temp.read_bytes()).hexdigest()!=sha:raise SystemExit('Dependency hash mismatch: '+url)
  temp.replace(path)
fetch(url,archive,sha)
tc=deps/'jieli-linux-toolchains-20260730.1'
if not (tc/'pi32v2/bin/clang').exists():
 # Python's data extraction filter rejects special files and strips archive ownership.
 with tarfile.open(archive) as tar:tar.extractall(deps,filter='data')
sdk=deps/'sdk/cpu/wl82/tools';sdk.mkdir(parents=True,exist_ok=True)
hashes={'uboot.boot':'4e3b4c220dc96641cb5a723f41e68ce41d5261ae9434bb33fbd7f2c59976ded4','cfg_tool.bin':'276579954f076886a6a7694f65dc71c034a63a2c204b76749065c0ac7b010d1b','cfg/eq_cfg_hw.bin':'41167491bffed4651750719c973d2758adeb9021a5670d02d6a53c85ed80ea7d'}
for path,digest in hashes.items():
 target=sdk/path;target.parent.mkdir(parents=True,exist_ok=True);fetch('https://gitee.com/Jieli-Tech/fw-AC79_AIoT_SDK/raw/AC79NN_SDK_V1.2.1_2023-12-13/cpu/wl82/tools/'+path,target,digest)
print(json.dumps({'JIELI_TOOLCHAIN':str(tc),'AC79_SDK':str(deps/'sdk')}))
