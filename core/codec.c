/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include "memory.h"

uint32_t k9_crc(const uint8_t *p, size_t n) {
  uint32_t c = ~0u;
  size_t i;
  for (i = 0; i < n; ++i) {
    unsigned j;
    c ^= p[i];
    for (j = 0; j < 8; ++j)
      c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
  }
  return ~c;
}
static void put16(uint8_t *p, uint16_t v) {
  p[0] = (uint8_t)v;
  p[1] = (uint8_t)(v >> 8);
}
static void put32(uint8_t *p, uint32_t v) {
  put16(p, (uint16_t)v);
  put16(p + 2, (uint16_t)(v >> 16));
}
static uint16_t get16(const uint8_t *p) {
  return (uint16_t)(p[0] | (uint16_t)p[1] << 8);
}
static uint32_t get32(const uint8_t *p) {
  return get16(p) | (uint32_t)get16(p + 2) << 16;
}

int k9_song_validate(const k9_song *s) {
  unsigned i;
  uint32_t end = 0;
  if (!s || !s->count || s->count > K9_MAX_EVENTS || s->bpm < 30 ||
      s->bpm > 300 || !s->ticks || s->ticks > 96u * 60u * 30u)
    return 0;
  for (i = 0; i < s->count; ++i) {
    const k9_event *v = &s->events[i];
    if (!v->duration || v->tick < end || v->phone >= K9_NPHONE ||
        v->note > 127 || v->velocity > 127 || v->stress > 2 || v->reserved ||
        v->tick > s->ticks || v->duration > s->ticks - v->tick)
      return 0;
    end = v->tick + v->duration;
  }
  return 1;
}
size_t k9_encode(const k9_song *s, uint8_t *out, size_t cap) {
  unsigned i;
  size_t n;
  if (!k9_song_validate(s))
    return 0;
  n = 24u + 12u * s->count;
  if (cap < n)
    return 0;
  memset(out, 0, n);
  memcpy(out, "K9S1", 4);
  put16(out + 4, 1);
  put16(out + 6, s->count);
  put16(out + 8, s->bpm);
  put32(out + 12, s->ticks);
  put32(out + 16, (uint32_t)n);
  for (i = 0; i < s->count; ++i) {
    const k9_event *v = &s->events[i];
    uint8_t *p = out + 24 + 12 * i;
    put32(p, v->tick);
    put16(p + 4, v->duration);
    p[6] = v->phone;
    p[7] = v->note;
    p[8] = v->velocity;
    p[9] = v->stress;
  }
  put32(out + 20, k9_crc(out + 24, n - 24) ^ k9_crc(out, 20));
  return n;
}
/* Both versions are checked completely before any live destination is touched.
 * S2 uses delta ticks and retains editable UTF-8 project metadata after the
 * score. */
int k9_decode(k9_song *dst, const uint8_t *in, size_t n) {
  unsigned i, stride, compact;
  uint16_t count, metadata;
  uint32_t tick = 0, end = 0, duration, total_ticks;
  if (n < 24 || n > K9_WIRE_MAX || get32(in + 16) != n)
    return 0;
  compact = !memcmp(in, "K9S2", 4) && get16(in + 4) == 2;
  if (!compact && (memcmp(in, "K9S1", 4) || get16(in + 4) != 1))
    return 0;
  count = get16(in + 6);
  metadata = get16(in + 10);
  stride = compact ? 8u : 12u;
  total_ticks = get32(in + 12);
  if (!count || count > K9_MAX_EVENTS || (!compact && metadata) ||
      n != 24u + stride * count + metadata || get16(in + 8) < 30 ||
      get16(in + 8) > 300 || !total_ticks || total_ticks > 96u * 60u * 30u ||
      get32(in + 20) != (k9_crc(in + 24, n - 24) ^ k9_crc(in, 20)))
    return 0;
  for (i = 0; i < count; ++i) {
    const uint8_t *p = in + 24 + stride * i;
    if (compact) {
      tick += get16(p);
      duration = get16(p + 2);
      p += 4;
    } else {
      tick = get32(p);
      duration = get16(p + 4);
      p += 6;
    }
    if (!duration || tick < end || tick > total_ticks ||
        duration > total_ticks - tick || p[0] >= K9_NPHONE || p[1] > 127 ||
        p[2] > 127 || p[3] > 2 || (!compact && get16(p + 4)))
      return 0;
    end = tick + duration;
  }
  memset(dst, 0, sizeof(*dst));
  dst->count = count;
  dst->bpm = get16(in + 8);
  dst->ticks = total_ticks;
  tick = 0;
  for (i = 0; i < count; ++i) {
    const uint8_t *p = in + 24 + stride * i;
    k9_event *v = &dst->events[i];
    if (compact) {
      tick += get16(p);
      v->duration = get16(p + 2);
      p += 4;
    } else {
      tick = get32(p);
      v->duration = get16(p + 4);
      p += 6;
    }
    v->tick = tick;
    v->phone = p[0];
    v->note = p[1];
    v->velocity = p[2];
    v->stress = p[3];
  }
  return 1;
}
/* Opaque editable library records. Audio uses compiled events/voice parameters;
 * project editors validate the JSON schema before applying this UTF-8 payload.
 */
int k9_document_valid(const uint8_t *p, size_t n, uint8_t kind) {
  if (n < 17 || n > 3840 || memcmp(p, "K9D1", 4) || p[4] != 1 || p[5] != kind ||
      p[6] || p[7] || get32(p + 8) != n - 16 ||
      get32(p + 12) != k9_crc(p + 16, n - 16))
    return 0;
  return p[16] == '{' && p[n - 1] == '}';
}
