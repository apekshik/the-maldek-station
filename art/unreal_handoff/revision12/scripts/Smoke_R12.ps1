param([switch]$UseDefaultMap, [int]$BenchmarkSeconds = 300, [string]$ReportSubdirectory = '', [string]$ExpectedGameMode = 'BP_ForestGameMode_C', [string]$ExpectedPawn = 'BP_ForestWalker_C')
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$reportRoot = Split-Path $PSScriptRoot -Parent
if ($ReportSubdirectory) { $reportRoot = Join-Path $reportRoot $ReportSubdirectory }
$variant = if ($UseDefaultMap) {'default'} else {'explicit'}
$executable = Join-Path $repoRoot 'game/Saved/R12Package/Windows/game.exe'
if (-not (Test-Path -LiteralPath $executable)) { throw "Packaged executable missing: $executable" }
$logPath = Join-Path $reportRoot "package-$variant-smoke.log"
$shotPath = (Join-Path $reportRoot "package-$variant-startup.png").Replace('\','/')
$commands = "stat unit, obj list class=$ExpectedPawn, obj list class=SurfaceFootstepComponent, r.HighResScreenshotDelay 120, HighResShot 2560x1440 filename=$shotPath"
$arguments = @('-windowed','-ResX=2560','-ResY=1440','-unattended','-benchmark',"-seconds=$BenchmarkSeconds","-abslog=`"$logPath`"","-ExecCmds=`"$commands`"")
if (-not $UseDefaultMap) { $arguments = @('/Game/MaldekRefinement/R12/Station_R12') + $arguments }
$startedAt = Get-Date
$process = Start-Process -FilePath $executable -ArgumentList $arguments -WindowStyle Hidden -PassThru
$process.WaitForExit()
$process.Refresh()
$text = Get-Content -LiteralPath $logPath -Raw
$checks = @{
 normal_exit=($process.ExitCode -eq 0)
 r12_world=($text -match 'Bringing World /Game/MaldekRefinement/R12/Station_R12')
 expected_game_mode=($text.Contains("Game class is '$ExpectedGameMode'"))
 real_d3d12=($text -match 'LogD3D12RHI:')
 no_fatal=($text -notmatch 'Fatal error:|Assertion failed:|LowLevelFatalError|Unhandled Exception')
}
$report = @{ success=($checks.Values -notcontains $false); checks=$checks; explicit_map=(-not $UseDefaultMap.IsPresent); exit_code=$process.ExitCode; started=$startedAt.ToUniversalTime().ToString('o'); finished=(Get-Date).ToUniversalTime().ToString('o'); executable=$executable; log=$logPath; intended_benchmark_seconds=$BenchmarkSeconds; visual_review_required=$true }
$report | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $reportRoot "package-$variant-smoke.json")
if (-not $report.success) { exit 1 }
