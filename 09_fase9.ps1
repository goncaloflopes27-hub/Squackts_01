$ErrorActionPreference = 'Stop'
try {
  if (!(Test-Path .venv)) { py -3 -m venv .venv }
  .\.venv\Scripts\python -m pip install -r requirements.txt
  .\.venv\Scripts\python -m compileall .
  .\.venv\Scripts\python -c "import db; db.init_database(); print('DB OK')"
  $ws = New-Object -ComObject WScript.Shell
  $shortcut = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'),'SquackTS Enterprise.lnk'))
  $shortcut.TargetPath = (Resolve-Path .\.venv\Scripts\python.exe)
  $shortcut.Arguments = 'app.py'
  $shortcut.WorkingDirectory = (Get-Location).Path
  $shortcut.Save()
  .\.venv\Scripts\python app.py
  Write-Host 'SUCCESS'
} catch {
  Write-Host "FAIL: $($_.Exception.Message)"
  exit 1
}
