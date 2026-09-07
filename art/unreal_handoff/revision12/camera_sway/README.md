# Idle breathing and lateral gait sway

The R12 player now has slow, centered breathing and balance motion at rest. Two
different balance rhythms soften the regular breathing cycle. Idle movement
blends out as gait motion takes over, and fades while airborne. It never moves
the collision capsule or accumulates into the player's control rotation.

At the current HeadBobScale of 0.7, idle vertical movement peaks around 0.21 cm
and lateral balance around 0.14 cm. Walking lateral amplitude is about 0.63 cm;
running rises to about 1.16 cm. Gait cadence follows actual grounded speed. Small
pitch/yaw/roll offsets accompany the motion, with no FOV change. The held torch
shares idle motion and retains its existing aiming lag.

The critically damped stair-height correction is preserved, and gait motion is
still reduced on steps. HeadBobScale controls voluntary camera motion, including
idle breathing; zero disables it while retaining stair smoothing. IdleSwayScale,
WalkSwayCm and RunSwayCm allow independent tuning on the presentation component.

`polish_validate_player.py` now samples eight seconds of idle motion, verifies
that the capsule and input aim stay still and footsteps remain silent, compares
walk/run lateral range, tests the return to bounded idle motion, and verifies the
zero-scale option. Existing torch and unlimited-sprint checks remain. Run with
output `camera_sway` and focused_intensity 1.35. The earlier requirement for an
absolutely still idle camera is superseded by this requested breathing behavior.

Runtime route and player reports record measured results. Automated motion
bounds do not establish subjective comfort; the reopened R12 is available for
the user's playtest and further amplitude tuning.

Editor validation passed: measured lateral range was 1.26 cm walking and 2.31 cm
running. Idle breathing, unchanged aim/capsule, idle silence, return to idle and
zero-scale checks all passed. All six stair traversals passed at full walking
input. The Development Editor build succeeded; packaged results are recorded
separately in this directory.
