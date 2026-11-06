/* SPDX-License-Identifier: MIT */
#include "library.h"
#include "memory.h"
static uint32_t l32(const uint8_t *p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void s32(uint8_t *p,uint32_t n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);p[2]=(uint8_t)(n>>16);p[3]=(uint8_t)(n>>24);}
int k9_preset_valid(const k9_preset *p){unsigned i;if(p->voice>=7||p->style>=8||p->emotion>=4||p->morph>100||p->breath>100||p->vibrato>100||p->glide>100||p->harmony < -12||p->harmony>12||p->expression>127)return 0;for(i=0;i<7;i++)if(p->reserved[i])return 0;return 1;}
int k9_voicebank_read(const uint8_t *p,uint16_t n,k9_preset out[8]){unsigned i;if(n<146||n>3840||memcmp(p,"K9V2",4)||p[4]!=2||p[5]!=4||p[6]!=8||p[7]||l32(p+8)!=n-16u||l32(p+12)!=k9_crc(p+16,n-16u)||p[144]!='{'||p[n-1]!='}')return 0;for(i=0;i<8;i++)if(!k9_preset_valid((const k9_preset *)(p+16+i*16)))return 0;if(out)memcpy(out,p+16,128);return 1;}
uint16_t k9_voicebank_write(uint8_t *p,uint16_t n,const k9_preset in[8]){unsigned i;for(i=0;i<8;i++)if(!k9_preset_valid(in+i))return 0;if(!k9_voicebank_read(p,n,0)){n=146;memset(p,0,n);memcpy(p,"K9V2",4);p[4]=2;p[5]=4;p[6]=8;p[144]='{';p[145]='}';}memcpy(p+16,in,128);s32(p+8,n-16u);s32(p+12,k9_crc(p+16,n-16u));return n;}
