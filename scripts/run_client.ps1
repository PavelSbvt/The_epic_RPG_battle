$ProjectRoot = Split-Path $PSScriptRoot -Parent

$env:PYTHONPATH = "$ProjectRoot\src"

& "$ProjectRoot\.venv\Scripts\python.exe" "$ProjectRoot\src\server\client.py"