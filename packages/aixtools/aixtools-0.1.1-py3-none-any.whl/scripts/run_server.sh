#!/bin/bash -eu
set -o pipefail

#-----------------------------------------------------------------------------
#
# Template script for running the Chainlit server
#
#-----------------------------------------------------------------------------

# Get script directory
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPTS_DIR/config.sh"

# Activate virtual environment (with special handling for Windows)
cd "$PROJECT_DIR"

# Run linter before starting the server
"$SCRIPTS_DIR/lint.sh"

# Go into the sub-dir (most projects don't need this)
cd "$PROJECT_NAME"

# Run the server
chainlit run \
    --host 0.0.0.0 \
    --port $PORT \
    --root-path /$PROJECT_NAME \
    --watch \
    app.py
