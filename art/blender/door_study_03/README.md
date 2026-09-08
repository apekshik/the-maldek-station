# Standard and digital-keypad station doors

Current review source: `Maldek_Digital_Door_Variants.blend`.
This supersedes the mechanical padlock experiment in `door_study_02`.

Both variants preserve the approved petrol-painted steel door, broad frosted upper glass, warm enamel interior, lever handles and kick plates. The secure version adds a 142 × 260 mm electronic access panel with twelve separate tactile buttons, recessed display, red status lens, rain hood, gasket, tamper-resistant screws, drainage, interior electronics cover and electric strike. Wiring is concealed through the leaf.

The standard variant uses collections 01–03; the digital variant additionally enables 04–06. Preview `01_Closed.png` is standard; `07_Keypad_door.png`, `08_Keypad_detail.png` and `09_Keypad_and_handle.png` show the digital version. The original full-length door pivot and review animation are preserved.

The user requested selecting secure-door locations after reviewing both designs. No secure location or access code is approved. The keypad blueprint is intended to remain unplaced until that decision. Its default access code is empty, so an unconfigured keypad cannot accidentally accept an empty entry.

Scripts: build with `build_keypad.py`, export with `export_doors.py`. The latter writes only the dedicated `art/unreal_handoff/revision12/doors` handoff. It includes separate meshes for leaf, glass, fixed hardware, keypad, interior electronics and electric strike. The display label is omitted from the game mesh so runtime text can reflect locked/unlocked state. No mechanical padlock or hasp is part of this export manifest.

Unreal integration and actual test status are recorded under `art/unreal_handoff/revision12/doors`. Blender previews do not prove Unreal glass rendering or collision behavior.
