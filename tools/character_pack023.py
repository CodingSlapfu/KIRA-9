"""Compile original raster illustration to bounded row-addressed RGB565 RLE.
Only asset extraction/resampling/encoding, no procedurally substituted artwork.
"""
from pathlib import Path
from PIL import Image
import json
r=Path(__file__).resolve().parents[1];src=Image.open(r/'assets/character/poses-master.png').convert('RGB');w,h=src.size
frames=[src.crop((i%3*w//3,i//3*h//3,(i%3+1)*w//3,(i//3+1)*h//3)).resize((240,240),Image.Resampling.LANCZOS) for i in range(9)]
# One common 96-colour palette avoids palette changes at patch boundaries.
contact=Image.new('RGB',(240*9,240))
for i,im in enumerate(frames):contact.paste(im,(240*i,0))
pal=contact.quantize(colors=96,method=Image.Quantize.MEDIANCUT)
frames=[im.quantize(palette=pal,dither=Image.Dither.NONE).convert('RGB') for im in frames]
regions=[(0,0,240,240)]+[(66,86,112,39)]*3+[(102,141,42,34)]*6
indices=[0,1,2,8,0,3,4,5,6,7];data=[];offsets=[];spec=[]
for k,(x,y,ww,hh) in enumerate(regions):
 im=frames[indices[k]];spec.append([x,y,ww,hh,len(offsets)])
 for yy in range(y,y+hh):
  offsets.append(len(data));row=[]
  for xx in range(x,x+ww):
   red,g,b=im.getpixel((xx,yy));row.append(((red>>3)<<11)|((g>>2)<<5)|(b>>3))
  j=0
  while j<ww:
   n=1
   while j+n<ww and row[j+n]==row[j] and n<255:n+=1
   data.extend((n,row[j]&255,row[j]>>8));j+=n
text='/* Generated from original KIRA-9 cel artwork; RGB565 row RLE. */\n'
text+='static const uint8_t k9_art_data[]={\n'+','.join(map(str,data))+'};\n'
text+='static const uint32_t k9_art_rows[]={'+','.join(map(str,offsets))+'};\n'
text+='static const uint16_t k9_art_regions[][5]={'+','.join('{'+','.join(map(str,s))+'}' for s in spec)+'};\n'
(r/'core/character023.h').write_text(text)
for i,im in enumerate(frames):im.save(r/f'assets/character/pose-{i}.png')
(r/'assets/character/encoding.json').write_text(json.dumps({'source':'poses-master.png','format':'RGB565 RLE: count,low,high per run; independently indexed rows','regions':spec,'bytes':len(data)+4*len(offsets)+10*len(spec),'palette_colors':96,'size':[240,240]},indent=2)+'\n')
print('Character ROM bytes:',len(data)+4*len(offsets)+10*len(spec))
