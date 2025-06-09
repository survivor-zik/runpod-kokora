#!/bin/bash

# Start the original FastAPI server in the background
echo "Starting FastAPI server..."
./entrypoint.sh &

# Wait a moment for the server to start
sleep 5

# Run your handler (if it's a continuous process)
echo "Starting handler..."
python -u handler.py

# Keep the container running
wait
