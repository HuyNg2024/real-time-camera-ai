Set-Location $PSScriptRoot

$env:PGHOST = if ($env:PGHOST) { $env:PGHOST } else { "127.0.0.1" }
$env:PGPORT = if ($env:PGPORT) { $env:PGPORT } else { "15432" }
$env:PGDATABASE = if ($env:PGDATABASE) { $env:PGDATABASE } else { "camera_ai" }
$env:PGUSER = if ($env:PGUSER) { $env:PGUSER } else { "postgres" }
$env:PGPASSWORD = if ($env:PGPASSWORD) { $env:PGPASSWORD } else { "postgres" }

python .\seed_demo_data.py
