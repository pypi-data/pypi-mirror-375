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

# Run the server
streamlit run aixtools/log_view/app.py $*
