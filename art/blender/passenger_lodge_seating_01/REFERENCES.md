# Seating package — construction and texture references

Accessed 2026-09-10. These inform the authored kit; this is not a replica or engineered product.

- [Pilot Rock AT commercial picnic table](https://www.pilotrock.com/series/picnic-tables/at-series-traditional-a-frame-picnic-table-using-lumber/): timber legs, metal transverse supports, diagonal braces attaching to an underside centre channel, galvanized through-bolts. Adapted to independent benches and the fixed lodge footprint.
- [myCarpentry detached-bench plan](https://www.mycarpentry.com/picnic-table-plan.html): separated bench arrangement, plank gaps, underside framing, diagonal bracing and flat floor contact. The kit retains its own dimensions and trestle form.
- [Poly Haven Stained Pine](https://polyhaven.com/a/stained_pine): photographed grain, knots and restrained varnish scratches. Scanned by Jenelle van Heerden; processed by Dario Barresi. Downloaded 2K JPEG diffuse, roughness and OpenGL normal maps using the public asset API. The texture photographs are cropped in UV/shader space to avoid reproducing their board seams inside one modeled plank.
- [Poly Haven asset license](https://polyhaven.com/license): CC0; commercial use and redistribution permitted. Texture files are included and packed in the Blender file. No product photographs are redistributed.

The source atlas spans 0.9 m according to Poly Haven. Single-board strips are expanded to the authored 1.8 m boards for a restrained grain scale. Eight strip offsets supply variations while sharing one board mesh. End grain remains a separate procedural ring shader; station metal shaders remain Blender source materials. Export requires baking this atlas selection and procedural materials.

`texture_api.json` records the upstream file URLs, sizes and MD5 values. `scripts/download_textures.ps1` downloads only the three selected 2K JPEG maps and verifies their hashes. No credentials are required.
