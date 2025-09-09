#!/bin/bash -eu
set -o pipefail

# Get script directory
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPTS_DIR/config.sh"

cd "$PROJECT_DIR"

while true; do
    uv run aixtools/mcp/faulty_mcp.py "$@" || true
    echo "MCP server terminated. Restarting..."
done
