# Construction references

Consulted 2026-09-10 while authoring. These are design references, not supplied
meshes, a manufacturer replica, certified construction, or evidence of a 1990s
installation. Hardware dimensions remain fixed when the leaf width changes.

| Component | Primary reference | Detail used and adaptation |
|---|---|---|
| Leaf and hinges | [Bloxwich BCP22024 personnel door](https://www.bloxwichdoorgear.com/acatalog/BCP22024-Standard-Shipping-Container-Personnel-Door-1270.html) | 45 mm steel leaf, weather seals, stainless hardware; four hinges for the wider public leaves and three for staff. The lodge uses its own frosted vision opening and keyed mechanism. |
| Independent frame | [Bloxwich BCP22027 goal-post frame](https://www.bloxwichdoorgear.com/acatalog/BCP22027-Shipping-Container-Personnel-Door-Goal-Post-Frame-1251.html) | Separate steel opening surround within corrugated cladding. Lodge lining depth is fitted to the actual wall and cladding, rather than copying catalogue frame dimensions. |
| Lever scale and shape | [HOPPE / ARRONE AR963 dimensional sheet](https://www.hoppe.com/hoppe_media.php?path=DOK_DS_87109373_SEN-GB_AOF_V1.pdf) | 54 mm rose and 19 mm grip; compact returned lever proportions. The single continuous curved tube is authored from dimensions, not scaled from the old door. |
| Return grip construction | [Randi 1030.00](https://www.randi.dk/en/assortment/1030-00/) | Functional return-to-door silhouette and concealed spindle. Randi's 22 mm grip is a shape reference; this package consistently uses 19 mm. |
| Hinge construction | [ASSA ABLOY hardware catalogue](https://www.assaabloy.com/ae/en/product-assets/ansi-american-door-hardware/assets/documents/ASSA_ABLOY_American_Hardware_Catalogue_ME.pdf) | Separate leaves and knuckles, pin axis, mounting clearances. Searchable catalogue text was available; direct PDF retrieval failed, so no claim is made to have reviewed its full drawings. Package hinge height is 125 mm, tailored to the existing design language. |
| Brass mechanical cylinder | [ASSA ABLOY mechanical cylinder catalogue](https://www.assaabloy.com/ae/en/documents/solutions/products/keys-and-cylinders/AA_Mechanical_Cylinders_Technical_Catalog_ME.pdf) | Brass housing / moving-core distinction. Round 33 mm collar and 20.3 mm plug follow approved door study 04; these are not represented as a Euro-profile cylinder replica. |
| Frosted vision panel | [Pilkington Optifloat Opal technical leaflet](https://assetmanager-ws.pilkington.com/fileserver.aspx?cd=cd&cmd=get_file&ref=GL044) | Diffused transmitted light, low surface reflection, etched finish. The package uses 8 mm glass and a procedural rough-transmission shader; the leaflet lists 8 mm as an on-request thickness. No thermal or safety performance is claimed. |
| Door-bottom seal | [ASSA ABLOY LAS8001](https://www.assaabloy.com/uk/en/solutions/products/hardware-for-doors-and-windows/door-seals/architectural-seals-for-doors/las8001) | A retracting bottom seal allows a low/flush threshold. This is a simplified visual gasket and Blender pose release, not a replica mechanism or runtime implementation. |
| Threshold | [Bloxwich BCP22024 construction specification](https://www.bloxwichdoorgear.com/acatalog/BCP22024-Standard-Shipping-Container-Personnel-Door-1270.html) | Stainless threshold and restrained profile. This package adapts that idea to a flush pan to retain the exact source headroom; local floor/grating pockets prevent overlapping top faces. |

The Bloxwich linked drawing image timed out during retrieval. Its accessible
product specifications informed the model; the missing image is not counted as
reviewed evidence. Manufacturer images and documents are linked, not redistributed.

## Project evidence applied

- `door_study_01/README.md` and `scripts/build_door.py`: petrol exterior, cream
  inside, broad rough-transmission upper glass, kick plates and separate hinge.
- `door_study_03/README.md`: keyed/standard and keypad components remain distinct.
- `door_study_04/README.md` and `scripts/build_key_lock.py`: real cylinder bore,
  housing/plug clearance, a recessed keyway, and independent mechanism controls.
- `art/MESH_AUTHORING.md` and R12 `trim2/README.md`: one owner per visible reveal,
  concealed 4 mm core separation, and full assembly handing instead of angle-only
  swing reversal. Previous R12 repairs and source files are not overwritten.

Station VF06 materials are reused. Glass micro-etch, station paint variation and
any source procedural finishes remain Blender shaders; baking is future work.
