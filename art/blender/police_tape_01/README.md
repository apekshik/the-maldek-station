# Police tape crossing prototype

Yellow polyethylene ribbon with black POLICE LINE DO NOT CROSS lettering.
Source: `Maldek_Police_Tape_Prototype.blend`. Play frames 1–144 at 24 fps.
Timeline markers identify contact, tear, and release. The context trees and
understorey are review proxies, not proposed replacement forest assets.

The 76.2 mm ribbon has two deforming halves, matching shallow fracture edges,
separate trunk wraps, loose tails, UVs, and a packed original lettering texture.
The 3.18 m span is a study dimension; final anchors must fit actual trees.
The material uses a 0.076 mm solidify thickness for Blender inspection.

Motion is computed with a deterministic 120 Hz position-based dynamics study:
gravity, wind, fixed end anchors, distance constraints, torso contact, trunk
contact and floor contact. Continued forward contact opens a controlled seam at
frame 59; both ends remain simulated afterward. A second approach-and-retreat
test leaves the seam intact. This is baked into editable shape keys for review.
It is not an Unreal runtime implementation or physically calibrated LDPE fracture.

## Reproduce

1. Run `scripts/lettering.py` with Python/Pillow (Arial Bold, Windows font path).
2. Run `scripts/simulate.py` with Python.
3. Run `scripts/build.py` with Blender 5.0 in background mode.
4. Run `scripts/verify.py` with Blender for source and FBX round-trip checks.
5. Run `scripts/render_motion.py` with Blender for every-other-frame previews.
6. Run `scripts/encode_preview.py` with Python/Pillow for the looping GIF/WebP.

`exports/` contains six static FBXs at intact-frame positions. These do not
contain the deforming timeline. `motion.json` retains all simulated centrelines.
`simulation_check.json` and `verification.json` document actual checks.

## Unreal integration next

The game map has not been modified. First port the centreline solver and render
a two-sided ribbon from its positions in an isolated runtime actor. Preserve
lettering UV distance; do not use the tube renderer of CableComponent directly.
Use player movement/contact to load the seam, with a short visible tension phase
and the ability to retreat. An optional hand animation can follow after this
version feels convincing. Keep gravity/wind release independent from the authored
break decision. Reset explicitly on a new play session; retain the torn state
when walking back during a session. Do not add a full-width invisible wall.

Before installation, audit current path/tree positions and coordinate use of the
shared editor with the active door task. Fit wraps to trunk radii, preserve the
current route and lighting, and concentrate added grounded understorey outside
the walking corridor. Test slow walking, sprinting, retreat, side contact and
reverse traversal at multiple frame rates. This prototype has no sound; source
recorded plastic rustle and tear audio before adding sound, per user preference.

Visual sources (reference only; no news photographs included in the asset):

- https://www.cbsnews.com/sacramento/news/man-found-dead-grass-valley-california-storm/
- https://www.uline.com/Product/Detail/S-22041/Barricade-Tape/Barricade-Tape-3-x-1000-Police-Line-Do-Not-Cross
