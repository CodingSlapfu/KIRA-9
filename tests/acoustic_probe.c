/* SPDX-License-Identifier: MIT; isolated real DSP phoneme output, no model. */
#include "kira.h"
#include <stdio.h>
#include <math.h>
int main(void){k9_engine e;float b[512];unsigned long samples=0,clips=0;float peak=0;
 for(unsigned voice=0;voice<7;voice++)for(unsigned phone=1;phone<K9_NPHONE;phone++)for(unsigned note=48;note<=84;note+=12){k9_init(&e);e.voice=voice;k9_note(&e,phone,note,100);e.phone_frames=22050;
  for(unsigned i=0;i<40;i++){k9_render(&e,b,256);for(unsigned j=0;j<512;j++){float x=fabsf(b[j]);if(!isfinite(x))return 2;if(x>peak)peak=x;if(x>.93999f)clips++;samples++;}if(i>=32 && fwrite(b,sizeof(float),512,stdout)!=512)return 3;}}
 fprintf(stderr,"samples=%lu clips=%lu peak=%.6f\n",samples,clips,peak);return 0;}
