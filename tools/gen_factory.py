#!/usr/bin/env python3
"""Original lyrics with explicit pronunciation; factory source, never user-writable."""
import json,pathlib
lex={}
for line in '''neon N IY AA N
awake AH W EY K
my M AY
heart HH AA R T
is IH Z
a AH
light L AY T
in IH N
the DH AH
rain R EY N
we W IY
rise R AY Z
again AH G EH N
glass G L AE S
dreams D R IY M Z
hold HH OW L D
me M IY
near N IH R
soft S AO F T
stars S T AA R Z
shine SH AY N
clear K L IH R
ghost G OW S T
signal S IH G N AH L
through TH R UW
night N AY T
find F AY N
you Y UW
inside IH N S AY D
blue B L UW
after AE F T ER
fall F AO L
breathe B R IY DH
slow S L OW
let L EH T
all AO L
sorrow S AA R OW
go G OW
circuit S ER K AH T
bloom B L UW M
move M UW V
with W IH DH
this DH IH S
beat B IY T
feel F IY L
warm W AO R M
under AH N D ER
feet F IY T
electric IH L EH K T R IH K
lullaby L AH L AH B AY
close K L OW Z
your Y UH R
eyes AY Z
sleep S L IY P
sky S K AY
no N OW
gravity G R AE V AH T IY
free F R IY
fly F L AY
above AH B AH V
sea S IY
machine M AH SH IY N
remember R IH M EH M B ER
our AW ER
song S AO NG
carry K AE R IY
home HH OW M
belong B IH L AO NG'''.splitlines():
 w,*ps=line.split();lex[w]=ps
songs=[('Neon Awakening','pop',120,'neon awake\nmy heart is a light\nin the rain\nwe rise again'),('Glass Heart','dream pop',90,'glass dreams\nhold me near\nsoft stars\nshine clear'),('Ghost Frequency','IDM',132,'ghost signal\nthrough the night\nfind you\ninside the blue'),('After the Rain','trip hop',76,'after the rain\nbreathe slow\nlet all sorrow\ngo'),('Circuit Bloom','house',124,'circuit bloom\nmove with this beat\nfeel the warm light\nunder my feet'),('Electric Lullaby','ambient',60,'electric lullaby\nclose your eyes\nsleep in the light\nunder the sky'),('No Gravity','soul',84,'no gravity\nwe are free\nfly above\nthe sea'),('Machine Dreams','robotic',108,'machine dreams\nremember our song\ncarry me home\nwe belong')]
lex['are']=['AA','R']
phones='SIL AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH IY JH K L M N NG OW OY P R S SH T TH UH UW V W Y Z ZH'.split();vowels=set('AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW'.split())
compiled=[]
for idx,(name,style,bpm,lyrics) in enumerate(songs):
 events=[];tick=0
 for j,w in enumerate(lyrics.split()):
  ps=lex[w];dur=144 if j%4==3 else 96;cons=8;nv=sum(p in vowels for p in ps);vtime=(dur-cons*(len(ps)-nv))//max(1,nv)
  for p in ps:
   d=vtime if p in vowels else cons
   events.append(dict(tick=tick,duration=d,phone=phones.index(p),note=[60,64,67,69,67,64,62,60][j%8]+(12 if idx%3==0 else 0),velocity=90,stress=1 if p in vowels else 0));tick+=d
  tick+=24
 compiled.append(dict(name=name,style=style,bpm=bpm,lyrics=lyrics,ticks=tick,events=events))
pathlib.Path('factory').mkdir(exist_ok=True);pathlib.Path('factory/songs.json').write_text(json.dumps(compiled,indent=2)+'\n');pathlib.Path('factory/lexicon.json').write_text(json.dumps(lex,indent=2)+'\n')
lines=['/* SPDX-License-Identifier: MIT; generated original factory songs */','static const k9_song factory_songs[] = {']
for s in compiled:
 lines.append('{'+f'{len(s["events"])},{s["bpm"]},{s["ticks"]},'+'{')
 for e in s['events']:lines.append('{'+','.join(str(e[k]) for k in ['tick','duration','phone','note','velocity','stress'])+',0},')
 lines.append('}},')
lines+=['};','static const char *const factory_names[] = {'+','.join(json.dumps(s['name']) for s in compiled)+'};']
pathlib.Path('factory/songs.h').write_text('\n'.join(lines)+'\n')
