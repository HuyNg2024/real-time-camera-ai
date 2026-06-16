param(
    [switch]$KeepData
)

Set-Location $PSScriptRoot

$ErrorActionPreference = "Stop"

$env:PGHOST = "127.0.0.1"
$env:PGPORT = "15432"
$env:PGDATABASE = "camera_ai"
$env:PGUSER = "postgres"
$env:PGPASSWORD = "postgres"
$env:CAMERA_AI_API_BASE = "http://127.0.0.1:8000"

if ($KeepData) {
    Write-Host "[Docker] Stopping containers without deleting database volume..."
    docker compose down
}
else {
    Write-Host "[Docker] Resetting containers and database volume..."
    docker compose down -v
}

Write-Host "[Docker] Building and starting PostgreSQL + API..."
docker compose up -d --build

Write-Host "[API] Waiting for dashboard API..."
$ready = $false
for ($i = 1; $i -le 45; $i++) {
    try {
        $health = Invoke-RestMethod "$env:CAMERA_AI_API_BASE/health" -TimeoutSec 3
        if ($health.api -eq "ok" -and $health.database -eq "ok") {
            $ready = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    docker compose logs --tail=80 api
    throw "API did not become ready at $env:CAMERA_AI_API_BASE"
}

Write-Host "[Demo] Seeding demo detections, events, and alerts..."
.\run_seed_demo.ps1

Write-Host "[Test] Running system checks..."
.\test_system.ps1

Write-Host ""
Write-Host "Demo is ready: $env:CAMERA_AI_API_BASE/dashboard" -ForegroundColor Green
