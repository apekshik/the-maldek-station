# Handoff 03: emergency power room

Implement this standalone Blender package now. Read [shared contract](shared-contract.md) and [references](references.md) first. Work only in `art/blender/west_services_power_01/`.

## Purpose and fixed electrical rule

This is a small standby system for emergency lighting, communications and modest rescue-room heat. It cannot drive the gondola. Its readable controls must establish that distinction. Main drive equipment and the existing main generator remain elsewhere. Do not add a duplicate main-generator fuel grind or redesign the station's power system.

Interior station bounds: X [-37.2,-31.7], Y [-4.75,4.75], floor 1.20, slab underside 4.35. Local origin (-37.45,-5,1.20), collection `WSE_ASSETS`. Replace only `WS_POWER_PROXY`. The lower shell, structural slab, access walk and stairs belong to the master.

## Model scope

- Compact diesel engine and alternator on one skid; believable radiator/fan housing, guarded belt, filters, starter, serviceable covers, vibration feet and drain tray. The proxy reservation is 2.5 x 1.3 m. Refine within it unless a documented fit need requires an adjustment inside the room.
- Analog control panel: voltmeter, frequency indication, run/fault lamps, start/stop control and an emergency stop. Model a manual transfer selector with clear normal/off/emergency states. No LCD, holographic labels or invented live behavior.
- Emergency distribution cabinet, conduit/tray routes and clearly separated labeled lighting / radio / rescue-heat circuits. The drive circuit is absent. Accessible front service space >=1.0 m is a gameplay design target, not an electrical-code assertion.
- Battery cabinet with lid/door, hold-downs, protected terminals and short plausible cable runs. Fuel isolation and a modest day supply / integral tank with readable level; do not create a bulk fuel farm below occupied rooms.
- Two lower louvre assemblies and ducting. Read installation references before choosing flow direction. The current openings are on the west wall; assess intake/discharge separation. If a radiator discharge on another exterior wall is more coherent, deliver a precisely bounded shell-patch proposal in the fitted review rather than silently cutting the master. No exhaust or cooling air into the rooms above.
- Complete insulated exhaust route from engine to exterior riser: flexible connection, silencer, brackets, through-wall sleeve and weather cap. Current tubes are route proxies and include an unfinished wall connection. Correct them; do not preserve disconnected tubes merely to match the proxy. South reservation is clear of east occupied-room windows. No engineering certification is implied.
- West service double door with real inward pivots, louvred or solid as justified, frame, threshold and locking hardware. Finished opening >=1.40 x 2.10 m. Provide a plausible machine removal plan through the opening (or removable frame/panel) and document access-lift limitations of the elevated walkway.

## Gameplay / reach

Keep the doorway and path across the north half of the room clear. Position interactive controls where the operator can see them without stepping over pipes. Named empties: `WSE_START`, `WSE_TRANSFER`, `WSE_FUEL_ISOLATE`, `WSE_FUEL_CHECK`, `WSE_BATTERY_SERVICE`, `WSE_EMERGENCY_STOP`, `WSE_STATUS_READ`. Record reachable positions and state pivots in assembly.json. Provide stopped and running-indication review states; do not implement engine/audio/runtime code.

## Review and finish

Use references 9-12 for construction and room arrangement. Deliver neutral room overview, west service entrance, control close-up, machinery service side, louvre cross-section and entire exhaust route. Show a cutaway with slab hidden for review only and controls/cabinet doors open. Materials: concrete context, petrol machine paint, dark rubber, galvanized ducts, restrained oil/contact wear.

Verify fitted walking routes, service clearances, door/panel sweeps and every unique penetration. State ventilation, acoustic/fire separation and final load-sizing assumptions as design limitations rather than claiming a compliant installation. Follow the contract's asset-only source, fitted scene, manifests, provenance and saved/reopened checks. Live Unreal work remains a subsequent phase.
