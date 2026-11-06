/* SPDX-License-Identifier: MIT; original KIRA-9 app */
#include "../core/kira.h"
#include "../factory/songs.h"
static void text_cat(char *d,const char *s){unsigned n=0;while(d[n]&&n<38)n++;while(*s&&n<38)d[n++]=*s++;d[n]=0;}
static void int_text(int v,char *d){char b[12];unsigned n=0,j=0;uint32_t u=v<0?0u-(uint32_t)v:(uint32_t)v;if(v<0)d[j++]='-';do{b[n++]=(char)('0'+u%10);u/=10;}while(u);while(n)d[j++]=b[--n];d[j]=0;}
static k9_engine engine;
static k9_song custom;
static uint8_t song_wire[K9_WIRE_MAX];
static float audio_lr[512];
static struct {uint32_t magic;uint8_t song,voice,mode,sync,slot,emotion,twitch,ble;} prefs;
static uint32_t btn_last,keys_last,draw_at,block_max,blocks,overruns;
static uint8_t page,dirty,save_pending,load_pending,playing_cmd,stop_cmd,note_cmd,note_vel;
static char message[40];
static const char *const pages[]={"PLAY","SONG","VOICE","MIDI","LIBRARY","PERFORMANCE"};
static const char *const modes[]={"SOLO SONG","LIVE","PHRASE","WORD"};
static const char *const voices[]={"BRIGHT","DEEP","AIRY","SMOKY","YOUTH","MATURE","SYNTH"};
static void restart_song(void){engine.voice=prefs.voice;engine.external=prefs.sync!=0;engine.source=prefs.sync==1?PORT_BLE:PORT_USB;k9_start(&engine,load_pending?&custom:&factory_songs[prefs.song]);}
void app_init(void){memset(&prefs,0,sizeof prefs);prefs.magic=0x4b395031u;prefs.twitch=1;if(plat_store_load(OBJ_SETTINGS,&prefs,sizeof prefs)!=(int)sizeof prefs||prefs.magic!=0x4b395031u||prefs.song>=8||prefs.voice>=7||prefs.mode>=4||prefs.sync>=3||prefs.slot>=4||prefs.emotion>=4||prefs.twitch>=3||prefs.ble>=2){memset(&prefs,0,sizeof prefs);prefs.magic=0x4b395031u;prefs.twitch=1;}k9_init(&engine);engine.voice=prefs.voice;engine.song=&factory_songs[prefs.song];engine.external=prefs.sync!=0;engine.source=prefs.sync==1?PORT_BLE:PORT_USB;plat_ble_enable(prefs.ble);btn_last=keys_last=draw_at=0;message[0]=0;save_pending=playing_cmd=stop_cmd=load_pending=note_vel=0;page=dirty=0;blocks=block_max=overruns=0;}
void app_panic(void){k9_stop(&engine);engine.level=0;}
void app_render(int32_t *lr,uint32_t n,uint32_t master){uint32_t t=plat_ticks24(),i,pkt;int port;unsigned budget=32;
 if(stop_cmd){k9_stop(&engine);stop_cmd=0;}
 if(playing_cmd){restart_song();playing_cmd=0;}
 if(note_cmd){if(note_cmd==1)k9_note(&engine,K9_AH,note_vel?note_cmd+58:60,note_vel);else k9_note(&engine,K9_AH,note_cmd-2,note_vel);note_cmd=0;}
 while(budget--&&plat_midi_in(&pkt,&port))k9_midi(&engine,(uint8_t)port,(uint8_t)(pkt>>8),(uint8_t)(pkt>>16)&127,(uint8_t)(pkt>>24)&127);
 engine.voice=prefs.voice;
 if(n>256)n=256;k9_render(&engine,audio_lr,n);
 for(i=0;i<n*2;i++)lr[i]=(int32_t)(audio_lr[i]*(float)master*(8300000.0f/4096.0f));
 t=plat_ticks24()-t;if(t>block_max)block_max=t;if(t>139319u)overruns++;blocks++;
}
void app_say(const char *a,const char *b){message[0]=0;text_cat(message,a);if(b&&*b){text_cat(message," ");text_cat(message,b);}}
static void input(void){uint32_t f,buttons=plat_buttons(),press=buttons&~btn_last,keys=plat_keys(),down=keys&~keys_last,up=keys_last&~keys;int d;unsigned i;btn_last=buttons;keys_last=keys;
 if(press&(1u<<B_HOME))page=0;
 d=plat_enc(EN_SELECT);if(d)page=(uint8_t)((page+6+d%6)%6);
 if(press&(1u<<B_EDIT))page=(page+1)%6;
 if(press&(1u<<B_PLAY)){if(engine.playing||engine.velocity)stop_cmd=1;else playing_cmd=1;}
 if(press&(1u<<B_SAVE))save_pending=1;
 if(press&(1u<<B_SEL)){if(page==4){int len=plat_store_load(OBJ_SONG0+prefs.slot,song_wire,sizeof song_wire);if(len>0&&k9_decode(&custom,song_wire,(size_t)len)){load_pending=1;app_say("LOADED","");}else app_say("EMPTY OR INVALID","");}else if(page==3){prefs.ble=!prefs.ble;plat_ble_enable(prefs.ble);dirty=1;}}
 for(i=EN_ALGO;i<NE;i++){d=plat_enc(i);if(!d)continue;dirty=1;
 if(page==1||page==0){if(i==EN_K1){stop_cmd=1;prefs.song=(uint8_t)((prefs.song+8+d%8)%8);load_pending=0;}if(i==EN_K2){stop_cmd=1;prefs.mode=(uint8_t)((prefs.mode+4+d%4)%4);}}
 if(page==2){if(i==EN_K1)prefs.voice=(uint8_t)((prefs.voice+7+d%7)%7);if(i==EN_K2)prefs.emotion=(uint8_t)((prefs.emotion+4+d%4)%4);if(i==EN_K3)prefs.twitch=(uint8_t)((prefs.twitch+3+d%3)%3);}
 if(page==3&&i==EN_K1){f=plat_lock();k9_stop(&engine);prefs.sync=(uint8_t)((prefs.sync+3+d%3)%3);engine.external=prefs.sync!=0;engine.source=prefs.sync==1?PORT_BLE:PORT_USB;plat_unlock(f);}
 if(page==4&&i==EN_K1)prefs.slot=(uint8_t)((prefs.slot+4+d%4)%4);
 }
 if(prefs.mode){for(i=0;i<27;i++){if(down&(1u<<i)){f=plat_lock();note_cmd=(uint8_t)(55+i);note_vel=100;plat_unlock(f);plat_midi_send(0x09u|0x90u<<8|(53u+i)<<16|100u<<24,TO_USB|TO_BLE);}if(up&(1u<<i)){if(engine.note==53+i){f=plat_lock();note_cmd=(uint8_t)(55+i);note_vel=0;plat_unlock(f);}plat_midi_send(0x08u|0x80u<<8|(53u+i)<<16,TO_USB|TO_BLE);}}}
 if(save_pending){if(engine.playing||engine.level>.0001f)app_say("STOP BEFORE SAVE","");else{int rc;if(page==4){size_t n=k9_encode(load_pending?&custom:&factory_songs[prefs.song],song_wire,sizeof song_wire);rc=n&&n<=PLAT_STORE_MAX?plat_store_save(OBJ_SONG0+prefs.slot,song_wire,(uint32_t)n):-1;}else rc=plat_store_save(OBJ_SETTINGS,&prefs,sizeof prefs);if(!rc){dirty=0;app_say("SAVED","");}else app_say("SAVE FAILED","");}save_pending=0;}
 plat_leds((engine.playing?(1u<<B_PLAY):0)|(dirty?(1u<<B_SAVE):0),keys);
}
/* Analytic original face rig, drawn as six 40-row strips (19.2 KB canvas). */
static int face_y;
static void face_line(int x,int y,int xx,int yy,uint16_t c){cv_line(x,y-face_y,xx,yy-face_y,c);}
static void face_rect(int x,int y,int w,int h,uint16_t c){cv_rect(x,y-face_y,w,h,c);}
static void oval(int cx,int cy,int rx,int ry,uint16_t color){int y,x;for(y=cy-ry;y<=cy+ry;y++){if(y<face_y||y>=face_y+40)continue;for(x=cx-rx;x<=cx+rx;x++)if((x-cx)*(x-cx)*ry*ry+(y-cy)*(y-cy)*rx*rx<=rx*rx*ry*ry)cv_pset(x,y-face_y,color);}}
static void draw_face(k9_face f){uint16_t skin=RGB(221,175,163),hair=RGB(44,33,68),dark=RGB(27,24,43),amber=RGB(255,157,81),metal=RGB(102,116,137);int band,s;
 for(band=0;band<6;band++){face_y=band*40;cv_begin(240,40,RGB(13,16,30));
 oval(120,114,91,125,hair);oval(120,107,70,91,skin);oval(120,188,25,45,metal);
 for(s=-1;s<=1;s+=2){int x=120+s*40;oval(x,103,26,f.blink?2:12,C_WHITE);oval(x+f.gaze,103,10,f.blink?1:11,amber);oval(x+f.gaze,103,4,f.blink?1:8,dark);oval(x+f.gaze-3,100,2,f.blink?0:2,C_WHITE);face_line(x-25,88-f.cheek,x+19,85+f.cheek,dark);face_line(120+s*58,120,120+s*48,147+f.jaw,metal);face_line(120+s*66,121,120+s*51,153+f.jaw,C_WHITE);face_rect(120+s*52-4,141+f.cheek,8,13,metal);face_rect(120+s*52-2,143+f.cheek,4,5,amber);face_line(120+s*20,181,120+s*27+f.neck,216,amber);}
 face_line(119,116,115,131,metal);face_line(115,131,124,132,metal);
 {int w=f.mouth==3?10:f.mouth==2?25:17,h=f.mouth==4?1:2+f.open/3;oval(120,151+f.jaw,w+3,h+3,RGB(151,77,91));oval(120,151+f.jaw,w,h,dark);if(f.mouth==5)face_rect(102,148+f.jaw,36,3,C_WHITE);}
 /* asymmetric crown, ear hardware, copper cabling */
 oval(74,38,39,35,hair);oval(133,24,55,34,hair);face_line(53,53,100,72,amber);face_line(157,44,183,77,metal);face_rect(30,95,15,55,metal);face_rect(33,105,8,32,amber);face_rect(193,91,14,51,metal);face_line(38,151,53,183,amber);face_line(53,183,74,194,amber);
 if(band==0){cv_text(8,5,&FONT_XS,"KIRA-9  DEV",C_WHITE);cv_text(170,5,&FONT_XS,engine.playing?"SINGING":"READY",amber);}
 if(band==5){cv_rect(0,18,240,22,RGB(13,16,30));cv_text(5,20,&FONT_XS,"EDIT: PAGES   SELECT: MENU",C_WHITE);}
 cv_blit(0,(uint32_t)face_y);}}
