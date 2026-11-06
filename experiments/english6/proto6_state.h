/* SPDX-License-Identifier: MIT; original isolated English source/filter research. */
#ifndef P6_STATE_H
#define P6_STATE_H
typedef struct {float g,k,a,b,c,s1,s2;} p6_band;
typedef struct {
 p6_band band[6],fric;
 float f[6],bw[6],w[6],cal,phase,flow,source_last,level,voice,noise,gain;
 float raw_peak,band_peak,source_peak;unsigned init,control,last_phone;
 unsigned long frames,nonfinite,over;
} p6_state;
#endif
