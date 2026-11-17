#!/usr/bin/env bash
set -euo pipefail
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/check_repo.py
python -m pytest
python -m audioverse.main
