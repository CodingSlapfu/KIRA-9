/* SPDX-License-Identifier: MIT; original English articulation, no external DSP code. */
#ifndef K9_ARTICULATION_H
#define K9_ARTICULATION_H
#include "kira.h"
typedef struct { float voiced, noise; uint8_t closure; } k9_articulation;
static float k9_unit(float x) { return x<0?0:x>1?1:x; }
/* Milliseconds, independent of pitch and sung duration. Short events compress
 * only when necessary to fit a complete closure/release before the next phone. */
static k9_articulation k9_articulate(uint8_t phone,uint32_t age,uint32_t frames) {
 k9_articulation a={1,1,0};
 float ms=(float)age*(1000.0f/44100.0f),duration=(float)frames*(1000.0f/44100.0f);
 float close=0,burst=0,tail=0,voiced=0;
 switch(phone){
 case K9_P:close=24;burst=8;tail=20;break;
 case K9_T:close=18;burst=6;tail=18;break;
 case K9_K:close=28;burst=9;tail=24;break;
 case K9_B:close=18;burst=6;tail=14;voiced=1;break;
 case K9_D:close=14;burst=5;tail=13;voiced=1;break;
 case K9_G:close=20;burst=7;tail=15;voiced=1;break;
 case K9_CH:close=18;burst=7;tail=55;break;
 case K9_JH:close=16;burst=6;tail=48;voiced=1;break;
 default:break;
 }
 if(close){
  float scale=duration<close+burst+tail?duration/(close+burst+tail):1;
  close*=scale;burst*=scale;tail*=scale;
  a.voiced=0;a.noise=0;
  if(ms<close){a.closure=1;a.voiced=voiced*.045f;}
  else if(ms<close+burst){float u=(ms-close)/burst;a.noise=(voiced?.18f:.32f)*4*u*(1-u);a.voiced=voiced*.3f*k9_unit((ms-close)/3);}
  else if(ms<close+burst+tail){float u=(ms-close-burst)/tail;a.noise=(phone==K9_CH||phone==K9_JH?.5f:.09f)*(1-u)*(1-u);a.voiced=voiced*.6f*(1-u);}
 }else if(phone==K9_S||phone==K9_SH||phone==K9_F||phone==K9_TH||phone==K9_V||phone==K9_Z||phone==K9_ZH||phone==K9_HH){
  a.noise=k9_unit(ms/4)*k9_unit((duration-ms)/7);a.voiced=a.noise;
 }else if(phone==K9_M||phone==K9_N||phone==K9_NG){a.voiced=.8f*k9_unit(ms/6);a.noise=.1f;}
 else if(phone==K9_L||phone==K9_R||phone==K9_W||phone==K9_Y){a.voiced=k9_unit(ms/5);a.noise=.1f;}
 return a;
}
#endif
