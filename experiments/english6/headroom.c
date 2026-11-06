/* SPDX-License-Identifier: MIT; NEW prototype-only transition stress, no old acceptance replay. */
#include "kira.h"
#include <stdio.h>
#include <math.h>
static float audio[512];
int main(void){k9_engine e;float max=0,band=0;unsigned long frames=0,over=0,bad=0;
 for(unsigned voice=0;voice<7;voice++)for(unsigned note=48;note<=84;note+=12)for(unsigned order=0;order<2;order++){
  k9_init(&e);e.voice=voice;
  for(unsigned k=1;k<K9_NPHONE;k++){unsigned phone=order?K9_NPHONE-k:k;k9_note(&e,phone,note,127);e.phone_frames=4410;
   for(unsigned b=0;b<12;b++){k9_render(&e,audio,256);for(unsigned j=0;j<512;j++)if(!isfinite(audio[j]))bad++;frames+=256;}}
  k9_stop(&e);for(unsigned k=0;k<100;k++)k9_render(&e,audio,256);
  if(fabsf(audio[510])>.00001f)bad++;
  printf("case voice=%u note=%u order=%u peak=%.9f\n",voice,note,order,e.prototype.raw_peak);if(e.prototype.raw_peak>max)max=e.prototype.raw_peak;if(e.prototype.band_peak>band)band=e.prototype.band_peak;over+=e.prototype.over;bad+=e.prototype.nonfinite;
 }
 printf("frames=%lu raw_peak=%.9f band_peak=%.9f over94=%lu invalid_or_stop_failure=%lu state_bytes=%lu engine_bytes=%lu\n",frames,max,band,over,bad,(unsigned long)sizeof(p6_state),(unsigned long)sizeof(k9_engine));return (bad||over||max>.9f)?1:0;}
