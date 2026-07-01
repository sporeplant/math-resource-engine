<#
.SYNOPSIS
  Tray app that periodically shows a full-screen break overlay.

.DESCRIPTION
  Counts only while Windows is awake and this process is running. Shows a tray
  icon with remaining time and a full-screen black overlay during breaks.
#>
param(
    [ValidateRange(1, 1440)]
    [int]$WorkMinutes = 45,

    [ValidateRange(1, 120)]
    [int]$BreakMinutes = 5,

    [ValidateRange(1, 60)]
    [int]$TickSeconds = 1,

    [ValidateRange(0, 300)]
    [int]$WarningSeconds = 15
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class PostureBreakIdleNative {
    [StructLayout(LayoutKind.Sequential)]
    public struct LASTINPUTINFO {
        public uint cbSize;
        public uint dwTime;
    }

    [DllImport("user32.dll")]
    public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

    [DllImport("kernel32.dll")]
    public static extern uint GetTickCount();
}
'@

function Write-GuardLog {
    param([string]$Message)

    $logDir = Join-Path $env:LOCALAPPDATA 'PostureBreakGuard'
    if (-not (Test-Path -LiteralPath $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }

    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -LiteralPath (Join-Path $logDir 'guard.log') -Value "[$stamp] $Message"
}

function Format-Remaining {
    param([int]$Seconds)

    $time = [TimeSpan]::FromSeconds([Math]::Max(0, $Seconds))
    if ($time.TotalHours -ge 1) {
        return '{0:00}:{1:00}:{2:00}' -f [Math]::Floor($time.TotalHours), $time.Minutes, $time.Seconds
    }

    return '{0:00}:{1:00}' -f $time.Minutes, $time.Seconds
}

function Get-IdleSeconds {
    $info = New-Object PostureBreakIdleNative+LASTINPUTINFO
    $info.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($info)
    if (-not [PostureBreakIdleNative]::GetLastInputInfo([ref]$info)) {
        return 0
    }

    $elapsedMilliseconds = [PostureBreakIdleNative]::GetTickCount() - $info.dwTime
    return [Math]::Max(0, [int]($elapsedMilliseconds / 1000))
}

function Update-TrayText {
    $remainingText = Format-Remaining -Seconds $script:remainingSeconds
    if ($script:isWaitingReturn) {
        $status = '等待回来确认'
    }
    elseif ($script:isIdleRestComplete) {
        $status = '离开已满足休息，回来后重新计时'
    }
    elseif ($script:isBreak) {
        $status = "休息中，剩余 $remainingText"
    }
    else {
        $status = "工作中，距离休息 $remainingText"
    }

    $script:statusItem.Text = $status
    $tip = "Posture Break Guard - $status"
    if ($tip.Length -gt 63) {
        $tip = $tip.Substring(0, 63)
    }
    $script:notifyIcon.Text = $tip
}

function Show-WarningWindow {
    Hide-WarningWindow

    $script:warningForm = New-Object System.Windows.Forms.Form
    $script:warningForm.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedToolWindow
    $script:warningForm.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $script:warningForm.Size = New-Object System.Drawing.Size(520, 180)
    $script:warningForm.BackColor = [System.Drawing.Color]::FromArgb(255, 248, 220)
    $script:warningForm.TopMost = $true
    $script:warningForm.ShowInTaskbar = $false
    $script:warningForm.Text = '即将进入休息'

    $script:warningLabel = New-Object System.Windows.Forms.Label
    $script:warningLabel.AutoSize = $false
    $script:warningLabel.Dock = [System.Windows.Forms.DockStyle]::Fill
    $script:warningLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $script:warningLabel.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 18, [System.Drawing.FontStyle]::Bold)
    $script:warningLabel.ForeColor = [System.Drawing.Color]::FromArgb(80, 40, 0)
    $script:warningForm.Controls.Add($script:warningLabel)

    Update-WarningWindow
    $script:warningForm.Show()
    $script:warningForm.Activate()
}

function Update-WarningWindow {
    if ($script:warningForm -and $script:warningLabel) {
        $seconds = [Math]::Max(0, $script:remainingSeconds)
        $script:warningLabel.Text = "还有 $seconds 秒进入强制休息`r`n请保存当前工作内容"
        $script:warningForm.TopMost = $true
    }
}

function Hide-WarningWindow {
    if ($script:warningForm) {
        $script:warningForm.Close()
        $script:warningForm.Dispose()
        $script:warningForm = $null
        $script:warningLabel = $null
    }
}

function Start-EnforcedBreak {
    Hide-WarningWindow
    $script:isBreak = $true
    $script:isWaitingReturn = $false
    $script:remainingSeconds = $BreakMinutes * 60
    Write-GuardLog "Break started for $BreakMinutes minute(s)."
    $script:notifyIcon.ShowBalloonTip(5000, '该休息了', "将显示全屏遮罩 $BreakMinutes 分钟，请离开电脑活动一下。", [System.Windows.Forms.ToolTipIcon]::Warning)
    Show-BreakOverlay
}

function Start-IdleRestComplete {
    Hide-WarningWindow
    $script:isIdleRestComplete = $true
    $script:remainingSeconds = 0
    Write-GuardLog "Idle rest completed after $BreakMinutes minute(s) away; waiting for activity."
    $script:notifyIcon.ShowBalloonTip(5000, '已自动完成休息', "检测到你已离开电脑至少 $BreakMinutes 分钟，回来后将重新开始计时。", [System.Windows.Forms.ToolTipIcon]::Info)
}

function Show-BreakOverlay {
    Hide-BreakOverlay
    $script:overlayForms = New-Object System.Collections.Generic.List[System.Windows.Forms.Form]

    foreach ($screen in [System.Windows.Forms.Screen]::AllScreens) {
        $form = New-Object System.Windows.Forms.Form
        $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
        $form.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
        $form.Bounds = $screen.Bounds
        $form.BackColor = [System.Drawing.Color]::Black
        $form.TopMost = $true
        $form.ShowInTaskbar = $false
        $form.KeyPreview = $true
        $form.Cursor = [System.Windows.Forms.Cursors]::None

        $label = New-Object System.Windows.Forms.Label
        $label.ForeColor = [System.Drawing.Color]::DimGray
        $label.BackColor = [System.Drawing.Color]::Black
        $label.AutoSize = $false
        $label.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
        $label.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 22, [System.Drawing.FontStyle]::Bold)
        $label.Text = '休息时间，请离开电脑活动一下。'
        $form.Controls.Add($label)

        $button = New-Object System.Windows.Forms.Button
        $button.Text = '我回来了，开始计时'
        $button.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 18, [System.Drawing.FontStyle]::Bold)
        $button.Size = New-Object System.Drawing.Size(360, 70)
        $button.BackColor = [System.Drawing.Color]::White
        $button.ForeColor = [System.Drawing.Color]::Black
        $button.FlatStyle = [System.Windows.Forms.FlatStyle]::Standard
        $button.Visible = $false
        $button.Add_Click({
            if ($script:isWaitingReturn) {
                Start-NextWorkSession
            }
        })
        $form.Controls.Add($button)
        $form.Tag = @{ Label = $label; Button = $button }
        $form.Add_Shown({ param($sender, $eventArgs) Update-OverlayControlLayout -Form $sender })
        $form.Add_Resize({ param($sender, $eventArgs) Update-OverlayControlLayout -Form $sender })

        $form.Add_KeyDown({ param($sender, $eventArgs) $eventArgs.Handled = $true; $eventArgs.SuppressKeyPress = $true })
        $form.Add_KeyPress({ param($sender, $eventArgs) $eventArgs.Handled = $true })
        $form.Add_MouseDown({ param($sender, $eventArgs) $sender.Activate() })
        $form.Add_Deactivate({ param($sender, $eventArgs) if ($script:isBreak -or $script:isWaitingReturn) { $sender.Activate() } })

        $form.Show()
        $form.Activate()
        $script:overlayForms.Add($form)
    }
}

