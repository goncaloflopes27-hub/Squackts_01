$ErrorActionPreference = 'Stop'
$dirs = @('repositories','services','ui','ui/dialogs','images','backups')
foreach($d in $dirs){ New-Item -ItemType Directory -Force -Path $d | Out-Null }
Write-Host 'Fase 1 OK'
