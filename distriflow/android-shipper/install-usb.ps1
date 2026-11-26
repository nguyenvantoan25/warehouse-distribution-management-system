param([string]$Serial = '')
$ErrorActionPreference = 'Stop'
$androidSdkPath = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$adbPath = Join-Path $androidSdkPath 'platform-tools\adb.exe'
$apkPath = Join-Path $PSScriptRoot '..\artifacts\DistriFlow-Shipper-debug.apk'
if (!(Test-Path -LiteralPath $adbPath)) { throw 'Android platform-tools not found. Configure ANDROID_HOME.' }
if (!(Test-Path -LiteralPath $apkPath)) { throw 'APK not found. Run build.ps1 first.' }
$deviceLines = & $adbPath devices
$readyDevices = @($deviceLines | ForEach-Object { if ($_ -match '^(\S+)\s+device\s*$') { $Matches[1] } })
if (!$Serial) {
    if ($readyDevices.Count -ne 1) { throw 'Connect exactly one authorized device, or pass -Serial. Check USB debugging authorization.' }
    $Serial = $readyDevices[0]
}
if ($Serial -notin $readyDevices) { throw 'Selected device is offline, unauthorized or not connected.' }
& $adbPath -s $Serial install -r $apkPath
if ($LASTEXITCODE -ne 0) { throw 'APK installation failed.' }
& $adbPath -s $Serial reverse tcp:8000 tcp:8000
if ($LASTEXITCODE -ne 0) { throw 'USB reverse failed.' }
& $adbPath -s $Serial shell am start -n 'com.distriflow.shipper.debug/com.distriflow.shipper.ui.MainActivity'
if ($LASTEXITCODE -ne 0) { throw 'App launch failed.' }
Write-Output 'App installed. Server URL: http://127.0.0.1:8000. Backend must be running.'
