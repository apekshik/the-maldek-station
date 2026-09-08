# Integrated gondola drive, moving rope and positional machinery audio

The approved separate terminal study is installed in Station_R12. Millford has a motor, service brake, lower reducer, supported vertical shaft, upper angle gearbox and driven bullwheel. Maldek has a return bullwheel, guided tension carriage and hydraulic assembly. Old terminal meshes and the old disconnected lower-drive machinery are retired; the lower room's floor, walls and rails remain. Foundations extend to sampled terrain. The lower gearbox clears the retained perimeter upstand and has dedicated mounting feet.

## Motion

`AGondolaMechanism` reads `AGondolaSystem::GetRouteDistance()` after the gondola tick. Two bullwheels, two drive shafts and 80 pylon rollers use signed cable displacement to calculate rotation. Angles follow displacement/radius, with an illustrative 84.7224:1 input reduction and 8:1 intermediate shaft ratio. Stop and reversal propagate to every rotor. The 3.7755 m terminal wheels run about 17.7 rpm at the 3.5 m/s cruise speed. Round pylon rollers have visible hub fasteners.

The rope is a continuous 2,864.36 m tube, including both terminal wraps. UV.x is distance around the loop in metres; a dynamic material advects strand markings by the measured cable displacement. Full-precision UVs preserve detail over the long route. The empty return side travels in the opposite spatial direction. This is surface transport along the fixed sag profile; the rope's sag does not dynamically deform under the moving cabin.

The cabin remains a single reversing shuttle and stops before reaching either wheel. Its reduced lighting remains 12 lumens per interior light and 0.6 lamp emission. Separate cabin-door work is owned by the cabin task.

## Audio

Nine fixed spatial sources sit at the lower motor, gearbox, two bullwheels and five roller banks. A tenth moving emitter follows the cabin's hanger at 5.927 m above its floor. Motor and wheel playback responds to motion, speed controls pitch, and brake release/set cues play at transitions. The previous always-on flywheel loop is retired. Distance attenuation, stereo spatialization and wall occlusion make the sound originate at the machinery.

Source recordings, exact edits, licenses and hashes are in `art/audio/gondola_drive/sources.json`. Credits are also staged in `game/Content/AudioCredits/Gondola_Drive.txt`. Sources are onursamli's Electric Motor 1 and Felix Blume's Electric motor (CC0), plus Dan_AudioFile's ski-lift terminal recording (CC BY 4.0). Loop preparation uses recorded excerpts, mono conversion, filtering, soft peak compression and seam crossfades.

`audio_final/validation.json` records actual Unreal mixer output at the full configured sound gain: near motor about -14 dBFS in the dominant channel, approximately 39 dB left/right separation, combined nearby drive about -20 dBFS, digital silence at 200 m, and no clipped samples. The test temporarily uses an 80 cm/s cruise setting to exercise full sound gain during the staged approach. Normal gameplay remains 350 cm/s cruise. All nine motion loops stop at docking.

The initial background capture was muted by FApp's 0.0 unfocused volume multiplier. `StationMigrationLibrary.set_pie_audio_capture_enabled` temporarily overrides that setting and restores it afterward; no shipping audio-focus configuration was changed. Playback-state assertions alone are insufficient: the final checks also examine captured PCM levels.

## Validation and reproduction

- `runtime.json`: actual rider arrival, E departure, full outbound/return, occupied-gangway hold and boarding. 1,254 mechanism observations, maximum rotor-vector error 0.001731 (about 0.1 degree), rope phase error below 1e-10 m.
- `rope_shader.json`: every material connection checked and compiled shader errors empty.
- `reopen.json`: installed references, full-precision UVs, dim cabin lights, retired duplicates and unchanged terrain traces after reopening.
- `verified_views/` and `motion_final/`: in-engine review images. Far-terminal neutral inspection temporarily disables fog only in the disposable PIE world. Gameplay fog is retained.

Build/restart gameEditor after native changes. In background Blender run `gondola_mechanism_export.py`, `gondola_mechanism_lower_shell.py` and `gondola_mechanism_pylons.py`. Run `art/audio/gondola_drive/prepare.py` in the audio Python environment. In the idle editor run `gondola_mechanism_install.py`, then `gondola_mechanism_audio.py`, then `gondola_mechanism_rope_material.py`. This pass follows the previous gondola_route installation and supersedes its static terminal/cable meshes. Do not rerun the old route finish script after this pass: it moves the distant facade back into the terminal envelope.

Use unique request IDs with the existing R12 dispatcher and wait for asynchronous tests/captures to finish before another editor job. The export classifies objects by evaluated bounds because Blender curves can have an origin at zero with control points located at another terminal. Wheel export asserts a compact radius to catch cross-terminal grouping errors. Screenshot sequences wait for the actual file and a new cable displacement before requesting another frame.