function Update-OverlayControlLayout {
    param([System.Windows.Forms.Form]$Form)

    if (-not $Form -or -not $Form.Tag) {
        return
    }

    $label = $Form.Tag.Label
    $button = $Form.Tag.Button
    $label.Left = 0
    $label.Top = 0
    $label.Width = $Form.ClientSize.Width
    $label.Height = [int]($Form.ClientSize.Height * 0.62)
    $button.Left = [Math]::Max(0, [int](($Form.ClientSize.Width - $button.Width) / 2))
    $button.Top = [Math]::Max(0, [int]($label.Height + 20))
    $label.BringToFront()
    $button.BringToFront()
}

function Update-BreakOverlayText {
    if (-not $script:overlayForms) {
        return
    }

    foreach ($form in $script:overlayForms) {
        if ($form.Tag) {
            $label = $form.Tag.Label
            $button = $form.Tag.Button
            if ($script:isWaitingReturn) {
                $label.Text = "休息时间已到`r`n回来后请点击下方按钮开始下一轮计时"
                $button.Visible = $true
                $button.Enabled = $true
            }
            else {
                $label.Text = '休息时间，请离开电脑活动一下。'
                $button.Visible = $false
                $button.Enabled = $false
            }
            Update-OverlayControlLayout -Form $form
        }
    }
}

