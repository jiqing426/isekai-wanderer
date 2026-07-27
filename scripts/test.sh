#!/usr/bin/env sh
set -eu

TARGET="${1:-all}"

test_module() {
  module="$1"

  if [ ! -d "$module" ]; then
    echo "Missing module: $module"
    return 1
  fi

  if [ -f "$module/package.json" ]; then
    (cd "$module" && npm test)
  elif [ -f "$module/Makefile" ]; then
    (cd "$module" && make test)
  else
    echo "No test command configured for $module. Add package.json, Makefile, or customize scripts/test.sh."
  fi
}

case "$TARGET" in
  backend|frontend|admin)
    test_module "$TARGET"
    ;;
  e2e|system)
    if [ -f tests/package.json ]; then
      (cd tests && npm test)
    elif [ -f tests/Makefile ]; then
      (cd tests && make test)
    else
      echo "No system test command configured. Add tests/package.json, tests/Makefile, or customize scripts/test.sh."
    fi
    ;;
  all)
    test_module backend
    test_module frontend
    test_module admin
    "$0" system
    ;;
  *)
    echo "Usage: $0 [backend|frontend|admin|system|all]"
    exit 1
    ;;
esac
