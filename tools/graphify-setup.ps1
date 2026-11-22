# Cài graphify trên Windows (PowerShell). Chạy 1 lần trên máy mới:
#   powershell -ExecutionPolicy Bypass -File tools\graphify-setup.ps1
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
  Write-Host "Cài graphify..."
  if (Get-Command uv -ErrorAction SilentlyContinue) { uv tool install "graphifyy[gemini]" }
  elseif (Get-Command py -ErrorAction SilentlyContinue) { py -m pip install --user "graphifyy[gemini]" }
  else { python -m pip install --user "graphifyy[gemini]" }
}
if (Get-Command graphify -ErrorAction SilentlyContinue) {
  graphify hook install | Out-Null
  Write-Host "graphify sẵn sàng. Vault Obsidian: $root (Obsidian > Open folder as vault)"
} else {
  Write-Host "Chưa thấy lệnh graphify. Cài Python 3.10+ (python.org, tick 'Add to PATH') rồi chạy lại."
}
