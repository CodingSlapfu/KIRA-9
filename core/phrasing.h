/* SPDX-License-Identifier: MIT; bounded vowel timing, no recorded samples. */
#ifndef K9_PHRASING_H
#define K9_PHRASING_H
/* Hold a diphthong's nucleus, then complete the off-glide in at most 120 ms.
 * Short notes devote 35% to the movement. No libm/double or unbounded state. */
static float k9_diphthong_progress(float age, uint32_t frames) {
  float duration=(float)frames, travel=duration*.35f;
  if (travel>5292.0f) travel=5292.0f;
  if (travel<1.0f) travel=1.0f;
  float x=(age-(duration-travel))/travel;
  if (x<0) x=0;
  if (x>1) x=1;
  return x*x*(3.0f-2.0f*x);
}
#endif
