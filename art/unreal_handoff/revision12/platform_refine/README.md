# Quarters sightline and platform markers

The west/front canopy in front of the living quarters is removed from Station_R12,
including its west support assembly, bracket and attached R09 lamps. The eastern
canopy and quarters building remain. The removed actor list and original transforms
are recorded in installation.json; preserve.json records the other actor transforms.
No shared mesh assets were edited. Reimporting the old scene must not respawn these
retired canopy actors.

Fourteen rail-mounted red markers use the existing gondola lens and base materials:
eight platform corners and three pairs along the lookout bridge, including its far
end. Every location was traced to its existing rail top. Each marker has a 12 cm
lens, a small mounting base and a 0.045 lumen red spill with a 90 cm radius. Marker
geometry has no collision, and spill lights cast no shadows or volumetric light.

Run platform_refine_install.py through the R12 dispatcher to reproduce placement.
platform_review_capture.py records the quarters window and platform/bridge views.
The before and day_after folders show the opened sightline; night_after shows the
result at the original night settings. platform_refine_reopen.py saves, reopens and
checks actor preservation, removal, markers and restored sky settings.
