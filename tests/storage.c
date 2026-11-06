/* SPDX-License-Identifier: MIT; tests the unmodified MPL-2.0 platform storage implementation. */
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>
#define PLAT_HOST 1
#include "../app/app.h"
static uint8_t flash[1048576],baseline[1048576];static int cut=-1;
static int fail(void){if(cut<0)return 0;if(!cut)return 1;cut--;return 0;}
static int st_read(uint32_t off,void *p,uint32_t n){assert(off+n<=sizeof flash);memcpy(p,flash+off,n);return 0;}
static int st_erase(uint32_t off){assert(!(off&4095));if(fail())return -1;memset(flash+off,255,4096);return 0;}
static int st_prog(uint32_t off,const void *p,uint32_t n){const uint8_t *s=p;unsigned i;assert((off&255)+n<=256);if(fail())return -1;for(i=0;i<n;i++)flash[off+i]&=s[i];return 0;}
#include "../platform/device/storage.c"
int main(void){uint8_t old[3840],next[3840],out[3840];unsigned obj,j;memset(flash,255,sizeof flash);memset(old,0x55,sizeof old);memset(next,0xaa,sizeof next);
 for(obj=0;obj<OBJ_NOBJ;obj++){assert(st_save(obj,old,sizeof old)==0);assert(st_load(obj,out,sizeof out)==sizeof out&&!memcmp(old,out,sizeof old));}
 memcpy(baseline,flash,sizeof flash);
 for(obj=0;obj<OBJ_NOBJ;obj++){uint32_t a=st_sector(obj,0),b=st_sector(obj,1)+4096;unsigned other;assert((a>=0x97000&&b<=0xe0000)||(a>=0xfc000&&b<=0xff000));for(other=0;other<obj;other++)assert(b<=st_sector(other,0)||a>=st_sector(other,1)+4096);
  for(j=0;j<25;j++){memcpy(flash,baseline,sizeof flash);cut=(int)j;(void)st_save(obj,next,sizeof next);cut=-1;assert(st_load(obj,out,sizeof out)==sizeof out);assert(!memcmp(out,old,sizeof out)||!memcmp(out,next,sizeof out));}
 }
 puts("PASS all 29 actual app objects, full-size saves, disjoint partitions and 725 erase/program power-cut injections preserve old or new record");return 0;}
