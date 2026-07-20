$paths = @(
    'C:/MRE/support/easinote/MRE-Plugin/src/MrePlugin/obj/Release/net6.0-windows/MrePlugin.dll',
    'C:/MRE/support/easinote/MRE-Plugin/src/MrePlugin/bin/Release/net6.0-windows/MrePlugin.dll',
    'C:/Users/40466/AppData/Roaming/Seewo/EasiNote5/Extensions/MrePlugin/current/MrePlugin.dll'
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        $name = [System.Reflection.AssemblyName]::GetAssemblyName($p)
        Write-Host "---"
        Write-Host "Path: $p"
        Write-Host "Flags: $($name.Flags) (value: $([int]$name.Flags))"
        Write-Host "FullName: $($name.FullName)"
    } else {
        Write-Host "NOT FOUND: $p"
    }
}
