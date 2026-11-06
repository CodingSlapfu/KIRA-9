#!/usr/bin/env python3
"""One predeclared calibration pass, not iterative gain hunting: RMS .10/peak .30 caps."""
import pathlib,ctypes,numpy as np,re,json
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/english6';l=ctypes.CDLL(str(out/'prototype-unit.so'));l.web_render.restype=ctypes.POINTER(ctypes.c_float)
values=[];summary=[]
for voice in range(7):
 row=[]
 for phone in range(40):
  pitches=[]
  for note in [48,60,72]:
   if not phone:pitches.append(0);continue
   l.web_probe(phone,note,voice,127);samples=[]
   for _ in range(52):samples.append(np.ctypeslib.as_array(l.web_render(256),shape=(512,))[::2].copy())
   a=np.concatenate(samples);rms=float(np.sqrt(np.mean(a*a)));peak=float(np.max(abs(a)));gain=min(8,.10/max(rms,1e-9),.30/max(peak,1e-9));pitches.append(gain);summary.append({'voice':voice,'phone':phone,'note':note,'raw_rms':rms,'raw_peak':peak,'gain':gain})
  row.append(pitches)
 values.append(row)
p=out/'proto6_profiles.h';s=p.read_text();s=s[:s.index('static const float p6_pitch_gain')]+ 'static const float p6_pitch_gain[7][40][3]={\n'+',\n'.join('{'+','.join('{'+','.join(f'{g:.8f}f' for g in pitch)+'}' for pitch in voice)+'}' for voice in values)+'\n};\n';p.write_text(s)
(out/'calibration.json').write_text(json.dumps({'design':'Single offline pass: gain=min(8, .10/RMS, .30/peak), seven tract scales, every phone at 48/60/72; no output limiter or post-test global lowering.','measurements':summary},indent=2)+'\n');print('Calibrated',len(summary),'phone/voice/pitch cells from unit-peak filter outputs.')
