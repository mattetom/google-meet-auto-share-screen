# Auto Meet Screen Share

## Overview

This project contains:
- A Chrome extension that automates screen sharing on Google Meet (`auto-meet-screen-share/`).
- A Windows helper app that can auto-share and auto-update (`auto-python-screen-share/`).

## Chrome extension – Installation

1. Download or clone this repository.
2. Open Google Chrome and go to `chrome://extensions/`.
3. Enable "Developer mode" in the top right corner.
4. Click "Load unpacked" and select the `auto-meet-screen-share` folder.

## Chrome extension – Usage

1. Open Google Meet and start a meeting.
2. The extension will detect the meeting and initiate screen sharing.

## Windows app – Automated Build & Release (recommended)

A single script builds the EXE, prepares update files, and compiles a versioned installer.

Prerequisites
- Windows with PowerShell
- Inno Setup 6 (ISCC on PATH or installed to the default location)
- Python 3.x and a virtual environment at `.venv` in the repository root

Create the venv once (if you don’t have one):
- PowerShell
  - python -m venv .venv
  - .\.venv\Scripts\Activate

Run the unified release script from the repo root:
- PowerShell
  - .\auto-python-screen-share\build_release.ps1 -Version 1.0.3
  - Or auto-bump patch: .\auto-python-screen-share\build_release.ps1

What it does
- Installs/updates Python deps and PyInstaller in the venv
- Builds the Windows EXE via PyInstaller: `auto-python-screen-share/dist/auto_screen_share.exe`
- Prepares update payload in `auto-python-screen-share/updates/`:
  - `latest_version.txt`
  - `auto-screen-share_{version}.exe`
  - `auto-screen-share_{version}.exe.sha256`
- Compiles an Inno Setup installer with a versioned filename in `auto-python-screen-share/release/`:
  - `AutoScreenShare_Installer_{version}.exe`
  - `AutoScreenShare_Installer_{version}.exe.sha256`
- Prints SHA256 hashes for integrity checks

Hosting updates for auto-update
- Set `UPDATE_URL` in `auto-python-screen-share/update_checker.py` to your site, e.g.: `https://your-domain/updates/`
- Upload the contents of `auto-python-screen-share/updates/` to that path
- Clients will download `latest_version.txt` and the matching EXE

## Optional: Manual build steps (reference)

Create EXE manually (not recommended if using the script):
- pip install pyinstaller
- pyinstaller --onefile --noconsole auto_screen_share.py

Create installer manually:
- Install Inno Setup 6
- Open `auto-python-screen-share/installer.iss` in Inno Setup Compiler and Compile

## Debugging

- For the extension, open Chrome DevTools (F12 or Ctrl+Shift+I) to see logs.
- For the Windows app, run the built EXE from a console to view output.


