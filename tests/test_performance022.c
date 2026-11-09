#include "kira.h"
#include "phrasing.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static float pcm[512];
static void render(k9_engine *e,unsigned frames){while(frames){unsigned n=frames>256?256:frames;k9_render(e,pcm,n);for(unsigned i=0;i<n*2;i++)assert(isfinite(pcm[i])&&fabsf(pcm[i])<=.94f);frames-=n;}}
int main(void){
 k9_engine e;k9_init(&e);e.vocal_mode=K9_VOCALISE;k9_midi(&e,1,0x90,60,100);assert(e.freq==k9_pitch[60]);render(&e,12000);uint32_t onset=e.vibrato_start;k9_midi(&e,1,0x90,64,100);assert(e.vibrato_start==onset);assert(e.freq!=k9_pitch[64]);
 k9_midi(&e,1,0xb0,64,127);k9_midi(&e,1,0x80,64,0);assert(e.velocity&&e.deferred_off);k9_midi(&e,2,0xb0,64,0);assert(e.velocity&&e.sustain);k9_midi(&e,1,0xb0,64,0);assert(!e.velocity&&!e.sustain&&!e.live_transition);
 e.vocal_mode=K9_SCAT;k9_midi(&e,1,0x90,60,100);assert(e.live_transition);k9_midi(&e,1,0x80,60,0);assert(!e.live_transition);render(&e,3000);assert(!e.velocity);
 e.vocal_mode=K9_HUM;k9_midi(&e,1,0x90,60,100);k9_midi(&e,1,0xb0,64,127);k9_midi(&e,1,0x80,60,0);render(&e,1000);k9_face f=k9_face_at(&e,500,2,0);assert(!f.open&&!f.jaw&&f.lid==3);k9_midi(&e,1,0xb0,120,0);assert(!e.velocity&&!e.sustain&&!e.deferred_off);
 k9_init(&e);e.external=1;e.source=2;e.sample=2200;k9_clock_at(&e,2,1000);k9_clock_at(&e,2,1000);k9_clock_at(&e,2,3000);k9_clock_at(&e,1,1919);assert(e.clocks==1);k9_clock_at(&e,2,1919);assert(e.clocks==2&&e.clock_tick==8);e.sample=K9_RATE*3u;k9_clock_at(&e,2,2000);assert(e.clocks==2);
 assert(k9_diphthong_progress(22050,44100)==0);assert(k9_diphthong_progress(44100,44100)==1);assert(k9_diphthong_progress(800,1000)>0&&k9_diphthong_progress(800,1000)<1);
 k9_song s={.count=1,.bpm=120,.ticks=384,.events={{0,384,K9_AY,60,100,1,0}}};k9_init(&e);k9_start(&e,&s);render(&e,22050);assert(e.viseme==k9_phones[K9_AA].viseme);render(&e,65000);assert(e.viseme==k9_phones[K9_IY].viseme);
 puts("PASS first-note tuning, legato vibrato continuity, source-owned sustain/panic, cancelled scat onset, closed hum expression, duplicate/future/stale clock rejection, late diphthong/viseme timing and bounded PCM");
}
