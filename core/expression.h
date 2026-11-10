/* SPDX-License-Identifier: MIT; original bounded performance contours.
 * No recorded material, singer model, additional state, heap or libm. */
#ifndef K9_EXPRESSION_H
#define K9_EXPRESSION_H
typedef struct { float level, air, openness, vibrato; uint32_t period; } k9_expression;
static float k9_expression_unit(float x) { return x<0?0:x>1?1:x; }
static k9_expression k9_expression_at(unsigned style, float age, float progress,
                                     int timed, int connected, int voiced) {
  /* Accent settles into a held tone; long vowels bloom after the initial
   * consonant. Timed phrase endings relax without shortening a connected note.
   * Live notes use elapsed time only and never invent a scheduled release. */
  static const float accent[8]={.11f,.14f,.18f,.035f,.015f,.065f,.09f,0};
  static const float bloom[8]={.035f,.015f,.02f,.09f,.12f,.115f,.075f,0};
  static const float air[8]={.012f,.006f,.008f,.045f,.055f,.02f,.04f,0};
  static const uint32_t periods[8]={8018,7350,6682,9188,9800,7875,8647,8820};
  unsigned s=style%8u;
  float settle=1-k9_expression_unit(age/5292.f), swell=k9_expression_unit((age-4410.f)/17640.f);
  float end=timed&&!connected?k9_expression_unit((progress-.78f)/.22f):0;
  k9_expression x={1,0,0,1,periods[s]};
  if(voiced){
    x.level=1+accent[s]*settle+bloom[s]*swell-.10f*end;
    x.air=air[s]*(.3f+.7f*swell+end);
    x.openness=-.018f*settle+.022f*swell;
    x.vibrato=.65f+.35f*swell;
  }
  return x;
}
/* Smooth signed oscillator: continuous value AND slope at turning points.
 * Range [-1,1], zero mean, no cumulative pitch drift or integer wrap state. */
static float k9_vibrato_wave(uint32_t phase,uint32_t period) {
  float t=(float)(phase%period)/(float)period;
  float u=t<.5f?t*2.f:(t-.5f)*2.f;
  float q=u*u*(3.f-2.f*u);
  return t<.5f?-1.f+2.f*q:1.f-2.f*q;
}
#endif
