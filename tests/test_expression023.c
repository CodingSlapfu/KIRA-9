#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "kira.h"
#include "expression.h"
int main(void){
 for(unsigned s=0;s<8;s++){
  k9_expression a=k9_expression_at(s,0,0,1,0,1),b=k9_expression_at(s,44100,.5,1,0,1);
  k9_expression c=k9_expression_at(s,44100,1,1,1,1),d=k9_expression_at(s,44100,1,1,0,1);
  assert(a.level>=1&&a.level<=1.181f&&b.air<=.07f&&b.openness<=.0221f);
  assert(c.level>=d.level);assert(k9_expression_at(s,44100,1,0,0,1).level==c.level);
  double sum=0;float last=k9_vibrato_wave(0,b.period);
  for(unsigned j=0;j<b.period;j++){float x=k9_vibrato_wave(j,b.period);sum+=x;assert(fabsf(x)<=1.00001f);assert(fabsf(x-last)<.002f);last=x;}
  assert(fabs(sum/b.period)<.00001);
  k9_engine e;k9_init(&e);e.style=s;k9_note(&e,K9_AA,69,127);float pcm[512];float peak=0;
  for(unsigned j=0;j<400;j++){k9_render(&e,pcm,256);for(unsigned i=0;i<512;i++){assert(isfinite(pcm[i]));if(fabsf(pcm[i])>peak)peak=fabsf(pcm[i]);}}
  assert(peak>0&&peak<=.94f);k9_stop(&e);k9_render(&e,pcm,256);assert(!e.playing&&!e.velocity);
 }
 puts("PASS bounded expressive contours, connected/live tails, zero-mean smooth style vibrato, full-velocity finite PCM and STOP across eight styles");
}
