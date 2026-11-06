/* SPDX-License-Identifier: MIT. No external code, recordings or coefficients. */
#include "kira.h"
#include "cues.h"
/* Fixed one-pole coefficients computed offline from 1500/4000 Hz and 44100 Hz.
 * Stable convex updates: bounded input cannot make either state diverge.
 * This intentionally tests consonant cues only; vowels retain baseline DSP. */
static float unit(float x){return x<0?0:x>1?1:x;}
cue_signal cue_step(k9_engine *e,float noise,float voiced,float envelope){
  cue_state *s=&e->cue;
  cue_signal r={voiced,0,0};
  unsigned age=e->sample-e->phone_sample;
  if(s->phone_sample!=e->phone_sample || s->previous!=e->phone){
    s->phone_sample=e->phone_sample;s->previous=e->phone;
    if(e->phone==K9_P){
      /* Closure 24ms; voice onset 55ms after release, carried into vowel.
       * The old envelope ended aspiration at the phone boundary. */
      unsigned closure=1058;
      if(e->phone_frames && closure>e->phone_frames/2)closure=e->phone_frames/2;
      s->release_sample=e->sample+closure;
      s->voice_sample=s->release_sample+2426;s->pending=1;
    }else if(e->phone!=K9_IY && e->phone!=K9_P)s->pending=0;
  }
  s->low+=(noise-s->low)*.19243101f;
  s->mid+=(noise-s->mid)*.43441995f;
  if(e->phone==K9_S || e->phone==K9_SH){
    r.bypass=1;r.voice=0;
    r.direct=envelope*(e->phone==K9_S?.22f*(noise-s->mid):.42f*(s->mid-s->low));
  }else if(e->phone==K9_P || (s->pending && e->phone==K9_IY)){
    int since=(int)(e->sample-s->release_sample);
    int until=(int)(s->voice_sample-e->sample);
    if(since<0){r.voice=0;r.direct=0;r.bypass=1;}
    else if(until>0){
      r.voice=0;r.bypass=1;
      float onset=unit((float)since/88.0f);
      float tail=unit((float)until/220.0f);
      float burst=unit(1.0f-(float)since/220.0f);
      r.direct=onset*tail*(.12f+.18f*burst)*(noise-s->low);
    }else if(e->phone==K9_IY){r.voice*=unit((float)(e->sample-s->voice_sample)/220.0f);s->pending=(e->sample-s->voice_sample)<220;}
    else{r.voice=0;r.bypass=1;}
  }else if(e->phone==K9_B){
    /* Low periodic prevoicing + weak burst, no long aspirated interval. */
    float ms=(float)age*(1000.0f/44100.0f);
    r.bypass=1;r.voice=0;
    float triangle=1.0f-4.0f*(e->phase>.5f?e->phase-.5f:.5f-e->phase);
    r.direct=.045f*unit(ms/3)*triangle;
    if(ms>=18 && ms<24)r.direct+=.09f*unit((ms-18)/1)*unit((24-ms)/2)*(noise-s->low);
  }
  return r;
}
