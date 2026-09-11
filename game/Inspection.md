# Object inspection

The persistent sample is **Inspection_Cassette_Pickup_Hood** in
`/Game/MaldekRefinement/R12/Station_R12`, on the pickup truck's front hood corner
in the starting parking lot. Walk up to the front of the truck and aim at the
field cassette until the **E Examine** prompt appears.

| Input | Action |
| --- | --- |
| E / left click | Pick up the aimed object (E also returns) |
| Hold left mouse and drag | Rotate |
| Arrow keys | Rotate with keyboard |
| Mouse wheel | Zoom |
| Z / X | Roll |
| R | Reset rotation and zoom |
| E / Escape / Tab | Return to the exact original placement |

In Unreal PIE, the editor's Escape shortcut may stop play; use E or Tab to
return when testing in the editor. F7 places a temporary sample in front of the
player in development builds. The saved parking cassette needs no shortcut.

The bottom HUD floats directly over the scene: gold title and key hints, white
description and action labels, vector mouse icons, and subtle text shadows.
There is no filled panel. Controls wrap on narrow viewports.

## Adding props

Place a `StationInspectable` actor (or a Blueprint child), assign its `Mesh`,
and set `DisplayName`, `Description`, and optional `InspectionRotation`.
The mesh and attached primitive components must be Movable. Use a mesh with
visibility collision; physics simulation is optional on the root mesh.
Independently simulated children and props with bounding radii over 65 cm are
excluded. The system is intended for handheld props in the single-player game.

The local `HorrorPlayerController` owns `ObjectInspection`, with editable reach,
blend time, sensitivity, and inspection FOV. The session saves transforms,
attachments, collision, physics, pawn mesh visibility, and character movement
mode, then restores them on return, interruption, unpossess, and teardown.
Input locks are balanced rather than globally reset. Zoom does not adjust the
flashlight, and the gondola cannot depart while examining an object.

Optional pickup/return sounds and `OnInspectionStarted` / `OnInspectionFinished`
Blueprint events are available on each prop. This feature examines and returns
objects; it does not add inventory collection.

## Source and verification

- Editable sample: `art/blender/inspection_01/Inspection_Meter.blend`.
- Rebuild sample in background Blender with `build_samples.py` in that folder.
- Unreal import: `art/unreal_handoff/revision12/scripts/inspection_import.py`.
- Saved placement: `inspection_parking_install.py` in the same scripts folder.
- PIE checks: `inspection_test.py`; run through the existing local R12 dispatcher
  with PIE stopped. Results are written to `revision12/inspection/runtime_report.json`.
- Placement survey and report: `revision12/inspection/parking_survey.json` and
  `parking_install.json`.

The test checkpoint `Inspection_Parking_Checkpoint` is a non-rendered TargetPoint
for repeatable player placement. It does not replace PlayerStart.

## Field cassette

The approved Millford cassette is saved flat on the yellow pickup
hood. Actor: `Inspection_Cassette_Pickup_Hood`; mesh: `/Game/Inspection/Cassette/SM_ServiceCassette`.
Both sides carry readable geometry lettering, with open reel hubs and a translucent window.
The same E / drag / wheel / R / return controls apply.
Source: `art/blender/cassette_01/Millford_Service_Cassette.blend`; export: `export_cassette.py`.
Unreal install and test: `cassette_install.py` and `cassette_test.py` in the R12 scripts folder.

The meter was removed from the parking hood at the user’s request. The cassette is the only inspection prop there. Legacy meter import/placement scripts remain as development references; the build helper does not reinstall it.

A small center dot marks the camera aim used by inspection and door targeting.
Inspectable props show their name and E / LMB prompt above their world position.
A 4 cm aim allowance helps with small props and still checks visibility against occluders.
The dot hides while using the free cursor for inspection or lock controls.
Key locks accept drags across the projected key silhouette plus padding, with a larger grip radius.
