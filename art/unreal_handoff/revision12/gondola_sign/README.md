# Gondola neon status sign integration

Approved source: `art/blender/gondola_status_sign_01/Maldek_Gondola_Status_Sign.blend`.
Exported cabinet and four independent tube circuits are installed in
`/Game/MaldekRefinement/R12/GondolaSign` and placed in `Station_R12`.

The fixed pedestal sits on the **left when facing the mountains**, 150 cm left
of the cabin centre and 630 cm in front of its floor origin. Four support traces
confirm a level platform surface. The sign is never attached to `CabinParts`.
Only the cabinet/post have collision; the neon circuits have no collision.

`AGondolaStatusSign` reads `AGondolaSystem::GetPlatformStatus` every 0.1 seconds
after the gondola tick. Four dynamic material instances control `GlowStrength`.
The controller holds no duplicated travel timers or door animation state.
Runtime uses strength 7 for the active circuit and 0 for inactive emission,
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
inspection lighting and test settings are removed before saving. The first position
was screened by a column; the final placement moves the sign to player-view left,
forward of the machinery. Ten approach sightlines are checked, followed by fresh
night/neutral images, capsule boarding/exit and departure at the final position.
The extended walk begins 740 cm in front of the cabin, passes the sign at 630 cm,
boards, exits and reboards. A diagnostic starting at 780 cm overlapped the existing
approach barrier (exit stopped at 768.4 cm); the final test starts inside that barrier.

The shared map already contained the completed parking navigation changes. Those
are preserved; their two referenced mesh assets accompany the map in the remote
commit so that the saved level has no missing parking dependencies.
