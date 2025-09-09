#!/bin/bash -eu
set -o pipefail

#-----------------------------------------------------------------------------
#
# Template script for running the linter
#
#-----------------------------------------------------------------------------


# Get script directory
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPTS_DIR/config.sh"

# Check if the fix parameter is provided
FIX_MODE=false
if [[ $# -gt 0 && "$1" == "--fix" ]]; then
    FIX_MODE=true
fi

# Run linter
if [ "$FIX_MODE" = true ]; then
    echo "Running linters in fix mode..."
    ruff format .
    ruff check --fix .
else
    echo "Running linters in check mode..."
    ruff format --check .
    ruff check .
fi
echo "Running pylint..."
pylint aixtools/
