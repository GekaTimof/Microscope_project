#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR")
VISUALIZATION_DIR="$PROJECT_ROOT/Visualization"

sudo env "PATH=$PATH" poetry run python3 "$VISUALIZATION_DIR/main.py" "$@"

