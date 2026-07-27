#!/usr/bin/env sh
set -eu

TARGET="${1:-all}"

build_module() {
  module="$1"

  if [ ! -d "$module" ]; then
    echo "Missing module: $module"
    return 1
  fi

  if [ -f "$module/package.json" ]; then
    (cd "$module" && npm run build)
  elif [ -f "$module/Makefile" ]; then
    (cd "$module" && make build)
  else
    echo "No build command configured for $module. Add package.json, Makefile, or customize scripts/build.sh."
  fi
}

case "$TARGET" in
  backend|frontend|admin)
    build_module "$TARGET"
    ;;
  all)
    build_module backend
    build_module frontend
    build_module admin
    ;;
  *)
    echo "Usage: $0 [backend|frontend|admin|all]"
    exit 1
    ;;
esac
