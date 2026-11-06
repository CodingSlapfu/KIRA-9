/* SPDX-License-Identifier: MIT */
#include "../core/face.h"
#include "../core/kira.h"
#include "../core/library.h"
#include "../factory/songs.h"
static k9_engine web_engine;
static k9_song web_song;
static uint8_t web_bytes[K9_WIRE_MAX];
static float web_audio[2048];
__attribute__((visibility("default"))) void web_init(void) {
  k9_init(&web_engine);
}
__attribute__((visibility("default"))) uint8_t *web_input(void) {
  return web_bytes;
}
__attribute__((visibility("default"))) int web_load(unsigned n) {
  if (n > K9_WIRE_MAX || !k9_decode(&web_song, web_bytes, n))
    return 0;
  k9_start(&web_engine,&web_song);k9_preset p;if(k9_score_preset(web_bytes,(uint16_t)n,&p)){web_engine.voice=p.voice;web_engine.style=p.style;web_engine.emotion=p.emotion;web_engine.morph=(float)p.morph*.01f;web_engine.breath=(float)p.breath*.005f;web_engine.vibrato=(float)p.vibrato*.01f;web_engine.glide=.0002f+(float)p.glide*.00005f;web_engine.harmony=p.harmony;web_engine.expression=(float)p.expression/127.0f;}
  return 1;
}
__attribute__((visibility("default"))) void web_demo(unsigned n) {
  if (n < 8)
    k9_start(&web_engine, &factory_songs[n]);
}
__attribute__((visibility("default"))) void web_stop(void) {
  k9_stop(&web_engine);
}
__attribute__((visibility("default"))) void web_voice(unsigned v,
                                                      unsigned style) {
  web_engine.voice = v % 7;
  web_engine.style = style % 8;
  web_engine.breath = (v == 2 ? .3f : v == 3 ? .15f : .03f);
  web_engine.vibrato = style == 5 ? .8f : .2f;
}
__attribute__((visibility("default"))) float *web_render(unsigned n) {
  if (n > 1024)
    n = 1024;
  k9_render(&web_engine, web_audio, n);
  return web_audio;
}
__attribute__((visibility("default"))) unsigned web_viseme(void) {
  return web_engine.viseme;
}
__attribute__((visibility("default"))) unsigned web_tick(void) {
  return web_engine.tick;
}
__attribute__((visibility("default"))) unsigned web_playing(void) {
  return web_engine.playing;
}

static uint16_t web_portrait[240 * 240];
__attribute__((visibility("default"))) void
web_parameters(unsigned morph, unsigned breath, unsigned vibrato,
               unsigned glide, int harmony, unsigned expression,
               unsigned emotion) {
  web_engine.morph = (float)(morph > 100 ? 100 : morph) * .01f;
  web_engine.breath = (float)(breath > 100 ? 100 : breath) * .005f;
  web_engine.vibrato = (float)(vibrato > 100 ? 100 : vibrato) * .01f;
  web_engine.glide = .0002f + (float)(glide > 100 ? 100 : glide) * .00005f;
  web_engine.harmony = (int8_t)(harmony < -12  ? -12
                                : harmony > 12 ? 12
                                               : harmony);
  web_engine.expression = (float)(expression > 127 ? 127 : expression) / 127.0f;
  web_engine.emotion = emotion % 4;
}
__attribute__((visibility("default"))) uint16_t *
web_face(unsigned ms, unsigned emotion, unsigned twitch) {
  k9_face f = k9_face_at(&web_engine, ms, (uint8_t)emotion, (uint8_t)twitch);
  k9_face_render(web_portrait, 0, 240, &f);
  return web_portrait;
}
__attribute__((visibility("default"))) unsigned web_pose(void) {
  k9_face f = k9_face_at(&web_engine, 0, 0, 0);
  return (unsigned)f.mouth | ((unsigned)f.open << 8);
}
__attribute__((visibility("default"))) uint16_t *
web_face_pose(unsigned pose, unsigned ms, unsigned emotion, unsigned twitch) {
  k9_face f = k9_face_at(&web_engine, ms, (uint8_t)emotion, (uint8_t)twitch);
  f.mouth = (uint8_t)pose;
  f.open = (uint16_t)((pose >> 8) & 255);
  f.jaw = (int8_t)(f.open / 4);
  k9_face_render(web_portrait, 0, 240, &f);
  return web_portrait;
}
