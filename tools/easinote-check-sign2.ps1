$dll = 'C:/MRE/support/easinote/MRE-Plugin/src/MrePlugin/bin/Release/net6.0-windows/MrePlugin.dll'
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$name = $asm.GetName()
Write-Host "FullName: $($name.FullName)"
Write-Host "Flags: $($name.Flags)"
Write-Host "Flags value: $([int]$name.Flags)"
$token = $name.GetPublicKeyToken()
Write-Host "Token is null: $($null -eq $token)"
if ($token -ne $null) {
    Write-Host "Token length: $($token.Length)"
    Write-Host "Token hex: $([BitConverter]::ToString($token))"
} else {
    Write-Host "Token: NULL (no strong name)"
}
$pk = $name.GetPublicKey()
Write-Host "PublicKey is null: $($null -eq $pk)"
if ($pk -ne $null) {
    Write-Host "PublicKey length: $($pk.Length)"
}
