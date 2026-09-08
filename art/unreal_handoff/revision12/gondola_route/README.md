# Maldek gondola route

Installed in `/Game/MaldekRefinement/R12/Station_R12`. This extends the original
586 m controller path into a 1,416.25 m reversible route to Maldek, using the
confirmed gorge terrain and the approved pylon study 03 as the source.

## Operation

- The finished cabin starts 30.48 m along the route, inbound. A one-shot player
  sightline check starts its approach: within 150 m of the approach reference,
  looking toward the cabin, with no visibility collision between eye and cabin.
  The cabin is already in place, so the reveal does not teleport it.
- Approach speed is 0.8 m/s. Cruise is 3.5 m/s, with acceleration, slow zones at
  both ends, and a final braking curve. The first approach takes about 39.5 s;
  a complete crossing takes about 468 s (7 min 48 s).
- Walk through the rear cabin entrance and press **E** inside to depart. The
  cabin remains upright and does not turn around for the return journey.
- At Maldek the boarding gangway slides from the side landing to the cabin's
  rear doorway. The existing 180 s return dwell is retained. The gangway must
  retract before departure; it holds if the player's capsule occupies its deck.
- Twenty-four cabin actors (body, glass, details, adapter and lights) attach to
  the moving mesh component with their original dock offsets. Their existing
  collision carries the actual player; the player is not artificially attached.
  Existing positional cable audio follows that component.

## Route and supports

| Span | Horizontal length |
|---|---:|
| Millford to tower 01 | 331.4 m |
| 01–02 | 257.2 m |
| 02–03 | 262.2 m |
| 03–04 | 247.3 m |
| 04–05 | 188.0 m |
| 05 to Maldek | 98.9 m |

Cable contact heights above the higher sampled footing are approximately
66.0, 45.7, 42.3, 51.5 and 44.9 m. Each foot follows its own terrain elevation.
The conical shafts change length while the central portal retains the approved
design. Ladder rungs are rebuilt at no more than 30 cm spacing, and tower IDs
are numbered 01–05. Both terminals have a supported return sheave; one passenger
run and one bare return run form the visible rope loop.

The upper cabin adapter is one metre longer than the studio adapter, and the
cable lies 25 cm to the side of the cabin centre. This provides clearance on the
steepest banks without changing the cabin body. The grip stem is narrower where
it passes between the sheave flanges. Roller centres follow the surveyed cable
profile, which has smooth transitions across each bank.

The FBX exporter/importer used here maps Blender `(X,Y,Z)` to Unreal `(X,-Y,Z)`.
Route-only imports therefore use **180-degree actor yaw**, giving the required
`(-X,+Y,+Z)` mapping. The controller/cabin body keep their original orientation.
`orientation.json` verifies the visible cable's longitudinal bounds against the
route endpoints. Import converts metres to centimetres exactly once.

## Appearance

Nine local Unreal materials recreate the study's dull grey-green paint, rust
at joints, faded amber bands, rough galvanized steel and red markers. The
Blender procedural shader is not assumed to survive FBX. Broad local fog banks
hide the far route without changing the user's sky/global weather settings.
Two low-intensity warm interior lights make the approaching cabin legible.
The far facade is shifted 1 m uphill to clear the stopped cabin's nose; its
existing building design is retained. New landing columns are terrain-traced.

## Verification and physical limits

- `runtime.json`: actual PIE boarding through the entrance, E-key departure,
  full outbound and return crossings with a standing player, docking, and the
  occupied gangway interlock. Route speed tests use game time; long crossings
  are accelerated only in the test world. Player movement and floor collision
  remain active. `runtime_initial.json` preserves the initial timing test.
- `clearance.json`: 735 triangle-intersection poses across five towers, at 25 cm
  travel intervals and illustrative -8/0/+8 degree body swing. No intersections.
- `plan.json`: explicit illustrative assumptions: 12 kg/m rope, 250 kN horizontal
  tension, 1,800 kg loaded cabin. The support profile is raised as needed to keep
  downward rope reactions at all five support banks. It includes an additional
  stationary point-load sag envelope for terrain clearance. Outside 20 m of
  either terminal, the sampled minimum loaded floor clearance is about 11.7 m.
- Editor and Development game targets compile. `views/` contains actual player
  arrival/boarding views and separately labelled neutral-light and night/torch
  tower inspections. Temporary inspection lighting is removed after capture.
- `reopen.json` records saved-map persistence checks.

This is a physically informed game route, not a certified ropeway. Visible sag
is a fixed parabolic approximation; the moving load does not dynamically deform
the rope. Rope/grip strength, braking and wind loads, tower buckling, connection
capacity and ground-anchor capacity have not been established. The terrain and
mesh clearance checks do not establish those capacities.

## Reproduction

Preserve the current map first. `Station_R12_before_gondola.umap` is the local
pre-route rollback, including the confirmed gorge. Never replace it on a rerun.
The approved study remains at `art/blender/pylon_study_03/`.

Scripts are in `../scripts/`, prefixed `gondola_`. The survey and plan are local
evidence of the original route endpoints; re-survey deliberately if moving the
terminals or terrain. Build/restart the native game module before installing
its new serialized properties. Then run:

1. `gondola_route_plan.py` in standalone Python.
2. `gondola_route_export.py`, `gondola_terminal_export.py`, and
   `gondola_route_clearance.py` in background Blender.
3. In the idle editor: `gondola_route_install.py`, `gondola_terminal_install.py`,
   `gondola_route_polish.py`, `gondola_bridge_setup.py`, `gondola_route_finish.py`, then `gondola_dim.py`.
   This order restores the final gangway, material and lighting settings.
4. `gondola_route_verify.py`, runtime checks, inspection captures and reopen.

`gondola_orientation_fix.py` records the initial import correction and refreshes
only the five tower meshes. The normal import scripts now include its yaw fix.
Avoid sending another editor job while a PIE test or asynchronous capture owns
the editor. All material and route assets live under `R12/GondolaRoute`.

## Cabin brightness revision

Cabin lamps now use a dedicated material instance with EmissionStrength 0.6 (previously 3), and each interior light is 12 lumens (previously 35), with volumetric scattering 0.025. Shared station lamps are unchanged. `dimming.json`, `dim_views/` and the updated reopen check record this revision. Run `gondola_dim.py` after the final route setup to reproduce the material assignments.

The terminal transmission design is a separate Blender study at `art/blender/terminal_drive_study_01/`; it has not replaced the installed terminal meshes.
