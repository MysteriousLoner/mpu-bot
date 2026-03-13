#!/bin/sh
# Runs main.py once daily at 18:00 (Asia/Kuala_Lumpur), appending to /app/output/schedule.log

echo "[entrypoint] Starting class reminder bot (runs daily at 18:00 MYT)..."
while true; do
    now_epoch=$(date +%s)
    target_epoch=$(date -d "$(date +%Y-%m-%d) 01:13:00" +%s)
    if [ "$now_epoch" -ge "$target_epoch" ]; then
        target_epoch=$(date -d "$(date -d 'tomorrow' +%Y-%m-%d) 01:13:00" +%s)
    fi
    sleep_secs=$((target_epoch - now_epoch))
    echo "[entrypoint] Next run at 01:13 MYT. Sleeping for ${sleep_secs}s..."
    sleep "$sleep_secs"
    echo "[entrypoint] Running main.py at $(date)..." >> /app/output/schedule.log
    python /app/src/main.py >> /app/output/schedule.log 2>&1
done
