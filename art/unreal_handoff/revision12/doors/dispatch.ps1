param([Parameter(Mandatory=$true)][string]$Script)
$ErrorActionPreference='Stop'
$requestPath=Join-Path (Split-Path $PSScriptRoot -Parent) 'request.json'
$jobText=@{id=('doors-'+[guid]::NewGuid().ToString());script=$Script}|ConvertTo-Json -Compress
$jobBytes=[Text.Encoding]::UTF8.GetBytes($jobText)
$jobStream=[IO.File]::Open($requestPath,[IO.FileMode]::CreateNew)
try { $jobStream.Write($jobBytes,0,$jobBytes.Length) } finally { $jobStream.Dispose() }
Write-Output $jobText
