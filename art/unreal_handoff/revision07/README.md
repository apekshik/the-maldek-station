# R07 — fog around the playable station

Open `/Game/MaldekRefinement/R07/BlockOut_R07`.

R06's Ultra Dynamic Sky had volumetric fog disabled. Its height fog was already near platform elevation, but the broad distance haze did not provide light-scattering mist around the playable decks. R07 enables UDS volumetric fog, reduces global haze density and color intensity, and places two local fog volumes around the station and relay approach. Existing geometry, snow, trees and weather actors are inherited from R06.

The station volume has a 36 m radius; the relay volume has a 28 m radius. Both sit near deck elevation, use radial extinction 0.6, height extinction 0.05 and height falloff 2, with zero emissive contribution. Existing point lights use volumetric scattering intensity 2; their surface-light intensity stays at its R06 value.

Six provisional spotlights in the `R07_Lighting_Study` folder test architectural lighting positions: two beneath the main platform canopy, two beneath the platform around the lower machinery/exit, and two at the relay path bend and doorway. Neutral 4700 K main-floor lights contrast with warmer 3200-4000 K lower-deck and route lights. These are movable, shadow-casting light components with 9-11 m attenuation radii; decorative fixture meshes are not included. Their deliberately low 7-13 lumen values suit this level's existing night exposure. Moon intensity is restored to 0.15 and skylight to 1.0 after the ambient-light diagnostic.

The local fog start distance is explicitly set to 100 cm in `game/Config/DefaultEngine.ini`, overriding the engine's 2000 cm default. This project-wide setting lets local fog reach nearby player views; R07 is the first level in this work that contains local fog volumes. The UDS volumetric distance remains 80 metres. See [the final gallery](SHOTS.md).

Implementation notes from installed UE 5.7 source: `LocalFogVolumeComponent.h` defines the unscaled volume radius as 500 cm. Actor bounds return the editor icon, not that radius. `VolumetricFog.usf` combines radial and height coverage multiplicatively during local-volume injection; both extinction terms must be nonzero. A radial-only diagnostic therefore gave no useful local fog in this configuration. Height falloff 2 avoids an abrupt vertical density gradient.

The camera checks include the upper platform, lower deck, relay approach and the same overview used for R06. Captures use saved scene lighting with no temporary inspection lights or exposure changes. The level was saved and reopened, asserting both volume radii/densities, volumetric fog enabled, and 100 cm local start distance. This change requires a GPU performance check at the 1440p/60 FPS target; still images do not establish that target. Local fog spheres can enter enclosed rooms; room-specific exclusion and dynamic-weather transitions remain future tuning work.

To reproduce: open R07, run `../scripts/set_r07_local_fog.py`, then `../scripts/capture_r07_study.py` in Unreal's Python environment. The latter places the six lights, saves/reloads and verifies the map, then renders four views into `final_renders/`. Existing labeled actors are updated, so rerunning does not duplicate lights or mist volumes.

Reference: [Epic's UE 5.7 Local Fog Volumes documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/local-fog-volumes-in-unreal-engine?application_version=5.7). The documentation covers local placement, volumetric lighting, and the default local-fog start distance.
