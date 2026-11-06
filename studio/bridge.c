/* SPDX-License-Identifier: MIT */
#include "../core/kira.h"
#include "../factory/songs.h"
static k9_engine web_engine;static k9_song web_song;static uint8_t web_bytes[K9_WIRE_MAX];static float web_audio[2048];
__attribute__((visibility("default"))) void web_init(void){k9_init(&web_engine);}
__attribute__((visibility("default"))) uint8_t *web_input(void){return web_bytes;}
__attribute__((visibility("default"))) int web_load(unsigned n){if(n>K9_WIRE_MAX||!k9_decode(&web_song,web_bytes,n))return 0;k9_start(&web_engine,&web_song);return 1;}
__attribute__((visibility("default"))) void web_demo(unsigned n){if(n<8)k9_start(&web_engine,&factory_songs[n]);}
__attribute__((visibility("default"))) void web_stop(void){k9_stop(&web_engine);}
__attribute__((visibility("default"))) void web_voice(unsigned v,unsigned style){web_engine.voice=v%7;web_engine.style=style%8;web_engine.breath=(v==2?.3f:v==3?.15f:.03f);web_engine.vibrato=style==5?.8f:.2f;}
__attribute__((visibility("default"))) float *web_render(unsigned n){if(n>1024)n=1024;k9_render(&web_engine,web_audio,n);return web_audio;}
__attribute__((visibility("default"))) unsigned web_viseme(void){return web_engine.viseme;}
__attribute__((visibility("default"))) unsigned web_tick(void){return web_engine.tick;}
__attribute__((visibility("default"))) unsigned web_playing(void){return web_engine.playing;}