function Hide-BreakOverlay {
    if ($script:overlayForms) {
        foreach ($form in $script:overlayForms) {
            $form.Close()
            $form.Dispose()
        }
        $script:overlayForms = $null
    }
}

function Stop-EnforcedBreak {
    Hide-WarningWindow

    $script:isBreak = $false
    $script:isWaitingReturn = $true
    $script:remainingSeconds = 0
    Write-GuardLog 'Break ended; waiting for return confirmation.'
    Update-BreakOverlayText
    $script:notifyIcon.ShowBalloonTip(5000, '休息时间已到', '回来后请点击遮罩上的按钮开始下一轮计时。', [System.Windows.Forms.ToolTipIcon]::Info)
}

function Start-NextWorkSession {
    Hide-BreakOverlay
    Hide-WarningWindow
    $script:isBreak = $false
    $script:isWaitingReturn = $false
    $script:isIdleRestComplete = $false
    $script:remainingSeconds = $WorkMinutes * 60
    Write-GuardLog 'Next work session started after return confirmation.'
    $script:notifyIcon.ShowBalloonTip(5000, '已开始计时', "已开始新的 $WorkMinutes 分钟计时。", [System.Windows.Forms.ToolTipIcon]::Info)
}

Write-GuardLog "Guard started. WorkMinutes=$WorkMinutes; BreakMinutes=$BreakMinutes."

$script:isBreak = $false
$script:isWaitingReturn = $false
$script:isIdleRestComplete = $false
$script:overlayForms = $null
$script:warningForm = $null
$script:warningLabel = $null
$script:remainingSeconds = $WorkMinutes * 60

$script:notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$script:notifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$script:notifyIcon.Visible = $true

$menu = New-Object System.Windows.Forms.ContextMenuStrip
$script:statusItem = New-Object System.Windows.Forms.ToolStripMenuItem
$script:statusItem.Enabled = $false
[void]$menu.Items.Add($script:statusItem)

$script:notifyIcon.ContextMenuStrip = $menu
Update-TrayText
$script:notifyIcon.ShowBalloonTip(5000, '护背休息提醒已启动', "每 $WorkMinutes 分钟显示 $BreakMinutes 分钟休息遮罩。休息结束后需确认回来才会重新计时。", [System.Windows.Forms.ToolTipIcon]::Info)

$script:timer = New-Object System.Windows.Forms.Timer
$script:timer.Interval = $TickSeconds * 1000
$script:timer.Add_Tick({
    $idleSeconds = Get-IdleSeconds

    if (-not $script:isBreak -and -not $script:isWaitingReturn -and -not $script:isIdleRestComplete -and $idleSeconds -ge ($BreakMinutes * 60)) {
        Start-IdleRestComplete
    }
    elseif ($script:isIdleRestComplete) {
        if ($idleSeconds -lt 2) {
            Start-NextWorkSession
        }
    }
    else {
        $script:remainingSeconds -= $TickSeconds
    }

    if ($script:remainingSeconds -le 0) {
        if ($script:isWaitingReturn) {
            Update-BreakOverlayText
        }
        elseif ($script:isIdleRestComplete) {
            # Wait until the next real input before starting a new work session.
        }
        elseif ($script:isBreak) {
            Stop-EnforcedBreak
        }
        else {
            Start-EnforcedBreak
        }
    }
    elseif (-not $script:isBreak -and -not $script:isWaitingReturn -and $WarningSeconds -gt 0 -and $script:remainingSeconds -le $WarningSeconds) {
        if (-not $script:warningForm) {
            Show-WarningWindow
        }
        else {
            Update-WarningWindow
        }
    }
    elseif ($script:warningForm) {
        Hide-WarningWindow
    }
    if (($script:isBreak -or $script:isWaitingReturn) -and $script:overlayForms) {
        foreach ($form in $script:overlayForms) {
            $form.TopMost = $true
            $form.Activate()
        }
        Update-BreakOverlayText
    }
    Update-TrayText
})
$script:timer.Start()

try {
    [System.Windows.Forms.Application]::Run()
}
finally {
    Hide-BreakOverlay
    Hide-WarningWindow
    if ($script:notifyIcon) {
        $script:notifyIcon.Visible = $false
        $script:notifyIcon.Dispose()
    }
}
