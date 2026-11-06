/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include <string.h>
static float k9_abs(float v){return v<0?-v:v;}
void k9_init(k9_engine *e){memset(e,0,sizeof(*e));e->rng=0x4b495241u;e->note=69;e->freq=440;e->glide=.002f;e->breath=.03f;e->source=255;}
void k9_stop(k9_engine *e){e->playing=0;e->velocity=0;e->phone=K9_SIL;e->viseme=0;}
void k9_start(k9_engine *e,const k9_song *s){k9_stop(e);if(!k9_song_validate(s))return;e->song=s;e->sample=0;e->tick=0;e->clock_phase=0;e->next=0;e->event_end=0;e->playing=1;}
void k9_note(k9_engine *e,uint8_t p,uint8_t n,uint8_t v){if(p>=K9_NPHONE||n>127||v>127)return;e->phone=p;e->note=n;e->velocity=v;e->viseme=k9_phones[p].viseme;}
void k9_midi(k9_engine *e,uint8_t src,uint8_t st,uint8_t d1,uint8_t d2){uint8_t kind=st&0xf0;if(d1>127||d2>127)return;if(e->external&&src!=e->source)return;if(st==0xf8){if(e->external){e->tick+=4;e->clocks++;e->last_clock=e->sample;}return;}if(st==0xfa){if(e->external&&e->song)k9_start(e,e->song);return;}if(st==0xfb){if(e->external&&e->song)e->playing=1;return;}if(st==0xfc){if(e->external)k9_stop(e);return;}if(kind==0x90&&d2){k9_note(e,K9_AH,d1,d2);}else if(kind==0x80||(kind==0x90&&!d2)){if(e->note==d1)e->velocity=0;}else if(kind==0xb0){if(d1==120||d1==123)k9_stop(e);else if(d1==1)e->vibrato=(float)d2/127.0f;else if(d1==2)e->breath=(float)d2/254.0f;}else if(kind==0xc0){e->voice=d1%7;}}
void k9_render(k9_engine *e,float *lr,uint32_t n){uint32_t i;for(i=0;i<n;i++){
 const k9_phone *p;float x,noise,target,s=0;unsigned b;
 if(e->playing&&e->song){if(e->next<e->song->count&&e->tick>=e->song->events[e->next].tick){const k9_event *v=&e->song->events[e->next++];k9_note(e,v->phone,v->note,v->velocity);e->event_end=v->tick+v->duration;}if(e->tick>=e->event_end)e->velocity=0;if(e->tick>=e->song->ticks)k9_stop(e);if(!e->external){e->clock_phase+=(uint32_t)e->song->bpm*96u;if(e->clock_phase>=K9_RATE*60u){e->clock_phase-=K9_RATE*60u;e->tick++;}}}
 if(e->external&&e->playing&&e->sample-e->last_clock>K9_RATE*2u){e->late_clocks++;k9_stop(e);}
 p=&k9_phones[e->phone];target=e->velocity?(float)e->velocity/127.0f:0;e->level+=(target-e->level)*.003f;
 e->freq+=(k9_pitch[e->note]-e->freq)*e->glide;e->phase+=e->freq/K9_RATE;if(e->phase>=1)e->phase-=1;
 /* differentiated glottal pulse; voice identity changes glottal open quotient */
 {float q=.25f+.035f*(float)e->voice;float t=e->phase;x=t<q?(1.0f-2.0f*t/q):-.12f;}
 e->rng^=e->rng<<13;e->rng^=e->rng>>17;e->rng^=e->rng<<5;noise=(float)(int32_t)e->rng/2147483648.0f;
 x=x*(p->voiced?1.0f-p->noise:0)+noise*(p->noise+e->breath*.1f);
 for(b=0;b<3;b++){float y;e->a[b]+=(p->a[b]-e->a[b])*.002f;e->r[b]+=(p->r[b]-e->r[b])*.002f;e->gain[b]+=(p->gain[b]-e->gain[b])*.002f;y=x*e->gain[b]+e->a[b]*e->z1[b]-e->r[b]*e->z2[b];if(k9_abs(y)<1e-18f)y=0;e->z2[b]=e->z1[b];e->z1[b]=y;s+=y;}
 s*=e->level*.55f;if(s>.95f)s=.95f;if(s<-.95f)s=-.95f;lr[i*2]=s;lr[i*2+1]=s;e->sample++;
 }}
k9_face k9_face_at(const k9_engine *e,uint32_t ms,uint8_t emotion,uint8_t twitch){k9_face f;uint32_t gap=twitch==1?17000u:9000u;memset(&f,0,sizeof f);f.mouth=e->viseme;f.open=(uint16_t)(e->level*30);f.blink=(ms%4300u)<110u;f.gaze=(int8_t)((ms/2700u)%5u)-2;f.jaw=(int8_t)(f.open/4u);f.cheek=(int8_t)(emotion%4);if(twitch&&ms%gap<90u){f.cheek+=3;f.neck=2;f.gaze=-3;}return f;}
