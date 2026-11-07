/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include "memory.h"
#include "articulation.h"
#include "clarity.h"

typedef struct {
  float attack, release, breath, vibrato, glide, rasp, articulation, open;
} k9_style;
/* Independent technique presets: identity/formants are selected separately. */
static const k9_style styles[8] = {
    {.003f, .0024f, .025f, .22f, .0030f, .00f, .96f, .30f},  /* pop */
    {.005f, .0040f, .012f, .10f, .0050f, .01f, .84f, .25f},  /* house */
    {.008f, .0060f, .018f, .05f, .0120f, .06f, .74f, .22f},  /* IDM */
    {.002f, .0018f, .110f, .28f, .0008f, .10f, .94f, .38f},  /* trip-hop */
    {.001f, .0010f, .170f, .35f, .0006f, .00f, 1.00f, .44f}, /* ethereal */
    {.003f, .0020f, .055f, .80f, .0010f, .03f, .98f, .34f},  /* soul */
    {.002f, .0020f, .130f, .55f, .0016f, .15f, .91f, .40f},  /* experimental */
    {.010f, .0060f, .000f, .00f, 1.0000f, .00f, .93f, .20f}  /* robotic */
};
static float absolute(float x) { return x < 0 ? -x : x; }
static float bounded(float x, float lo, float hi) {
  return x < lo ? lo : x > hi ? hi : x;
}
static int vowel(uint8_t p) {
  return p == K9_AA || p == K9_AE || p == K9_AH || p == K9_AO || p == K9_AW ||
         p == K9_AY || p == K9_EH || p == K9_ER || p == K9_EY || p == K9_IH ||
         p == K9_IY || p == K9_OW || p == K9_OY || p == K9_UH || p == K9_UW;
}
static int plosive(uint8_t p) {
  return p == K9_P || p == K9_B || p == K9_T || p == K9_D || p == K9_K ||
         p == K9_G || p == K9_CH || p == K9_JH;
}
static float glottis(float phase, float open, float *last) {
  float flow = 0, output;
  if (phase < open) {
    float t = phase / open;
    if (t < .65f) {
      float u = t / .65f;
      flow = u * u * (3.0f - 2.0f * u);
    } else {
      float u = (1.0f - t) / .35f;
      flow = u * u;
    }
  }
  output = (flow - *last) * 9.0f;
  *last = flow;
  return output;
}
void k9_init(k9_engine *e) {
  memset(e, 0, sizeof *e);
  e->rng = 0x4b495241u;
  e->note = 69;
  e->freq = 440;
  e->glide = .002f;
  e->breath = .03f;
  e->source = 255;
  e->live_note = 255;
  e->live_source = 255;
  e->bend = 1;
  e->expression = 1;
  e->clock_interval = 918.75f;
}
void k9_stop(k9_engine *e) {
  e->playing = 0;
  e->velocity = 0;
  e->phone = K9_SIL;
  e->viseme = 0;
  e->live_note = 255;
  e->live_source = 255;
  e->live_velocity = 0;
  e->external_melody = 0;
  e->sense_armed = 0;
}
static void seek(k9_engine *e, uint32_t tick) {
  e->tick = tick;
  e->clock_tick = tick;
  e->next = 0;
  e->velocity = 0;
  while (e->song && e->next < e->song->count &&
         e->song->events[e->next].tick + e->song->events[e->next].duration <=
             tick)
    e->next++;
}
static void begin_song(k9_engine *e, const k9_song *s) {
  k9_stop(e);
  if (!k9_song_validate(s))
    return;
  e->song = s;
  e->sample = 0;
  e->tick = 0;
  e->clock_tick = 0;
  e->clock_phase = 0;
  e->next = 0;
  e->event_end = 0;
  e->last_clock = 0;
  e->clocks = 0;
  e->last_message = 0;
  e->clock_interval =
      (float)(K9_RATE * 60u) /
      (float)((e->tempo_override ? e->tempo_override : s->bpm) * 24u);
  e->playing = 1;
}
void k9_start(k9_engine *e, const k9_song *s) {
  e->playlist_count = 0;
  e->playlist_index = 0;
  begin_song(e, s);
}
int k9_playlist(k9_engine *e, const k9_song *const *songs, unsigned count) {
  unsigned i;
  if (!count || count > 8)
    return 0;
  for (i = 0; i < count; i++)
    if (!k9_song_validate(songs[i]))
      return 0;
  k9_start(e, songs[0]);
  for (i = 0; i < count; i++)
    e->playlist[i] = songs[i];
  e->playlist_count = (uint8_t)count;
  return 1;
}
void k9_note(k9_engine *e, uint8_t p, uint8_t note, uint8_t velocity) {
  if (p >= K9_NPHONE || note > 127 || velocity > 127)
    return;
  e->phone = p;
  e->note = note;
  e->velocity = velocity;
  e->viseme = k9_phones[p].viseme;
  e->phone_start = e->tick;
  e->phone_sample = e->sample;
  e->phone_frames = K9_RATE / 5u;
}
void k9_midi(k9_engine *e, uint8_t src, uint8_t status, uint8_t d1,
             uint8_t d2) {
  uint8_t kind = status & 0xf0u;
  if (d1 > 127 || d2 > 127)
    return;
  if (e->external == 2 && e->source == 255 && status == 0xfa)
    e->source = src;
  if (e->external && src != e->source)
    return;
  if (status == 0xfe) {
    e->sense_armed = 1;
    e->sense_source = src;
    e->last_message = e->sample;
    return;
  }
  if (e->sense_armed && src == e->sense_source)
    e->last_message = e->sample;
  if (status == 0xf8) {
    if (e->external) {
      uint32_t delta = e->sample - e->last_clock;
      if (e->clocks && delta > 44u && delta < 22050u)
        e->clock_interval += ((float)delta - e->clock_interval) * .125f;
      e->clock_tick += 4u;
      e->tick = e->clock_tick;
      e->clocks++;
      e->last_clock = e->sample;
    }
    return;
  }
  if (status == 0xfa) {
    if (e->external && e->song)
      k9_start(e, e->song);
    return;
  }
  if (status == 0xfb) {
    if (e->external && e->song) {
      seek(e, e->tick);
      e->last_clock = e->sample;
      e->playing = 1;
    }
    return;
  }
  if (status == 0xfc) {
    if (e->external) {
      k9_stop(e);
      if (e->external == 2)
        e->source = 255;
    }
    return;
  }
  if (status == 0xf2) {
    if (e->external && e->song)
      seek(e, ((uint32_t)d1 | ((uint32_t)d2 << 7)) * 24u);
    return;
  }
  if (kind == 0x90 && d2) {
    e->live_note = d1;
    e->live_source = src;
    e->live_velocity = d2;
    e->external_melody = e->playing && e->external;
    if (!e->playing)
      k9_note(e, K9_AH, d1, d2);
    else {
      e->note = d1;
      e->velocity = d2;
    }
  } else if (kind == 0x80 || (kind == 0x90 && !d2)) {
    if (src != e->live_source)
      return;
    if (e->live_note == d1) {
      e->live_note = 255;
      e->live_source = 255;
    }
    if (e->note == d1)
      e->velocity = 0;
  } else if (kind == 0xb0) {
    if (d1 == 120 || d1 == 123)
      k9_stop(e);
    else if (d1 == 1)
      e->vibrato = (float)d2 / 127.0f;
    else if (d1 == 2)
      e->breath = (float)d2 / 254.0f;
    else if (d1 == 11)
      e->expression = (float)d2 / 127.0f;
  } else if (kind == 0xc0)
    e->voice = d1 % 7u;
  else if (kind == 0xe0) {
    float x = (float)((int)d1 + ((int)d2 << 7) - 8192) * (.11552453f / 8192.0f);
    e->bend = 1.0f + x + x * x * .5f + x * x * x * (1.0f / 6.0f);
  }
}
void k9_render(k9_engine *e, float *out, uint32_t frames) {
  uint32_t i;
  for (i = 0; i < frames; i++) {
    const k9_style *style = &styles[e->style % 8u];
    const k9_phone *bank = k9_voice_phones[e->voice % 7u],
                   *other = k9_voice_phones[(e->voice + 1u) % 7u];
    const k9_phone *phone;
    float progress, level_target, age, noise, excitation,
        sample = 0, harmonic = 0, aspiration, gate = 1,
        morph = bounded(e->morph, 0, 1);
    unsigned b, from, to;
    if (e->playing && e->song) {
      if (e->external && e->clocks) {
        unsigned partial = (unsigned)((float)(e->sample - e->last_clock) *
                                      4.0f / e->clock_interval);
        if (partial > 3u)
          partial = 3u;
        e->tick = e->clock_tick + partial;
      }
      if (e->tick >= e->song->ticks) {
        if (!e->external && e->playlist_count &&
            e->playlist_index + 1u < e->playlist_count) {
          e->playlist_index++;
          begin_song(e, e->playlist[e->playlist_index]);
        } else if (!e->external && e->loop) {
          e->playlist_index = 0;
          begin_song(e, e->playlist_count ? e->playlist[0] : e->song);
        } else
          k9_stop(e);
      }
      if (e->playing && e->next < e->song->count &&
          e->tick >= e->song->events[e->next].tick) {
        const k9_event *v = &e->song->events[e->next++];
        uint8_t note =
            e->external_melody && e->live_note != 255 ? e->live_note : v->note;
        uint8_t velocity = e->external_melody
                               ? (e->live_note == 255 ? 0 : e->live_velocity)
                               : v->velocity;
        k9_note(e, v->phone, note, velocity);
        e->phone_start = v->tick;
        e->event_end = v->tick + v->duration;
        e->phone_end = e->event_end;
        e->phone_frames =
            (uint32_t)((float)v->duration *
                       (e->external
                            ? e->clock_interval * .25f
                            : (float)(K9_RATE * 60u) /
                                  (float)((e->tempo_override ? e->tempo_override
                                                             : e->song->bpm) *
                                          96u)));
        if (!e->phone_frames)
          e->phone_frames = 1;
      }
      if (e->tick >= e->event_end)
        e->velocity = 0;

      if (!e->external) {
        e->clock_phase +=
            (uint32_t)(e->tempo_override ? e->tempo_override : e->song->bpm) *
            96u;
        if (e->clock_phase >= K9_RATE * 60u) {
          e->clock_phase -= K9_RATE * 60u;
          e->tick++;
        }
      }
    }
    if (e->external && e->playing && e->sample - e->last_clock > K9_RATE * 2u) {
      e->late_clocks++;
      k9_stop(e);
      if (e->external == 2)
        e->source = 255;
    }
    if (e->sense_armed && e->sample - e->last_message > K9_RATE / 3u) {
      k9_stop(e);
      e->sense_armed = 0;
      if (e->external == 2)
        e->source = 255;
    }
    phone = &bank[e->phone];
    age = (float)(e->sample - e->phone_sample);
    progress =
        e->phone_frames ? bounded(age / (float)e->phone_frames, 0, 1) : 0;
    from = to = e->phone;
    if (from == K9_AW) {
      from = K9_AA;
      to = K9_UW;
    } else if (from == K9_AY) {
      from = K9_AA;
      to = K9_IY;
    } else if (from == K9_EY) {
      from = K9_EH;
      to = K9_IY;
    } else if (from == K9_OW) {
      from = K9_AO;
      to = K9_UW;
    } else if (from == K9_OY) {
      from = K9_AO;
      to = K9_IY;
    }
    for (b = 0; b < 3; b++) {
      float a = bank[from].a[b] + (bank[to].a[b] - bank[from].a[b]) * progress;
      float r = bank[from].r[b] + (bank[to].r[b] - bank[from].r[b]) * progress;
      float g = bank[from].gain[b] +
                (bank[to].gain[b] - bank[from].gain[b]) * progress;
      float aa =
          other[from].a[b] + (other[to].a[b] - other[from].a[b]) * progress;
      float rr =
          other[from].r[b] + (other[to].r[b] - other[from].r[b]) * progress;
      float gg = other[from].gain[b] +
                 (other[to].gain[b] - other[from].gain[b]) * progress;
      a += (aa - a) * morph;
      r += (rr - r) * morph;
      g += (gg - g) * morph;
      e->a[b] += (a - e->a[b]) * .003f;
      e->r[b] += (r - e->r[b]) * .003f;
      e->gain[b] += (g - e->gain[b]) * .003f;
    }
    k9_articulation articulation=k9_articulate(e->phone,e->sample-e->phone_sample,e->phone_frames);
    if (vowel(e->phone) && e->playing && progress > style->articulation)
      gate = bounded((1.0f - progress) / (1.001f - style->articulation), 0, 1);
    level_target =
        (float)e->velocity * (1.0f / 127.0f) * bounded(e->expression, 0, 1.2f);
    if (e->playing && e->next) {
      uint8_t stress = e->song->events[e->next - 1u].stress;
      level_target *= stress == 1 ? 1.0f : stress == 2 ? .91f : .82f;
    }
    e->level += (level_target - e->level) *
                (level_target > e->level ? style->attack : style->release);
    e->lfo++;
    {
      float triangle = (float)(e->lfo % 8820u) * (1.0f / 4410.0f) - 1.0f;
      float delay = bounded((age - 4410.0f) * (1.0f / 6615.0f), 0, 1),
            vibrato = (style->vibrato + e->vibrato) * .004f * delay;
      float wobble = 1.0f + vibrato * (1.0f - 2.0f * absolute(triangle));
      float slew = style->glide * bounded(e->glide * 500.0f, .05f, 4.0f);
      if (slew > 1)
        slew = 1;
      e->freq += (k9_pitch[e->note] * e->bend - e->freq) * slew;
      e->phase += e->freq * wobble * (1.0f / 44100.0f);
      if (e->phase >= 1)
        e->phase -= 1;
    }
    e->rng ^= e->rng << 13;
    e->rng ^= e->rng >> 17;
    e->rng ^= e->rng << 5;
    noise = (float)(int32_t)e->rng * (1.0f / 2147483648.0f);
    aspiration = noise - e->noise_last;
    e->noise_last = noise;
    excitation =
        glottis(e->phase, style->open + .015f * (float)e->voice, &e->flow_last);
    if (style->rasp)
      excitation *= 1.0f - style->rasp + style->rasp * noise;
    excitation = excitation * articulation.voiced * (phone->voiced ? 1.0f - phone->noise : 0) +
                 aspiration * articulation.noise * (phone->noise + style->breath +
                               bounded(e->breath, 0, .7f));
    excitation *= gate;
    for (b = 0; b < 3; b++) {
      float y =
          excitation * e->gain[b] + e->a[b] * e->z1[b] - e->r[b] * e->z2[b];
      if (absolute(y) < 1e-18f)
        y = 0;
      e->z2[b] = e->z1[b];
      e->z1[b] = y;
      sample += y * k9_spectral_weights[e->phone][b];
    }
    /* Retain a periodic voicing bar under voiced frication. Its low band is
     * independent of the upper-band noise balance (/z/ must not become /s/). */
    if(e->phone==K9_Z||e->phone==K9_ZH||e->phone==K9_V||e->phone==K9_DH)
      sample += .035f * articulation.voiced * (1.0f-4.0f*absolute(e->phase-.5f));
    if (e->harmony && vowel(e->phone)) {
      int note = (int)e->note + e->harmony;
      float hx;
      if (note < 0)
        note = 0;
      if (note > 127)
        note = 127;
      e->hphase += k9_pitch[note] * e->bend * (1.0f / 44100.0f);
      if (e->hphase >= 1)
        e->hphase -= 1;
      hx = glottis(e->hphase, style->open, &e->hflow_last) * gate;
      for (b = 0; b < 3; b++) {
        float y = hx * e->gain[b] + e->a[b] * e->hz1[b] - e->r[b] * e->hz2[b];
        if (absolute(y) < 1e-18f)
          y = 0;
        e->hz2[b] = e->hz1[b];
        e->hz1[b] = y;
        harmonic += y * k9_spectral_weights[e->phone][b];
      }
    }
    /* Reserve output headroom for upper-formant recovery at velocity 127. */
    sample *= e->level * .40f;
    harmonic *= e->level * .109f;
    out[i * 2] = bounded(sample + harmonic * .65f, -.94f, .94f);
    out[i * 2 + 1] = bounded(sample + harmonic, -.94f, .94f);
    e->sample++;
  }
}
k9_face k9_face_at(const k9_engine *e, uint32_t ms, uint8_t emotion,
                   uint8_t twitch) {
  k9_face f;
  uint32_t gap = twitch == 1 ? 17000u : 9000u, phase;
  memset(&f, 0, sizeof f);
  f.mouth = e->viseme;
  f.open = (uint16_t)(bounded(e->level, 0, 1) * 30.0f);
  if (e->viseme == 4)
    f.open = 0;
  else if (e->viseme == 5)
    f.open /= 3u;
  else if (e->viseme == 3)
    f.open = f.open * 2u / 3u;
  phase = ms % 4300u;
  f.blink = (uint8_t)(phase < 55u    ? phase * 255u / 55u
                      : phase < 110u ? (110u - phase) * 255u / 55u
                                     : 0u);
  f.gaze = (int8_t)((ms / 2700u) % 5u) - 2;
  if (e->phone == K9_SIL || e->level <= .0001f) {
    f.open = 0;
    f.mouth = 0;
  }
  if (plosive(e->phone) && e->phone_frames &&
      !k9_articulate(e->phone,e->sample-e->phone_sample,e->phone_frames).closure) {
    f.mouth = 1;
    f.open = (uint16_t)(bounded(e->level, 0, 1) * 10.0f);
  }
  f.jaw = (int8_t)(f.open / 4u);
  f.cheek = (int8_t)(emotion % 4u);
  phase = ms % gap;
  if (twitch && ms > gap && phase < 120u) {
    f.cheek += (phase < 60u ? 3 : 1);
    f.neck = (phase < 60u ? 2 : -1);
    f.gaze = -3;
  }
  return f;
}
