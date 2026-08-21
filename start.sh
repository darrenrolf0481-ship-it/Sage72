#!/bin/bash
python3 server.py &
FRONTEND_PID=$!
npm run dev &
wait