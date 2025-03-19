# Auto Meet Screen Share

## English

This Google Chrome extension automates the screen sharing process on Google Meet.

### Installation

1. Download or clone this repository.
2. Open Google Chrome and navigate to `chrome://extensions/`.
3. Enable "Developer mode" in the top right corner.
4. Click on "Load unpacked" and select the `auto-meet-screen-share` folder.

### Usage

1. Open Google Meet and start a meeting.
2. The extension will automatically detect the meeting and initiate screen sharing.

### Debugging

- Open the Chrome console (F12 or Ctrl+Shift+I) to see logs and any errors.

### Creating Executable

To create a standalone executable:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --onefile --noconsole auto_screen_share.py
   ```
   This will create a single executable file in the `dist` folder.

### Creating Installer

To create an installer using Inno Setup:

1. Install Inno Setup from [innosetup.com](https://jrsoftware.org/isinfo.php)
2. Open your `installer.iss` file with Inno Setup Compiler
3. Compile the installer by clicking on the "Compile" button or pressing F9
4. The compiled installer will be created in the output directory specified in your script


