# Build on the Mac

Use Unreal Engine **5.7** and Git LFS. The current rendering baseline is the
18 GB M3 Pro; performance and the Mac build still need validation on that machine.

Install UE 5.7 through Epic Games Launcher, including Mac platform support, and
install full Xcode. Open Xcode once to finish its setup and accept its license.
Select it with `sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer`.
Epic lists macOS Sonoma 14 and Xcode 15.2 as minimums, with Xcode 15.4 or newer
recommended. Use a version accepted by the installed engine's
`Engine/Config/Apple/Apple_SDK.json` rather than bypassing its version checks.
[Epic's requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/macos-development-requirements-for-unreal-engine?application_version=5.7).

From the repository root on the Mac:

```sh
git lfs install
git pull --ff-only origin main
git lfs pull
git lfs fsck
bash tools/build-mac.sh editor
```

For a new checkout, first run
`git clone https://github.com/apekshik/the-maldek-station.git` and enter its directory.
Do not copy Windows Binaries, Intermediate, or Saved folders. The assets are in
Git LFS: downloading just the GitHub source ZIP is insufficient.

After the editor build succeeds, open `game/game.uproject` in UE 5.7 and test
`/Game/MaldekRefinement/R12/Station_R12`. Shader compilation on the first launch
can take time. To compile, cook and package a local Development build:

```sh
bash tools/build-mac.sh package
```

Output goes to `game/Saved/MacPackage`. Override the default engine path with
`UE_ROOT="/your/path/UE_5.7" bash tools/build-mac.sh editor`.
The package command explicitly cooks the current station map and its dependencies.
It does not configure distribution signing or notarization for friends' machines.

The optional Gaea import plugin is local Windows authoring tooling and is excluded
on Mac. Baked landscape/assets remain in the project. The bundled Procedural
Vegetation plugin declares Mac support; StationMigrationTools and the game module
ship their source. No Windows-only calls were found in the project C++ sources.
This is a source review, not a successful Mac compilation or performance test.