static void draw_menu(void){char t[32];unsigned row;for(row=0;row<6;row++){cv_begin(240,40,RGB(13,16,30));if(!row){cv_text(8,5,&FONT_M,pages[page],RGB(255,157,81));}else if(row==1){cv_text(8,0,&FONT_XS,factory_names[prefs.song],C_WHITE);cv_text(8,17,&FONT_XS,modes[prefs.mode],C_WHITE);}else if(row==2){cv_text(8,0,&FONT_XS,voices[prefs.voice],RGB(255,157,81));int_text((int)engine.tick,t);cv_text(8,17,&FONT_XS,t,C_WHITE);}else if(row==3){if(page==3){cv_text(8,0,&FONT_XS,prefs.sync==0?"K1 CLOCK: INTERNAL":prefs.sync==1?"K1 CLOCK: BLE":"K1 CLOCK: USB",C_WHITE);cv_text(8,17,&FONT_XS,prefs.ble?"SEL: BLUETOOTH OFF":"SEL: BLUETOOTH ON",C_WHITE);}else if(page==2){cv_text(8,0,&FONT_XS,"K1 VOICE  K2 EMOTION",C_WHITE);int_text(prefs.twitch,t);cv_text(8,17,&FONT_XS,"K3 TWITCH",C_WHITE);cv_text(90,17,&FONT_XS,t,C_WHITE);}else if(page==4){int_text(prefs.slot+1,t);cv_text(8,0,&FONT_XS,"K1 SAVE SLOT",C_WHITE);cv_text(110,0,&FONT_XS,t,C_WHITE);cv_text(8,17,&FONT_XS,"SAVE: WRITE   SEL: LOAD",C_WHITE);}else if(page==5){int_text((int)(block_max/24u),t);cv_text(8,0,&FONT_XS,"MAX AUDIO US",C_WHITE);cv_text(122,0,&FONT_XS,t,C_WHITE);int_text((int)overruns,t);cv_text(8,17,&FONT_XS,"OVERRUNS",C_WHITE);cv_text(122,17,&FONT_XS,t,C_WHITE);}else{cv_text(8,0,&FONT_XS,"K1 SONG   K2 MODE",C_WHITE);cv_text(8,17,&FONT_XS,"PLAY: START / STOP",C_WHITE);}}else if(row==4)cv_text(8,5,&FONT_XS,message,C_WHITE);else{cv_text(8,0,&FONT_XS,"EDIT / SELECT: PAGES",C_WHITE);cv_text(8,17,&FONT_XS,"HOME: FACE   SAVE: STORE",C_WHITE);}cv_blit(0,row*40);}}
void app_ui_init(void){palette_set(1);lcd_fill(0,0,240,240,C_BLACK);}
void app_input_only(void){input();}
void app_frame(void){uint32_t now=plat_ms();input();if(now-draw_at<50u)return;draw_at=now;if(!page){k9_face f;uint32_t lock=plat_lock();f=k9_face_at(&engine,now,prefs.emotion,prefs.twitch);plat_unlock(lock);draw_face(f);}else draw_menu();}
#ifdef PLAT_HOST
int app_expect(const char *what,int *got){if(!strcmp(what,"playing"))*got=engine.playing;else if(!strcmp(what,"song"))*got=prefs.song;else if(!strcmp(what,"voice"))*got=prefs.voice;else if(!strcmp(what,"mode"))*got=prefs.mode;else if(!strcmp(what,"sync"))*got=prefs.sync;else if(!strcmp(what,"note"))*got=engine.velocity?engine.note:-1;else if(!strcmp(what,"dirty"))*got=dirty;else return 0;return 1;}
#endif
