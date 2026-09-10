$ErrorActionPreference = 'Stop'
$package = Split-Path $PSScriptRoot -Parent
$metadata = Get-Content (Join-Path $package 'texture_api.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force (Join-Path $package 'textures') | Out-Null
foreach ($map in @('Diffuse', 'Rough', 'nor_gl')) {
    $entry = $metadata.$map.'2k'.jpg
    $filename = [IO.Path]::GetFileName(([Uri]$entry.url).AbsolutePath)
    $destination = Join-Path $package "textures/$filename"
    Invoke-WebRequest $entry.url -OutFile $destination
    if ((Get-FileHash $destination -Algorithm MD5).Hash.ToLower() -ne $entry.md5) {
        throw "Texture hash mismatch: $filename"
    }
}
