# Global fog increase

Ultra Dynamic Sky `Scale Fog Density` increased from 0.35 to 0.455 (+30%)
in the saved Station_R12 map. The pass preserves time of day, weather, color,
volumetric fog, view distance and extinction settings.

`settings.json` records the before/after settings. `views/capture.json` verifies
0.455 in PIE; the forest and bridge captures retain readable paths and lamps.
The apply script sets the final value directly, so rerunning it does not compound
the increase. Run `../scripts/fog_density_pass.py` through the editor dispatcher
with `apply: true` only while owning the shared editor.
