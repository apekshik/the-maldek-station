param([switch]$UseDefaultMap, [string]$ReportSubdirectory = '')
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$reportRoot = Split-Path $PSScriptRoot -Parent
if ($ReportSubdirectory) { $reportRoot = Join-Path $reportRoot $ReportSubdirectory }
$uat = 'C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/RunUAT.bat'
$projectFile = Join-Path $repoRoot 'game/game.uproject'
$packageDirectory = Join-Path $repoRoot 'game/Saved/R12Package'
$buildLog = Join-Path $reportRoot 'package-build.log'
$arguments = @('BuildCookRun', "-project=$projectFile", '-noP4', '-platform=Win64', '-clientconfig=Development', '-build', '-cook', '-stage', '-pak', '-archive', "-archivedirectory=$packageDirectory", '-unattended', '-utf8output')
if (-not $UseDefaultMap) { $arguments += '-map=/Game/MaldekRefinement/R12/Station_R12' }
$startedAt = Get-Date
& $uat @arguments *> $buildLog
$resultCode = $LASTEXITCODE
$report = @{ success=($resultCode -eq 0); exit_code=$resultCode; started=$startedAt.ToUniversalTime().ToString('o'); finished=(Get-Date).ToUniversalTime().ToString('o'); configuration='Development'; platform='Win64'; explicit_map=(-not $UseDefaultMap.IsPresent); archive=$packageDirectory; log=$buildLog }
$report | ConvertTo-Json | Set-Content (Join-Path $reportRoot $(if ($UseDefaultMap) {'package-default-build.json'} else {'package-explicit-build.json'}))
exit $resultCode
