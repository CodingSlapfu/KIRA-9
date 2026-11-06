/* SPDX-License-Identifier: MIT; original KIRA-9 app */
#include "../core/face.h"
#include "../core/kira.h"
#include "../core/library.h"
#include "../core/transfer.h"
#include "../factory/songs.h"
static int k9_text_equal(const char *a, const char *b) {
  unsigned i;
  for (i = 0; i < 21u; i++) {
    if (a[i] != b[i])
      return 0;
    if (!a[i])
      return 1;
  }
  return 0;
}
static void text_cat(char *d, const char *s) {
  unsigned n = 0;
  while (d[n] && n < 38)
    n++;
  while (*s && n < 38)
    d[n++] = *s++;
  d[n] = 0;
}
static void int_text(int v, char *d) {
  char b[12];
  unsigned n = 0, j = 0;
  uint32_t u = v < 0 ? 0u - (uint32_t)v : (uint32_t)v;
  if (v < 0)
    d[j++] = '-';
  do {
    b[n++] = (char)('0' + u % 10);
    u /= 10;
  } while (u);
  while (n)
    d[j++] = b[--n];
  d[j] = 0;
}
static k9_engine engine;
static k9_song custom, cues[2];
static k9_song validation_song PLAT_POOL;
static k9_song phrase_cache[8] PLAT_POOL, word_cache[8] PLAT_POOL;
static uint8_t library_busy;
static k9_transfer transfer_state;
static k9_preset presets[8];
static uint8_t voice_wire[3840], custom_wire[3840];
static uint16_t voice_length, custom_length;
static uint8_t tx_reply[160];
static uint16_t tx_length, tx_position;
static uint8_t preset_pick, delete_confirm, library_action, save_confirm;
static uint32_t delete_until;
static uint8_t cue_ready, cue_active;
static uint8_t song_wire[K9_WIRE_MAX];
static float audio_lr[512];
typedef struct {
  uint32_t magic;
  uint8_t song, voice, mode, sync, slot, emotion, twitch, ble, reconnect, kind,
      style, channel;
  char peer[21];
  uint8_t morph, breath, vibrato, glide, expression;
  int8_t harmony;
  uint8_t loop;
  uint16_t tempo;
} k9_settings;
static k9_settings prefs;
static uint32_t btn_last, keys_last, draw_at, block_max, blocks, overruns;
static uint8_t peer_pick, ble_was, backup_hold;
static uint32_t retry_at;
static uint8_t page, dirty, save_pending, load_pending, playing_cmd, stop_cmd,
    note_cmd, note_vel;
static char message[40];
static const char *const pages[] = {
    "PLAY", "SONG", "VOICE", "MIDI", "LIBRARY", "PERFORMANCE", "EXPRESSION"};
static const char *const modes[] = {"SOLO SONG", "LIVE", "PHRASE", "WORD"};
static const char *const voices[] = {"BRIGHT", "DEEP",   "AIRY", "SMOKY",
                                     "YOUTH",  "MATURE", "SYNTH"};
