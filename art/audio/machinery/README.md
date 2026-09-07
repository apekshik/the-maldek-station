# Station machinery audio

Four sourced CC0 recordings, preserved in originals with provenance in sources.json. Generator is a real diesel generator; flywheel is a recorded coffee-grinder wheel mechanism used as bearing foley; ventilation is the creator's edited extractor-fan recording; cable is a real rope pulley. These are sound-design proxies where noted, not recordings of this specific gondola. No synthesis or generated sound.

Preparation performs only excerpts, mono conversion/resampling, DC removal, gain and 250ms circular loop crossfades. World loops have finite linear distance attenuation, 3D panning, and wall occlusion (0.35 volume and 1.8kHz low-pass). Generator emitter is above its housing to prevent self-occlusion. Flywheel emitter is beside the surveyed bearing pedestal. Ventilation is at control-room ceiling height. Installation is idempotent by actor label.

Cable audio follows the moving cabin mesh of the existing GondolaSystem, not its long spline bounds. Motion drives an attack/release envelope. The source reaches silence beyond 67.5m and loses high frequencies with distance; it fades out at rest. Teleports above 30m/s do not trigger motion sound. This adds audio without changing departure schedules or cabin geometry.

Flashlight clicks retain their original recordings, raised from 0.35 to 0.85 peak and pawn switch multiplier from 0.7 to 1.0: approximately +10.8dB combined. A/B intro selection is preserved.

Install with revision12/scripts/install_machinery_audio.py and install_opening.py. Credits are staged in Content/AudioCredits/Machinery.txt. Runtime evidence is in revision12/machinery_audio/.

Validation: 13 machinery/click/motion checks passed in PIE, including cable activation during travel and silence after stopping. Six recorded output captures are non-silent and unclipped. Generator near capture is over 7dB louder than the far capture (which retains other world ambience). The revised A/B pass adds 15 successful transition/gain/timed-fade checks; its combined recording peaks at 0.658. Cable movement validation disables the target's ordinary tick and moves its mesh only inside PIE, preserving the saved production spline and departure schedule.

The updated default-map Development package built successfully and passed startup smoke. Packaged machinery credits verified; startup screenshot reviewed. Editor reopened normally in Station_R12 after capture (no unfocused-audio override).
