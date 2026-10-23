#!/usr/bin/env bash
cd "$(dirname "$0")"; [ -d .venv ] || ./setup.sh; source .venv/bin/activate; python -m arena gui
