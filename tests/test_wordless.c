#include "kira.h"
#include <assert.h>
#include <stdio.h>
static float pcm[512];
int main(void){k9_engine e;for(unsigned mode=0;mode<K9_NMODES;mode++){k9_init(&e);e.vocal_mode=mode;k9_midi(&e,0,0x90,60,100);assert(e.velocity==100);if(mode==K9_HUM){assert(e.phone==K9_M);k9_render(&e,pcm,256);k9_face f=k9_face_at(&e,200,1,1);assert(f.open==0&&f.jaw==0);}if(mode==K9_SCAT){assert(e.phone==K9_B);for(int i=0;i<8;i++)k9_render(&e,pcm,256);assert(e.phone==K9_AA);}k9_midi(&e,0,0x80,60,0);assert(!e.velocity);for(int i=0;i<10;i++)k9_render(&e,pcm,256);assert(!e.live_transition);k9_stop(&e);assert(!e.velocity&&!e.live_transition);}puts("PASS five live/MIDI modes, scat consonant sustain, closed hum face, note-off/STOP");}
