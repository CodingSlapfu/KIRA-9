/* SPDX-License-Identifier: MIT; independent firmware regression gaps only. */
#include "kira.h"
#include "face.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static float pcm[512];
static void render(k9_engine *e,unsigned n){while(n){unsigned c=n>256?256:n;k9_render(e,pcm,c);n-=c;}}
static k9_song song;
int main(void){
 song.bpm=120;song.count=1;song.ticks=100000;song.events[0]=(k9_event){0,65535,K9_AH,60,100,1,0};
 k9_engine e;k9_init(&e);e.song=&song;e.external=2;k9_midi(&e,2,0xfa,0,0);assert(e.source==2&&e.playing);render(&e,K9_RATE*2+256);assert(!e.playing);assert(e.source==255);k9_midi(&e,4,0xfa,0,0);assert(e.source==4&&e.playing);
 k9_midi(&e,2,0xf8,0,0);assert(e.clocks==0);k9_midi(&e,4,0xf8,0,0);assert(e.clocks==1);
 k9_midi(&e,4,0xfe,0,0);render(&e,K9_RATE/3+256);assert(!e.playing&&!e.sense_armed&&e.source==255);k9_midi(&e,2,0xfa,0,0);render(&e,K9_RATE/3+256);assert(e.playing&&e.source==2);
 k9_init(&e);e.song=&song;e.external=1;e.source=4;k9_midi(&e,4,0xfa,0,0);render(&e,K9_RATE*2+256);assert(!e.playing&&e.source==4);k9_midi(&e,2,0xfa,0,0);assert(!e.playing);k9_midi(&e,4,0xfa,0,0);assert(e.playing);
 /* Sample counter wrap does not invent a two-second clock loss. */
 e.sample=0xfffffff0u;e.last_clock=e.sample;render(&e,64);assert(e.playing);k9_midi(&e,4,0xf8,0,0);assert(e.clocks==1);
 /* A silent labiodental pose closes rather than forcing visible teeth. */
 static uint16_t a[240*240],b[240*240];k9_face p={0};k9_face_render(a,0,240,&p);p.mouth=5;k9_face_render(b,0,240,&p);assert(!memcmp(a,b,sizeof a));
 k9_init(&e);e.phone=K9_F;e.viseme=5;e.level=0;k9_face f=k9_face_at(&e,100,0,0);assert(f.mouth==0&&f.open==0);
 /* Face snapshots, all emotions and twitch phases, never mutate audio state. */
 k9_note(&e,K9_P,60,100);render(&e,256);k9_engine before=e;
 for(unsigned emotion=0;emotion<4;emotion++)for(unsigned ms=17001;ms<17121;ms+=20){f=k9_face_at(&e,ms,emotion,1);assert(f.open<=30);assert(!memcmp(&e,&before,sizeof e));}
 puts("PASS new auto clock/active-sensing recovery, source isolation, fixed binding, wrap, silent lip closure and immutable face snapshots");return 0;
}
