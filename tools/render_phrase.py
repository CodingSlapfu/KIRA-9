#!/usr/bin/env python3
"""Render an encoded score through the real C engine for listening/assessment."""
import argparse,ctypes,pathlib,struct,wave
p=argparse.ArgumentParser();p.add_argument('score');p.add_argument('output');p.add_argument('--library',default='build/libkira.so');p.add_argument('--voice',type=int,default=0);p.add_argument('--style',type=int,default=0);a=p.parse_args()
lib=ctypes.CDLL(str(pathlib.Path(a.library).resolve()));lib.web_input.restype=ctypes.c_void_p;lib.web_render.restype=ctypes.POINTER(ctypes.c_float)
raw=pathlib.Path(a.score).read_bytes();lib.web_init();ctypes.memmove(lib.web_input(),raw,len(raw));assert lib.web_load(len(raw));lib.web_voice(a.voice,a.style)
samples=[];blocks=0
while lib.web_playing() and blocks<44100*180//256:
 ptr=lib.web_render(256);samples.extend(ptr[i] for i in range(512));blocks+=1
for _ in range(30):
 ptr=lib.web_render(256);samples.extend(ptr[i] for i in range(512))
with wave.open(a.output,'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(struct.pack('<'+'h'*len(samples),*(round(max(-1,min(1,x))*32767) for x in samples)))
print(a.output,len(samples)//2,'frames')
