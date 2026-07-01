# Posture Break Guard

Windows-only helper. After login, it shows a tray icon and counts while the computer is awake. It shows a save-your-work countdown before each break, then shows a full-screen black break overlay for the configured break interval.

## Install

Run from this repository. This creates a shortcut in your current user's Windows Startup folder and starts the guard immediately:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install_posture_break_guard.ps1 -WorkMinutes 45 -BreakMinutes 5
```

Change `45` and `5` to your preferred work and break minutes.
Use `-WarningSeconds 15` to change the pre-break countdown.

If keyboard/mouse blocking does not work on your computer, open PowerShell as administrator and install as an elevated scheduled task:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install_posture_break_guard.ps1 -WorkMinutes 45 -BreakMinutes 5 -RunAsAdmin
```

## Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\uninstall_posture_break_guard.ps1
```

## Notes

- The task starts at user login. Windows does not run normal user programs before login.
- The tray menu does not include an exit option, so breaks cannot be skipped casually.
- Sleep or hibernation suspends the script, so the countdown resumes after wake.
- Logs are written to `%LOCALAPPDATA%\PostureBreakGuard\guard.log`.
- If input blocking fails due to Windows permissions, the screen still locks.
