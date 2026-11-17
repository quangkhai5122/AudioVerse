$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.venv')) { py -3.11 -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python scripts/check_repo.py
python -m pytest
$env:AUDIOVERSE_DB_PATH = "$PWD\local_data\audioverse.db"
python -m audioverse.main
