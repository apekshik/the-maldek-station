# Gondola neon status sign — design review

Editable source: `Maldek_Gondola_Status_Sign.blend`. This is a separate Blender
study; the approved cabin source and the live game are untouched.

A stationary petrol-enamel cabinet with two sharp brass borders, rain hood,
recessed exposed neon tubes, porcelain electrodes, bolted steel pedestal,
rear transformer enclosure and supply conduit. Each word is its own physical
neon circuit, so the inactive lettering remains visible as unlit glass.

Timeline review states (24 fps, stepped changes):

| Frame | Lit circuit | Proposed later game meaning |
| --- | --- | --- |
| 1 | BOARD, green | Cabin stopped, landing ready, doors fully open |
| 49 | ARRIVING, amber | Approaching or settling; wait to board |
| 97 | DEPART, orange | Departure requested; doors closing and latching |
| 145 | AWAY, pale blue | Cabin absent |

The four circuits use independently named `NS01_Circuit_*` materials. No flashing
is included. Runtime transitions and obstruction handling remain for implementation
after design approval. Inactive tube emission is 0.015; active emission is 7.

The cabinet is 1.48 m wide and 1.39 m tall, with its hood at 2.91 m above platform
level. The mounting origin is 2.55 m to the right of the cabin centre, beside its
entrance. Its inner cabinet edge remains outside the door travel and handles.
The platform slab is a provisional placement aid, not a replacement station mesh.
The reference cabin is frozen in its open boarding pose for this design review.

`previews/` contains all four lit states, a boarding placement view and rear
construction detail. `scripts/build.py` reproduces the study from the approved
cabin source using Blender 5.0. `scripts/verify.py` checks the reopened source.

The review glow compositor uses Blender 5.0's group output API, documented in
[Blender's compositor migration notes](https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/).

No FBX, Unreal import, collision changes, map edits or game logic are included.
Those checks and the final station mounting position belong to the approved
implementation pass.
