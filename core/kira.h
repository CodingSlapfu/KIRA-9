/* SPDX-License-Identifier: MIT */
#ifndef KIRA_H
#define KIRA_H
#include <stddef.h>
#include <stdint.h>
#define K9_RATE 44100u
#define K9_MAX_EVENTS 512u
#define K9_WIRE_MAX (24u + 12u * K9_MAX_EVENTS)
/* ARPAbet inventory, stable file-format IDs. */
enum {
  K9_SIL,
  K9_AA,
  K9_AE,
  K9_AH,
  K9_AO,
  K9_AW,
  K9_AY,
  K9_B,
  K9_CH,
  K9_D,
  K9_DH,
  K9_EH,
  K9_ER,
  K9_EY,
  K9_F,
  K9_G,
  K9_HH,
  K9_IH,
  K9_IY,
  K9_JH,
  K9_K,
  K9_L,
  K9_M,
  K9_N,
  K9_NG,
  K9_OW,
  K9_OY,
  K9_P,
  K9_R,
  K9_S,
  K9_SH,
  K9_T,
  K9_TH,
  K9_UH,
  K9_UW,
  K9_V,
  K9_W,
  K9_Y,
  K9_Z,
  K9_ZH,
  K9_NPHONE
};
enum { K9_LYRICS, K9_VOCALISE, K9_SCAT, K9_HUM, K9_VOCABLES, K9_NMODES };
typedef struct {
  uint32_t tick;
  uint16_t duration;
  uint8_t phone, note, velocity, stress;
  uint16_t reserved;
} k9_event;
typedef struct {
  uint16_t count, bpm;
  uint32_t ticks;
  k9_event events[K9_MAX_EVENTS];
} k9_song;
typedef struct {
  float a[3], r[3], gain[3], noise;
  uint8_t viseme, voiced;
} k9_phone;
extern const k9_phone k9_phones[K9_NPHONE];
extern const k9_phone k9_voice_phones[7][K9_NPHONE];
extern const char *const k9_phone_names[K9_NPHONE];
extern const float k9_pitch[128];
typedef struct {
  uint8_t voice, style, emotion, morph, breath, vibrato, glide;
  int8_t harmony;
  uint8_t expression, reserved[7];
} k9_preset;
/* One owner (audio thread) mutates engine. UI uses bounded command handoff. */
typedef struct {
  const k9_song *song;
  uint32_t sample, tick, clock_phase, rng, event_end;
  uint32_t phone_start, phone_end, lfo, phone_sample, phone_frames, clock_tick,
      last_message;
  float bend, clock_interval;
  float flow_last, noise_last, hphase, hflow_last, hz1[3], hz2[3], morph,
      expression;
  int8_t harmony;
  uint8_t vocal_mode, vocal_family, vocal_step, live_vowel;
  uint32_t live_transition;
  uint8_t sustain, sustain_source, deferred_off;
  uint32_t vibrato_start;
  uint8_t emotion, external_melody, live_note, live_velocity, live_source,
      sense_armed, sense_source;
  const k9_song *playlist[8];
  const k9_preset *playlist_profiles[8];
  uint8_t playlist_count, playlist_index;
  uint16_t tempo_override;
  uint8_t loop;
  uint16_t next;
  uint8_t playing, phone, note, velocity, voice, style, viseme, source,
      external;
  float phase, level, freq, z1[3], z2[3], a[3], r[3], gain[3], noise, breath,
      vibrato, glide;
  uint32_t clocks, last_clock, late_clocks;
} k9_engine;
uint32_t k9_crc(const uint8_t *p, size_t n);
int k9_song_validate(const k9_song *s);
size_t k9_encode(const k9_song *s, uint8_t *out, size_t cap);
int k9_decode(k9_song *dst, const uint8_t *in, size_t len);
int k9_document_valid(const uint8_t *p, size_t n, uint8_t kind);
void k9_init(k9_engine *e);
void k9_start(k9_engine *e, const k9_song *s);
void k9_stop(k9_engine *e);
int k9_playlist(k9_engine *, const k9_song *const *, unsigned);
void k9_apply_preset(k9_engine *, const k9_preset *);
void k9_perform(k9_engine *, uint8_t note, uint8_t velocity);
void k9_note(k9_engine *e, uint8_t phone, uint8_t note, uint8_t velocity);
void k9_render(k9_engine *e, float *stereo, uint32_t n);
void k9_midi(k9_engine *e, uint8_t source, uint8_t status, uint8_t d1,
             uint8_t d2);
/* Clock timestamp is in engine sample units; delivery delay must not change tempo. */
void k9_clock_at(k9_engine *e, uint8_t source, uint32_t sample);
/* UI animation snapshot. Does not mutate audio state. */
typedef struct {
  uint8_t mouth, blink;
  int8_t gaze, jaw, cheek, neck, brow;
  uint8_t lid;
  uint16_t open;
} k9_face;
k9_face k9_face_at(const k9_engine *e, uint32_t ms, uint8_t emotion,
                   uint8_t twitch);
#endif
