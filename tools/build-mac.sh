#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != Darwin ]]; then
  echo "Run this script on macOS with Unreal Engine 5.7 and full Xcode installed." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
engine_root="${UE_ROOT:-/Users/Shared/Epic Games/UE_5.7}"
project="$repo_root/game/game.uproject"
mode="${1:-editor}"
if [[ ! -f "$engine_root/Engine/Build/BatchFiles/Mac/Build.sh" ]]; then
  echo "UE 5.7 not found at $engine_root; set UE_ROOT to its installation directory." >&2
  exit 1
fi
xcodebuild -version

case "$mode" in
  editor)
    bash "$engine_root/Engine/Build/BatchFiles/Mac/Build.sh" \
      gameEditor Mac Development "$project" -WaitMutex
    ;;
  package)
    bash "$engine_root/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun \
      -project="$project" -noP4 -platform=Mac -clientconfig=Development \
      -build -cook -map=/Game/MaldekRefinement/R12/Station_R12 \
      -stage -pak -archive -archivedirectory="$repo_root/game/Saved/MacPackage" \
      -utf8output
    ;;
  *)
    echo "Usage: bash tools/build-mac.sh [editor|package]" >&2
    exit 2
    ;;
esac
