/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
static k9_song song,decoded;static uint8_t wire[K9_WIRE_MAX];
int main(void){k9_engine a,b;float x[512],y[512];size_t n,i;double energy=0;clock_t start;
 song.count=3;song.bpm=120;song.ticks=96;song.events[0]=(k9_event){0,12,K9_HH,69,90,0,0};song.events[1]=(k9_event){12,60,K9_EH,69,90,1,0};song.events[2]=(k9_event){72,24,K9_L,69,90,0,0};
 assert(k9_song_validate(&song));n=k9_encode(&song,wire,sizeof wire);assert(n==60&&k9_decode(&decoded,wire,n));assert(memcmp(&decoded,&song,sizeof song)==0);
 for(i=0;i<n;i++){uint8_t old=wire[i];wire[i]^=1;memset(&decoded,0xa5,sizeof decoded);assert(!k9_decode(&decoded,wire,n));assert(decoded.count==0xa5a5);wire[i]=old;}
 for(i=0;i<n;i++)assert(!k9_decode(&decoded,wire,i));assert(!k9_decode(&decoded,wire,n+1));
 song.events[1].tick=1;assert(!k9_song_validate(&song));song.events[1].tick=12;
 k9_init(&a);k9_start(&a,&song);b=a;
 for(i=0;i<100;i++){k9_face f=k9_face_at(&a,(uint32_t)i*90,2,2);(void)f;k9_render(&a,x,256);k9_render(&b,y,256);assert(memcmp(x,y,sizeof x)==0);for(n=0;n<512;n++){assert(isfinite(x[n]));assert(fabs(x[n])<=.951);energy+=x[n]*x[n];}}
 assert(energy>1);k9_stop(&a);for(i=0;i<100;i++)k9_render(&a,x,256);assert(fabs(x[510])<.00001);
 k9_init(&a);a.external=1;a.source=1;a.song=&song;k9_midi(&a,0,0xfa,0,0);assert(!a.playing);k9_midi(&a,1,0xfa,0,0);assert(a.playing);k9_midi(&a,0,0xf8,0,0);assert(a.tick==0);k9_midi(&a,1,0xf8,0,0);assert(a.tick==4);k9_midi(&a,1,0x90,60,100);assert(a.note==60&&a.velocity==100);k9_midi(&a,1,0x90,60,0);assert(!a.velocity);k9_midi(&a,1,0x90,60,100);k9_midi(&a,1,0xb0,123,0);assert(!a.velocity&&!a.playing);
 k9_init(&a);start=clock();for(i=0;i<4000;i++){k9_note(&a,(uint8_t)(1+i%(K9_NPHONE-1)),60+(i%24),110);k9_render(&a,x,256);for(n=0;n<512;n++)assert(isfinite(x[n]));}printf("PASS codec corruption/truncation, transactional decode, stop tails, clock authority, panic, animation/audio parity, all-phoneme stability; host 4000 blocks %.3fs (not device timing)\n",(double)(clock()-start)/CLOCKS_PER_SEC);return 0;}
