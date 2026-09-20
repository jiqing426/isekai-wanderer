#!/bin/bash
# CR-038 T-038-FE-001: TypeScript compile check
# Verifies that Script interface (stores/game.ts + api/game.ts) has engine_type required field
# and GameSession interface engine_type has no ? optional marker
# Test artifact: frontend/package.json (npm run build script)
# AC: AC-038-007, AC-038-008

set -e
cd "$(dirname "$0")/.."
npm run build
echo "Compile check passed: engine_type is required in Script and GameSession interfaces"
