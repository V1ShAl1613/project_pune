$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root 'backend')
& 'C:\Program Files\Python312\python.exe' -m pytest tests/test_executive_platform.py tests/test_database_models.py -q -p no:langsmith

Set-Location (Join-Path $root 'frontend')
npm run typecheck

Write-Host 'Enterprise validation completed'