static uint32_t library_object(uint8_t kind, uint8_t slot) {
  if (kind == 3)
    return OBJ_PRONUNCIATION;
  if (kind == 4)
    return OBJ_VOICES;
  if (kind == 1)
    return OBJ_PHRASE0 + slot;
  if (kind == 2)
    return OBJ_WORD0 + slot;
  return slot < 4 ? OBJ_SONG0 + slot : OBJ_SONG4 + slot - 4;
}
static void library_cache_load(void) {
  unsigned i;
  for (i = 0; i < 8; i++) {
    int n;
    phrase_cache[i].count = word_cache[i].count = 0;
    n = plat_store_load(OBJ_PHRASE0 + i, song_wire, sizeof song_wire);
    if (n > 0)
      k9_decode(&phrase_cache[i], song_wire, (size_t)n);
    n = plat_store_load(OBJ_WORD0 + i, song_wire, sizeof song_wire);
    if (n > 0)
      k9_decode(&word_cache[i], song_wire, (size_t)n);
  }
}
static void presets_load(void) {
  unsigned i;
  int n;
  memset(presets, 0, sizeof presets);
  for (i = 0; i < 8; i++) {
    presets[i].voice = i % 7;
    presets[i].style = i;
    presets[i].breath = 6;
    presets[i].vibrato = 20;
    presets[i].glide = 50;
    presets[i].expression = 110;
  }
  n = plat_store_load(OBJ_VOICES, voice_wire, sizeof voice_wire);
  if (n > 0 && k9_voicebank_read(voice_wire, (uint16_t)n, presets))
    voice_length = (uint16_t)n;
  else
    voice_length = k9_voicebank_write(voice_wire, 0, presets);
}
static int xbusy(void *ctx) {
  (void)ctx;
  return backup_hold || engine.playing || engine.velocity ||
         engine.level > .0001f;
}
static int xload(void *ctx, uint8_t kind, uint8_t slot, uint8_t *p,
                 uint16_t cap) {
  (void)ctx;
  return plat_store_load(library_object(kind, slot), p, cap);
}
static int xvalid(void *ctx, uint8_t kind, const uint8_t *p, uint16_t n) {
  (void)ctx;
  if (kind < 3)
    return k9_decode(&validation_song, p, n);
  if (kind == 4)
    return k9_voicebank_read(p, n, 0);
  return k9_document_valid(p, n, kind);
}
static int xsave(void *ctx, uint8_t kind, uint8_t slot, const uint8_t *p,
                 uint16_t n) {
  int rc;
  (void)ctx;
  rc = plat_store_save(library_object(kind, slot), p, n);
  if (!rc) {
    if (kind < 3) {
      memcpy(&custom, &validation_song, sizeof custom);
      memcpy(custom_wire, p, n);
      custom_length = n;
      load_pending = 1;
    }
    if (kind == 4)
      presets_load();
    library_cache_load();
    app_say("TRANSFER SAVED", "");
  }
  return rc;
}
static const k9_transfer_io xio = {0, xbusy, xload, xvalid, xsave};
static void transfer_send(const uint8_t *body, uint16_t n) {
  uint8_t raw[120];
  unsigned i, bits = 0, acc = 0;
  uint8_t sum = 0;
  raw[0] = 0;
  raw[1] = 0x59;
  raw[2] = 0x67;
  raw[3] = (uint8_t)n;
  raw[4] = (uint8_t)(n >> 8);
  raw[5] = 0;
  memcpy(raw + 6, body, n);
  for (i = 0; i < n; i++)
    sum = (uint8_t)(sum + body[i]);
  raw[6 + n] = (uint8_t)~sum;
  tx_position = 0;
  tx_length = 0;
  tx_reply[tx_length++] = 0xf0;
  for (i = 0; i < n + 7u; i++) {
    acc |= (unsigned)raw[i] << bits;
    bits += 8;
    while (bits >= 7) {
      tx_reply[tx_length++] = (uint8_t)(acc & 127);
      acc >>= 7;
      bits -= 7;
    }
  }
  if (bits)
    tx_reply[tx_length++] = (uint8_t)acc;
  tx_reply[tx_length++] = 0xf7;
}
static void transfer_poll(void) {
  k9_transfer_poll(&transfer_state, plat_ms());
  while (tx_position < tx_length && plat_midi_out_room(TO_USB)) {
    uint32_t p;
    unsigned left = tx_length - tx_position, take = left >= 3 ? 3 : left,
             cin = left > 3 ? 4 : 4 + take;
    p = cin;
    for (unsigned i = 0; i < take; i++)
      p |= (uint32_t)tx_reply[tx_position + i] << (8u + 8u * i);
    plat_midi_send(p, TO_USB);
    tx_position = (uint16_t)(tx_position + take);
  }
}
static void restart_song(void) {
  engine.voice = prefs.voice;
  engine.external = (prefs.sync == 1 || prefs.sync == 3) ? 2 : prefs.sync != 0;
  engine.source = (prefs.sync == 1 || prefs.sync == 3) ? 255 : TO_USB;
  k9_start(&engine, load_pending ? &custom : &factory_songs[prefs.song]);
}
static void prefs_defaults(void) {
  memset(&prefs, 0, sizeof prefs);
  prefs.magic = 0x4b395032u;
  prefs.twitch = 1;
  prefs.breath = 6;
  prefs.vibrato = 20;
  prefs.glide = 50;
  prefs.expression = 110;
}
static void prefs_apply(void) {
  engine.voice = prefs.voice;
  engine.style = prefs.style;
  engine.emotion = prefs.emotion;
  engine.morph = (float)prefs.morph * .01f;
  engine.breath = (float)prefs.breath * .005f;
  engine.vibrato = (float)prefs.vibrato * .01f;
  engine.glide = .0002f + (float)prefs.glide * .00005f;
  engine.harmony = prefs.harmony;
  engine.expression = (float)prefs.expression / 127.0f;
  engine.tempo_override = prefs.tempo;
  engine.loop = prefs.loop;
}
void app_init(void) {
  uint8_t raw[sizeof prefs];
  int got;
  prefs_defaults();
  got = plat_store_load(OBJ_SETTINGS, raw, sizeof raw);
  if (got == (int)sizeof prefs) {
    memcpy(&prefs, raw, sizeof prefs);
  } else if (got == 40u && raw[0] == 0x31 && raw[1] == 0x50 && raw[2] == 0x39 &&
             raw[3] == 0x4b) {
    memcpy(&prefs, raw, offsetof(k9_settings, morph));
    prefs.magic = 0x4b395032u;
  }
  if (prefs.magic != 0x4b395032u || prefs.song >= 8 || prefs.voice >= 7 ||
      prefs.mode >= 4 || prefs.sync >= 4 || prefs.slot >= 8 ||
      prefs.emotion >= 4 || prefs.twitch >= 3 || prefs.ble >= 2 ||
      prefs.channel > 16 || prefs.style >= 8 || prefs.kind >= 5 ||
      prefs.reconnect >= 2 || prefs.morph > 100 || prefs.breath > 100 ||
      prefs.vibrato > 100 || prefs.glide > 100 || prefs.expression > 127 ||
      prefs.harmony < -12 || prefs.harmony > 12 || prefs.loop > 1 ||
      (prefs.tempo && (prefs.tempo < 30 || prefs.tempo > 300)))
    prefs_defaults();
  prefs.peer[20] = 0;
  k9_init(&engine);
  prefs_apply();
  engine.song = &factory_songs[prefs.song];
  engine.external = (prefs.sync == 1 || prefs.sync == 3) ? 2 : prefs.sync != 0;
  engine.source = (prefs.sync == 1 || prefs.sync == 3) ? 255 : TO_USB;
  plat_ble_enable(prefs.ble);
  btn_last = keys_last = draw_at = 0;
  message[0] = 0;
  save_pending = playing_cmd = stop_cmd = load_pending = note_vel = 0;
  page = dirty = 0;
  cue_ready = cue_active = 0;
  blocks = block_max = overruns = 0;
  library_cache_load();
  presets_load();
  k9_transfer_init(&transfer_state);
  custom_length = 0;
}
void app_panic(void) {
  k9_stop(&engine);
  engine.level = 0;
}
void app_render(int32_t *lr, uint32_t n, uint32_t master) {
  uint32_t t = plat_ticks24(), i, pkt;
  int port;
  unsigned budget = 32;
  if (stop_cmd) {
    k9_stop(&engine);
    if (engine.external == 2)
      engine.source = 255;
    stop_cmd = 0;
    note_cmd = 0;
    cue_ready = 0;
  }
  if (cue_ready) {
    cue_active = cue_ready - 1;
    cue_ready = 0;
    k9_start(&engine, &cues[cue_active]);
  }
  if (playing_cmd) {
    restart_song();
    playing_cmd = 0;
  }
  if (note_cmd) {
    k9_note(&engine, K9_AH, note_cmd - 2, note_vel);
    note_cmd = 0;
  }
  while (budget-- && plat_midi_in(&pkt, &port)) {
    uint8_t source = (uint8_t)plat_midi_in_from(), st = (uint8_t)(pkt >> 8),
            d1 = (uint8_t)(pkt >> 16) & 127u, d2 = (uint8_t)(pkt >> 24) & 127u;
    if (prefs.sync == 1 && port != PORT_BLE)
      continue;
    if (library_busy || transfer_state.active)
      continue;
    if (st < 0xf0u && prefs.channel && ((st & 15u) + 1u) != prefs.channel)
      continue;
    if (prefs.sync == 1 && engine.source == 255 && st < 0xf0u)
      engine.source = source;
    if ((st & 0xf0u) == 0xc0u && (!engine.external || engine.source == source))
      prefs.voice = d1 % 7u;
    if ((st & 0xf0u) == 0xb0u &&
        (!engine.external || engine.source == 255 || engine.source == source)) {
      if (d1 == 20u && d2 < 8u && phrase_cache[d2].count) {
        k9_start(&engine, &phrase_cache[d2]);
        continue;
      }
      if (d1 == 21u && d2 < 8u && word_cache[d2].count) {
        k9_start(&engine, &word_cache[d2]);
        continue;
      }
      if (d1 == 22u && d2 < 8u) {
        k9_start(&engine, &factory_songs[d2]);
        continue;
      }
      if (d1 == 23u) {
        prefs.voice = d2 % 7u;
        continue;
      }
      if (d1 == 24u) {
        prefs.style = d2 % 8u;
        continue;
      }
      if (d1 == 25u) {
        prefs.emotion = d2 % 4u;
        continue;
      }
    }
    k9_midi(&engine, source, st, d1, d2);
  }
  prefs_apply();
  if (n > 256)
    n = 256;
  k9_render(&engine, audio_lr, n);
  for (i = 0; i < n * 2; i++)
    lr[i] = (int32_t)(audio_lr[i] * (float)master * (8300000.0f / 4096.0f));
  t = plat_ticks24() - t;
  if (t > block_max)
    block_max = t;
  if (t > 139319u)
    overruns++;
  blocks++;
}
void app_say(const char *a, const char *b) {
  message[0] = 0;
  text_cat(message, a);
  if (b && *b) {
    text_cat(message, " ");
    text_cat(message, b);
  }
}
static void input(void) {
  uint32_t f, buttons = plat_buttons(), press = buttons & ~btn_last,
              keys = plat_keys(), down = keys & ~keys_last,
              up = keys_last & ~keys;
  int d;
  unsigned i;
  btn_last = buttons;
  keys_last = keys;
  if (press & (1u << B_HOME))
    page = 0;
  d = plat_enc(EN_SELECT);
  if (d)
    page = (uint8_t)((page + 7 + d % 7) % 7);
  if (press & (1u << B_EDIT))
    page = (page + 1) % 7;
  if (press & (1u << B_PLAY)) {
    if (transfer_state.active) {
      app_say("FINISH TRANSFER FIRST", "");
    } else if (engine.playing || engine.velocity)
      stop_cmd = 1;
    else
      playing_cmd = 1;
  }
  if (press & (1u << B_SAVE))
    save_pending = 1;
  if (press & (1u << B_SEL)) {
    if (page == 4) {
      if (xbusy(0) || transfer_state.active) {
        app_say("STOP BEFORE LIBRARY EDIT", "");
      } else if (save_confirm == 1) {
        save_confirm = 2;
        save_pending = 1;
      } else if (library_action) {
        if (delete_confirm && (int32_t)(plat_ms() - delete_until) < 0) {
          int rc = plat_store_save(library_object(prefs.kind, prefs.slot),
                                   song_wire, 0);
          delete_confirm = 0;
          if (!rc) {
            library_busy = 1;
            library_cache_load();
            presets_load();
            library_busy = 0;
            app_say("USER SLOT DELETED", "");
          } else
            app_say("DELETE FAILED", "");
        } else {
          delete_confirm = 1;
          delete_until = plat_ms() + 5000u;
          app_say("SEL AGAIN TO DELETE", "");
        }
      } else if (prefs.kind >= 3) {
        app_say("EDIT IN WEB STUDIO", "");
      } else {
        int len = plat_store_load(library_object(prefs.kind, prefs.slot),
                                  song_wire, sizeof song_wire);
        if (len > 0 && k9_decode(&custom, song_wire, (size_t)len)) {
          load_pending = 1;
          custom_length = (uint16_t)len;
          memcpy(custom_wire, song_wire, (uint32_t)len);
          app_say("LOADED", "");
        } else
          app_say("EMPTY OR INVALID", "");
      }
    } else if (page == 2) {
      prefs.voice = presets[preset_pick].voice;
      prefs.style = presets[preset_pick].style;
      prefs.emotion = presets[preset_pick].emotion;
      prefs.morph = presets[preset_pick].morph;
      prefs.breath = presets[preset_pick].breath;
      prefs.vibrato = presets[preset_pick].vibrato;
      prefs.glide = presets[preset_pick].glide;
      prefs.harmony = presets[preset_pick].harmony;
      prefs.expression = presets[preset_pick].expression;
      dirty = 1;
      app_say("PRESET LOADED", "");
    } else if (page == 3) {
      if (plat_ble_device() >= BLE_DEV_CONNECTING)
        plat_ble_disconnect();
      else {
        int rssi;
        if (plat_ble_found(peer_pick, prefs.peer, &rssi)) {
          plat_ble_connect(peer_pick);
          dirty = 1;
        }
      }
    }
  }
  for (i = EN_ALGO; i < NE; i++) {
    d = plat_enc(i);
    if (!d)
      continue;
    dirty = 1;
    if (page == 1) {
      if (i == EN_K1) {
        stop_cmd = 1;
        prefs.song = (uint8_t)((prefs.song + 8 + d % 8) % 8);
        load_pending = 0;
      }
      if (i == EN_K2) {
        stop_cmd = 1;
        prefs.mode = (uint8_t)((prefs.mode + 4 + d % 4) % 4);
      }
    }
    if (page == 1 && i == EN_K3)
      prefs.tempo = (uint16_t)clamp(
          (prefs.tempo ? prefs.tempo : factory_songs[prefs.song].bpm) + d, 30,
          300);
    if (page == 1 && i == EN_K4)
      prefs.loop = !prefs.loop;
    if (page == 6) {
      if (i == EN_K1)
        prefs.breath = (uint8_t)clamp(prefs.breath + d, 0, 100);
      if (i == EN_K2)
        prefs.vibrato = (uint8_t)clamp(prefs.vibrato + d, 0, 100);
      if (i == EN_K3)
        prefs.glide = (uint8_t)clamp(prefs.glide + d, 0, 100);
      if (i == EN_K4)
        prefs.morph = (uint8_t)clamp(prefs.morph + d, 0, 100);
      if (i == EN_PRESET)
        prefs.harmony = (int8_t)clamp(prefs.harmony + d, -12, 12);
      if (i == EN_ALGO)
        prefs.expression = (uint8_t)clamp(prefs.expression + d, 0, 127);
    }
    if (page == 2) {
      if (i == EN_PRESET)
        preset_pick = (uint8_t)((preset_pick + 8 + d % 8) % 8);
      if (i == EN_K4)
        prefs.style = (uint8_t)((prefs.style + 8 + d % 8) % 8);
      if (i == EN_K1)
        prefs.voice = (uint8_t)((prefs.voice + 7 + d % 7) % 7);
      if (i == EN_K2)
        prefs.emotion = (uint8_t)((prefs.emotion + 4 + d % 4) % 4);
      if (i == EN_K3)
        prefs.twitch = (uint8_t)((prefs.twitch + 3 + d % 3) % 3);
    }
    if (page == 3 && i == EN_K1) {
      f = plat_lock();
      k9_stop(&engine);
      prefs.sync = (uint8_t)((prefs.sync + 4 + d % 4) % 4);
      engine.external =
          (prefs.sync == 1 || prefs.sync == 3) ? 2 : prefs.sync != 0;
      engine.source = (prefs.sync == 1 || prefs.sync == 3) ? 255 : TO_USB;
      plat_unlock(f);
    }
    if (page == 3 && i == EN_PRESET)
      prefs.channel = (uint8_t)((prefs.channel + 17 + d % 17) % 17);
    if (page == 3 && i == EN_K2)
      peer_pick = (uint8_t)((peer_pick + 8 + d % 8) % 8);
    if (page == 3 && i == EN_K3)
      prefs.reconnect = !prefs.reconnect;
    if (page == 3 && i == EN_K4) {
      prefs.ble = !prefs.ble;
      plat_ble_enable(prefs.ble);
    }
    if (page == 4) {
      delete_confirm = save_confirm = 0;
      if (i == EN_K3)
        library_action = !library_action;
    }
    if (page == 4 && i == EN_K2)
      prefs.kind = (uint8_t)((prefs.kind + 5 + d % 5) % 5);
    if (page == 4 && i == EN_K1 && prefs.kind < 3)
      prefs.slot = (uint8_t)((prefs.slot + 8 + d % 8) % 8);
  }
  if (prefs.mode && !transfer_state.active) {
    for (i = 0; i < 27; i++) {
      if (down & (1u << i)) {
        if (prefs.mode == 1) {
          f = plat_lock();
          note_cmd = (uint8_t)(55 + i);
          note_vel = 100;
          plat_unlock(f);
        } else if ((prefs.mode == 2 ? phrase_cache[i % 8].count
                                    : word_cache[i % 8].count)) {
          f = plat_lock();
          k9_start(&engine,
                   prefs.mode == 2 ? &phrase_cache[i % 8] : &word_cache[i % 8]);
          plat_unlock(f);
        } else {
          uint8_t index = 1u - cue_active;
          k9_song *cue = &cues[index];
          const k9_song *src = &factory_songs[prefs.song];
          unsigned first, last, j, word = i % factory_word_counts[prefs.song];
          f = plat_lock();
          cue_ready = 0;
          index = 1u - cue_active;
          plat_unlock(f);
          cue = &cues[index];
          if (prefs.mode == 2) {
            unsigned phrase = i % 4u;
            first =
                factory_word_starts[prefs.song]
                                   [factory_phrase_starts[prefs.song][phrase]];
            last = factory_word_starts
                [prefs.song][factory_phrase_starts[prefs.song][phrase + 1u]];
          } else {
            first = factory_word_starts[prefs.song][word];
            last = factory_word_starts[prefs.song][word + 1u];
          }
          cue->count = (uint16_t)(last - first);
          cue->bpm = src->bpm;
          cue->ticks = src->events[last - 1u].tick +
                       src->events[last - 1u].duration -
                       src->events[first].tick;
          for (j = first; j < last; j++) {
            cue->events[j - first] = src->events[j];
            cue->events[j - first].tick -= src->events[first].tick;
            cue->events[j - first].note =
                (uint8_t)clamp((int)src->events[j].note + (int)i - 12, 0, 127);
          }
          f = plat_lock();
          cue_ready = index + 1u;
          plat_unlock(f);
        }
        plat_midi_send(0x09u | 0x90u << 8 | (53u + i) << 16 | 100u << 24,
                       TO_USB | TO_BLE);
      }
      if (up & (1u << i)) {
        if (prefs.mode == 1 && engine.note == 53 + i) {
          f = plat_lock();
          note_cmd = (uint8_t)(55 + i);
          note_vel = 0;
          plat_unlock(f);
        }
        plat_midi_send(0x08u | 0x80u << 8 | (53u + i) << 16, TO_USB | TO_BLE);
      }
    }
  }
  if (save_pending) {
    if (backup_hold || transfer_state.active) {
      app_say("BACKUP IN PROGRESS", "");
      save_pending = 0;
      return;
    }
    if (engine.playing || engine.level > .0001f)
      app_say("STOP BEFORE SAVE", "");
    else {
      int rc;
      if (page == 4 && prefs.kind >= 3) {
        app_say("EDIT AND SAVE IN STUDIO", "");
        save_pending = 0;
        return;
      }
      if (page == 4 &&
          plat_store_size(library_object(prefs.kind, prefs.slot)) > 0 &&
          save_confirm != 2) {
        save_confirm = 1;
        app_say("SEL TO OVERWRITE SLOT", "");
        save_pending = 0;
        return;
      }
      save_confirm = 0;
      if (page == 4 && prefs.kind < 3) {
        size_t n = k9_encode(prefs.mode && engine.song ? engine.song
                             : load_pending            ? &custom
                                            : &factory_songs[prefs.song],
                             song_wire, sizeof song_wire);
        if (load_pending && custom_length && prefs.mode == 0) {
          n = custom_length;
          memcpy(song_wire, custom_wire, n);
        }
        rc = n && n <= PLAT_STORE_MAX
                 ? plat_store_save(library_object(prefs.kind, prefs.slot),
                                   song_wire, (uint32_t)n)
                 : -1;
      } else if (page == 2) {
        presets[preset_pick].voice = prefs.voice;
        presets[preset_pick].style = prefs.style;
        presets[preset_pick].emotion = prefs.emotion;
        presets[preset_pick].morph = prefs.morph;
        presets[preset_pick].breath = prefs.breath;
        presets[preset_pick].vibrato = prefs.vibrato;
        presets[preset_pick].glide = prefs.glide;
        presets[preset_pick].harmony = prefs.harmony;
        presets[preset_pick].expression = prefs.expression;
        voice_length = k9_voicebank_write(voice_wire, voice_length, presets);
        rc = voice_length
                 ? plat_store_save(OBJ_VOICES, voice_wire, voice_length)
                 : -1;
        if (!rc)
          rc = plat_store_save(OBJ_SETTINGS, &prefs, sizeof prefs);
      } else
        rc = plat_store_save(OBJ_SETTINGS, &prefs, sizeof prefs);
      if (!rc) {
        if (page == 4) {
          library_busy = 1;
          library_cache_load();
          library_busy = 0;
        }
        dirty = 0;
        app_say("SAVED", "");
      } else
        app_say("SAVE FAILED", "");
    }
    save_pending = 0;
  }
  plat_leds((engine.playing ? (1u << B_PLAY) : 0) |
                (dirty ? (1u << B_SAVE) : 0),
            keys);
}
/* The native and browser portraits use this exact band renderer. */
static void draw_face(k9_face f) {
  for (unsigned band = 0; band < 6; band++) {
    cv_begin(240, 40, 0);
    k9_face_render(cv_px, band * 40u, 40, &f);
    for (unsigned i = 0; i < 240u * 40u; i++)
      cv_px[i] = swap16(cv_px[i]);
    if (!band) {
      cv_text(6, 3, &FONT_XS, "KIRA-9", C_WHITE);
      int bars = plat_battery();
      char battery[12];
      if (bars >= 0) {
        int_text(bars, battery);
        cv_text(206, 3, &FONT_XS, bars == 4 ? "USB" : battery, C_WHITE);
      }
    }
    if (band == 5) {
      cv_rect(0, 26, 240, 14, RGB(14, 18, 31));
      cv_text(5, 25, &FONT_T, "EDIT / SELECT: PAGES   PLAY: SING", C_WHITE);
    }
    cv_blit(0, band * 40u);
  }
}
static void draw_menu(void) {
  char t[32];
  unsigned row;
  for (row = 0; row < 6; row++) {
    cv_begin(240, 40, RGB(13, 16, 30));
    if (page == 6 && row > 0 && row < 5) {
      const char *label = "";
      int value = 0;
      switch (row) {
      case 1:
        label = "K1 BREATH";
        value = prefs.breath;
        break;
      case 2:
        label = "K2 VIBRATO";
        value = prefs.vibrato;
        break;
      case 3:
        label = "K3 GLIDE";
        value = prefs.glide;
        break;
      case 4:
        label = "K4 MORPH";
        value = prefs.morph;
        break;
      }
      cv_text(8, 0, &FONT_XS, label, C_WHITE);
      int_text(value, t);
      cv_text(148, 0, &FONT_XS, t, C_HI);
      if (row == 3) {
        int_text(prefs.harmony, t);
        cv_text(8, 17, &FONT_XS, "PRESET: HARMONY", C_WHITE);
        cv_text(148, 17, &FONT_XS, t, C_HI);
      }
      if (row == 4) {
        int_text(prefs.expression, t);
        cv_text(8, 17, &FONT_XS, "ALGO: EXPRESSION", C_WHITE);
        cv_text(148, 17, &FONT_XS, t, C_HI);
      }
    } else if (!row) {
      cv_text(8, 5, &FONT_M, pages[page], RGB(255, 157, 81));
    } else if (row == 1 && page == 5) {
      int_text((int)plat_cpu_pct(), t);
      cv_text(8, 0, &FONT_XS, "AUDIO CPU %", C_WHITE);
      cv_text(130, 0, &FONT_XS, t, C_WHITE);
      int_text((int)plat_xruns(), t);
      cv_text(8, 17, &FONT_XS, "DMA XRUNS", C_WHITE);
      cv_text(130, 17, &FONT_XS, t, C_WHITE);
    } else if (row == 1) {
      cv_text(8, 0, &FONT_XS, factory_names[prefs.song], C_WHITE);
      cv_text(8, 17, &FONT_XS, modes[prefs.mode], C_WHITE);
      if (page == 2) {
        int_text(preset_pick + 1, t);
        cv_text(130, 17, &FONT_XS, "PRESET", C_WHITE);
        cv_text(192, 17, &FONT_XS, t, C_HI);
      }
    } else if (row == 2 && page == 3) {
      int_text(prefs.channel, t);
      cv_text(8, 0, &FONT_XS, "PRESET: MIDI CHANNEL", C_WHITE);
      cv_text(150, 0, &FONT_XS, prefs.channel ? t : "OMNI", C_WHITE);
      cv_text(8, 17, &FONT_XS,
              prefs.reconnect ? "K3 RECONNECT: ON" : "K3 RECONNECT: OFF",
              C_WHITE);
    } else if (row == 2 && page == 4) {
      cv_text(8, 0, &FONT_XS, message, C_WHITE);
      cv_text(8, 17, &FONT_XS,
              prefs.kind < 3 ? "SAVE: STORE PERFORMANCE"
                             : "WEB STUDIO: EDIT LIBRARY",
              C_WHITE);
    } else if (row == 2) {
      cv_text(8, 0, &FONT_XS, voices[prefs.voice], RGB(255, 157, 81));
      int_text((int)engine.tick, t);
      cv_text(8, 17, &FONT_XS, t, C_WHITE);
    } else if (row == 3) {
      if (page == 3) {
        cv_text(8, 0, &FONT_XS,
                prefs.sync == 0   ? "K1 CLOCK: INTERNAL"
                : prefs.sync == 1 ? "K1 CLOCK: BLE"
                : prefs.sync == 2 ? "K1 CLOCK: USB"
                                  : "K1 CLOCK: AUTO",
                C_WHITE);
        cv_text(8, 17, &FONT_XS,
                prefs.sync == 3 ? "AUTO: START ARMS SOURCE"
                : prefs.ble     ? "K4 BLE: ON"
                                : "K4 BLE: OFF",
                C_WHITE);
      } else if (page == 2) {
        cv_text(8, 0, &FONT_XS, "K1 VOICE  K2 EMOTION", C_WHITE);
        int_text(prefs.twitch, t);
        cv_text(8, 17, &FONT_XS, "K3 TWITCH", C_WHITE);
        cv_text(90, 17, &FONT_XS, t, C_WHITE);
      } else if (page == 4) {
        int_text(prefs.slot + 1, t);
        if (prefs.kind >= 3)
          cv_text(8, 0, &FONT_XS, "INDEPENDENT LIBRARY", C_WHITE);
        else
          cv_text(8, 0, &FONT_XS,
                  prefs.kind == 0   ? "K1 SONG SLOT"
                  : prefs.kind == 1 ? "K1 PHRASE SLOT"
                                    : "K1 WORD SLOT",
                  C_WHITE);
        if (prefs.kind < 3)
          cv_text(130, 0, &FONT_XS, t, C_HI);
        cv_text(8, 17, &FONT_XS,
                library_action ? "K3 DELETE / SEL CONFIRM"
                               : "K3 LOAD / SEL SELECT",
                C_WHITE);
      } else if (page == 5) {
        int_text((int)(block_max / 24u), t);
        cv_text(8, 0, &FONT_XS, "MAX AUDIO US", C_WHITE);
        cv_text(122, 0, &FONT_XS, t, C_WHITE);
        int_text((int)overruns, t);
        cv_text(8, 17, &FONT_XS, "OVERRUNS", C_WHITE);
        cv_text(122, 17, &FONT_XS, t, C_WHITE);
      } else {
        cv_text(8, 0, &FONT_XS, "K1 SONG   K2 MODE", C_WHITE);
        int_text(prefs.tempo ? prefs.tempo : factory_songs[prefs.song].bpm, t);
        cv_text(8, 17, &FONT_XS, "K3 BPM", C_WHITE);
        cv_text(65, 17, &FONT_XS, t, C_HI);
        cv_text(118, 17, &FONT_XS, prefs.loop ? "K4 LOOP ON" : "K4 LOOP OFF",
                C_WHITE);
      }
    } else if (row == 4) {
      if (page == 2) {
        static const char *const style_names[] = {
            "POP",     "HOUSE", "IDM",          "TRIP-HOP",
            "AMBIENT", "SOUL",  "EXPERIMENTAL", "ROBOTIC"};
        cv_text(8, 0, &FONT_XS, "K4 STYLE", C_WHITE);
        cv_text(90, 0, &FONT_XS, style_names[prefs.style], C_WHITE);
        int_text(prefs.emotion, t);
        cv_text(8, 17, &FONT_XS, "EMOTION", C_WHITE);
        cv_text(90, 17, &FONT_XS, t, C_WHITE);
      } else if (page == 4) {
        static const char *const kinds[] = {"SONG", "PHRASE", "WORD",
                                            "PRONUNCIATION", "VOICE PRESETS"};
        cv_text(8, 0, &FONT_XS, "K2 TYPE", C_WHITE);
        cv_text(80, 0, &FONT_XS, kinds[prefs.kind], C_HI);
        int bytes = plat_store_size(library_object(prefs.kind, prefs.slot));
        int_text(bytes < 0 ? 0 : bytes, t);
        cv_text(8, 17, &FONT_XS, t, C_HI);
        cv_text(60, 17, &FONT_XS, "/3840 BYTES USED", C_WHITE);
      } else if (page == 3) {
        char name[21];
        int rssi;
        if (plat_ble_found(peer_pick, name, &rssi))
          cv_text(8, 0, &FONT_XS, name, C_WHITE);
        else
          cv_text(8, 0, &FONT_XS, "K2: CHOOSE MIDI PEER", C_WHITE);
        cv_text(8, 17, &FONT_XS, "SEL: CONNECT / DISCONNECT", C_WHITE);
      } else
        cv_text(8, 5, &FONT_XS, message, C_WHITE);
    } else {
      cv_text(8, 0, &FONT_XS, "EDIT / SELECT: PAGES", C_WHITE);
      cv_text(8, 17, &FONT_XS, "HOME: FACE   SAVE: STORE", C_WHITE);
    }
    cv_blit(0, row * 40);
  }
}
void app_ui_init(void) {
  palette_set(1);
  lcd_fill(0, 0, 240, 240, C_BLACK);
}
void app_input_only(void) {
  transfer_poll();
  input();
}
void app_frame(void) {
  uint32_t now = plat_ms();
  transfer_poll();
  input();
  if (plat_usb_lost() && prefs.sync != 0) {
    stop_cmd = 1;
    k9_transfer_init(&transfer_state);
  }
  {
    uint8_t linked =
        (uint8_t)(plat_ble_connected() || plat_ble_device() == BLE_DEV_READY);
    if (ble_was && !linked && prefs.sync != 2 && prefs.sync != 0)
      stop_cmd = 1;
    ble_was = linked;
    plat_ble_scan(prefs.ble && !linked && (page == 3 || prefs.reconnect));
    if (prefs.ble && prefs.reconnect && prefs.peer[0] && !linked &&
        now - retry_at > 5000u) {
      int j, rssi;
      char name[21];
      retry_at = now;
      for (j = 0; j < 8; j++)
        if (plat_ble_found(j, name, &rssi) && k9_text_equal(name, prefs.peer)) {
          plat_ble_connect(j);
          break;
        }
    }
  }
  if (now - draw_at < 50u)
    return;
  draw_at = now;
  if (!page) {
    k9_face f;
    uint32_t lock = plat_lock();
    f = k9_face_at(&engine, now, prefs.emotion, prefs.twitch);
    plat_unlock(lock);
    draw_face(f);
  } else
    draw_menu();
}
#ifdef PLAT_HOST
int app_expect(const char *what, int *got) {
  if (!strcmp(what, "playing"))
    *got = engine.playing;
  else if (!strcmp(what, "song"))
    *got = prefs.song;
  else if (!strcmp(what, "voice"))
    *got = prefs.voice;
  else if (!strcmp(what, "mode"))
    *got = prefs.mode;
  else if (!strcmp(what, "sync"))
    *got = prefs.sync;
  else if (!strcmp(what, "note"))
    *got = engine.velocity ? engine.note : -1;
  else if (!strcmp(what, "dirty"))
    *got = dirty;
  else
    return 0;
  return 1;
}
#endif

