/* SPDX-License-Identifier: MIT. Original TPT bandpass/glottal prototype.
 * No external synthesizer code, coefficients, waveforms or recordings used. */
#include "kira.h"
#include "articulation.h"
#include "proto6_profiles.h"
static float limit(float x,float a,float b){return x<a?a:x>b?b:x;}
static float absolute6(float x){return x<0?-x:x;}
static float shape(float x){return x*x*(3-2*x);}
/* tan(x) series on x<=.57: control-rate only, no libm call in native audio. */
static void tune(p6_band *b,float f,float width){
 float x=3.141592654f*limit(f,100,8000)*(1.0f/44100),x2=x*x;
 b->g=x*(1+x2*(.333333333f+x2*(.133333333f+x2*.053968254f)));
 b->k=limit(width/f,.05f,2.5f);b->a=1/(1+b->g*(b->g+b->k));b->b=b->g*b->a;b->c=b->g*b->b;
}
static float band(p6_band *b,float x){float v3=x-b->s2,v1=b->a*b->s1+b->b*v3,v2=b->s2+b->b*b->s1+b->c*v3;b->s1=2*v1-b->s1;b->s2=2*v2-b->s2;return b->k*v1;}
static int nucleus(unsigned p){return p==K9_AA||p==K9_AE||p==K9_AH||p==K9_AO||p==K9_AW||p==K9_AY||p==K9_EH||p==K9_ER||p==K9_EY||p==K9_IH||p==K9_IY||p==K9_OW||p==K9_OY||p==K9_UH||p==K9_UW;}
static unsigned vowel_target(k9_engine *e){
 if(nucleus(e->phone))return e->phone;
 if(e->playing&&e->song){for(unsigned j=e->next;j<e->song->count&&j<e->next+5;j++)if(nucleus(e->song->events[j].phone))return e->song->events[j].phone;}
 return K9_AH;
}
static void profiles(k9_engine *e){
 p6_state *s=&e->prototype;unsigned p=e->phone,v=vowel_target(e),to=v;float t=0;
 if(v==K9_AY){v=K9_AA;to=K9_IY;}else if(v==K9_AW){v=K9_AA;to=K9_UW;}else if(v==K9_EY){v=K9_EH;to=K9_IY;}else if(v==K9_OW){v=K9_AO;to=K9_UW;}else if(v==K9_OY){v=K9_AO;to=K9_IY;}
 if(v!=to&&e->phone_frames)t=limit((float)(e->sample-e->phone_sample)/(float)e->phone_frames,0,1);
 float scale=p6_voice_scale[e->voice%7],morph=limit(e->morph,0,1);scale+=(p6_voice_scale[(e->voice+1)%7]-scale)*morph;
 int nasal=p==K9_M||p==K9_N||p==K9_NG;float weight[6]={.50f,-.29f,.14f,-.06f,0,.01f};
 float target[6];for(unsigned i=0;i<4;i++)target[i]=(p6_formants[v][i]+(p6_formants[to][i]-p6_formants[v][i])*t)*scale;
 /* Prototype pitch-aware R1 floor, motivated by soprano resonance research;
  * R2 contrasts remain the independent English measurements. */
 if(e->freq>target[0])target[0]+=(e->freq*.98f-target[0])*limit((e->freq-350)/450,0,1);
 target[1]=target[1]<target[0]*1.2f?target[0]*1.2f:target[1];target[4]=280*scale;target[5]=6100*scale;
 float widths[6]={100,150,210,280,140,2500};
 if(nasal){weight[0]=.08f;weight[1]=-.025f;weight[2]=.01f;weight[3]=0;weight[4]=.6f;weight[5]=0;}
 float vg=nucleus(p)||p==K9_L||p==K9_R||p==K9_W||p==K9_Y||nasal?1:0;
 float noise=0,center=4500,width=3000;
 switch(p){case K9_S:case K9_Z:center=6600;width=3000;noise=.14f;vg=p==K9_Z?.3f:0;break;
 case K9_SH:case K9_ZH:case K9_CH:case K9_JH:center=3400;width=2200;noise=.14f;vg=(p==K9_ZH||p==K9_JH)?.3f:0;break;
 case K9_F:case K9_V:center=5200;width=5000;noise=.08f;vg=p==K9_V?.3f:0;break;
 case K9_TH:case K9_DH:center=4100;width=5000;noise=.065f;vg=p==K9_DH?.3f:0;break;
 case K9_P:case K9_B:center=1800;width=3500;noise=.11f;vg=p==K9_B?.3f:0;break;
 case K9_T:case K9_D:center=5100;width=2600;noise=.11f;vg=p==K9_D?.3f:0;break;
 case K9_K:case K9_G:center=2700;width=2100;noise=.11f;vg=p==K9_G?.3f:0;break;
 case K9_HH:vg=0;noise=0;break;default:break;}
 if(p==K9_SIL)vg=0;
 float smoothing=s->init?.08f:1; /* 16-frame control block, ~4.4ms coefficient trajectory. */
 for(unsigned i=0;i<6;i++){s->f[i]+=(target[i]-s->f[i])*smoothing;s->bw[i]+=(widths[i]-s->bw[i])*smoothing;s->w[i]+=(weight[i]-s->w[i])*smoothing;tune(&s->band[i],s->f[i],s->bw[i]);}
 tune(&s->fric,center,width);s->voice=vg;s->noise=noise;
 float note=limit((float)e->note,48,72),u=(note-48)/12;unsigned j=u>=1?1:0;u-=j;
 float gain=p6_pitch_gain[e->voice%7][p][j]+(p6_pitch_gain[e->voice%7][p][j+1]-p6_pitch_gain[e->voice%7][p][j])*u;
 s->cal+=(gain-s->cal)*smoothing;s->init=1;s->last_phone=p;
}
void p6_process(k9_engine *e,float *lr){
 p6_state *s=&e->prototype;unsigned p=e->phone;
 e->freq+=(k9_pitch[e->note]*e->bend-e->freq)*limit(e->glide*2,.002f,.08f);
 if(!s->control||p!=s->last_phone){profiles(e);s->control=16;}s->control--;
 float dt=e->freq*(1.0f/44100),close=.10f+.10f*limit((e->freq-450)/650,0,1);s->phase+=dt;if(s->phase>=1)s->phase-=1;
 float flow=0;if(s->phase<.60f)flow=shape(s->phase/.60f);else if(s->phase<.60f+close)flow=1-shape((s->phase-.60f)/close);
 float source=(flow-s->flow)/dt*(close/1.5f);s->flow=flow;float emphasized=(source-.4f*s->source_last)/1.4f;s->source_last=source;
 e->rng^=e->rng<<13;e->rng^=e->rng>>17;e->rng^=e->rng<<5;float noise=(float)(int32_t)e->rng*(1.0f/2147483648.0f);
 k9_articulation art=k9_articulate(p,e->sample-e->phone_sample,e->phone_frames);
 float aspiration=noise*flow*(p==K9_HH?.4f:.008f+limit(e->breath,0,.5f)*.03f);
 float drive=emphasized*s->voice*art.voiced+aspiration;float y=0;
 for(unsigned i=0;i<6;i++){float z=band(&s->band[i],drive);if(absolute6(z)>s->band_peak)s->band_peak=absolute6(z);y+=z*s->w[i];}
 y+=band(&s->fric,noise)*s->noise*art.noise;
 float target=(float)e->velocity/127*limit(e->expression,0,1.2f);if(e->playing&&e->next){unsigned stress=e->song->events[e->next-1].stress;target*=stress==1?1:stress==2?.92f:.8f;}
 s->level+=(target-s->level)*(target>s->level?.004f:.002f);e->level=s->level;
 y*=s->level*s->cal;
 if(absolute6(source)>s->source_peak)s->source_peak=absolute6(source);if(absolute6(y)>s->raw_peak)s->raw_peak=absolute6(y);if(absolute6(y)>.94f)s->over++;
 if(!(y<100&&y>-100)){s->nonfinite++;y=0;}s->frames++;
 /* No output clamp: headroom instrumentation must see the real waveform. */
 lr[0]=lr[1]=y;
}
