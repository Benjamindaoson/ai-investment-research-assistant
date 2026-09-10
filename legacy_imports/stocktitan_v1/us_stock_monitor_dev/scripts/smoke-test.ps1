param(
    [string]$WebBase = "http://127.0.0.1:6060",
    [string]$McpBase = "http://127.0.0.1:7070",
    [string]$GatewayBase = "",
    [string]$ApiKeyHeader = "X-API-KEY",
    [string]$ApiKey = "",
    [string]$EnvFile = ".env.prod",
    [switch]$InsecureTls
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

function Assert-True([bool]$cond, [string]$message) {
    if (-not $cond) {
        throw $message
    }
}

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

function Get-EffectiveSecret([string]$key, [string]$envFilePath, [string]$rootPath) {
    $direct = Get-EnvValue $key $envFilePath
    if (-not [string]::IsNullOrWhiteSpace($direct)) {
        return $direct
    }
    $fileKey = "${key}_FILE"
    $secretFile = Resolve-SecretFilePath (Get-EnvValue $fileKey $envFilePath) $rootPath
    if ([string]::IsNullOrWhiteSpace($secretFile) -or -not (Test-Path $secretFile)) {
        return ""
    }
    return ((Get-Content $secretFile | Select-Object -First 1).Trim())
}

function Invoke-CurlJson([string]$method, [string]$url, [string]$body, [hashtable]$headers, [bool]$insecure) {
    $curlArgs = @("--noproxy", "*", "-s", "-X", $method, $url, "-w", "`n__HTTP_STATUS__:%{http_code}")
    $tempBodyFile = $null
    if ($insecure) {
        $curlArgs += "-k"
    }
    foreach ($k in $headers.Keys) {
        $curlArgs += @("-H", "${k}: $($headers[$k])")
    }
    if (-not [string]::IsNullOrWhiteSpace($body)) {
        $tempBodyFile = New-TemporaryFile
        Set-Content -Path $tempBodyFile.FullName -Value $body -NoNewline
        $curlArgs += @("-H", "Content-Type: application/json", "--data-binary", "@$($tempBodyFile.FullName)")
    }

    try {
        $raw = (curl.exe @curlArgs) -join "`n"
    } finally {
        if ($null -ne $tempBodyFile -and (Test-Path $tempBodyFile.FullName)) {
            Remove-Item $tempBodyFile.FullName -Force -ErrorAction SilentlyContinue
        }
    }
    $marker = "`n__HTTP_STATUS__:"
    $idx = $raw.LastIndexOf($marker)
    if ($idx -lt 0) {
        return [PSCustomObject]@{
            Status = 0
            Body = $raw
            Json = $null
        }
    }

    $bodyText = $raw.Substring(0, $idx)
    $statusText = $raw.Substring($idx + $marker.Length).Trim()
    $statusCode = 0
    [void][int]::TryParse($statusText, [ref]$statusCode)

    $json = $null
    try {
        if (-not [string]::IsNullOrWhiteSpace($bodyText)) {
            $json = $bodyText | ConvertFrom-Json
        }
    } catch {
        $json = $null
    }

    return [PSCustomObject]@{
        Status = $statusCode
        Body = $bodyText
        Json = $json
    }
}

Write-Host "== Smoke Test Start =="

$effectiveWebBase = $WebBase
$effectiveMcpBase = $McpBase
$effectiveSseBase = $McpBase
if (-not [string]::IsNullOrWhiteSpace($GatewayBase)) {
    $effectiveWebBase = $GatewayBase
    $effectiveMcpBase = "$GatewayBase/mcp"
    $effectiveSseBase = $GatewayBase
    if ($GatewayBase.StartsWith("https://")) {
        $gatewayHttpPort = Get-EnvValue "GATEWAY_HTTP_PORT" $EnvFile
        if ([string]::IsNullOrWhiteSpace($gatewayHttpPort)) {
            $gatewayHttpPort = "8080"
        }
        $gatewayUri = [Uri]$GatewayBase
        $effectiveSseBase = "http://$($gatewayUri.Host):$gatewayHttpPort"
    }
}

$webHealthResp = Invoke-CurlJson "GET" "$effectiveWebBase/actuator/health" "" @{} $InsecureTls
Assert-True ($webHealthResp.Status -eq 200) "web health status code is not 200"
Assert-True (($null -ne $webHealthResp.Json) -and ($webHealthResp.Json.status -eq "UP")) "web health is not UP"
Write-Host "web health: UP"

$mcpHealthResp = Invoke-CurlJson "GET" "$effectiveMcpBase/actuator/health" "" @{} $InsecureTls
Assert-True ($mcpHealthResp.Status -eq 200) "mcp health status code is not 200"
Assert-True (($null -ne $mcpHealthResp.Json) -and ($mcpHealthResp.Json.status -eq "UP")) "mcp health is not UP"
Write-Host "mcp health: UP"

$resolvedApiKey = if ([string]::IsNullOrWhiteSpace($ApiKey)) { Get-EffectiveSecret "APP_SECURITY_API_KEY" $EnvFile $root } else { $ApiKey }
$headers = @{}
if (-not [string]::IsNullOrWhiteSpace($resolvedApiKey)) {
    $headers[$ApiKeyHeader] = $resolvedApiKey
}

$overviewResp = Invoke-CurlJson "GET" "$effectiveWebBase/api/statistics/overview" "" $headers $InsecureTls
Assert-True ($overviewResp.Status -eq 200) "statistics overview status code is not 200"
Assert-True (($null -ne $overviewResp.Json) -and ($overviewResp.Json.code -eq 200)) "statistics overview failed"
Write-Host "statistics overview: OK"

$chatBody = @{ sessionId = "smoke-script"; message = "hello" } | ConvertTo-Json -Compress
$chatResp = Invoke-CurlJson "POST" "$effectiveWebBase/api/ai/enhanced/chat" $chatBody $headers $InsecureTls
Assert-True ($chatResp.Status -eq 200) "chat endpoint status code is not 200"
Assert-True (($null -ne $chatResp.Json) -and ($chatResp.Json.code -eq 200)) "chat endpoint failed"
Write-Host "chat endpoint: OK"

$invalidResp = Invoke-CurlJson "POST" "$effectiveWebBase/api/ai/enhanced/chat" "{invalid" $headers $InsecureTls
Assert-True (($invalidResp.Status -eq 400) -or ($invalidResp.Status -eq 401)) "invalid JSON request did not return HTTP 400/401"
Write-Host "invalid JSON handling: OK"

$curlArgs = @("--noproxy", "*", "-s", "-N", "-m", "5", "-i", "-H", "Accept: text/event-stream")
if ($InsecureTls) {
    $curlArgs += "-k"
}
if ($headers.ContainsKey($ApiKeyHeader)) {
    $curlArgs += @("-H", "${ApiKeyHeader}: $($headers[$ApiKeyHeader])")
}
$curlArgs += "$effectiveSseBase/sse"
$sseRaw = (curl.exe @curlArgs) -join "`n"
Assert-True (($sseRaw -match "HTTP/1.1 200")) "mcp sse did not return 200"
Assert-True (($sseRaw -match "event:endpoint")) "mcp sse response missing endpoint event"
Write-Host "mcp sse: OK"

Write-Host "== Smoke Test Passed =="
