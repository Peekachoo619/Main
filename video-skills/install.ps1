# Install the three video skills as personal Claude Code skills on this Windows PC.
# After this, they load in Claude Code in EVERY folder/repo you open.
#   powershell -ExecutionPolicy Bypass -File video-skills\install.ps1
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "skills"
$base = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$dest = Join-Path $base "skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($skill in "ffmpeg-skill", "design-to-motion", "voicestudio") {
  $target = Join-Path $dest $skill
  if (Test-Path $target) { Remove-Item -Recurse -Force $target }
  Copy-Item -Recurse (Join-Path $src $skill) $target
  Write-Host "installed $skill -> $target"
}
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Write-Host "NOTE: ffmpeg not found. Install it with: winget install Gyan.FFmpeg" }
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command py -ErrorAction SilentlyContinue)) { Write-Host "NOTE: Python 3.10+ not found. Install it with: winget install Python.Python.3.12" }
Write-Host "Done. Restart Claude Code to pick them up."
