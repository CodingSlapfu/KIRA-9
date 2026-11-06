#!/usr/bin/env python3
"""Generate an isolated baseline adapter; never edit product source."""
import pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/consonant-cues';out.mkdir(exist_ok=True)
header=(root/'core/kira.h').read_text().replace('#include <stdint.h>','#include <stdint.h>\n#include "cues.h"').replace('} k9_engine;','  cue_state cue;\n} k9_engine;')
(out/'kira.h').write_text(header)
base=(root/'core/engine.c').read_text().replace('#include "clarity.h"','#include "clarity.h"\n#include "cues.h"\ncue_signal cue_step(k9_engine*,float,float,float);\nstatic float cue_raw_peak;\nstatic unsigned cue_over;')
needle='    excitation = excitation * articulation.voiced'
assert base.count(needle)==1
base=base.replace(needle,'    cue_signal cues=cue_step(e,noise,excitation,articulation.noise);\n    excitation=cues.voice;\n'+needle)
needle='    excitation *= gate;'
base=base.replace(needle,'    if(cues.bypass)excitation=0;\n'+needle)
needle='    /* Retain a periodic voicing bar'
base=base.replace(needle,'    sample+=cues.direct*gate;\n'+needle)
needle='    out[i * 2] = bounded'
base=base.replace(needle,'    float raw=absolute(sample+harmonic);if(raw>cue_raw_peak)cue_raw_peak=raw;if(raw>.94f)cue_over++;\n'+needle)
base+='\nfloat cue_peak(void){return cue_raw_peak;}\nunsigned cue_clips(void){return cue_over;}\nvoid cue_reset(void){cue_raw_peak=0;cue_over=0;}\n'
(out/'adapter.c').write_text(base)
bridge=(root/'build/english6/bridge.c').read_text();bridge=bridge[:bridge.index('__attribute__((visibility("default"))) float *web_diagnostics')]
bridge+='''\n__attribute__((visibility("default"))) void cue_note(unsigned p,unsigned n,unsigned vel,unsigned frames){k9_note(&web_engine,p,n,vel);web_engine.phone_frames=frames;}\n__attribute__((visibility("default"))) unsigned cue_state_size(void){return sizeof(cue_state);}\n'''
(out/'bridge.c').write_text(bridge)
subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-I'+str(out),'-Iexperiments/consonant_cues','-Icore',str(out/'adapter.c'),'experiments/consonant_cues/cues.c','core/codec.c','core/library.c','core/tables.c','core/face.c',str(out/'bridge.c'),'-o',str(out/'candidate.so')],cwd=root,check=True)
print('Built isolated consonant cue adapter; core/app/studio unchanged.')
