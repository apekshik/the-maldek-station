# Hold right mouse to look closer

Hold the right mouse button for a restrained 12-degree field-of-view reduction.
The view eases in and out with an exponential response (about 0.3 seconds to reach
90%). Releasing restores the underlying camera FOV. This is a temporary camera
offset; it does not change the saved FOV, torch focus/range, movement speed or
collision. Existing breathing, gait sway and stair smoothing remain active.

The presentation component exposes InspectFovReduction for tuning. The offset
cannot narrow the base camera below 40 degrees. Zoom requires both the press
request and the currently held physical input, preventing a missed release from
latching it on; ignored look input also suppresses it.

`scripts/test_look_closer.py` sends real PIE mouse-button events and samples the
camera manager. It checks intermediate/monotonic FOV changes, the 12-degree
endpoint, release restoration, independent torch focus and speed, and the
missing-release guard. `runtime.json` records the actual test outcome.

The real PIE check passed: 90-degree normal view to 78 degrees held, intermediate
frames present, monotonic transition, restored FOV on release, unchanged beam and
speed, and no latch without the button. The initial background-throttled trial
sampled only after most of the transition; the final test disables that editor
throttle temporarily and restores it afterward. Development Editor build passed.
