#!/usr/bin/env python3
"""Create isolated one-cause candidates; never edit production DSP or replay acceptance."""
import pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/nucleus-study';out.mkdir(parents=True,exist_ok=True)
sha='3a407ec870481833f7b13fbdf98b3122f7fc4bc2'
subprocess.run(['git','fetch','origin',sha,'--depth=1'],cwd=root,check=True)
base=subprocess.check_output(['git','show',sha+':core/engine.c'],cwd=root,text=True)
late=base.replace('    for (b = 0; b < 3; b++) {\n      float a = bank[from]', '    float tract_progress = from == to ? progress : bounded((progress-.60f)*2.5f,0,1);\n    for (b = 0; b < 3; b++) {\n      float a = bank[from]',1)
start=late.index('    float tract_progress');end=late.index('    k9_articulation articulation',start);late=late[:start]+late[start:end].replace(' * progress',' * tract_progress')+late[end:]
smooth=base.replace('      g += (gg - g) * morph;','      g += (gg - g) * morph;\n      g *= k9_spectral_weights[e->phone][b];').replace('sample += y * k9_spectral_weights[e->phone][b];','sample += y;').replace('harmonic += y * k9_spectral_weights[e->phone][b];','harmonic += y;')
for name,source in [('baseline',base),('late',late),('smooth',smooth)]:
 path=out/f'engine-{name}.c';path.write_text(source)
 subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-Icore',str(path),'core/codec.c','core/library.c','core/tables.c','core/face.c','studio/bridge.c','-o',str(out/f'{name}.so')],cwd=root,check=True)
print('Isolated baseline, late-glide and smoothed-weight candidates compiled; production engine unchanged.')
