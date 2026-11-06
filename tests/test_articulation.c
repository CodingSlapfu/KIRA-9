/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include "articulation.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static float a[8820],b[8820];
int main(void){
 const uint8_t phones[]={K9_P,K9_T,K9_K,K9_B,K9_D,K9_G,K9_CH,K9_JH};
 for(unsigned p=0;p<8;p++){
  unsigned onset=0;
  for(unsigned i=0;i<4410;i++){k9_articulation x=k9_articulate(phones[p],i,4410),y=k9_articulate(phones[p],i,22050);assert(x.voiced==y.voiced&&x.noise==y.noise&&x.closure==y.closure);if(!onset&&x.noise>0)onset=i;assert(isfinite(x.noise)&&x.noise>=0&&x.noise<=1);}
  assert(onset>400&&onset<1400);
  for(unsigned n=1;n<100;n++)for(unsigned i=0;i<n;i++){k9_articulation x=k9_articulate(phones[p],i,n);assert(isfinite(x.noise)&&x.noise>=0&&x.noise<=1);}
 }
 for(unsigned note=48;note<=84;note+=12){k9_engine x,y;k9_init(&x);k9_note(&x,K9_P,note,100);x.phone_frames=4410;y=x;y.phone_frames=22050;k9_render(&x,a,4410);k9_render(&y,b,4410);assert(!memcmp(a,b,sizeof a));double burst=0;for(unsigned i=0;i<900;i++)assert(a[i]==0);for(unsigned i=2200;i<2900;i++)burst+=a[i]*a[i];assert(burst>0);for(unsigned i=0;i<8820;i++)assert(isfinite(a[i])&&fabs(a[i])<=.94);}
 puts("PASS fixed-time consonant windows, short-event bounds, real PCM closure/burst, duration invariance at four pitches and peak safety");
}
