# EasiNote API Discovery v2 — with proper assembly resolution
$enDir = "C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801\Main"
$runtimeDir = "C:\Program Files (x86)\Seewo\EasiNote5\EasiNote5_5.2.4.9801\runtime"
$sharedFx = Join-Path $runtimeDir "shared\Microsoft.NETCore.App"
$sharedWpf = Join-Path $runtimeDir "shared\Microsoft.WindowsDesktop.App"

# Find actual shared framework version directories
$netcoreDir = Get-ChildItem $sharedFx -Directory | Sort-Object Name -Desc | Select-Object -First 1
$wpfDir = Get-ChildItem $sharedWpf -Directory | Sort-Object Name -Desc | Select-Object -First 1

$output = ""
function WriteLog($msg) { $script:output += $msg + "`r`n" }

WriteLog "Runtime base: $runtimeDir"
WriteLog "NETCore: $($netcoreDir.FullName)"
WriteLog "WPF: $($wpfDir.FullName)"
WriteLog ""

# Assembly resolver
$resolver = {
    param($sender, $args)
    $name = $args.Name.Split(',')[0].Trim()

    $searchPaths = @(
        $enDir,
        $netcoreDir.FullName,
        $wpfDir.FullName,
        (Join-Path $runtimeDir "runtimes\win\lib\net6.0")
    )

    foreach ($dir in $searchPaths) {
        $dllPath = Join-Path $dir "$name.dll"
        if (Test-Path $dllPath) {
            try {
                return [System.Reflection.Assembly]::LoadFrom($dllPath)
            } catch { }
        }
    }
    return $null
}

[System.AppDomain]::CurrentDomain.add_AssemblyResolve($resolver)

# DLLs to analyze
$dlls = @("Cvte.Paint.Framework.dll")

foreach ($dll in $dlls) {
    $path = Join-Path $enDir $dll
    if (-not (Test-Path $path)) { WriteLog "SKIP: $dll"; continue }
    try {
        $asm = [System.Reflection.Assembly]::LoadFrom($path)
        WriteLog "===== $dll ====="
        WriteLog "  FullName: $($asm.FullName)"

        $types = $asm.GetExportedTypes()
        WriteLog "  Exported types count: $($types.Count)"

        # Slide
        $slideType = $types | Where-Object { $_.Name -eq "Slide" } | Select-Object -First 1
        if ($slideType) {
            WriteLog ""
            WriteLog ">>> Slide: $($slideType.FullName)"
            WriteLog "    BaseType: $($slideType.BaseType)"
            WriteLog "    IsAbstract: $($slideType.IsAbstract)"

            WriteLog "    --- Public Constructors ---"
            foreach ($c in $slideType.GetConstructors()) {
                $pars = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                WriteLog "    $($slideType.Name)($pars)"
            }

            WriteLog "    --- Properties (declared on Slide) ---"
            foreach ($p in $slideType.GetProperties() | Where-Object { $_.DeclaringType -eq $slideType }) {
                $gs = & { if ($p.CanRead) { "get" } } + & { if ($p.CanWrite) { ";set" } }
                WriteLog "    $($p.PropertyType.Name) $($p.Name) {$gs}"
            }

            WriteLog "    --- Methods with Create/Add/Slide in name ---"
            foreach ($m in $slideType.GetMethods() | Where-Object { $_.Name -match "Create|Add|Insert|Remove|Slide|Element|Page" }) {
                $pars = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                WriteLog "    $($m.ReturnType.Name) $($m.Name)($pars)"
            }
        }

        # TextElement
        $textTypes = $types | Where-Object { $_.Name -eq "TextElement" -and -not $_.IsAbstract }
        foreach ($tt in $textTypes) {
            WriteLog ""
            WriteLog ">>> TextElement: $($tt.FullName)"
            WriteLog "    BaseType: $($tt.BaseType)"
            foreach ($c in $tt.GetConstructors() | Where-Object { $_.IsPublic }) {
                $pars = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                WriteLog "    ctor($pars)"
            }
            foreach ($p in $tt.GetProperties() | Where-Object { $_.DeclaringType -eq $tt }) {
                $gs = & { if ($p.CanRead) { "get" } } + & { if ($p.CanWrite) { ";set" } }
                WriteLog "    $($p.PropertyType.Name) $($p.Name) {$gs}"
            }
        }

        # All concrete Element types
        $elements = $types | Where-Object { $_.Name -match "Element$" -and -not $_.IsAbstract -and $_.IsPublic }
        WriteLog ""
        WriteLog ">>> All concrete *Element types: $($elements.Count)"
        foreach ($el in $elements | Select-Object -First 15) {
            $ctors = ($el.GetConstructors() | Where-Object { $_.IsPublic } | Measure-Object).Count
            WriteLog "    $($el.Name) ($($el.FullName)) — $ctors public ctors"
        }

        # Board/Editing types
        $boardTypes = $types | Where-Object { $_.Name -match "Board|Editing|SlideApi" -and $_.IsPublic }
        WriteLog ""
        WriteLog ">>> Board/Editing API types:"
        foreach ($bt in $boardTypes) {
            WriteLog "    $($bt.Name): $($bt.FullName)"
            $createMethods = $bt.GetMethods() | Where-Object { $_.Name -match "Create|Add|Insert" -and $_.IsPublic }
            foreach ($m in $createMethods) {
                $pars = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
                WriteLog "      $($m.ReturnType.Name) $($m.Name)($pars)"
            }
        }
    } catch {
        WriteLog "ERROR $dll : $_"
    }
}

$outPath = Join-Path $env:TEMP "MrePlugin_ApiDiscovery.txt"
$output | Out-File -FilePath $outPath -Encoding UTF8
Write-Output $output
