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
Filename: "{cmd}"; Parameters: "/C powershell -NoProfile -ExecutionPolicy Bypass -Command ""$app=\""{app}\""; echo 'Creating scheduled task...' > \""{app}\schtasks_create.log\""; Register-ScheduledTask -TaskName 'AutoScreenShare' -Action (New-ScheduledTaskAction -Execute (Join-Path $app 'auto_screen_share.exe') -WorkingDirectory $app) -Trigger (New-ScheduledTaskTrigger -AtLogOn) -RunLevel Highest -Force; echo 'SUCCESS: Task created successfully' >> \""{app}\schtasks_create.log\"""" > ""{app}\powershell_task.log"" 2>&1"; Flags: runhidden runascurrentuser waituntilterminated
Filename: "{cmd}"; Parameters: "/C powershell -NoProfile -ExecutionPolicy Bypass -Command ""$app=\""{app}\""; $task=Get-ScheduledTask -TaskName 'AutoScreenShare'; $task.Settings.DisallowStartIfOnBatteries=$false; $task.Settings.StopIfGoingOnBatteries=$false; $action=New-ScheduledTaskAction -Execute (Join-Path $app 'auto_screen_share.exe') -WorkingDirectory $app; Set-ScheduledTask -TaskName 'AutoScreenShare' -Action $action -Settings $task.Settings"" > ""{app}\powershell_config.log"" 2>&1"; Flags: runhidden runascurrentuser waituntilterminated

; Starts the application immediately after installation
Filename: "{app}\auto_screen_share.exe"; Description: "Start Auto Screen Share"; Flags: nowait postinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[UninstallRun]
; Removes the scheduled task upon uninstallation
Filename: "schtasks"; Parameters: "/Delete /TN AutoScreenShare /F"; Flags: runhidden runascurrentuser; RunOnceId: "RemoveTask"
