# Gondola neon status sign integration

Approved source: `art/blender/gondola_status_sign_02/Maldek_Gondola_Status_Sign.blend`.
Blender revision 02 replaces the tall pole-mounted design with a 2.60 m wide by 1.30 m tall panel: BOARD / ARRIVING above DEPART / AWAY. Exported cabinet and four independent tube circuits are installed in
`/Game/MaldekRefinement/R12/GondolaSign` and placed in `Station_R12`.

The wide two-by-two cabinet on two low bolted shoes sits on the small roof to the **right of the gondola** when facing the mountains, 350 cm right and 250 cm in front of the cabin floor origin, with its base 360 cm above the platform. It faces left toward the incoming upper-platform route (actor yaw -90 degrees). Eight support traces confirm the roof surface. The sign is never attached to `CabinParts`.
Only the cabinet and mounting shoes have collision; the neon circuits have no collision.

`AGondolaStatusSign` reads `AGondolaSystem::GetPlatformStatus` every 0.1 seconds
after the gondola tick. Four dynamic material instances control `GlowStrength`.
The controller holds no duplicated travel timers or door animation state.
Runtime uses strength 11 for the active circuit and 0 for inactive emission,
keeping the coloured glass visible under normal lighting without glowing at night.

| Status | Runtime condition |
| --- | --- |
| BOARD | Stopped at this terminal, landing ready, doors fully open, no departure request |
| ARRIVING | Inbound within the existing slow zone, or stopped while landing/doors prepare |
| DEPART | Departure queued, including obstruction reopening and latch/bridge interlocks |
| AWAY | Cabin absent, outbound, or still waiting for the first arrival trigger |

A missing gondola reference falls back to AWAY. The other terminal's status is
also supported by the controller; this pass installs the approved Millford sign.

Validation evidence: `install.json`, `placement.json`, `runtime.json`,
`first_runtime.json`, `reopen.json` and `review/`.
The first runtime exercise uses the actual route and door state machine, including an
obstruction and a full return journey; travel is accelerated 8× during the test.
Player boarding and exit and review captures run at normal speed. Temporary
inspection lighting and test settings are removed before saving. The roof placement is checked from two points along the incoming upper platform, with ten clear sightlines. Fresh night and neutral views include the incoming route (10_approach_night). The waiting hall still occludes the sign earlier on the intro route (11_intro_approach); it becomes visible as the player rounds the buildings onto the gondola-facing upper platform. These views are retained together with capsule boarding/exit and departure checks. The earlier full-roundtrip test remains applicable to the unchanged sign controller.

The shared map already contained the completed parking navigation changes. Those
are preserved; their two referenced mesh assets accompany the map in the remote
commit so that the saved level has no missing parking dependencies.

The brightness pass is captured under actual night lighting, with the torch off, at three player-height viewpoints in `night_distance/`. Exact eye-to-panel distances and runtime circuit validation are recorded in `night_distance.json`. The earlier `review/` captures show the prior strength 7 finish.
