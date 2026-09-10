$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$mvn = Join-Path $root ".tools\apache-maven-3.9.12\bin\mvn.cmd"

if (-not (Test-Path $mvn)) {
  throw "Maven not found: $mvn"
}

Push-Location $root
try {
  & $mvn -pl stock-web -DskipTests package
  if ($LASTEXITCODE -ne 0) { throw "build failed" }

  $jar = Join-Path $root "stock-web\target\stock-web-1.0-SNAPSHOT.jar"
  if (-not (Test-Path $jar)) {
    throw "jar not found: $jar"
  }

  Write-Host "Starting demo at http://127.0.0.1:6060/demo/index.html"
  java -jar $jar --spring.profiles.active=demo --server.port=6060 --app.scheduler.enabled=false --spring.task.scheduling.enabled=false
}
finally {
  Pop-Location
}
