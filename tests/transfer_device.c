/* SPDX-License-Identifier: MIT; pipe fixture runs the exact device transfer and validation code. */
#include "kira.h"
#include "transfer.h"
#include "library.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t objects[5][8][3840];static uint16_t lengths[5][8];static unsigned saves;static int busy,fail_save;static k9_song scratch;
static int isbusy(void *p){(void)p;return busy;}
static int load(void *p,uint8_t kind,uint8_t slot,uint8_t *data,uint16_t cap){unsigned n=lengths[kind][slot];(void)p;if(!n)return -1;if(n>cap)return -1;memcpy(data,objects[kind][slot],n);return (int)n;}
static int valid(void *p,uint8_t kind,const uint8_t *data,uint16_t n){(void)p;return kind<3?k9_decode(&scratch,data,n):kind==4?k9_voicebank_read(data,n,0):k9_document_valid(data,n,kind);}
static int save(void *p,uint8_t kind,uint8_t slot,const uint8_t *data,uint16_t n){(void)p;if(fail_save)return -1;memcpy(objects[kind][slot],data,n);lengths[kind][slot]=n;saves++;return 0;}
int main(void){char line[1000];k9_transfer transfer;k9_transfer_io io={0,isbusy,load,valid,save};uint32_t now=0;k9_transfer_init(&transfer);while(fgets(line,sizeof line,stdin)){unsigned op;uint8_t data[256],out[128];uint16_t n=0,got;char *p=line,*end;if(!strncmp(line,"stats",5)){printf("!%u\n",saves);fflush(stdout);continue;}if(!strncmp(line,"busy",4)){busy=atoi(line+5);puts("!");fflush(stdout);continue;}if(!strncmp(line,"fail",4)){fail_save=atoi(line+5);puts("!");fflush(stdout);continue;}if(!strncmp(line,"advance",7)){now+=(uint32_t)strtoul(line+8,0,10);puts("!");fflush(stdout);continue;}op=(unsigned)strtoul(p,&end,16);p=end;while(*p&&*p!='\n'){unsigned x=(unsigned)strtoul(p,&end,16);if(end==p)break;if(n>=sizeof data)return 2;data[n++]=(uint8_t)x;p=end;}got=k9_transfer_command(&transfer,&io,++now,(uint8_t)op,data,n,out,sizeof out);for(unsigned i=0;i<got;i++)printf("%02x",out[i]);putchar('\n');fflush(stdout);}return 0;}
