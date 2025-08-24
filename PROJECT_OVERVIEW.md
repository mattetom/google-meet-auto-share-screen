# Project Overview — Google Meet Auto Screen Share

This repository contains two complementary ways to automate joining a Google Meet and starting screen sharing:
- A Chrome Extension (Manifest V3) that auto-joins and clicks “Present now” inside the Meet page.
- A Windows Python app that detects an active Meet window and uses OS-level automation to select and confirm full-screen sharing.

Use this document as the single source of truth for how things work, how to run/package, and common tweaks.

## Repository structure

- `auto-meet-screen-share/` — Chrome extension (MV3)
  - `manifest.json` — Declares content script, host permissions, icons
  - `meetContent.js` — Content script that auto-clicks Join and Present
  - `README.md` — Basic usage notes
  - `icons/` — Extension icons
- `auto-python-screen-share/` — Windows desktop helper (Python)
  - `auto_screen_share.py` — Main loop: finds Meet window, focuses, presses keys to share
  - `update_checker.py` — Optional self-updater (placeholder URL)
  - `requirements.txt` — Python dependencies
  - `auto_screen_share.spec` — PyInstaller spec
  - `installer.iss` — Inno Setup script (installs app and creates a scheduled task on logon)
  - `release/AutoScreenShare_Installer.exe` — Example built installer (if present)
- `Chrome extension screenshots/` — Visuals for the extension
- `README.md` — High-level repo instructions

## High-level architecture

Two layers work together or independently:
- In-page automation (extension): clicks UI elements on meet.google.com (Join/Present) using DOM selectors.
- OS-level automation (Python): once the Present dialog appears, simulates keystrokes to select Entire screen and confirm.

This split is necessary because browsers restrict webpage scripts from controlling OS-level share pickers.

## Chrome extension (MV3)

- Permissions
  - `host_permissions`: `*://meet.google.com/*`
  - `content_scripts.matches`: `*://meet.google.com/*-*` (typical Meet URL pattern)
  - `run_at`: `document_idle`
- Logic (`meetContent.js`)
  - On window load: waits 1s then tries to:
    - Find and click Join: queries `[aria-label='Partecipa ora'], [aria-label='Join now']` (fallback scans button text for “Partecipa”/“Join”).
    - When joined, find and click Present: queries `[aria-label='Present now'], [aria-label='Presenta ora']`.
  - Retries up to ~10 seconds per action, with logs to the console.

Notes:
- The script supports English and Italian labels. Add more locales by extending the selectors.
- The extension can bring up the Present UI but cannot select the OS-level share source.

## Windows Python app

Main file: `auto-python-screen-share/auto_screen_share.py`

Key functions:
- `find_meet_window()`
  - Uses `pygetwindow` to list windows with title starting “Meet - ” and matches regex `Meet - (\w{3,4}-){2}\w{3,4}`.
  - Returns the first matching window or `None`.
- `share_entire_screen()`
  - Uses `pyautogui` to simulate: Tab → Right → Right → Tab×2 → Enter
  - Intention: move focus to “Entire screen”, then to the Share button, then confirm.
- `monitor_meet()`
  - Infinite loop: looks for a Meet window, focuses it via `pywinctl`, waits 5s, then calls `share_entire_screen()`.
  - Debounces per window title to avoid repeating on the same call; rechecks every 120s when a call is active, 1s otherwise.

Self-update (optional): `update_checker.py`
- `UPDATE_URL` is a placeholder: `https://tuoserver.com/updates/`.
- Compares `latest_version.txt` vs local `version.txt`; if newer, downloads `auto-screen-share_<version>.exe`, replaces the executable, updates version file, relaunches.
- Requires a hosted update endpoint to be functional; otherwise it logs an error and continues.

Packaging & install
- PyInstaller spec: `auto_screen_share.spec` builds `auto_screen_share.exe` (windowless, UPX enabled).
- Inno Setup: `installer.iss`
  - Installs to `{commonpf}\AutoScreenShare`.
  - Creates a Scheduled Task on logon with highest privileges: `AutoScreenShare` → runs the EXE.
  - Uninstall removes task and app dir; installer may optionally launch the app post-install.

## Dependencies

Python packages (from `requirements.txt`):
- `pygetwindow` — enumerate windows by title
- `pywinctl` — activate/focus windows
- `pyautogui` — simulate keypresses
- `requests` — updater HTTP calls

External tools
- Google Chrome (for Meet)
- PyInstaller (build) and Inno Setup (installer) — optional
- Windows OS (the Python app targets Windows UI automation)

## Setup and usage

Chrome extension
- Load unpacked at `chrome://extensions`: select `auto-meet-screen-share/`.
- Join a Meet; the extension will attempt to click Join and Present automatically. Check DevTools console for logs.

Python app (dev run)
- From `auto-python-screen-share/`:
  - Install deps:
    - PowerShell: `pip install -r requirements.txt`
  - Run:
    - PowerShell: `python auto_screen_share.py`

Packaging (optional)
- PyInstaller one-file (example): `pyinstaller --onefile --noconsole auto_screen_share.py`
- Build installer: open `installer.iss` in Inno Setup Compiler and build. The script also registers a Scheduled Task on install.

## Limitations and caveats

- Language/locale: selectors currently support English and Italian. Different UI languages may require new selectors.
- Timing: keystroke sequence assumes the share dialog is focused and that Tab/Right order matches your Chrome/OS version and screen layout. Multi-monitor setups may differ.
- Window title pattern: the regex targets codes like `abcd-efgh-ijkl`. If Google changes title formats, detection may fail. Adjust `find_meet_window()` as needed.
- Permissions: installer uses admin privileges and creates a task with highest run level. Some environments may restrict this.
- Updater: `UPDATE_URL` is a stub; without a real endpoint, updates won’t apply (but the app continues to work).

## Common tweaks (quick reference)

- Add another language for selectors (extension):
  - Edit `auto-meet-screen-share/meetContent.js` and extend the query selectors/fallback text checks for Join/Present.
- Slow/fast UI transitions:
  - Adjust `setTimeout` delays in `meetContent.js` and `time.sleep(...)` values in `auto_screen_share.py`.
- Different window titles:
  - Update the regex in `find_meet_window()` or relax it by checking for `"Meet - "` only.
- Disable self-update:
  - Comment out the `update_checker.update_script()` call in `__main__` of `auto_screen_share.py`.

## Troubleshooting

- Nothing happens in Meet:
  - Open DevTools console to see extension logs; ensure extension is loaded for the current profile.
- Present dialog opens but doesn’t share:
  - Ensure the Python app is running and has focus permissions. Try increasing sleeps in `share_entire_screen()`.
- Wrong screen shared / selection doesn’t move:
  - The Tab/Arrow sequence may differ. Use `pyautogui` to script the exact sequence for your OS/Chrome version.
- Multiple calls in a row:
  - The Python app debounces per window title for 2 minutes. Reduce the 120s wait if needed.

## Security and privacy

- The extension only runs on `meet.google.com` and doesn’t request network permissions.
- The Python app simulates keystrokes globally; avoid running it while typing sensitive information.

## Future improvements (nice-to-have)

- More robust, language-agnostic selectors (role/text heuristics) and broader locale coverage.
- Detect and handle Chrome’s “Choose what to share” dialog variants and multi-monitor layouts more reliably.
- Add a simple UI tray icon to start/stop the Python helper and show status.
- Telemetry-free health logs to a local file for diagnostics (opt-in).
- Provide signed builds and a real update endpoint.

---
Last updated: 2025-08-24