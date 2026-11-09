#include "kira.h"
#include <assert.h>
#include <stdio.h>
static float out[512];
int main(void){
 k9_song s={.count=1,.bpm=120,.ticks=12,.events={{0,12,K9_AA,60,90,1,0}}};
 const k9_song *list[]={&s,&s};k9_preset a={.voice=0,.style=0,.expression=110},b={.voice=3,.style=4,.emotion=2,.expression=75,.glide=65};
 k9_engine e;k9_init(&e);assert(k9_playlist(&e,list,2));e.playlist_profiles[0]=&a;e.playlist_profiles[1]=&b;k9_apply_preset(&e,&a);
 unsigned n=0;while(e.playlist_index==0&&n++<10000)k9_render(&e,out,1);
 assert(e.playing&&e.playlist_index==1&&e.voice==3&&e.style==4&&e.emotion==2);assert(e.expression>.59f&&e.expression<.60f);
 e.loop=1;while(e.playlist_index==1&&n++<20000)k9_render(&e,out,1);assert(e.playing&&e.voice==0&&e.style==0);
 k9_stop(&e);assert(!e.velocity&&!e.playing);k9_start(&e,&s);assert(!e.playlist_count&&!e.playlist_profiles[0]);
 puts("PASS sample-boundary section presets, expression/emotion, loop restore, STOP and playlist profile isolation");
}
