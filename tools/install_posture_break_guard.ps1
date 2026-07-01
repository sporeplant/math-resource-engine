<#
.SYNOPSIS
  Installs or updates Posture Break Guard auto-start.
#>
param(
    [ValidateRange(1, 1440)]
    [int]$WorkMinutes = 45,

    [ValidateRange(1, 120)]
    [int]$BreakMinutes = 5,

    [ValidateRange(0, 300)]
    [int]$WarningSeconds = 15,

    [string]$TaskName = 'Posture Break Guard',

    [switch]$RunAsAdmin
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'posture_break_guard.ps1'
if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "Cannot find $scriptPath"
}

$quotedScriptPath = '"{0}"' -f $scriptPath
$arguments = '-NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File {0} -WorkMinutes {1} -BreakMinutes {2} -WarningSeconds {3}' -f $quotedScriptPath, $WorkMinutes, $BreakMinutes, $WarningSeconds

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments
if ($RunAsAdmin) {
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName

    "Installed and started scheduled task '$TaskName'. WorkMinutes=$WorkMinutes; BreakMinutes=$BreakMinutes; WarningSeconds=$WarningSeconds; RunLevel=Highest."
    exit 0
}

$startupDir = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDir "$TaskName.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = 'powershell.exe'
$shortcut.Arguments = $arguments
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.WindowStyle = 7
$shortcut.Description = 'Starts Posture Break Guard after Windows login.'
$shortcut.Save()

Start-Process -FilePath 'powershell.exe' -ArgumentList $arguments -WindowStyle Hidden

"Installed startup shortcut '$shortcutPath' and started guard. WorkMinutes=$WorkMinutes; BreakMinutes=$BreakMinutes; WarningSeconds=$WarningSeconds."
