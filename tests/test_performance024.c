/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../core/kira.h"
#include "../factory/songs.h"

static float a[512], b[512];

static void check_demo(unsigned index) {
  k9_engine music, dry;
  const k9_song *song = &factory_songs[index];
  uint32_t end = ((song->ticks + 383u) / 384u) * 384u;
  uint32_t last = 0, wraps = 0;
  double backing_energy = 0, voice_energy = 0;
  k9_init(&music);
  k9_init(&dry);
  dry.music_level = 0;
  k9_start_demo(&music, song, index);
  k9_start_demo(&dry, song, index);
  while (wraps < 2) {
    k9_render(&music, a, 256);
    k9_render(&dry, b, 256);
    assert(music.playing && dry.playing && music.tick == dry.tick);
    assert(music.viseme == dry.viseme && music.next == dry.next);
    assert(music.tick <= end);
    if (music.tick < last)
      wraps++;
    last = music.tick;
    for (unsigned i = 0; i < 512; i++) {
      double delta = a[i] - b[i];
      backing_energy += delta * delta;
      voice_energy += b[i] * b[i];
      assert(isfinite(a[i]) && fabsf(a[i]) <= .940001f);
    }
  }
  assert(backing_energy > 1 && voice_energy > 1);
  music.music_level = 0;
  for (unsigned i = 0; i < 20; i++)
    k9_render(&music, a, 256);
  assert(music.music_gain < .0001f && music.playing);
  printf("%s | %u BPM | %u bars | 2 loops | backing/vocal energy %.2f\n",
         factory_names[index], song->bpm, end / 384, backing_energy / voice_energy);
}

int main(void) {
  for (unsigned i = 0; i < 8; i++)
    check_demo(i);
  k9_engine e;
  k9_init(&e);
  e.perfect_key = 1;
  e.external = 2;
  k9_midi(&e, 8, 0x90, 61, 100);
  assert(e.note == 60 && e.live_note == 61 && e.velocity == 100);
  k9_midi(&e, 2, 0x80, 61, 0);
  assert(e.velocity == 100);
  k9_midi(&e, 8, 0x80, 61, 0);
  assert(e.velocity == 0);
  k9_midi(&e, 8, 0x90, 61, 100);
  k9_disconnect(&e, 8);
  assert(e.velocity == 0 && e.live_note == 255);

  k9_start_demo(&e, &factory_songs[0], 0);
  k9_midi(&e, 2, 0xfa, 0, 0);
  for (unsigned i = 0; i < 961; i++) {
    k9_clock_at(&e, 2, e.sample);
    k9_render(&e, a, 256);
  }
  assert(e.playing && e.tick < 20 && e.demo_clock_origin == 3840);
  k9_disconnect(&e, 8);
  assert(e.playing && e.source == 2);
  k9_disconnect(&e, 2);
  assert(!e.playing && e.source == 255);

  k9_engine wet, dry;
  k9_init(&wet);
  k9_init(&dry);
  wet.tuning = 3;
  wet.tune_strength = wet.tune_speed = 100;
  for (unsigned i = 0; i < 4; i++)
    wet.fx_mix[i] = 100;
  k9_note(&wet, K9_AA, 69, 110);
  k9_note(&dry, K9_AA, 69, 110);
  double effect = 0, stereo = 0;
  for (unsigned i = 0; i < 100; i++) {
    k9_render(&wet, a, 256);
    k9_render(&dry, b, 256);
    for (unsigned j = 0; j < 512; j += 2) {
      effect += fabsf(a[j] - b[j]);
      stereo += fabsf(a[j] - a[j + 1]);
      assert(isfinite(a[j]) && fabsf(a[j]) <= .940001f);
    }
  }
  assert(effect > 1 && stereo > 1);
  k9_stop(&wet);
  assert(!wet.fx_valid && !wet.fx_left && !wet.fx_right);
  puts("PASS raw MIDI key ownership, BLE source loss, external demo looping, FX routing and bounded output");
}
