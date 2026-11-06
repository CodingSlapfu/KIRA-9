/* SPDX-License-Identifier: MIT. Original implementation. Source residual data
 * is modified CMU ARCTIC SLT0.95; see data notice, not covered by this MIT tag. */
#include "residual.h"
#include "units.h"
#include "grains.h"
void rp_init(rp_state *s){unsigned char *p=(unsigned char*)s;for(unsigned i=0;i<sizeof(*s);i++)p[i]=0;}
static void coefficients(rp_state *s,const int16_t *k){
 float a[12]={0},next[12];
 for(unsigned m=0;m<12;m++){
  float r=(float)k[m]*(1.0f/32768.0f);
  for(unsigned j=0;j<m;j++)next[j]=a[j]+r*a[m-1-j];
  next[m]=r;for(unsigned j=0;j<=m;j++)a[j]=next[j];
 }
 for(unsigned j=0;j<12;j++)s->a[j]=a[j];
}
void rp_start(rp_state *s,unsigned unit,unsigned midi,unsigned hold){
 if(unit>=16)return;
 rp_init(s);s->unit=unit;s->holding=hold && unit>=12;s->running=1;s->frame=~0u;
 s->period=rp_period[midi>127?127:midi];
}
void rp_stop(rp_state *s){rp_init(s);}
static float sample16(rp_state *s){
 if(!s->running)return 0;
 const rp_unit *u=&rp_units[s->unit];float residual=0;
 if(s->holding){
  /* Add a native-time, Hann-windowed two-period residual grain at each
   * target pitchmark. No data respeeding to change the vocal-tract envelope. */
  if(s->phase<=0){
   /* phase<0 is the fractional time since the desired pitchmark. Evaluate
    * the grain at that phase rather than rounding every pulse to16kHz's
    * integer grid (the first diagnostic exposed off-harmonic sidebands). */
   float fraction=-s->phase;
   static const unsigned path[9]={2,3,4,3,2,1,0,1,2};
   unsigned slot=(s->grain_tick/8u)%8u;
   unsigned g0=path[slot],g1=path[slot+1u];
   float blend=(float)(s->grain_tick%8u)*.125f;
   unsigned vowel=s->unit-12u;
   const int8_t *q0=mg_res[vowel][g0],*q1=mg_res[vowel][g1];
   float scale0=mg_scale[vowel][g0],scale1=mg_scale[vowel][g1];
   for(unsigned i=0;i<u->samples;i++){
    float a0=(float)q0[i],b0=i+1<u->samples?(float)q0[i+1]:0;
    float a1=(float)q1[i],b1=i+1<u->samples?(float)q1[i+1]:0;
    float x0=(a0+(b0-a0)*fraction)*scale0;
    float x1=(a1+(b1-a1)*fraction)*scale1;
    s->ring[(s->head+i)&511u]+=x0+(x1-x0)*blend;
   }
   s->grain_tick=(s->grain_tick+1u)%64u;
   s->phase+=s->period;
  }
  s->phase-=1;residual=s->ring[s->head];s->ring[s->head]=0;s->head=(s->head+1)&511u;
  if(s->frame!=0){coefficients(s,u->reflection);s->frame=0;}
 }else{
  if(s->pos>=u->samples){s->running=0;return 0;}
  unsigned f=s->pos/160;if(f>=u->frames)f=u->frames-1;
  if(s->frame!=f){coefficients(s,u->reflection+f*12);s->frame=f;}
  residual=(float)u->residual[s->pos++]*u->scale;
 }
 float y=residual;
 for(unsigned j=0;j<12;j++)y-=s->a[j]*s->history[j];
 for(unsigned j=11;j;j--)s->history[j]=s->history[j-1];s->history[0]=y;
 return y*.35f; /* fixed in PLAN before measuring; no clamp or limiter */
}
void rp_render(rp_state *s,float *out,unsigned n){
 for(unsigned i=0;i<n;i++){
  s->resample+=16000.0f/44100.0f;
  if(s->resample>=1){s->resample-=1;s->last=s->next;s->next=sample16(s);}
  out[i]=s->last+(s->next-s->last)*s->resample;
 }
}
unsigned rp_size(void){return sizeof(rp_state);}
unsigned rp_data_size(void){return RP_DATA_BYTES+MG_EXTRA_BYTES;}
