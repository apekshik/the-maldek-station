# Three-strand police cordon

Extends the approved single-tape study without replacing its Blender file.
Open `Maldek_Police_Cordon_Prototype.blend`, frames 1–144 at 24 fps.

Three yellow/black strands cross the approach at unequal heights, slopes and
small depth offsets. Each has separate simulated halves and trunk wraps. The
lower, middle and upper strands release during the same short crossing, with
slightly staggered breaks, leaving all three openings clear. Retreat checks
leave the new strands intact. There is no hand/lifting animation yet.

Eight additional spans connect seven neighbouring tree proxies and the two
crossing trees to form a closed perimeter in the study. This illustrates a
restricted area rather than only a blocked trail. In the live map the perimeter
must be fitted around the actual station-side area and current trees; this small
review loop is not a final world layout. Review foliage is placeholder geometry.

`scripts/build.py` uses the first study's ribbon helpers and simulator, then
renders three review views and exports static FBXs. The Blender file contains
the baked motion; FBXs do not. `manifest.json` records dimensions and limitations.
The independent ribbon simulations do not include ribbon-to-ribbon collisions.
Perimeter spans are static in this study. No Unreal assets or maps are modified.

Yellow/black lettering and material references remain those in
`../police_tape_01/README.md`. No audio is included.
