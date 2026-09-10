param(
    [string]$EnvFile = ".env.prod",
    [string]$SecretsDir = "infra/secrets",
    [switch]$NoClearPlaintext
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$envFilePath = Join-Path $root $EnvFile
$secretsDirPath = Join-Path $root $SecretsDir

if (-not (Test-Path $envFilePath)) {
    throw "env file not found: $envFilePath"
}

New-Item -ItemType Directory -Force -Path $secretsDirPath | Out-Null

$lines = Get-Content $envFilePath

function Get-LineValue([string]$key) {
    $line = $lines | Where-Object { $_ -match "^$key=" } | Select-Object -First 1
    if (-not $line) { return "" }
    return ($line -replace "^$key=", "").Trim()
}

function Set-LineValue([string]$key, [string]$value) {
    $found = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^$key=") {
            $lines[$i] = "$key=$value"
            $found = $true
            break
        }
    }
    if (-not $found) {
        $script:lines += "$key=$value"
    }
}

$mappings = @(
    @{ Key = "APP_SECURITY_API_KEY"; FileName = "app_security_api_key.txt"; Required = $true },
    @{ Key = "OPENAI_API_KEY"; FileName = "openai_api_key.txt"; Required = $true },
    @{ Key = "DB_PASSWORD"; FileName = "db_password.txt"; Required = $true },
    @{ Key = "MAIL_PASSWORD"; FileName = "mail_password.txt"; Required = $false },
    @{ Key = "REDIS_PASSWORD"; FileName = "redis_password.txt"; Required = $false }
)

foreach ($m in $mappings) {
    $key = $m.Key
    $fileKey = "${key}_FILE"
    $directValue = Get-LineValue $key
    $fileValue = Get-LineValue $fileKey

    if (-not [string]::IsNullOrWhiteSpace($directValue)) {
        $targetFile = Join-Path $secretsDirPath $m.FileName
        Set-Content -Path $targetFile -Value $directValue -NoNewline
        Set-LineValue $fileKey "/run/secrets/$($m.FileName)"
        if (-not $NoClearPlaintext) {
            Set-LineValue $key ""
        }
        Write-Host "Migrated $key to file $targetFile"
        continue
    }

    if ($m.Required -and [string]::IsNullOrWhiteSpace($fileValue)) {
        Write-Warning "Required secret missing in env file: $key or $fileKey"
    }
}

Set-LineValue "GATEWAY_NGINX_CONF" "infra/nginx/nginx-tls.conf"
Set-LineValue "GATEWAY_HTTP_PORT" "8080"
Set-LineValue "GATEWAY_HTTPS_PORT" "8443"

$lines | Set-Content $envFilePath
Write-Host "Updated env file: $envFilePath"
