#!/bin/bash
set -e
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPTS_DIR/template"
echo "Installing backend-building-v2 dependencies..."
npm install
echo "Setup complete: $SCRIPTS_DIR/template"
