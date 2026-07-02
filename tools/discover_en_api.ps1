$enDir = "C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801\Main"
$output = ""
function WriteLog($msg) { $script:output += $msg + "`r`n" }

# 注册依赖解析，指向 EasiNote 安装目录和 runtime 目录
$runtimeDir = Join-Path $enDir "runtimes\win\lib\net6.0"
$null = [System.AppDomain]::CurrentDomain.add_AssemblyResolve({
    param($sender, $args)
    $name = $args.Name.Split(',')[0].Trim()
    $searchPaths = @($enDir, (Join-Path $enDir "runtimes\win\lib\net6.0"))
    foreach ($dir in $searchPaths) {
        $dllPath = Join-Path $dir "$name.dll"
        if (Test-Path $dllPath) {
            Write-Host "  [resolve] $name -> $dllPath"
            return [System.Reflection.Assembly]::LoadFrom($dllPath)
        }
    }
    return $null
})

$dlls = @(
    "Cvte.Paint.Framework.dll",
    "Cvte.Paint.Shell.dll",
    "EasiNote.Api.dll",
    "EasiNote.PublicApi.dll",
    "Cvte.Core.dll",
    "EasiNote.Business.dll",
    "Cvte.GurnetUI.EasiNote.dll"
)

foreach ($dll in $dlls) {
    $path = Join-Path $enDir $dll
    if (-not (Test-Path $path)) { WriteLog "SKIP: $dll not found"; continue }
    try {
        $asm = [System.Reflection.Assembly]::LoadFrom($path)
        WriteLog "===== $dll ====="

        foreach ($t in $asm.GetExportedTypes()) {
            # ── Slide 类型 ──
            if ($t.Name -eq "Slide") {
                WriteLog "[Slide] $($t.FullName)"
                WriteLog "  BaseType: $($t.BaseType)"
                WriteLog "  IsPublic: $($t.IsPublic)  IsAbstract: $($t.IsAbstract)"
                WriteLog "  --- Constructors ---"
                foreach ($c in $t.GetConstructors() | Where-Object { $_.IsPublic }) {
                    $pars = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                    WriteLog "  ctor($pars)"
                }
                WriteLog "  --- Properties ---"
                foreach ($p in $t.GetProperties() | Where-Object { $_.DeclaringType -eq $t }) {
                    $gs = ""
                    if ($p.CanRead) { $gs += "get" }
                    if ($p.CanWrite) { $gs += ";set" }
                    if ($gs) {
                        WriteLog "  $($p.PropertyType.Name) $($p.Name) {$gs}"
                    }
                }
                WriteLog "  --- Key Methods ---"
                foreach ($m in $t.GetMethods() | Where-Object { $_.DeclaringType -eq $t -and $_.Name -match "Create|Add|Insert|Remove|Element|Slide|Page" }) {
                    $pars = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                    WriteLog "  $($m.ReturnType.Name) $($m.Name)($pars)"
                }
                WriteLog ""
            }

            # ── TextElement ──
            if ($t.Name -eq "TextElement" -and $t.IsPublic -and -not $t.IsAbstract) {
                WriteLog "[TextElement] $($t.FullName)"
                WriteLog "  BaseType: $($t.BaseType)"
                foreach ($c in $t.GetConstructors() | Where-Object { $_.IsPublic }) {
                    $pars = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                    WriteLog "  ctor($pars)"
                }
                foreach ($p in $t.GetProperties() | Where-Object { $_.DeclaringType -eq $t }) {
                    $gs = ""
                    if ($p.CanRead) { $gs += "get" }
                    if ($p.CanWrite) { $gs += ";set" }
                    WriteLog "  $($p.PropertyType.Name) $($p.Name) {$gs}"
                }
                WriteLog ""
            }

            # ── Image 相关类型 ──
            if ($t.Name -match "Image" -and $t.IsPublic -and -not $t.IsAbstract) {
                WriteLog "[$($t.Name)] $($t.FullName)"
                WriteLog "  BaseType: $($t.BaseType)"
                foreach ($c in $t.GetConstructors() | Where-Object { $_.IsPublic }) {
                    $pars = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                    WriteLog "  ctor($pars)"
                }
                WriteLog ""
            }

            # ── 带 Board/Editing 的类型的方法 ──
            if ($t.Name -match "Board|Editing|SlideApi|PageApi" -and $t.IsPublic) {
                $keyMethods = $t.GetMethods() | Where-Object {
                    $_.IsPublic -and $_.Name -match "Create|Add|Insert|Remove|New|Slide|Page"
                }
                if ($keyMethods) {
                    WriteLog "[$($t.Name)] $($t.FullName) -- key methods:"
                    foreach ($m in $keyMethods) {
                        $pars = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                        WriteLog "  $($m.ReturnType.Name) $($m.Name)($pars)"
                    }
                    WriteLog ""
                }
            }
        }
    } catch {
        WriteLog "ERROR loading $dll : $_"
    }
}

$outPath = Join-Path $env:TEMP "MrePlugin_ApiDiscovery.txt"
$output | Out-File -FilePath $outPath -Encoding UTF8
Write-Output "Discovery complete. Output: $outPath"
Write-Output $output
