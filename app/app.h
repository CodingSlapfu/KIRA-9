/* SPDX-License-Identifier: MIT */
#pragma once
#include <stdint.h>
#include "plat.h"
#define APP_NAME "KIRA-9"
#define APP_SPLASH_RGB RGB(255,110,90)
#define APP_BLOCK 256u
#define APP_CANVAS_PX (240u*40u)
#define APP_HOST_EXPECT
#define APP_BLE_AT_BOOT 0
/* Exclusive A/B pairs in platform's allowed storage windows. */
enum {OBJ_SETTINGS,OBJ_PANEL,OBJ_BLE,OBJ_SONG0,OBJ_SONG1,OBJ_SONG2,OBJ_SONG3,OBJ_NOBJ};
#define APP_STORE_MAP {0xFC000u,0xDC000u,0xDE000u,0x97000u,0x99000u,0x9B000u,0x9D000u}
void app_init(void);
void app_render(int32_t*,uint32_t,uint32_t);
void app_panic(void);
void app_ui_init(void);
void app_frame(void);
void app_input_only(void);
void app_say(const char*,const char*);
int app_expect(const char*,int*);
