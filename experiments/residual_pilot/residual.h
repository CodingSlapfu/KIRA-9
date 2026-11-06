/* SPDX-License-Identifier: MIT; original isolated runtime, not product API. */
#ifndef K9_RESIDUAL_H
#define K9_RESIDUAL_H
#include <stdint.h>
typedef struct { const int8_t *residual; const int16_t *reflection; unsigned samples,frames; float scale,period; } rp_unit;
typedef struct {
 float history[12],a[12],ring[512];
 float phase,period,last,next,resample;
 unsigned unit,pos,frame,head,holding,running;
} rp_state;
void rp_init(rp_state*);
void rp_start(rp_state*,unsigned unit,unsigned midi,unsigned hold);
void rp_stop(rp_state*);
void rp_render(rp_state*,float *out,unsigned frames);
unsigned rp_size(void);
unsigned rp_data_size(void);
#endif
