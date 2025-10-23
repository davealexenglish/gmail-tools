#!/bin/bash
# Convenience script to run Gmail Tools with virtual environment activated

cd "$(dirname "$0")"
source venv/bin/activate
python cli.py "$@"
