/* SPDX-License-Identifier: MIT */
#pragma once
#include "plat.h"
#include <stdint.h>
#define APP_NAME "KIRA-9"
#define APP_SPLASH_RGB RGB(255, 110, 90)
#define APP_BLOCK 256u
#define APP_CANVAS_PX (240u * 40u)
#define APP_TICK
#define APP_USB_CMD
#define APP_HOST_EXPECT
#define APP_BLE_AT_BOOT 0
/* Exclusive A/B pairs in platform's allowed storage windows. */
enum {
  OBJ_SETTINGS,
  OBJ_PANEL,
  OBJ_BLE,
  OBJ_SONG0,
  OBJ_SONG1,
  OBJ_SONG2,
  OBJ_SONG3,
  OBJ_SONG4,
  OBJ_SONG5,
  OBJ_SONG6,
  OBJ_SONG7,
  OBJ_PHRASE0,
  OBJ_PHRASE1,
  OBJ_PHRASE2,
  OBJ_PHRASE3,
  OBJ_PHRASE4,
  OBJ_PHRASE5,
  OBJ_PHRASE6,
  OBJ_PHRASE7,
  OBJ_WORD0,
  OBJ_WORD1,
  OBJ_WORD2,
  OBJ_WORD3,
  OBJ_WORD4,
  OBJ_WORD5,
  OBJ_WORD6,
  OBJ_WORD7,
  OBJ_PRONUNCIATION,
  OBJ_VOICES,
  OBJ_ARRANGEMENT,
  OBJ_NOBJ
};
#define APP_STORE_MAP                                                          \
  {0xfc000u, 0xdc000u, 0xde000u, 0x97000u, 0x99000u, 0x9b000u,                 \
   0x9d000u, 0xa0000u, 0xa2000u, 0xa4000u, 0xa6000u, 0xa8000u,                 \
   0xaa000u, 0xac000u, 0xae000u, 0xb0000u, 0xb2000u, 0xb4000u,                 \
   0xb6000u, 0xb8000u, 0xba000u, 0xbc000u, 0xbe000u, 0xc0000u,                 \
   0xc2000u, 0xc4000u, 0xc6000u, 0xc8000u, 0xca000u, 0xcc000u}
#define APP_BACKUP_OBJS                                                        \
  {OBJ_SETTINGS,      OBJ_SONG0,   OBJ_SONG1,      OBJ_SONG2,   OBJ_SONG3,     \
   OBJ_SONG4,         OBJ_SONG5,   OBJ_SONG6,      OBJ_SONG7,   OBJ_PHRASE0,   \
   OBJ_PHRASE1,       OBJ_PHRASE2, OBJ_PHRASE3,    OBJ_PHRASE4, OBJ_PHRASE5,   \
   OBJ_PHRASE6,       OBJ_PHRASE7, OBJ_WORD0,      OBJ_WORD1,   OBJ_WORD2,     \
   OBJ_WORD3,         OBJ_WORD4,   OBJ_WORD5,      OBJ_WORD6,   OBJ_WORD7,     \
   OBJ_PRONUNCIATION, OBJ_VOICES,  OBJ_ARRANGEMENT}
#define APP_BACKUP_MAGIC 0x3142394Bu
#define APP_BACKUP_VERSION 1
#define APP_BACKUP_WHAT                                                        \
  "KIRA-9 user songs, phrases, words, pronunciation, voices and settings"

void app_init(void);
void app_render(int32_t *, uint32_t, uint32_t);
void app_panic(void);
void app_ui_init(void);
void app_frame(void);
void app_input_only(void);
void app_say(const char *, const char *);
int app_expect(const char *, int *);

void app_usb_cmd(const uint8_t *, uint32_t);

int app_backup_playing(void);
void app_backup_flush(void);
void app_backup_hold(int);
void app_backup_restored(void);

void app_tick(void);
