"""Original typographic tape artwork, built from text; no photographic assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(2048,128),(245,194,12));d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',79)
label='POLICE LINE DO NOT CROSS'
b=d.textbbox((0,0),label,font=font)
d.text(((2048-(b[2]-b[0]))/2,(128-(b[3]-b[1]))/2-b[1]),label,font=font,fill=(12,13,10))
for x in (42,1970):
    d.polygon([(x,31),(x+17,31),(x+39,97),(x+22,97)],fill=(12,13,10))
im.save(out/'T_PoliceTape_BaseColor.png')
print(out/'T_PoliceTape_BaseColor.png')
