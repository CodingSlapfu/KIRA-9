/* SPDX-License-Identifier: MIT; original bounded consonant-cue experiment. */
#ifndef K9_CUES_H
#define K9_CUES_H
typedef struct {
  float low, mid;
  unsigned release_sample, voice_sample, phone_sample;
  unsigned previous;
  unsigned pending;
} cue_state;
typedef struct { float voice, direct; unsigned bypass; } cue_signal;
#endif
