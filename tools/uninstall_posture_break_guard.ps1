param(
    [string]$TaskName = 'Posture Break Guard'
)

$ErrorActionPreference = 'Stop'

$startupDir = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDir "$TaskName.lnk"
if (Test-Path -LiteralPath $shortcutPath) {
    Remove-Item -LiteralPath $shortcutPath -Force
    "Removed startup shortcut '$shortcutPath'."
}

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -eq $task) {
    "Scheduled task '$TaskName' is not installed."
    exit 0
}

Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
"Uninstalled scheduled task '$TaskName'."
