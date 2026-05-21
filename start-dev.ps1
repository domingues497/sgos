$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root 'backend\api'
$frontendDir = Join-Path $root 'frontend'
$envFile = Join-Path $backendDir '.env'

if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { return }
    if ($line.StartsWith('#')) { return }
    $parts = $line.Split('=', 2)
    if ($parts.Count -ne 2) { return }
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()
    if ($key) { Set-Item -Path "Env:$key" -Value $value }
  }
}

if ($env:POSTGRES_HOST -eq 'localhost') { $env:POSTGRES_HOST = '127.0.0.1' }
if (-not $env:ALLOWED_HOSTS) { $env:ALLOWED_HOSTS = 'localhost,127.0.0.1' }
if (-not $env:DEBUG) { $env:DEBUG = 'True' }

Write-Host 'Abra 2 terminais e rode os comandos abaixo'
Write-Host ''
Write-Host 'Terminal 1 (backend)'
Write-Host ("cd `"{0}`"" -f $backendDir)
Write-Host 'python -m pip install -r requirements.txt'
Write-Host 'python manage.py migrate'
Write-Host 'python manage.py seed'
Write-Host 'python manage.py runserver 0.0.0.0:8000'
Write-Host ''
Write-Host 'Terminal 2 (frontend)'
Write-Host ("cd `"{0}`"" -f $frontendDir)
Write-Host 'python -m http.server 5501'
Write-Host ''
Write-Host 'URLs'
Write-Host 'Backend:  http://localhost:8000/api/'
Write-Host 'Frontend: http://localhost:5501/login.html'
