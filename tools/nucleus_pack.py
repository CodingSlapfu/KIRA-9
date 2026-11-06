#!/usr/bin/env python3
"""Archive already-rendered evidence; never rerun recognition or DSP tests."""
import pathlib,json,wave,hashlib,gzip,shutil,zipfile
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/nucleus-study';items=json.loads((out/'corpus.json').read_text());records=json.loads((out/'recognition.json').read_text())['results']+json.loads((out/'recognition-smooth.json').read_text())['results'];hashes={}
for r in records:
 p=out/f"{r['id']}-{r['variant']}.wav";assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],p
for variant in ['late','smooth']:
 wav=out/f'paired-{variant}.wav'
 with wave.open(str(wav),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100)
  for item in items:
   for v in ['baseline',variant]:
    with wave.open(str(out/f"{item['id']}-{v}.wav")) as r:w.writeframes(r.readframes(r.getnframes()))
    w.writeframes(bytes(44100*4))
 compressed=out/f'paired-{variant}.wav.gz'
 with wav.open('rb') as source,gzip.open(compressed,'wb',compresslevel=9) as destination:shutil.copyfileobj(source,destination)
 hashes[compressed.name]=hashlib.sha256(compressed.read_bytes()).hexdigest()

metadata=['corpus.json','recognition.json','recognition-smooth.json','analysis.json','analysis-smooth.json','environment.json','transition-guard.json']
for name in metadata:hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
(out/'MANIFEST.json').write_text(json.dumps({'baseline':'3a407ec870481833f7b13fbdf98b3122f7fc4bc2','firmware_changed':False,'release_accepted':False,'order':'For each case in corpus.json: baseline then candidate, each followed by one second silence. Same cases/order for each lossless FLAC.','files':hashes},indent=2)+'\n')
with zipfile.ZipFile(out/'nucleus-evidence.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in list(hashes)+['MANIFEST.json']:z.write(out/name,name)
archive=out/'nucleus-evidence.zip';(out/'SHA256SUMS').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  nucleus-evidence.zip\n')
print('Verified all 36 original WAV hashes; archived lossless paired recordings and result/score metadata.',flush=True);print('ZIP bytes',archive.stat().st_size,'sha256',hashlib.sha256(archive.read_bytes()).hexdigest())