/* USB command 0x61: slot:u8, wire length:u16, whole-file CRC:u32. Pulls bounded
 * chunks, checks before writing an inactive A/B store sector; ACK address
 * C2000000|result. */
void app_usb_cmd(const uint8_t *d, uint32_t n) {
  uint32_t len, crc, off;
  uint8_t ack = 0, result = 1;
  if (n >= 9u && d[2] >= 0x62u && d[2] <= 0x66u) {
    uint8_t response[109];
    uint16_t rn =
        k9_transfer_command(&transfer_state, &xio, plat_ms(), d[2], d + 6,
                            (uint16_t)(n - 7u), response, sizeof response);
    if (rn)
      transfer_send(response, rn);
    return;
  }
  if (n != 15u || d[2] != 0x61u)
    return;
  len = (uint32_t)d[7] | (uint32_t)d[8] << 8;
  crc = (uint32_t)d[9] | (uint32_t)d[10] << 8 | (uint32_t)d[11] << 16 |
        (uint32_t)d[12] << 24;
  if (d[6] >= 8u || d[13] >= 3u || len < 24u || len > PLAT_STORE_MAX)
    result = 2;
  else if (engine.playing || engine.velocity || engine.level > .0001f)
    result = 3;
  else {
    plat_host_patience(500u, 10000u);
    result = 0;
    for (off = 0; off < len;) {
      uint32_t chunk = len - off;
      if (chunk > 128u)
        chunk = 128u;
      if (plat_host_read(off, song_wire + off, chunk)) {
        result = 4;
        break;
      }
      off += chunk;
    }
    if (!result &&
        (k9_crc(song_wire, len) != crc || !k9_decode(&custom, song_wire, len)))
      result = 5;
    if (!result && plat_store_save(library_object(d[13], d[6]), song_wire, len))
      result = 6;
    if (!result) {
      prefs.slot = d[6];
      prefs.kind = d[13];
      load_pending = 1;
      library_busy = 1;
      library_cache_load();
      library_busy = 0;
      app_say("SONG TRANSFERRED", "");
    }
    plat_host_patience(5000u, 0u);
  }
  plat_host_read(0xC2000000u | result, &ack, 1u);
}

