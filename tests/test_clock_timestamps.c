/* SPDX-License-Identifier: MIT */
#include "kira.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){k9_engine e;k9_init(&e);e.external=1;e.source=2;e.sample=2200;
 k9_clock_at(&e,2,1000);k9_clock_at(&e,2,1919);assert(e.clocks==2&&e.clock_tick==8&&e.last_clock==1919);assert(fabsf(e.clock_interval-918.78125f)<.01f);
 k9_clock_at(&e,2,1000);assert(e.clocks==2);k9_clock_at(&e,8,2150);assert(e.clocks==2);
 e.clocks=1;e.last_clock=0xfffffff0u;e.sample=1024;k9_clock_at(&e,2,903);assert(e.clocks==2&&e.last_clock==903);
 k9_init(&e);e.external=1;e.source=8;unsigned stamp=0;for(unsigned i=0;i<10000;i++){stamp=(unsigned)((i+1)*918.75);e.sample=stamp+(i*97u)%257u;k9_clock_at(&e,8,stamp);}assert(e.clocks==10000&&e.clock_tick==40000);assert(fabsf(e.clock_interval-918.75f)<.2f);
 puts("PASS timestamped burst clocks, delayed/stale/wrong-source handling, wrap and10000 jittered delivery timestamps without tempo drift");return 0;}
