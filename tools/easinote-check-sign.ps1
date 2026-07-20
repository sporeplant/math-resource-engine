$dll = 'C:/MRE/support/easinote/MRE-Plugin/src/MrePlugin/bin/Release/net6.0-windows/MrePlugin.dll'
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$name = $asm.GetName()
$token = $name.GetPublicKeyToken()
Write-Host "FullName: $($name.FullName)"
Write-Host "Flags: $($name.Flags)"
Write-Host "ContentType: $($name.ContentType)"
if ($token -eq $null -or $token.Length -eq 0) {
    Write-Host "RESULT: UNSIGNED - no PublicKeyToken"
} else {
    Write-Host "RESULT: SIGNED - PublicKeyToken = $([BitConverter]::ToString($token))"
}
# Also check runtimeconfig for reference
Write-Host "---"
Get-Content 'C:/MRE/support/easinote/MRE-Plugin/src/MrePlugin/bin/Release/net6.0-windows/MrePlugin.runtimeconfig.json'
