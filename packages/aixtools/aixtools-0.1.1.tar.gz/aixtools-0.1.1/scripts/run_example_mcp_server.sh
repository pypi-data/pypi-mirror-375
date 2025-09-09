#!/bin/bash -eu
set -o pipefail

# Get script directory
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPTS_DIR/config.sh"

# Activate virtual environment (with special handling for Windows)
cd "$PROJECT_DIR"

# Run the example MCP server
fastmcp run \
    --transport http \
    "$PROJECT_DIR/aixtools/mcp/example_server.py"
