/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include "library.h"
#include "face.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static uint16_t full[240*240],bands[240*240];
int main(void){
 k9_song song={0};song.bpm=120;song.ticks=12;song.count=1;song.events[0]=(k9_event){0,12,K9_AA,60,90,1,0};
 const k9_song *list[3]={&song,&song,&song};k9_engine e;k9_init(&e);float audio[512];assert(!k9_playlist(&e,list,0));assert(!k9_playlist(&e,list,9));assert(k9_playlist(&e,list,3));
 unsigned steps=0;while(e.playing&&steps++<100)k9_render(&e,audio,256);assert(!e.playing&&e.playlist_index==2&&steps<100);
 assert(k9_playlist(&e,list,3));e.loop=1;for(steps=0;steps<100;steps++)k9_render(&e,audio,256);assert(e.playing);k9_stop(&e);assert(!e.playing&&!e.velocity);
 e.loop=0;e.tempo_override=240;k9_start(&e,&song);steps=0;while(e.playing&&steps++<100)k9_render(&e,audio,256);assert(steps<9);
 for(unsigned emotion=0;emotion<4;emotion++)for(unsigned mouth=0;mouth<6;mouth++){k9_face f={0};f.mouth=mouth;f.open=20;f.cheek=emotion;f.blink=75;f.neck=2;k9_face_render(full,0,240,&f);for(unsigned y=0;y<240;y+=40)k9_face_render(bands+y*240,y,40,&f);assert(!memcmp(full,bands,sizeof full));}
 k9_arrangement a={113,3,1,1,{2,0,1,3,4,5,6,7}},out;uint8_t bytes[29];assert(k9_arrangement_write(bytes,&a)==29);assert(k9_arrangement_read(bytes,29,&out));assert(out.tempo==113&&out.slots[0]==2);bytes[19]=2;assert(!k9_arrangement_read(bytes,29,&out));a.slots[4]=8;assert(!k9_arrangement_write(bytes,&a));
 puts("PASS standalone chain/end/loop/tempo/stop, shared full/banded face across expressions and mouths, arrangement bounds/corruption");return 0;
}
