#!/usr/bin/env sh
set -eu

ENVIRONMENT="${1:-}"

if [ -z "$ENVIRONMENT" ]; then
  echo "Usage: $0 [staging|production]"
  exit 1
fi

case "$ENVIRONMENT" in
  staging)
    echo "Deploying to staging using project-specific deployment settings."
    echo "Customize scripts/deploy.sh before enabling real deployments."
    ;;
  production)
    if [ "${DEPLOY_CONFIRM:-}" != "production" ]; then
      echo "Set DEPLOY_CONFIRM=production to deploy to production."
      exit 1
    fi
    echo "Run deploy/production-checklist.md before production deployment."
    echo "Customize scripts/deploy.sh before enabling real deployments."
    ;;
  *)
    echo "Usage: $0 [staging|production]"
    exit 1
    ;;
esac
