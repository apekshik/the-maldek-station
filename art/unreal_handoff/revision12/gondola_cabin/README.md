# Gondola cabin integration

Source: `art/blender/gondola_cabin_01/Maldek_Gondola_Cabin.blend`.
The finished cabin retains its envelope and clear 120 × 210 cm entry, with two
63.5 cm sliding leaves, captive rollers, rack/pinion drive and guarded mechanism.
The interior adds olive seating, service panels, rails, framed service-box mounts,
assistance/release fittings, floor ribs and period signage.

`GondolaDoors.cpp` extends the existing route controller. Arrival stays closed
until stopped, the far gangway deployed, and a 0.75-second settling pause elapsed.
Opening takes 3.5 seconds; closing takes 1.75 seconds, followed by a 0.6-second
latch hold. Departure input queues this sequence. The far automatic dwell begins
after the doors are fully open; E also requests return from inside the cabin.

A player capsule in the doorway reverses closing and holds it open. An occupied
gangway delays departure. If someone steps onto the gangway after latching,
retraction is cancelled and the landing is restored before reopening. Movement
and gangway retraction require closed doors. The existing route geometry, speed
profile, terminal mechanisms and dim interior lamps remain in use.

Six exported meshes separate shell, glazing, leaves, pinion and reusable roller.
The shell uses ten explicit convex hulls for floor, roof, walls, jambs and benches;
independent moving boxes supply leaf collision. The imported basis is `(x,-y,z)`;
the established cabin yaw of 180 degrees produces `(-x,y,z)` at the floor-centre
pivot. Studio inspection lights are excluded. Old shell/detail actors are replaced
to avoid doubled surfaces; the original cabin-part list preserves the hanger and
lights without attaching the separate station machinery controller to the cabin.

The opening and closing sounds are actual CC0 train-door recordings by iamaviolin,
stored in `art/audio/gondola_doors`, referenced by the level and emitted from the
door drive with distance attenuation. Audio credits ship in
`game/Content/AudioCredits/Gondola_Doors.txt`.

Reproducible scripts live in `../scripts/gondola_cabin_*.py`. `manifest.json`
records source/FBX hashes, slots, pivots and collision; `install.json`,
`runtime.json`, `review/report.json` and `reopen.json` record the corresponding
Unreal checks when run. Test-only time acceleration, lighting and audio capture
overrides are restored at completion and are not level settings.

## Runtime evidence

The full player-capsule roundtrip passes at the existing route test's 8× time
acceleration, including door obstruction, occupied gangway and a late obstruction
during retraction. A separate run confirms 15 seconds of rider stability after
departure at normal game speed. Opening and closing recordings were captured
from the actual spatial audio output with nonzero samples and no clipping.

An exploratory 16× time-dilation run lost the rider during outbound travel;
`runtime_accelerated16.json` retains that result. Arbitrary accelerated moving-base
physics is not validated by this pass. The shipped game uses normal time; no
global movement or time-dilation setting was changed to make these checks pass.
