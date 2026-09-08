# Title and loading flow

The native `UStationStartupGameInstance` owns the packaged desktop startup. The default game map is the small engine Entry map; the editor startup remains Station_R12. Begin shift travels to Station_R12. Quit exits normally. The title screen crossfades between three real map captures staged under Content/UI/Menu, with stationary controls on a dark panel. It has no live station scene dependency. Loading screens use built-in Slate text and shapes.

The initial packaged readiness test exposed a streaming refresh ID that never advanced. The gate now observes pending render-asset initialization/streaming and outstanding resource demand directly. A packaged warm-cache test released the opening after 5.6 seconds, with the opening starting exactly once at elapsed 0.000. Final Win64 Development game compilation and packaging passed. Mac/Metal validation remains outstanding.

Scenic menu validation: Win64 Development game build and package restaging passed. An offscreen packaged run loaded all three captures and produced a 1280x720 UI screenshot, visually checked for framing and readable controls (`game/Saved/StartupValidation/scenic-menu.png`). The test exited automatically. Logs: `scenic-build.log`, `scenic-stage.log`, and `scenic-preview.log` in the same validation directory. Mac/Metal has not been tested for this change.

## Loading stages

1. A MoviePlayer Slate screen animates during blocking map travel. It contains no UObject bindings and can render while the game thread loads the map. Its automatic completion only ends this travel phase.
2. A matching opaque viewport screen covers the loaded station while the world continues rendering. Player movement/look and gameplay input remain held. The existing opening component does not advance its clock or start its opening audio yet.
3. Readiness requires BeginPlay, a local pawn/camera, no outstanding async package load, all requested-visible streaming levels visible, and `FShaderPipelineCache::NumPrecompilesRemaining() == 0`.
4. The render-asset streamer wanted-resource count and all non-template render assets pending initialization/streaming must reach zero. This is demand under the current streaming budget, not a requirement to load every texture at maximum resolution.
5. These conditions must remain satisfied for 30 consecutive scene draw submissions, allowing the initial camera view and temporal histories to warm up. This is a configurable heuristic; it does not prove every GPU effect has converged. New queue activity resets that count. A render-command fence must complete before the next core tick releases the cover.
6. The cover is removed and input ownership is returned; the existing opening starts on its next tick, with its original six-second opening timing intact.

There is no fixed-time success or fake percentage. After 90 seconds the message acknowledges a longer preparation; the user can continue waiting or quit. A travel failure shows an installation error and Quit. During blocking travel the animated indicator remains active; the viewport Quit button becomes interactive once map travel returns.

PIE bypasses the startup screen/gate to preserve direct editor iteration. Test the complete flow in a packaged build or standalone game. Starting standalone with Station_R12 explicitly on the command line skips the title, but still performs the readiness gate.

## Platform and diagnostic limits

Cooked shader code, runtime driver PSO creation, texture streaming, and temporal-history warmup are separate stages. A pixelated first scene and a transient 0 FPS display do not establish which one was responsible. `LogStationStartup` records outstanding PSOs, wanted resources, pending render assets, visible levels, consecutive ready frames, and time to release. These are startup diagnostics, not a full performance profile.

The same C++ code targets UE 5.7 Windows and Mac/Metal. It uses the RHI-supported precache count; zero does not prove that every future view is precached. Windows driver caches cannot be shipped as Metal caches. Generate and test any bundled cache per target platform, and validate cold and warm starts on the 18 GB M3 Pro separately. Avoid forcing full texture residency or importing Windows-only PSO settings into the Mac profile.

The Mac package script explicitly cooks both Entry and Station_R12. Keep both when overriding maps on any command line. Source/Config changes must reach the Mac only after its current build finishes; these changes have not been pushed by this task.

## Validation procedure

- Build game and gameEditor Win64 Development, then cook/package both maps.
- Launch without a map argument: title should cover Entry, accept keyboard/mouse Begin shift, and Quit normally.
- Begin shift: inspect the animated travel screen and the post-load preparation cover; no playable scene or opening audio should start early.
- Verify readiness logs reach zero PSOs/resources and the frame threshold, followed by one opening release. Check the existing opening, flashlight guidance, and movement after its original delay.
- Test Quit from the title and preparation screen. Test an invalid StationMap override for a clear failure state.
- Test with ordinary and cold driver cache conditions on each platform; do not infer cold-cache behavior from an already-warmed editor.
- Inspect memory pressure and startup Insights traces on the 18 GB Mac. This UI does not by itself raise steady-state FPS.

Reference: [Epic UE 5.7 PSO precaching](https://dev.epicgames.com/documentation/en-us/unreal-engine/pso-precaching-for-unreal-engine?application_version=5.7).

## Latest packaged checks

The final native Begin shift action was exercised through its shared StationBeginShift Exec entry point in an offscreen Win64 Development package. With -clearPSODriverCache, the log confirmed cache clearing and the outstanding PSO queue drained before release at 65.6 seconds. The opening then started exactly once at elapsed 0.000. This is one machine's startup measurement, not a Mac estimate. The shorter initial cold test timed out before compilation completed; the extended test verified release.

An invalid StationMap override exercised the same action and produced the expected missing-map failure without starting the opening. Runtime smoke tests disabled audio; opening timing was checked through logs. The final native build tested the game target; the editor target was built earlier in development. Logs and validation.json are under game/Saved/StartupValidation. The playable local package is game/Saved/StartupReadyStage/Windows/game.exe. Changes remain local and unpushed.
