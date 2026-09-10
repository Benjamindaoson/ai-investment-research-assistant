param(
    [switch]$StrictApi
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Add-Error([string]$msg) { $errors.Add($msg) }
function Add-Warn([string]$msg) { $warnings.Add($msg) }

function Get-EnvValue([string]$key, [string]$envFilePath) {
    $envValue = [Environment]::GetEnvironmentVariable($key)
    if (![string]::IsNullOrWhiteSpace($envValue)) {
        return $envValue
    }

    if (Test-Path $envFilePath) {
        $line = Get-Content $envFilePath | Where-Object { $_ -match "^$key=" } | Select-Object -First 1
        if ($line) {
            return ($line -replace "^$key=", "").Trim()
        }
    }
    return ""
}

function Resolve-SecretFilePath([string]$path, [string]$rootPath) {
    if ([string]::IsNullOrWhiteSpace($path)) {
        return ""
    }
    if ($path.StartsWith("/run/secrets/")) {
        $fileName = $path.Substring("/run/secrets/".Length)
        return Join-Path "$rootPath\infra\secrets" $fileName
    }
    return $path
}

function Get-EffectiveSecret([string]$key, [string]$envFilePath) {
    $directValue = Get-EnvValue $key $envFilePath
    if (-not [string]::IsNullOrWhiteSpace($directValue)) {
        return $directValue
    }
    $fileKey = "${key}_FILE"
    $secretFilePath = Resolve-SecretFilePath (Get-EnvValue $fileKey $envFilePath) $root
    if ([string]::IsNullOrWhiteSpace($secretFilePath)) {
        return ""
    }
    if (-not (Test-Path $secretFilePath)) {
        Add-Error "$fileKey points to missing file: $secretFilePath"
        return ""
    }
    $fileValue = Get-Content $secretFilePath | Select-Object -First 1
    return ($fileValue).Trim()
}

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Add-Error "java not found in PATH"
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Add-Error "docker not found in PATH"
}
if (-not (Get-Command mvn -ErrorAction SilentlyContinue) -and -not (Test-Path "$root\.tools\apache-maven-3.9.12\bin\mvn.cmd")) {
    Add-Error "maven not found and local toolchain missing: .tools/apache-maven-3.9.12/bin/mvn.cmd"
}

$webJar = "$root\stock-web\target\stock-web-1.0-SNAPSHOT.jar"
$mcpJar = "$root\stock-mcp\target\stock-mcp-1.0-SNAPSHOT.jar"
if (-not (Test-Path $webJar)) { Add-Warn "missing artifact: $webJar (run mvn clean verify)" }
if (-not (Test-Path $mcpJar)) { Add-Warn "missing artifact: $mcpJar (run mvn clean verify)" }

$composeFile = "$root\docker-compose.prod.yml"
if (-not (Test-Path $composeFile)) {
    Add-Error "missing docker-compose.prod.yml"
}

$gatewayConfig = "$root\infra\nginx\nginx.conf"
if (-not (Test-Path $gatewayConfig)) {
    Add-Error "missing gateway config: $gatewayConfig"
}
$gatewayTlsConfig = "$root\infra\nginx\nginx-tls.conf"
if (-not (Test-Path $gatewayTlsConfig)) {
    Add-Error "missing gateway tls config: $gatewayTlsConfig"
}

$dbInitSql = "$root\..\us_stock_monitor_dev.sql"
if (-not (Test-Path $dbInitSql)) {
    Add-Error "missing database init SQL: $dbInitSql"
} else {
    $dbInitItem = Get-Item $dbInitSql
    if ($dbInitItem.PSIsContainer) {
        Add-Error "database init SQL path points to a directory: $dbInitSql"
    }
}

$envProdPath = "$root\.env.prod"
if (-not (Test-Path $envProdPath)) {
    Add-Warn ".env.prod not found (copy from .env.prod.example before production launch)"
}

if ($StrictApi) {
    $apiKey = Get-EffectiveSecret "APP_SECURITY_API_KEY" $envProdPath
    $openAiKey = Get-EffectiveSecret "OPENAI_API_KEY" $envProdPath
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Add-Error "APP_SECURITY_API_KEY/APP_SECURITY_API_KEY_FILE is empty (required in final production step)"
    }
    if ([string]::IsNullOrWhiteSpace($openAiKey)) {
        Add-Warn "OPENAI_API_KEY/OPENAI_API_KEY_FILE is empty (AI endpoints will degrade)"
    }
}

$gatewayConfigSelection = Get-EnvValue "GATEWAY_NGINX_CONF" $envProdPath
if ($gatewayConfigSelection -match "nginx-tls\.conf") {
    $tlsCrt = "$root\infra\secrets\tls\tls.crt"
    $tlsKey = "$root\infra\secrets\tls\tls.key"
    if (-not (Test-Path $tlsCrt)) { Add-Error "TLS cert missing for gateway: $tlsCrt" }
    if (-not (Test-Path $tlsKey)) { Add-Error "TLS key missing for gateway: $tlsKey" }
}

Write-Host "== Preflight Summary =="
if ($warnings.Count -gt 0) {
    Write-Host "Warnings:"
    $warnings | ForEach-Object { Write-Host " - $_" }
}
if ($errors.Count -gt 0) {
    Write-Host "Errors:"
    $errors | ForEach-Object { Write-Host " - $_" }
    exit 1
}
Write-Host "Preflight passed."
