/* SPDX-License-Identifier: MIT; focused stability after moving weights into gain smoothing. */
#include "kira.h"
#include <math.h>
#include <assert.h>
#include <stdio.h>
static float a[512];
int main(void){k9_engine e;float peak=0;unsigned long samples=0,clipped=0;
 for(unsigned voice=0;voice<7;voice++)for(unsigned style=0;style<8;style++)for(unsigned note=48;note<=84;note+=12){k9_init(&e);e.voice=voice;e.style=style;
  for(unsigned phone=1;phone<K9_NPHONE;phone++){k9_note(&e,phone,note,127);e.phone_frames=4410;for(unsigned block=0;block<12;block++){k9_render(&e,a,256);for(unsigned j=0;j<512;j++){float v=fabsf(a[j]);assert(isfinite(v));if(v>peak)peak=v;if(v>.93999f)clipped++;samples++;}}}
  k9_stop(&e);for(unsigned i=0;i<100;i++)k9_render(&e,a,256);assert(fabsf(a[510])<.00001f);
 }
 printf("Transition sweep: %lu samples, %lu limiter hits, peak %.6f; stop tails pass\n",samples,clipped,peak);return clipped?1:0;}
