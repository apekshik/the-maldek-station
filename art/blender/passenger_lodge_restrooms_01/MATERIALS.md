# Abandoned restroom surface treatment

Four 2048-pixel maps from Poly Haven **Metal Plate 02**, by Rob Tuytel, are retained in `textures/` and packed into the blend. CC0: https://polyhaven.com/license. Powered by Poly Haven. Exact URLs, source MD5 and local SHA-256 are in `textures/provenance.json`; the builder verifies source MD5 before packing. Rebuilds are offline.

- Hardware, kickplates, feet, rails, traps and dispenser housings: scan albedo blended with the original metal color, scanned metalness/roughness, restrained OpenGL normal strength 0.22. This suggests dull plating and light pitting while keeping recognizable metal highlights.
- Petrol laminate, stall leaves and bins: scan-derived roughness variation plus authored patchy grime. The scan color and metalness are not used on laminate.
- Cream ceramic: glaze with localized broken mineral deposits at the basin rim, inner wall and drain; light general age elsewhere. The `PLR_Deposit` point attribute controls the basin-specific distribution on the actual shell, without overlapping decal geometry.
- Ivory seats: restrained uneven dirt and roughness. Mirrors retain their existing reflective finish.

Shader nodes are labeled. `Abandonment amount` adjusts general dirt independently in each finish. Basin `PLR_Deposit` weights plus `Broken deposit edges` control wet-area stains. Textures use a 2 m repeat in face-aligned metric UVs; every asset mesh has `PLR_Metric_2m`. UVs follow door motion. Albedo uses sRGB; data maps use Non-Color. Normal maps are tangent-space OpenGL. No displacement changes geometry or clearance.

The intentionally clean reference walls/floor are outside this package's surface ownership. Lighting in all previews is temporary neutral review lighting, not final abandoned-station lighting. This is an editable Blender look-development package: procedural grime and face-projected UV seams still need baking/recreation and close player/torch review during Unreal integration. No engine-material or PIE validation is claimed.

Both basins now use one closed rounded-rectangular shell with an integrated rear deck, sloped interior and drain throat. Outer width 620 mm, projection span 510 mm, corner radius 75 mm. Separate old tap-deck blocks are eliminated; faucets, waste connections and installed centers remain. `material_verification.json` records packed textures, color spaces and UV coverage.
