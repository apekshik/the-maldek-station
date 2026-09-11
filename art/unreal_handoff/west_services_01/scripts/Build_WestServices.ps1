$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$reportRoot = Split-Path $PSScriptRoot -Parent
$uat = 'C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/RunUAT.bat'
$projectFile = Join-Path $repoRoot 'game/game.uproject'
$packageDirectory = Join-Path $repoRoot 'game/Saved/WestServicesPackage'
$buildLog = Join-Path $reportRoot 'package-build.log'
$arguments = @('BuildCookRun', "-project=$projectFile", '-noP4', '-platform=Win64', '-clientconfig=Development', '-build', '-cook', '-stage', '-pak', '-archive', "-archivedirectory=$packageDirectory", '-unattended', '-utf8output')
$startedAt = Get-Date
& $uat @arguments *> $buildLog
$resultCode = $LASTEXITCODE
@{ success=($resultCode -eq 0); exit_code=$resultCode; started=$startedAt.ToUniversalTime().ToString('o'); finished=(Get-Date).ToUniversalTime().ToString('o'); configuration='Development'; platform='Win64'; entry='Default Entry / StationBeginShift'; archive=$packageDirectory; log=$buildLog } | ConvertTo-Json | Set-Content (Join-Path $reportRoot 'package-build.json')
exit $resultCode
