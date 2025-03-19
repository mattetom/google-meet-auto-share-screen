[Setup]
AppName=Auto Screen Share
AppVersion=1.0
DefaultDirName={autopf}\AutoScreenShare
DefaultGroupName=Auto Screen Share
UninstallDisplayIcon={app}\auto_screen_share.exe
OutputDir=release
OutputBaseFilename=AutoScreenShare_Installer
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\auto_screen_share.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Auto Screen Share"; Filename: "{app}\auto_screen_share.exe"

[Run]
; Creates a scheduled task to auto-start the script at login with admin rights
Filename: "schtasks"; Parameters: "/Create /TN AutoScreenShare /TR ""{app}\auto_screen_share.exe"" /SC ONLOGON /RL HIGHEST /F"; Flags: runhidden

; Starts the application immediately after installation
Filename: "{app}\auto_screen_share.exe"; Description: "Start Auto Screen Share"; Flags: nowait postinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[UninstallRun]
; Removes the scheduled task upon uninstallation
Filename: "schtasks"; Parameters: "/Delete /TN AutoScreenShare /F"; Flags: runhidden; RunOnceId: "RemoveTask"
