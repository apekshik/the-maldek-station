# Station dressing 01

Latest combined authoring scene: `Maldek_Station_Furnished.blend`, scene `Station_Furnished`.

Derived from `../west_services_02/Maldek_Station_West_Integrated.blend`. The earlier master and all three delivered room packages remain untouched.

- Janitor: replaces the solid `FIT_Cleaning_cupboard` placeholder with an open cupboard in the same footprint: five shelves, divided tool bay, mop, broom, bucket, bottles, folded cloths, paper rolls and supported cleaning rota.
- Rescue: two bracketed wall shelves with labeled dressing/glove/tape boxes and rolled blankets. Shelves raised clear of the existing chair; original readiness checklist retained.
- Emergency power: four-tier spares rack, six labeled boxes, filter tins and a wall-mounted spanner board.

The three `SD_*` dressing collections keep additions separately editable. `manifest.json` records exact additions, the single removed placeholder, source hash and retained object transforms. Reproduce with Blender Python `scripts/build.py`; render with `scripts/review.py`; reopen and check with `scripts/verify.py`.

Verification is Blender-only: manifold evaluated dressing meshes, unchanged retained transforms, immutable source file, and sampled supporting surfaces/body clearances along the six integrated routes plus janitor access. These samples do not replace continuous collision or Unreal capsule tests. Render lighting is review-only and is not saved to the master. Unreal export, material preparation and integration planning remain the next stage.

Final result: 141 added objects, including 125 evaluated manifold meshes. Seven sampled routes pass (762 samples). All 16,377 retained object transforms match the source. Five rendered views inspected.
