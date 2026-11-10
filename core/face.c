/* SPDX-License-Identifier: MIT; original KIRA-9 cel portrait and phonetic rig.
 * Row-addressed immutable ROM art; no heap, decompression buffer or DSP changes. */
#include "face.h"
#include "character023.h"
static void layer(uint16_t *p,unsigned y0,unsigned height,unsigned region,int dx,int dy){
 const uint16_t *r=k9_art_regions[region];
 for(unsigned row=0;row<r[3];row++){
  int y=(int)r[1]+(int)row+dy;if(y<(int)y0||y>=(int)(y0+height)||y<0||y>=240)continue;
  unsigned pos=k9_art_rows[r[4]+row],used=0;
  while(used<r[2]){
   unsigned n=k9_art_data[pos++];uint16_t color=k9_art_data[pos++];color|=(uint16_t)k9_art_data[pos++]<<8;
   for(unsigned j=0;j<n;j++){int x=(int)r[0]+(int)used+(int)j+dx;if(x>=0&&x<240)p[(y-y0)*240+x]=color;}used+=n;
  }
 }
}
void k9_face_render(uint16_t *pixels,unsigned y0,unsigned height,const k9_face *f){
 if(y0>=240||!height)return;if(height>240-y0)height=240-y0;
 layer(pixels,y0,height,0,0,0);
 /* Art-derived lids preserve eyelashes/anatomy. Half-lid is used on both
  * sides of the blink. Emotional eye state follows the engine's real pose. */
 if(f->blink>190)layer(pixels,y0,height,2,0,0);
 else if(f->blink>65||f->lid>=3)layer(pixels,y0,height,1,0,0);
 else if(f->brow<0||f->cheek==3)layer(pixels,y0,height,3,0,0);
 /* Small eye tracking moves the registered eye patch by at most one pixel.
  * Head, skin silhouette and cybernetic neck never wobble with the audio. */
 else if(f->gaze)layer(pixels,y0,height,3,f->gaze>0?1:-1,0);
 unsigned mouth=4;
 if(f->mouth!=4&&f->open>2){
  mouth=f->mouth==3?7:f->mouth==2?6:f->mouth==5?8:5;
 }else if(f->cheek==1)mouth=9;
 layer(pixels,y0,height,mouth,0,0);
}
