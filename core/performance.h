/* SPDX-License-Identifier: MIT */
#ifndef K9_PERFORMANCE_H
#define K9_PERFORMANCE_H

/* Factory lyrics and melody share a C pentatonic pitch set. Each row is
 * a four-bar harmonic plan, with a separate pulse and percussion pattern. */
static const struct {
  uint8_t roots[4];
  uint16_t bass, drums;
  float pad;
} demo_arrangements[] = {
    {{0, 9, 5, 7}, 0x1111, 0x1111, .035f},
    {{9, 5, 0, 7}, 0x0101, 0x0401, .044f},
    {{0, 7, 9, 5}, 0x5555, 0x1111, .021f},
    {{5, 0, 9, 7}, 0x0101, 0x0001, .046f},
    {{9, 0, 5, 7}, 0x5251, 0x1111, .029f},
    {{0, 5, 9, 7}, 0x0001, 0x0001, .041f},
    {{5, 9, 0, 7}, 0x2141, 0x1001, .039f},
    {{9, 7, 5, 0}, 0x4545, 0x1511, .025f},
};

static float triangle(float p) {
  return 1.0f - 4.0f * absolute(p - .5f);
}

static float oscillator(float *phase, float step) {
  *phase += step;
  if (*phase >= 1.0f)
    *phase -= 1.0f;
  return triangle(*phase);
}

static float demo_backing(k9_engine *e, uint32_t tick, float noise) {
  if (!e->demo || !e->playing)
    return 0;
  unsigned plan = e->demo - 1u;
  if (tick != e->backing_tick) {
    e->backing_tick = tick;
    if (tick % 24u == 0) {
      unsigned step = (tick / 24u) & 15u;
      unsigned root = demo_arrangements[plan].roots[(tick / 384u) & 3u];
      unsigned third = root == 9u ? 3u : 4u;
      e->backing_hz[0] = k9_pitch[36u + root] / K9_RATE;
      e->backing_hz[1] = k9_pitch[48u + root + third] / K9_RATE;
      e->backing_hz[2] = k9_pitch[48u + root + (step & 4u ? 7u : 12u)] / K9_RATE;
      if ((demo_arrangements[plan].bass >> step) & 1u)
        e->bass_env = 1.0f;
      if ((demo_arrangements[plan].drums >> step) & 1u)
        e->kick_env = 1.0f;
      if (step == 4 || step == 12)
        e->snare_env = 1.0f;
      if ((step + plan) % (plan == 3 || plan == 5 ? 4u : 2u) == 0)
        e->hat_env = 1.0f;
    }
  }
  e->bass_env *= .99963f;
  e->kick_env *= .9987f;
  e->snare_env *= .9982f;
  e->hat_env *= .995f;
  float bass = oscillator(&e->backing_phase[0], e->backing_hz[0]);
  float chord = oscillator(&e->backing_phase[1], e->backing_hz[1]) +
                oscillator(&e->backing_phase[2], e->backing_hz[2]);
  float kick = oscillator(&e->backing_phase[3],
                          (.0012f + .0022f * e->kick_env));
  float accompaniment = bass * e->bass_env * .11f +
                        chord * demo_arrangements[plan].pad +
                        kick * e->kick_env * .15f +
                        noise * (e->snare_env * .058f + e->hat_env * .022f);
  e->music_gain += (e->music_level - e->music_gain) * .004f;
  return accompaniment * e->music_gain;
}

static float fx_tap(const k9_engine *e, unsigned samples) {
  if (samples > e->fx_valid)
    return 0;
  return (float)e->fx_history[(e->fx_write + K9_FX_LENGTH - samples) &
                              (K9_FX_LENGTH - 1u)] / 32768.0f;
}

static void vocal_fx(k9_engine *e, float sample, float *left, float *right) {
  unsigned active = e->fx_mix[0] | e->fx_mix[1] | e->fx_mix[2] | e->fx_mix[3];
  if (!active && e->fx_valid == 0)
    return;
  if ((e->fx_phase++ & 3u) == 0) {
    float wet = 0;
    for (unsigned i = 0; i < 4; i++) {
      e->fx_amount[i] += ((float)e->fx_mix[i] * .01f - e->fx_amount[i]) * .02f;
      wet += e->fx_amount[i];
    }
    if (!active && wet < .001f) {
      e->fx_valid = 0;
      e->fx_left = e->fx_right = 0;
      return;
    }
    float mod = triangle((float)((e->fx_phase >> 2) & 32767u) / 32768.0f);
    float chorus_l = fx_tap(e, (unsigned)(155.0f + 43.0f * mod));
    float chorus_r = fx_tap(e, (unsigned)(190.0f - 49.0f * mod));
    float echo = fx_tap(e, 1060u) + .35f * fx_tap(e, 2120u);
    float quarter = e->external && e->clocks ? e->clock_interval * 3.0f :
        (float)(K9_RATE * 60u) / (8.0f * (float)(e->tempo_override ?
            e->tempo_override : e->song ? e->song->bpm : 120u));
    unsigned delay_samples = (unsigned)bounded(quarter, 1, K9_FX_LENGTH - 1);
    float delay = fx_tap(e, delay_samples);
    float reverb = (fx_tap(e, 449u) + fx_tap(e, 683u) +
                    fx_tap(e, 953u) + fx_tap(e, 1321u)) * .25f;
    float input = (sample + e->fx_input) * .5f +
                  delay * e->fx_amount[2] * .44f +
                  reverb * e->fx_amount[3] * .32f;
    e->fx_history[e->fx_write] =
        (int16_t)(bounded(input, -.98f, .98f) * 32768.0f);
    e->fx_write = (e->fx_write + 1u) & (K9_FX_LENGTH - 1u);
    if (e->fx_valid < K9_FX_LENGTH - 1u)
      e->fx_valid++;
    float mono = echo * e->fx_amount[1] * .4f +
                 delay * e->fx_amount[2] * .5f + reverb * e->fx_amount[3] * .46f;
    e->fx_target_l = mono + chorus_l * e->fx_amount[0] * .42f;
    e->fx_target_r = mono + chorus_r * e->fx_amount[0] * .42f;
  }
  e->fx_input += (sample - e->fx_input) * .35f;
  e->fx_left += (e->fx_target_l - e->fx_left) * .35f;
  e->fx_right += (e->fx_target_r - e->fx_right) * .35f;
  *left += e->fx_left;
  *right += e->fx_right;
}
#endif
