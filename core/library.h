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
int k9_score_preset(const uint8_t *, uint16_t, k9_preset *);
int k9_score_update_preset(uint8_t *, uint16_t, const k9_preset *);
typedef struct {uint16_t tempo;uint8_t count,loop,active,slots[8];} k9_arrangement;
int k9_arrangement_read(const uint8_t *,uint16_t,k9_arrangement *);
uint16_t k9_arrangement_write(uint8_t *,const k9_arrangement *);
#endif