int app_backup_playing(void) {
  return transfer_state.active || engine.playing || engine.velocity ||
         engine.level > .0001f;
}
void app_backup_flush(void) {
  if (dirty && !app_backup_playing() &&
      !plat_store_save(OBJ_SETTINGS, &prefs, sizeof prefs))
    dirty = 0;
}
void app_backup_hold(int on) { backup_hold = on != 0; }
void app_backup_restored(void) {
  app_init();
  app_ui_init();
}

/* Local master: sample-driven song, bounded 1 kHz MIDI clock tick. Never echoes
 * an external master. */
void app_tick(void) {
  static uint32_t phase;
  static uint8_t was;
  uint8_t active = (uint8_t)(engine.playing && !engine.external);
  if (active && !was) {
    phase = 0;
    plat_midi_send(0x0fu | 0xfau << 8, TO_USB | TO_BLE);
  }
  if (!active && was)
    plat_midi_send(0x0fu | 0xfcu << 8, TO_USB | TO_BLE);
  was = active;
  if (active && engine.song) {
    phase += (uint32_t)(prefs.tempo ? prefs.tempo : engine.song->bpm) * 24u;
    if (phase >= 60000u) {
      phase -= 60000u;
      plat_midi_send(0x0fu | 0xf8u << 8, TO_USB | TO_BLE);
    }
  }
}
