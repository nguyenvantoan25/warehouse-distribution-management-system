$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python -m app.setup.migrate
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed. Ensure PostgreSQL is running.' }
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} finally { Pop-Location }
