$ErrorActionPreference = 'Stop'
$portableNode = Join-Path $PSScriptRoot '..\.tools\node-v22.14.0-win-x64'
if (Test-Path -LiteralPath (Join-Path $portableNode 'node.exe')) { $env:Path = "$portableNode;$env:Path" }
Push-Location $PSScriptRoot
try { node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 }
finally { Pop-Location }
