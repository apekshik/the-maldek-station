from pathlib import Path
from PIL import Image
out=Path(__file__).resolve().parents[1]/'previews'
paths=sorted((out/'motion_frames').glob('frame_*.png'));assert len(paths)==48
frames=[Image.open(p).convert('RGB') for p in paths]
palette=frames[0].quantize(colors=192)
gif=[im.quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG) for im in frames]
gif[0].save(out/'crisscross_motion.gif',save_all=True,append_images=gif[1:],duration=[120,130]*24,loop=0,optimize=False)
with Image.open(out/'crisscross_motion.gif') as im:assert im.n_frames==48
print(out/'crisscross_motion.gif')
