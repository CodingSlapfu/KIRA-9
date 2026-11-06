/* SPDX-License-Identifier: MIT; maximum-velocity audio headroom boundary. */
#include "kira.h"
#include <stdio.h>
#include <math.h>
int main(void){k9_engine e;float b[512],peak=0;unsigned long clips=0,samples=0;for(unsigned voice=0;voice<7;voice++)for(unsigned style=0;style<8;style++)for(unsigned phone=1;phone<K9_NPHONE;phone++)for(unsigned note=48;note<=84;note+=12){k9_init(&e);e.voice=voice;e.style=style;e.harmony=7;e.morph=0;k9_note(&e,phone,note,127);e.phone_frames=22050;for(unsigned i=0;i<12;i++){k9_render(&e,b,256);for(unsigned j=0;j<512;j++){float x=fabsf(b[j]);if(!isfinite(x))return 2;if(x>peak)peak=x;if(x>.93999f)clips++;samples++;}}}printf("samples=%lu clips=%lu peak=%.6f\n",samples,clips,peak);return clips?1:0;}
