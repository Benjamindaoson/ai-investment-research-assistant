param(
    [string]$Domain = "localhost",
    [string]$OutputDir = "infra/secrets/tls",
    [int]$Days = 365
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$targetDir = Join-Path $root $OutputDir
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$crtPath = Join-Path $targetDir "tls.crt"
$keyPath = Join-Path $targetDir "tls.key"

function Use-OpenSsl([string]$opensslBin) {
    & $opensslBin req -x509 -nodes -newkey rsa:2048 `
        -keyout $keyPath `
        -out $crtPath `
        -days $Days `
        -subj "/CN=$Domain" | Out-Null
}

$opensslCommand = Get-Command openssl -ErrorAction SilentlyContinue
if ($opensslCommand) {
    Use-OpenSsl $opensslCommand.Source
    Write-Host "Generated TLS cert with openssl: $crtPath"
    exit 0
}

$gitOpenSsl = "C:\Program Files\Git\usr\bin\openssl.exe"
if (Test-Path $gitOpenSsl) {
    Use-OpenSsl $gitOpenSsl
    Write-Host "Generated TLS cert with Git openssl: $crtPath"
    exit 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "openssl not found and docker unavailable; cannot generate TLS cert."
}

$dockerVolume = "${targetDir}:/out"
$dockerCmd = "apk add --no-cache openssl >/dev/null && openssl req -x509 -nodes -newkey rsa:2048 -keyout /out/tls.key -out /out/tls.crt -days $Days -subj '/CN=$Domain'"
docker run --rm -v $dockerVolume alpine:3.20 sh -lc $dockerCmd | Out-Null

if (-not (Test-Path $crtPath) -or -not (Test-Path $keyPath)) {
    throw "TLS cert generation failed: expected files not found in $targetDir"
}

Write-Host "Generated TLS cert with docker: $crtPath"
