#!/usr/bin/env sh
set -eu

TARGET="${1:-all}"

run_module() {
  module="$1"

  if [ ! -d "$module" ]; then
    echo "Missing module: $module"
    return 1
  fi

  if [ -f "$module/package.json" ]; then
    (cd "$module" && npm run dev)
  elif [ -f "$module/Makefile" ]; then
    (cd "$module" && make dev)
  else
    echo "No dev command configured for $module. Add package.json, Makefile, or customize scripts/dev.sh."
  fi
}

case "$TARGET" in
  backend|frontend|admin)
    run_module "$TARGET"
    ;;
  infra|infrastructure)
    docker compose up db redis
    ;;
  all)
    run_module backend &
    BACKEND_PID=$!
    run_module frontend &
    FRONTEND_PID=$!
    run_module admin &
    ADMIN_PID=$!
    trap 'kill "$BACKEND_PID" "$FRONTEND_PID" "$ADMIN_PID" 2>/dev/null || true' INT TERM
    wait
    ;;
  *)
    echo "Usage: $0 [backend|frontend|admin|infra|all]"
    exit 1
    ;;
esac
