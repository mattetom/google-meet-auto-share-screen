; Preprocessor: version is injected via ISCC with /DMyAppVersion=...
#ifndef MyAppVersion
$11.0.5"
#endif
[Setup]
AppName=Auto Screen Share
AppVersion={#MyAppVersion}
DefaultDirName={commonpf}\AutoScreenShare
DefaultGroupName=Auto Screen Share
UninstallDisplayIcon={app}\auto_screen_share.exe
OutputDir=release
OutputBaseFilename=AutoScreenShare_Installer_{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64os


[Files]
Source: "dist\auto_screen_share.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Auto Screen Share"; Filename: "{app}\auto_screen_share.exe"

[Run]
Filename: "schtasks"; Parameters: "/Create /TN AutoScreenShare /TR """"{app}\auto_screen_share.exe"""" /SC ONLOGON /RL HIGHEST /F /NP"; Flags: runhidden runascurrentuser
Filename: "powershell"; Parameters: "-NoProfile -ExecutionPolicy Bypass -Command ""$app=''{app}''; $task=Get-ScheduledTask -TaskName ''AutoScreenShare''; $task.Settings.DisallowStartIfOnBatteries=$false; $task.Settings.StopIfGoingOnBatteries=$false; $action=New-ScheduledTaskAction -Execute (Join-Path $app ''auto_screen_share.exe'') -WorkingDirectory $app; Set-ScheduledTask -TaskName ''AutoScreenShare'' -Action $action -Settings $task.Settings"""; Flags: runhidden runascurrentuser

; Starts the application immediately after installation
Filename: "{app}\auto_screen_share.exe"; Description: "Start Auto Screen Share"; Flags: nowait postinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[UninstallRun]
; Removes the scheduled task upon uninstallation
Filename: "schtasks"; Parameters: "/Delete /TN AutoScreenShare /F"; Flags: runhidden runascurrentuser; RunOnceId: "RemoveTask"
