#!/bin/bash

RECORDINGS_DIR="$1"

if [ -z "$RECORDINGS_DIR" ]; then
    RECORDINGS_DIR="/recordings"
fi

LOG_FILE="/tmp/finalize.log"

echo "[Finalize] Running at $(date)" >> "$LOG_FILE"
echo "[Finalize] RECORDINGS_DIR=$RECORDINGS_DIR" >> "$LOG_FILE"

timestamp=$(date +%Y-%m-%d_%H-%M-%S)

# Parent directory where the session folder is located
parent_dir=$(dirname "$RECORDINGS_DIR")
# New name for the folder
new_dir="${parent_dir}/${timestamp}"

echo "[Finalize] Renaming \"$RECORDINGS_DIR\" to \"$new_dir\"" >> "$LOG_FILE"
mv "$RECORDINGS_DIR" "$new_dir"

# --- New Part: find most recent .mp4 file ---
LATEST_FILE=$(find "$new_dir" -type f -iname "*.mp4" -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

if [[ -z "$LATEST_FILE" ]]; then
    echo "[Finalize] No MP4 files found in $new_dir" >> "$LOG_FILE"
    exit 0
fi

echo "[Finalize] Latest file: $LATEST_FILE" >> "$LOG_FILE"

# --- Set SRT file path to match video name ---
BASENAME="${LATEST_FILE%.*}"
SRT_FILE="${BASENAME}.srt"

# --- Curl to transcription service ---
TRANSCRIBE_URL="http://your-server-address/transcribe/srt"  # Change to your Flask server
LANGUAGE="en"  # Or leave empty for auto-detect

echo "[Finalize] Sending file to $TRANSCRIBE_URL" >> "$LOG_FILE"
curl -s -X POST \
    -F "file=@${LATEST_FILE}" \
    -F "language=${LANGUAGE}" \
    "$TRANSCRIBE_URL" \
    --output "$SRT_FILE"

if [[ -s "$SRT_FILE" ]]; then
    echo "[Finalize] SRT saved to $SRT_FILE" >> "$LOG_FILE"
else
    echo "[Finalize] Transcription failed or returned empty file" >> "$LOG_FILE"
fi

echo "[Finalize] Done." >> "$LOG_FILE"
