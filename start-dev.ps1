$ErrorActionPreference = 'Stop'

param(
  [switch]$Run
)

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

if ($Run) {
  Start-Process -FilePath 'py' -WorkingDirectory $backendDir -ArgumentList @('manage.py','runserver','0.0.0.0:8010')
  Start-Process -FilePath 'py' -WorkingDirectory $frontendDir -ArgumentList @('-m','http.server','5010')
  Start-Process 'http://localhost:5010/login.html'
  return
}

Write-Host 'Abra 2 terminais e rode os comandos abaixo'
Write-Host ''
Write-Host 'Terminal 1 (backend)'
Write-Host ("cd `"{0}`"" -f $backendDir)
Write-Host 'py -m pip install -r requirements.txt'
Write-Host 'py manage.py migrate'
Write-Host 'py manage.py seed'
Write-Host 'py manage.py runserver 0.0.0.0:8010'
Write-Host ''
Write-Host 'Terminal 2 (frontend)'
Write-Host ("cd `"{0}`"" -f $frontendDir)
Write-Host 'py -m http.server 5010'
Write-Host ''
Write-Host 'URLs'
Write-Host 'Backend:  http://localhost:8010/api/'
Write-Host 'Frontend: http://localhost:5010/login.html'
