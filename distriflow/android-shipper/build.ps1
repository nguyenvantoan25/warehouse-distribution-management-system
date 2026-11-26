$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & .\gradlew.bat --console plain assembleDebug testDebugUnitTest
    if ($LASTEXITCODE -ne 0) { throw 'Android build or tests failed.' }
    $artifactFolder = Join-Path $PSScriptRoot '..\artifacts'
    New-Item -ItemType Directory -Path $artifactFolder -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'app\build\outputs\apk\debug\app-debug.apk') -Destination (Join-Path $artifactFolder 'DistriFlow-Shipper-debug.apk')
    Get-FileHash -LiteralPath (Join-Path $artifactFolder 'DistriFlow-Shipper-debug.apk') -Algorithm SHA256
} finally { Pop-Location }
