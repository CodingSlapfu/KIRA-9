/* SPDX-License-Identifier: MIT */
#ifndef K9_LIBRARY_H
#define K9_LIBRARY_H
#include "kira.h"
/* Fixed compiled preset parameters plus optional editable JSON
 * names/annotations. */
typedef struct {
  uint8_t voice, style, emotion, morph, breath, vibrato, glide;
  int8_t harmony;
  uint8_t expression, reserved[7];
} k9_preset;
int k9_preset_valid(const k9_preset *);
int k9_voicebank_read(const uint8_t *, uint16_t, k9_preset[8]);
uint16_t k9_voicebank_write(uint8_t *, uint16_t, const k9_preset[8]);
#endif
