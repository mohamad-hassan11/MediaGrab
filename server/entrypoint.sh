#!/bin/sh
set -e

# Start the local PO Token provider HTTP server (bound to loopback only)
# used by the bgutil-ytdlp-pot-provider yt-dlp plugin.
node /opt/bgutil-ytdlp-pot-provider/server/build/main.js \
    --host 127.0.0.1 --port 4416 &

# Wait briefly for the provider to come up before serving traffic.
for _ in $(seq 1 20); do
    if curl -s -o /dev/null http://127.0.0.1:4416/; then
        break
    fi
    sleep 0.5
done

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
