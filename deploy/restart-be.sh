#!/bin/bash
set -e
# Kill old uvicorn
pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
sleep 2
echo "Old uvicorn killed."

# Start new uvicorn with production .env
cd /root/isekai-wanderer/backend
source .venv/bin/activate
nohup python -c "
from app.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
" > /tmp/uvicorn-deploy2.log 2>&1 &
NEW_PID=$!
echo "New uvicorn PID: $NEW_PID"

# Wait for health
for i in $(seq 1 10); do
  sleep 1
  RESULT=$(curl -s http://localhost:8000/health 2>/dev/null || true)
  if echo "$RESULT" | grep -q "ok"; then
    echo "Health check PASSED: $RESULT"
    break
  fi
  if [ "$i" -eq 10 ]; then
    echo "Health check TIMEOUT after 10s"
    echo "=== Startup log ==="
    cat /tmp/uvicorn-deploy2.log | tail -30
  fi
done

echo "=== Startup warnings ==="
grep -iE "jwt|cors|warning|security|production|Uvicorn" /tmp/uvicorn-deploy2.log 2>/dev/null | head -15 || echo "(no matches)"
