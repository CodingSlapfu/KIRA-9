#!/usr/bin/env python3
import ctypes,pathlib,wave,struct,json,hashlib
lib=ctypes.CDLL(str(pathlib.Path('build/libkira.so').resolve()));lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
lib.web_init();lib.web_demo(0);lib.web_voice(0,0);pcm=[]
for _ in range(100):
 p=lib.web_render(256);pcm.extend(p[i] for i in range(512))
pathlib.Path('build/golden.f32').write_bytes(struct.pack('<'+'f'*len(pcm),*pcm))
metrics=[]
for voice in range(7):
 lib.web_init();lib.web_demo(0);lib.web_voice(voice,0);samples=[]
 for _ in range(172):
  p=lib.web_render(256);samples.extend(p[i] for i in range(512))
 peak=max(abs(v) for v in samples);rms=(sum(v*v for v in samples)/len(samples))**.5
 metrics.append({'voice':voice,'peak':peak,'rms':rms,'pcm_sha256':hashlib.sha256(struct.pack('<'+'f'*len(samples),*samples)).hexdigest()})
 with wave.open(f'build/voice-{voice}.wav','wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(struct.pack('<'+'h'*len(samples),*(int(max(-1,min(1,v))*32767) for v in samples)))
assert len({m['pcm_sha256'] for m in metrics})==7
pathlib.Path('validation/audio-metrics.json').write_text(json.dumps({'note':'Host DSP evidence; hashes and spectra cannot certify English intelligibility or musical quality.','voices':metrics},indent=2)+'\n')
print('PASS seven distinct native PCM voice fixtures; listening acceptance remains open')
