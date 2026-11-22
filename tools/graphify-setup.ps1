# Cai graphify tren Windows (PowerShell). Chay 1 lan tren may moi:
#   powershell -ExecutionPolicy Bypass -File tools\graphify-setup.ps1
# Luu y: file chi dung chu khong dau de Windows PowerShell 5.1 doc dung.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
  Write-Host "Dang cai graphify..."
  if (Get-Command uv -ErrorAction SilentlyContinue) { uv tool install "graphifyy[gemini]" }
  elseif (Get-Command py -ErrorAction SilentlyContinue) { py -m pip install --user "graphifyy[gemini]" }
  else { python -m pip install --user "graphifyy[gemini]" }
}
if (Get-Command graphify -ErrorAction SilentlyContinue) {
  graphify hook install | Out-Null
  Write-Host "graphify da san sang. Vault Obsidian: $root (Obsidian > Open folder as vault)"
} else {
  Write-Host "Chua thay lenh graphify. Cai Python 3.10+ tu python.org (tick 'Add python.exe to PATH'), dong PowerShell, mo lai roi chay lai file nay."
}
