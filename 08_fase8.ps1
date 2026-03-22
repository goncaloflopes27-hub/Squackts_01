$ErrorActionPreference = 'Stop'
function Write-FileUtf8NoBom([string]$Path,[string]$Content){
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path,$Content,$utf8NoBom)
}
Write-Host 'Fase 8 OK'
