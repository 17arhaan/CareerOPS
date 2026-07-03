#!/bin/bash
# Double-click this in Finder to launch the CareerOPS app.
# It starts the local server and opens the app in your browser.
cd "$(dirname "$0")"
echo "Starting CareerOPS..."
python3 scripts/serve_dashboard.py &
SERVER_PID=$!
sleep 1
open "http://localhost:8787"
echo "App running at http://localhost:8787  (close this window to stop)"
trap "kill $SERVER_PID 2>/dev/null" EXIT
wait $SERVER_PID
