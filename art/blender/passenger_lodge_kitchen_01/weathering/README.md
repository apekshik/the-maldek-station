# Kitchen weathered finish variant

Open `Maldek_Passenger_Lodge_Kitchen_Weathered.blend`, scene `PLK_Fitted_Review`.
Append `PLK_Assets` from `PLK_Assets_Weathered.blend` for the asset-only version.
Use either this collection or the clean collection, never both in the same location.
The clean package one directory above is preserved. This is a material pass for a
sheltered early-1990s interior left unused for several years; the precise duration
and moisture history are art-direction assumptions, not established story facts.

## Downloaded references and materials

All downloaded maps are CC0. No account, purchase, artwork generator or API key is
required. Original filenames are retained in `textures/`; `texture_sources.json`
records individual download URLs and SHA-256 hashes. Provider metadata snapshots
are included for reproducibility. Licenses checked 2026-09-10:
[ambientCG](https://docs.ambientcg.com/license/) and
[Poly Haven](https://polyhaven.com/license).

| Source | Use in this package |
| --- | --- |
| [ambientCG SurfaceImperfections015](https://ambientcg.com/view?id=SurfaceImperfections015) | Dust opacity at a 0.65 m repeat, biased toward upward-facing surfaces; quieter film on vertical faces. |
| [ambientCG SurfaceImperfections001](https://ambientcg.com/view?id=SurfaceImperfections001) | Fine dried-water spotting in metal and porcelain colour/roughness. A shared finish, not a simulated leak history. |
| [ambientCG SurfaceImperfections007](https://ambientcg.com/view?id=SurfaceImperfections007) | Faint coffee/cup ring atlas on upward laminate faces, projected over 2.5 m. |
| [ambientCG Scratches004](https://ambientcg.com/view?id=Scratches004) | Hairline scuffs in roughness and microscopic bump on metal, laminate, enamel, paint, glass and rubber. |
| [ambientCG Smear004](https://ambientcg.com/view?id=Smear004) | Low-contrast fingerprint/smear roughness on the same handled finishes. |
| [Poly Haven wood_cabinet_worn_long](https://polyhaven.com/a/wood_cabinet_worn_long) | Subdued worn furniture colour blended into pine/birch, plus roughness. Photography: Dimitrios Savva; processing: Rico Cilliers. |

Fourteen source maps are retained; seven are used by shaders. Alternate colour,
roughness and the wood tangent normal are reference/integration inputs only. The
wood normal is deliberately unused: box projection cannot correctly interpret a
tangent-space normal without corresponding aligned UVs. No external example
renders or logos are redistributed.

## Finish construction

Eleven package-specific material copies retain the petrol, cream enamel, warm
wood and stainless palette. Directional dust overlays the original colour, while
a short-range 45 mm ambient-occlusion mask adds joint residue. Scuffs and smears
mostly change roughness. The fine bump distance is 0.16 mm at 0.22 strength;
there is no displacement, added decal plane, mesh damage or collision change.
The furniture scan is blended at 78% with a warm wood tint, avoiding crossed grain
from stacking the scan over the original procedural grain.
No blanket orange rust or flaking-metal treatment is applied to stainless steel.
Chalk lettering and the small red indices keep their clean materials for legibility.

Maps use component-space metre coordinates (box projection except planar cup
rings), avoiding normalized bounding-box texture stretching. Colour maps use
sRGB; opacity and roughness use Non-Color. Dust direction uses world normals;
the cavity effect depends on Cycles scene occlusion. Named nodes expose the
blend strengths and physical frequency. See `material_manifest.json` for the
exact clean-to-weathered material mapping and texture use.

## Review and verification

`previews/` repeats all ten clean cameras under the same temporary neutral review
lighting: customer, staff counter, staff entry, rear prep, washing, overhead
access, handwashing, opening mechanisms, lost property and beverage equipment.
Frame 1 is closed; frame 40 shows representative open mechanisms. These lights,
reference architecture and access lines are excluded from the asset library.

`verification.json` records a saved/reopened comparison against the clean scene:
exact mesh vertices and polygon indices, all object transforms and parents, and
reference material slots remain unchanged. All seven shader images are packed.
The clean package's proxy replacements, surface ownership, clearances and pivot
manifest remain authoritative. This pass changes no opening or circulation space.

Rebuild with Blender 5.0:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/weather.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/render_weathering.py
```

`scripts/download_weathering.py` can restore source maps using the saved metadata
and public download endpoints. The Blender shaders remain procedural/image hybrid
studies: UV planning, texture baking/channel packing, engine materials and engine
collision review are later integration work. No Unreal import or playtest is claimed.
