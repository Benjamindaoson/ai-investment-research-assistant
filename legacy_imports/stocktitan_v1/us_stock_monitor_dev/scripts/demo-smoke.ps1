$ErrorActionPreference = "Stop"

$base = "http://127.0.0.1:6060"

Write-Host "[1] GET /api/demo/health"
$health = Invoke-RestMethod -Uri "$base/api/demo/health" -Method Get -TimeoutSec 20
$health | ConvertTo-Json -Depth 6

Write-Host "[2] POST /api/demo/one-click"
$payload = @{
  sessionId = "resume-demo"
  symbol = "AAPL"
  strategyTemplateId = "earnings"
} | ConvertTo-Json

$demo = Invoke-RestMethod -Uri "$base/api/demo/one-click" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 40
$demo | ConvertTo-Json -Depth 8

Write-Host "[3] GET /api/ai/product/signals/metrics"
$metrics = Invoke-RestMethod -Uri "$base/api/ai/product/signals/metrics" -Method Get -TimeoutSec 20
$metrics | ConvertTo-Json -Depth 8

Write-Host "Demo smoke passed."
