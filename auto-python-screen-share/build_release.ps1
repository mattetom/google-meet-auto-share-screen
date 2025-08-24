param(
  [string]$Version
)

$ErrorActionPreference = 'Stop'

function Resolve-ScriptRoot {
  if ($PSScriptRoot) { return $PSScriptRoot }
  if ($PSCommandPath) { return (Split-Path -Parent $PSCommandPath) }
  if ($MyInvocation.MyCommand.Path) { return (Split-Path -Parent $MyInvocation.MyCommand.Path) }
  throw 'Cannot resolve script root.'
}

function Get-CurrentVersionFromInstaller($installerPath) {
  $content = Get-Content -Raw -Path $installerPath
  $m = [Regex]::Match($content, '#define\s+MyAppVersion\s+"([^"]+)"')
  if (-not $m.Success) { throw "Cannot find MyAppVersion in $installerPath" }
  return $m.Groups[1].Value
}

function Bump-Patch($ver) {
  $parts = $ver.Split('.')
  if ($parts.Count -lt 3) { $parts = @($parts + (0) * (3 - $parts.Count)) }
  $parts[-1] = [int]$parts[-1] + 1
  return ($parts -join '.')
}

function Set-InstallerVersion($installerPath, $newVersion) {
  $content = Get-Content -Raw -Path $installerPath
  $updated = [Regex]::Replace($content, '(#define\s+MyAppVersion\s+")([^"]+)(")', "`$1$newVersion`$3")
  if ($updated -ne $content) { Set-Content -NoNewline -Path $installerPath -Value $updated }
}

try {
  $root = Resolve-ScriptRoot
  $repoRoot = Split-Path -Parent $root
  $installer = Join-Path $root 'installer.iss'
  $spec = Join-Path $root 'auto_screen_share.spec'
  $distExe = Join-Path $root 'dist' | Join-Path -ChildPath 'auto_screen_share.exe'
  $updatesDir = Join-Path $root 'updates'
  $releaseDir = Join-Path $root 'release'
  $venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'

  if (-not (Test-Path $venvPython)) { throw "Python venv not found at $venvPython" }
  if (-not (Test-Path $spec)) { throw "Spec file not found: $spec" }
  if (-not (Test-Path $installer)) { throw "Installer script not found: $installer" }

  # Decide version
  $current = Get-CurrentVersionFromInstaller $installer
  if (-not $Version -or [string]::IsNullOrWhiteSpace($Version)) {
    $Version = Bump-Patch $current
  }
  Write-Host "Release version: $Version (previous: $current)" -ForegroundColor Cyan

  # Ensure tools and deps
  & $venvPython -m pip install --upgrade pip setuptools wheel | Out-Null
  & $venvPython -m pip install -r (Join-Path $root 'requirements.txt') | Out-Null
  & $venvPython -m pip install pyinstaller | Out-Null

  # Build EXE with PyInstaller
  & $venvPython -m PyInstaller $spec --noconfirm --distpath (Join-Path $root 'dist') --workpath (Join-Path $root 'build')

  if (-not (Test-Path $distExe)) { throw "Build failed, EXE not found: $distExe" }

  # Update installer version and build
  Set-InstallerVersion -installerPath $installer -newVersion $Version

  # Build installer via ISCC
  $iscc = 'iscc.exe'
  if (-not (Get-Command $iscc -ErrorAction SilentlyContinue)) {
    $defaultIscc = 'C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe'
    if (Test-Path $defaultIscc) { $iscc = $defaultIscc } else { throw 'ISCC (Inno Setup) not found on PATH.' }
  }
  & $iscc "/DMyAppVersion=$Version" $installer
  if ($LASTEXITCODE -ne 0) { throw "ISCC failed with exit code $LASTEXITCODE" }

  # Determine installer output path (uses versioned filename in script)
  if (-not (Test-Path $releaseDir)) { New-Item -ItemType Directory -Path $releaseDir | Out-Null }
  $installerPattern = "AutoScreenShare_Installer_${Version}.exe"
  $installerPath = Join-Path $releaseDir $installerPattern
  if (-not (Test-Path $installerPath)) {
    # fallback to non-versioned if user edited script
    $fallback = Join-Path $releaseDir 'AutoScreenShare_Installer.exe'
    if (Test-Path $fallback) { $installerPath = $fallback } else { throw "Installer not found in $releaseDir" }
  }

  # Prepare update payload
  if (-not (Test-Path $updatesDir)) { New-Item -ItemType Directory -Path $updatesDir | Out-Null }
  $versionedName = "auto-screen-share_${Version}.exe"
  $updateExe = Join-Path $updatesDir $versionedName
  Copy-Item -Force $distExe $updateExe
  Set-Content -NoNewline -Path (Join-Path $updatesDir 'latest_version.txt') -Value $Version
  $updateHash = (Get-FileHash -Algorithm SHA256 -Path $updateExe).Hash
  Set-Content -NoNewline -Path ($updateExe + '.sha256') -Value $updateHash

  # Hash the installer
  $installerHash = (Get-FileHash -Algorithm SHA256 -Path $installerPath).Hash
  $installerSha = "$installerPath.sha256"
  Set-Content -NoNewline -Path $installerSha -Value $installerHash

  Write-Host ""; Write-Host "Build complete" -ForegroundColor Green
  Write-Host "  EXE:          $distExe"
  Write-Host "  Update EXE:   $updateExe" 
  Write-Host "  Update Hash:  $updateHash"
  Write-Host "  latest_version.txt: $(Join-Path $updatesDir 'latest_version.txt')"
  Write-Host "  Installer:    $installerPath"
  Write-Host "  Installer Hash: $installerHash"
  Write-Host "Upload updates/* to your site /updates/ and distribute the installer from release/."
}
catch {
  Write-Error $_
  exit 1
}
