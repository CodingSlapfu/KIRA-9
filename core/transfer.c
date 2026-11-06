/* SPDX-License-Identifier: MIT */
#include "transfer.h"
#include "kira.h"
#include "memory.h"
static uint16_t x16(const uint8_t *p){return p[0]|(uint16_t)p[1]<<8;}
static uint32_t x32(const uint8_t *p){return x16(p)|(uint32_t)x16(p+2)<<16;}
static void w16(uint8_t *p,uint16_t n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void w32(uint8_t *p,uint32_t n){w16(p,(uint16_t)n);w16(p+2,(uint16_t)(n>>16));}
void k9_transfer_init(k9_transfer *t){memset(t,0,sizeof *t);}
void k9_transfer_poll(k9_transfer *t,uint32_t now){if(t->active&&(int32_t)(now-t->deadline)>=0)t->active=0;}
uint16_t k9_transfer_command(k9_transfer *t,const k9_transfer_io *io,uint32_t now,uint8_t op,const uint8_t *p,uint16_t n,uint8_t *r,uint16_t cap){
 uint16_t tx,nout=0,offset=0,total=0;uint32_t crc=0;uint8_t result=K9_X_BAD;
 if(n<2||cap<13)return 0;tx=x16(p);k9_transfer_poll(t,now);
 if(op==0x62&&n==10){uint8_t kind=p[2],slot=p[3];uint16_t len=x16(p+4);uint32_t sum=x32(p+6);
  if(kind>4||slot>7||(kind>=3&&slot)||!len||len>K9_XFER_MAX)result=K9_X_BOUNDS;
  else if(io->busy(io->ctx))result=K9_X_BUSY;
  else if(t->active&&t->transaction!=tx)result=K9_X_BUSY;
  else if(t->active&&t->transaction==tx){result=t->kind==kind&&t->slot==slot&&t->length==len&&t->crc==sum?K9_X_OK:K9_X_BAD;}
  else{t->transaction=tx;t->kind=kind;t->slot=slot;t->length=len;t->crc=sum;t->received=0;t->active=1;t->last_valid=0;result=K9_X_OK;}
  if(!result){t->deadline=now+5000;offset=t->received;total=t->length;crc=t->crc;}
 }else if(op==0x63&&n>4&&n<=4+K9_XFER_CHUNK){offset=x16(p+2);total=t->length;
  if(!t->active||tx!=t->transaction)result=K9_X_EXPIRED;
  else if(offset>t->received||offset+n-4>t->length)result=K9_X_ORDER;
  else if(offset<t->received){result=offset+n-4<=t->received&&!memcmp(t->data+offset,p+4,n-4)?K9_X_OK:K9_X_ORDER;}
  else{memcpy(t->data+offset,p+4,n-4);t->received=(uint16_t)(offset+n-4);result=K9_X_OK;}
  offset=t->received;if(!result)t->deadline=now+5000;
 }else if(op==0x64&&n==2){
  if(!t->active&&t->last_valid&&tx==t->last_transaction)result=t->last_result;
  else if(!t->active||tx!=t->transaction)result=K9_X_EXPIRED;
  else if(t->received!=t->length)result=K9_X_ORDER;
  else if(io->busy(io->ctx))result=K9_X_BUSY;
  else if(k9_crc(t->data,t->length)!=t->crc||!io->validate(io->ctx,t->kind,t->data,t->length))result=K9_X_CRC;
  else if(io->save(io->ctx,t->kind,t->slot,t->data,t->length))result=K9_X_SAVE;
  else result=K9_X_OK;
  if(t->active&&tx==t->transaction&&result!=K9_X_ORDER&&result!=K9_X_BUSY){t->active=0;t->last_transaction=tx;t->last_result=result;t->last_valid=1;}
  total=t->length;offset=t->received;crc=t->crc;
 }else if(op==0x65&&n==6){uint8_t kind=p[2],slot=p[3];int got;offset=x16(p+4);
  if(kind>4||slot>7||(kind>=3&&slot))result=K9_X_BOUNDS;
  else if(t->active||io->busy(io->ctx))result=K9_X_BUSY;
  else if((got=io->load(io->ctx,kind,slot,t->data,K9_XFER_MAX))<0)result=K9_X_MISSING;
  else if(got>(int)K9_XFER_MAX||offset>(uint16_t)got)result=K9_X_BOUNDS;
  else{total=(uint16_t)got;crc=k9_crc(t->data,total);nout=(uint16_t)(total-offset);if(nout>K9_XFER_CHUNK)nout=K9_XFER_CHUNK;if(cap<13u+nout)return 0;memcpy(r+13,t->data+offset,nout);result=K9_X_OK;}
 }else if(op==0x66&&n==2){if(t->active&&t->transaction!=tx)result=K9_X_BUSY;else{t->active=0;result=K9_X_OK;}}
 w16(r,tx);r[2]=op;r[3]=result;w16(r+4,offset);w16(r+6,total);w32(r+8,crc);r[12]=(uint8_t)nout;return (uint16_t)(13+nout);
}
