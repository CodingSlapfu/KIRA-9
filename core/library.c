/* SPDX-License-Identifier: MIT */
#include "library.h"
#include "memory.h"
static uint32_t l32(const uint8_t *p) {
  return p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 |
         (uint32_t)p[3] << 24;
}
static void s32(uint8_t *p, uint32_t n) {
  p[0] = (uint8_t)n;
  p[1] = (uint8_t)(n >> 8);
  p[2] = (uint8_t)(n >> 16);
  p[3] = (uint8_t)(n >> 24);
}
int k9_preset_valid(const k9_preset *p) {
  unsigned i;
  if (p->voice >= 7 || p->style >= 8 || p->emotion >= 4 || p->morph > 100 ||
      p->breath > 100 || p->vibrato > 100 || p->glide > 100 ||
      p->harmony < -12 || p->harmony > 12 || p->expression > 127)
    return 0;
  for (i = 0; i < 7; i++)
    if (p->reserved[i])
      return 0;
  return 1;
}
int k9_voicebank_read(const uint8_t *p, uint16_t n, k9_preset out[8]) {
  unsigned i;
  if (n < 146 || n > 3840 || memcmp(p, "K9V2", 4) || p[4] != 2 || p[5] != 4 ||
      p[6] != 8 || p[7] || l32(p + 8) != n - 16u ||
      l32(p + 12) != k9_crc(p + 16, n - 16u) || p[144] != '{' ||
      p[n - 1] != '}')
    return 0;
  for (i = 0; i < 8; i++)
    if (!k9_preset_valid((const k9_preset *)(p + 16 + i * 16)))
      return 0;
  if (out)
    memcpy(out, p + 16, 128);
  return 1;
}
uint16_t k9_voicebank_write(uint8_t *p, uint16_t n, const k9_preset in[8]) {
  unsigned i;
  for (i = 0; i < 8; i++)
    if (!k9_preset_valid(in + i))
      return 0;
  if (!k9_voicebank_read(p, n, 0)) {
    n = 146;
    memset(p, 0, n);
    memcpy(p, "K9V2", 4);
    p[4] = 2;
    p[5] = 4;
    p[6] = 8;
    p[144] = '{';
    p[145] = '}';
  }
  memcpy(p + 16, in, 128);
  s32(p + 8, n - 16u);
  s32(p + 12, k9_crc(p + 16, n - 16u));
  return n;
}

int k9_score_preset(const uint8_t *p, uint16_t n, k9_preset *out) {
  uint32_t count;
  if (n < 42 || n > 6170 || memcmp(p, "K9S3", 4) || p[4] != 3 || p[5])
    return 0;
  count = p[6] | (uint32_t)p[7] << 8;
  if (!count || count > 512 || 24u + 8u * count + 18u > n || l32(p + 16) != n ||
      l32(p + 20) != (k9_crc(p + 24, n - 24u) ^ k9_crc(p, 20u)))
    return 0;
  const k9_preset *preset = (const k9_preset *)(p + 24u + 8u * count);
  if (!k9_preset_valid(preset))
    return 0;
  if (out)
    memcpy(out, preset, sizeof *out);
  return 1;
}
int k9_score_update_preset(uint8_t *p, uint16_t n, const k9_preset *preset) {
  uint32_t count;
  if (!k9_score_preset(p, n, 0) || !k9_preset_valid(preset))
    return 0;
  count = p[6] | (uint32_t)p[7] << 8;
  memcpy(p + 24u + 8u * count, preset, 16);
  s32(p + 20, k9_crc(p + 24, n - 24u) ^ k9_crc(p, 20u));
  return 1;
}

int k9_arrangement_read(const uint8_t *p,uint16_t n,k9_arrangement *out){unsigned i;if(n!=29||memcmp(p,"K9A1",4)||p[4]!=1||p[5]!=5||p[6]||p[7]||l32(p+8)!=13||l32(p+12)!=k9_crc(p+16,13))return 0;uint16_t tempo=p[16]|(uint16_t)p[17]<<8;if((tempo&&(tempo<30||tempo>300))||!p[18]||p[18]>8||p[19]>1||p[20]>1)return 0;for(i=0;i<8;i++)if(p[21+i]>7)return 0;if(out){out->tempo=tempo;out->count=p[18];out->loop=p[19];out->active=p[20];memcpy(out->slots,p+21,8);}return 1;}
uint16_t k9_arrangement_write(uint8_t *p,const k9_arrangement *a){memset(p,0,29);memcpy(p,"K9A1",4);p[4]=1;p[5]=5;s32(p+8,13);p[16]=(uint8_t)a->tempo;p[17]=(uint8_t)(a->tempo>>8);p[18]=a->count;p[19]=a->loop;p[20]=a->active;memcpy(p+21,a->slots,8);s32(p+12,k9_crc(p+16,13));return k9_arrangement_read(p,29,0)?29:0;}
