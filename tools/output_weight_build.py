#!/usr/bin/env python3
"""Isolated output-weight candidate; production sources and previous experiments unchanged."""
import pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1];out=root/'build/output-weight-study';out.mkdir(parents=True,exist_ok=True)
header=(root/'core/kira.h').read_text();assert '} k9_engine;' in header
(out/'kira.h').write_text(header.replace('} k9_engine;','  float output_weight[3];\n} k9_engine;'))
base=(root/'core/engine.c').read_text();candidate=base.replace('  e->rng = 0x4b495241u;','  e->rng = 0x4b495241u;\n  for(unsigned b=0;b<3;b++)e->output_weight[b]=1.0f;')
needle='      e->gain[b] += (g - e->gain[b]) * .003f;';assert needle in candidate
candidate=candidate.replace(needle,needle+'\n      e->output_weight[b] += (k9_spectral_weights[e->phone][b]-e->output_weight[b])*.003f;')
candidate=candidate.replace('y * k9_spectral_weights[e->phone][b]','y * e->output_weight[b]')
bridge=(root/'studio/bridge.c').read_text().replace('#include "../core/face.h"','#include "kira.h"\n#include "face.h"').replace('#include "../core/kira.h"','').replace('#include "../core/library.h"','#include "library.h"').replace('#include "../factory/songs.h"','#include "../../factory/songs.h"')
bridge+='''\n__attribute__((visibility("default"))) void web_probe_phone(unsigned p,unsigned n){k9_note(&web_engine,(uint8_t)p,(uint8_t)n,127);web_engine.phone_frames=4410;}\n/* Diagnostic only: verify feedback states stay unweighted and identical. */
__attribute__((visibility("default"))) unsigned web_feedback_hash(void){unsigned h=2166136261u;const unsigned char *p;unsigned j;const float *arrays[]={web_engine.z1,web_engine.z2,web_engine.hz1,web_engine.hz2};for(unsigned i=0;i<4;i++){p=(const unsigned char *)arrays[i];for(j=0;j<12;j++)h=(h^p[j])*16777619u;}return h;}\n'''
(out/'bridge.c').write_text(bridge)
for name,source in [('baseline',base),('output',candidate)]:
 p=out/f'engine-{name}.c';p.write_text(source)
 subprocess.run(['cc','-shared','-fPIC','-O2','-ffp-contract=off','-I'+str(out),'-Icore',str(p),'core/codec.c','core/library.c','core/tables.c','core/face.c',str(out/'bridge.c'),'-o',str(out/f'{name}.so')],cwd=root,check=True)
# Same existing transition guard, correctly sized isolated engine header.
subprocess.run(['cc','-O2','-ffp-contract=off','-I'+str(out),'-Icore','tests/nucleus_transition.c',str(out/'engine-output.c'),'core/tables.c','core/codec.c','core/library.c','-o',str(out/'transition-guard')],cwd=root,check=True)
print('Candidate: 3 smoothed OUTPUT weights, 12 diagnostic bytes; raw resonator feedback untouched. Production unchanged.')
