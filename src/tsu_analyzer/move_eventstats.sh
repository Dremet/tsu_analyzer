#!/bin/sh

# Path to the eventstats.json file
EVENT_STATS_FILE="./eventstats.json"

# Directory where the file should be moved
DEST_DIR=~/eventstats

# Ensure the destination directory exists
mkdir -p "$DEST_DIR"

# Attempt to extract the track name from the JSON file
TRACK_NAME=$(jq -r '.level.name // empty' "$EVENT_STATS_FILE" 2>/dev/null | tr -d ' ')

# Get the current timestamp in the desired format
CURRENT_TIMESTAMP=$(date "+%Y%m%d_%H%M%S")

# Base for the new filename: timestamp
NEW_FILE_NAME="${CURRENT_TIMESTAMP}"

# Add the track name if available
if [ -n "$TRACK_NAME" ]; then
  NEW_FILE_NAME="${NEW_FILE_NAME}_${TRACK_NAME}"
fi

# Append the file extension to the filename
NEW_FILE_NAME="${NEW_FILE_NAME}.json"

# Check if the source file exists and is not empty
if [ ! -s "$EVENT_STATS_FILE" ]; then
  echo "Warning: The file '$EVENT_STATS_FILE' is empty or does not exist. An empty document will be moved."
fi

# Move the eventstats.json file to the destination directory with the new filename
mv "$EVENT_STATS_FILE" "$DEST_DIR/$NEW_FILE_NAME"

echo "File successfully moved to: $DEST_DIR/$NEW_FILE_NAME"
